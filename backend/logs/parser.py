# logs/parser.py
import re
from datetime import datetime
from logs.models import MysqlLogLine    

import sqlparse
from sqlparse.sql import Identifier, IdentifierList
from sqlparse.tokens import Keyword, DML
from django.db import connection
from django.db import connections
from django.utils import timezone



EXISTING_TABLES = None
TABLE_COLUMNS = None



#Lee cada linea del txt, y extrae la info util
#El parser es el que mira la caja de papeles arrugados, los lee, ordena y extrae lo importante
#El modelo es la estanteria donde se guardan luego en nuestra bd

#regex->define el formato de las líneas utiles.
#Tiene los campos que extraeremos: date, time, thread_id, command_type, argument
LOG_PATTERN = re.compile(
    r'(?P<year>\d{2})(?P<month>\d{1,2})(?P<day>\d{1,2})\s+'
    r'(?P<time>\d{1,2}:\d{1,2}:\d{1,2})\s+'
    r'(?P<thread_id>\d+)\s+'
    r'(?P<command_type>\w+)\s*'
    r'(?P<argument>.*)'
)

#Diccionario de sintaxis de sql
SQL_KEYWORDS = (
    "select", "insert", "update", "delete", "create", "drop", "alter",
    "from", "where", "join", "on", "group", "order", "limit", "use", "show", "describe"
)


#Devuelve TODAS las tablas de la bd
def get_existing_tables():
    with connections['mysql_logs'].cursor() as cursor:  #Me conecto a la bd de practicas, con las credenciales en settings.py. Cursor es lo que ejecuta las consultas
        cursor.execute("SHOW TABLES;")  #Ejecuta al consulta
        return {row[0].lower() for row in cursor.fetchall()}    #Devuelve el indice 0 de la tupla anterior (nombre de tablas), lo pasa a minusculas (para comparar),y lo devuelve todo


#Devuelve las columnas de cada tabla. TODAS
def get_table_columns():
    table_columns = {}  #diccionario vacío  
    tables = get_existing_tables()  #Obtengo las tablas existentes, con la funcion anterior

    with connections['mysql_logs'].cursor() as cursor:
        for table in tables:
            cursor.execute(f"SHOW COLUMNS FROM `{table}`;") #Recorre cada tabla, para obtener las columnas de cada una de ellas
            cols = {row[0].lower() for row in cursor.fetchall()}  # row[0] es nombre de columna, el primer elemento, como arriba
            table_columns[table] = cols #a cada tabla (articulos) = se le asigna un set {id, .....}
    return table_columns   

#Obtener las tablas referenciadas de una query. IMPORTANTE
def extract_tables(sql):
    """Extrae nombres de tablas de FROM y JOIN, ignorando alias y columnas."""
    tables = []
                                    #[<DML 'SELECT'>, <Whitespace ' '>, <Identifier 'art_nom'>, <Whitespace ' '>, <Keyword 'FROM'>, <Whitespace ' '>, <Identifier 'articulos'>]
    parsed = sqlparse.parse(sql)    #[<Statement 'SELECT art_nom FROM articulos' at 0x...>], si hubiera mas consultas separadas por ; pondria mas posiciones
    
    if not parsed:  #
        return tables


    stmt = parsed[0]    #Cogemos la primera palabra
    tokens = list(stmt.tokens)  #Lo pasamos a lista

    #Recorre todos los tokens, i indice del token, token es el token actual
    for i, token in enumerate(tokens):
        # Buscar FROM o JOIN
        if token.ttype is Keyword and token.value.upper() in ("FROM", "JOIN"):
            # El siguiente token suele ser un Identifier o IdentifierList
            next_token = stmt.token_next(i)[1]
            if isinstance(next_token, IdentifierList):
                for identifier in next_token.get_identifiers():
                    real = identifier.get_real_name()
                    if real:
                        tables.append(real.lower())
            elif isinstance(next_token, Identifier):
                tables.append(next_token.get_real_name().lower())

    return tables


#Verifica si un objeto identifier, identifica una tabla en la bd o no
def identifier_is_table(identifier):
    """True si la estructura encaja con tabla [AS alias]"""
    return (
        isinstance(identifier, sqlparse.sql.Identifier) and
        identifier.get_real_name() is not None
    )

#Columnas mencionadas de una determinada query
def extract_columns(sql):
    parsed = sqlparse.parse(sql)
    if not parsed:
        return []

    stmt = parsed[0]
    collecting = False  #Estamos antes del select o no
    columns = []    

    for token in stmt.tokens:
        if token.ttype is DML and token.value.upper() == "SELECT":  #parte del select
            collecting = True
            continue

        if token.ttype is Keyword and token.value.upper() == "FROM":    #Fin de columna 
            break

        if not collecting:
            continue

         # Ignorar comas y whitespace
        if token.is_whitespace or token.ttype == sqlparse.tokens.Punctuation:
            continue

         # Ignorar asterisco y funciones
        if token.value.strip() == "*" or "(" in token.value:
            continue

        # Extraer columnas individuales
        if isinstance(token, IdentifierList):
            for identifier in token.get_identifiers():
                real_name = identifier.get_real_name()
                if real_name:
                    columns.append(real_name.lower())
        elif isinstance(token, Identifier):
            real_name = token.get_real_name()
            if real_name:
                columns.append(real_name.lower())
        else:
            # Token simple, como "art_num"
            columns.append(token.value.lower())

    return columns  # Devuelve columnas en minúsculas


#las columnas de mi query existen en la tabla mencionada
def validate_columns(query, tables_in_query, table_columns):
    """
    Valida columnas, soporta alias, tabla.col y funciones.
    """ 
    columns_in_query = extract_columns(query)   #Columnas de la query

    # Crear mapa alias → tabla
    #Recorre los tokens, por cada identifier que tenga alias crea un diccionario
    alias_map = {}
    parsed = sqlparse.parse(query)[0]
    for token in parsed.tokens:
        if isinstance(token, Identifier):
            table = token.get_real_name()
            alias = token.get_alias()

            if table and alias:
                alias_map[alias.lower()] = table.lower()

    #Por cada columna separa alias, y lo resuelve, comprueba si la tabla existe, y si contiene esa columna
    for col in columns_in_query:

        # Caso tabla.col → separar
        if '.' in col:
            table_alias, col_name = col.split('.', 1)

            # Resolver alias si es necesario
            table_real = alias_map.get(table_alias, table_alias)

            if table_real not in table_columns:
                return False, f"Table '{table_real}' does not exist"

            if col_name not in table_columns[table_real]:
                return False, f"Column '{col_name}' does not exist in table '{table_real}'"

            continue


        # Columna simple: buscar en todas las tablas, sin prefijo
        found = False
        for table in tables_in_query:
            if col in table_columns.get(table, set()):
                found = True
                break

        #si no lo encuentra, comprueba columnas mediante alias
        if not found:
            # Buscar en alias (u.col)
            for alias, real_table in alias_map.items():
                if col in table_columns.get(real_table, set()):
                    found = True
                    break
        #si no encuentra nada, devuelve error
        if not found:
            return False, f"Column '{col}' does not exist in any referenced table"

    return True, None   #none es el mensaje de error


def validate_sql(query: str):
    """
    Valida sintaxis SQL básica.
    Devuelve un mensaje de error en texto si la query es inválida,
    o None si está OK.
    """

    if not query or not query.strip():
        return "Error SQL: sentencia vacía o incompleta."

    q = query.lower().strip()

    # Normalización
    q_clean = " ".join(q.split())

       # =========================
    #       SELECT
    # =========================
    if q.startswith("select"):
        # SELECT sin columnas: "select from"
        if re.match(r"select\s+from\b", q_clean):
            return "Error SQL: falta especificar columnas en SELECT."

        # Si no hay FROM: permitir SELECT que sean solo expresiones, funciones o literales,
        # por ejemplo: SELECT 1, SELECT 'texto', SELECT now(), SELECT database(), SELECT 1+2
        if " from " not in q_clean:
            # Aceptamos SELECT <expr>[, <expr>...]
            # <expr> puede contener: letras, dígitos, guiones bajos, paréntesis, comillas simples/dobles,
            # puntos, operadores aritméticos y comas.
            # Nota: no intentamos parsear a fondo aquí, solo validar forma.
            if re.match(r"^select\s+[a-z0-9_\(\)\.\'\"]+([,\s\+\-\*\/\%a-z0-9_\(\)\.\'\"]*)*$", q_clean):
                # Consideramos válido: devolver None para que siga el flujo normal
                pass
            else:
                return "Error SQL: falta la cláusula FROM en la sentencia SELECT o sintaxis inválida para SELECT sin FROM."

        # FROM mal espaciado (p. ej., "*FROM")
        if "from" in q_clean and " from " not in q_clean:
            return "Error SQL: sintaxis incorrecta en la cláusula FROM."

        # SELECT FROM tabla → falta columnas
        if re.match(r"select\s+from\s+\w+", q_clean):
            return "Error SQL: deben especificarse columnas antes de FROM."

    # =========================
    #       UPDATE
    # =========================
    elif q.startswith("update"):

        # UPDATE tabla sin SET
        if " set " not in q_clean:
            return "Error SQL: falta la cláusula SET en la sentencia UPDATE."

        # UPDATE sin tabla → ej: "UPDATE SET"
        if re.match(r"update\s+set\b", q_clean):
            return "Error SQL: falta el nombre de la tabla en UPDATE."

    # =========================
    #       DELETE
    # =========================
    elif q.startswith("delete"):

        # DELETE sin FROM
        if " from " not in q_clean:
            return "Error SQL: falta la cláusula FROM en DELETE."

        # DELETE FROM → pero sin tabla
        if re.match(r"delete\s+from\s*$", q_clean):
            return "Error SQL: falta el nombre de la tabla en DELETE."

    # =========================
    #       INSERT
    # =========================
    elif q.startswith("insert"):

        # INSERT sin INTO
        if " into " not in q_clean:
            return "Error SQL: falta la cláusula INTO en INSERT."

        # INSERT INTO sin tabla
        if re.match(r"insert\s+into\s*$", q_clean):
            return "Error SQL: falta el nombre de la tabla en INSERT."

        # INSERT INTO tabla sin VALUES
        if " values " not in q_clean:
            return "Error SQL: falta la cláusula VALUES en INSERT."

    # =========================
    #   CONSULTA DEMASIADO CORTA
    # =========================
    tokens = q_clean.split()
    if len(tokens) < 2:
        return "Error SQL: sentencia demasiado corta o incompleta."

    # Si todo está OK
    return None


def is_valid_sql(query: str):
    """
    Valida SQL de forma permisiva pero detectando errores comunes.
    Devuelve (is_valid: bool, error_message: str|None)
    """
    #Variables globales para evitar consultas repetidas, gracias a la caché
    #Asi cada vez que subamos el .log, no habra una nueva conexion para verificar la existencia de tablas o columnas, 
    #sino que por muchas veces que subamos el .log solo habra una conexión extra (la que comprueba)
    #Asi tampoco crea logs nuevos innecesarios, con esas nuevas conexiones para comprobar
    global EXISTING_TABLES, TABLE_COLUMNS
    if EXISTING_TABLES is None:
        EXISTING_TABLES = get_existing_tables()
    if TABLE_COLUMNS is None:
        TABLE_COLUMNS = get_table_columns()

    original = query
    query = query.strip().lower()

    if not query:
        return False, "Empty query"
    
    # Comandos administrativos
    if query.startswith(("use", "show", "describe")):
        return True, None

    # Sólo analizamos SELECT en detalle
    if query.startswith("select"):

        # Error típico: SELECT ** 
        if "**" in query:
            return False, "Double asterisks '**'"

        # Paréntesis
        if query.count("(") != query.count(")"):
            return False, "Unbalanced parentheses"

        # Comillas
        if query.count("'") % 2 != 0 or query.count('"') % 2 != 0:
            return False, "Unbalanced quotes"

        # EXTRA: detectar "form" en vez de "from"
        if re.search(r"\bform\b", query):
            return False, "Typo detected: 'form' instead of 'from'"
        
        # tables_in_query = extract_tables(query)
        # columns_in_query = extract_columns(query)

        # # --- DEBUG: mostrar tablas y columnas detectadas ---
        # print("DEBUG: query:", query)
        # print("DEBUG: tablas encontradas en la query:", tables_in_query)
        # print("DEBUG: columnas encontradas en la query:", columns_in_query)
        # for table in tables_in_query:
        #     print(f"DEBUG: columnas de la tabla {table}:", TABLE_COLUMNS.get(table))

        # Comprobación de FROM
        if "from" not in query:
            # pero permitimos "select 1", "select database()" etc
            if re.match(r"^select\s+.+", query):
                return True, None
            else:
                return False, "Missing FROM clause"

        # Detectar palabras sospechosas
        words = re.findall(r"[a-z_]+", query)
        for w in words:
            if w not in SQL_KEYWORDS and not re.match(r"[a-z_][a-z0-9_]*", w):
                return False, f"Unknown token '{w}'"
            
        #validar tablas inexistentes
        tables_in_query = extract_tables(query)
        for table in tables_in_query:
            # print("DEBUG: tablas extraídas:", tables_in_query)  # <--- línea de debug
            if table not in EXISTING_TABLES:
                return False, f"Table '{table}' does not exist"

            
        #validar columnas inexistentes
        if tables_in_query:    
            is_valid_cols, error_cols = validate_columns(query, tables_in_query, TABLE_COLUMNS)
            if not is_valid_cols:
                return False, error_cols



        return True, None

    # Otros comandos normales
    if query.startswith(("insert", "update", "delete", "create", "drop", "alter")):
        return True, None

    return False, f"Unknown or unsupported SQL command ({original})"


def parse_mysql_log(filepath):
    parsed_lines = 0
    thread_user_map = {}  # <--- Mapa thread_id -> user_host


    with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:    #Abro el txt evitando posibles excepciones
        for raw_line in file:   #itero en cada linea
            line = raw_line.strip() #Elimino saltos de líneas y espacios al principio y fin

            # Saltar encabezados inútiles de XAMPP
            if line.startswith("C:\\xampp") or line.startswith("TCP Port") or line.startswith("Time"):
                continue

            #Si la linea no sigue el formato definido en el regex LOG_PATTERN la descarta
            match = LOG_PATTERN.match(line)     
            if not match:
                continue

            
            #Crea datetime real con todo lo anterior
            year = 2000 + int(match.group('year'))
            month = int(match.group('month'))
            day = int(match.group('day'))
            hour, minute, second = map(int, match.group('time').split(':'))

            timestamp = datetime(year, month, day, hour, minute, second)
            timestamp = timezone.make_aware(timestamp, timezone.get_current_timezone())


            argument= match.group("argument").strip()
            user_host = None
            query = ''
            was_error=False
            error_message=None

            command_type = match.group('command_type')
            thread_id = int(match.group('thread_id'))


            # Extraer user@host si es Connect
            if match.group('command_type') == "Connect":
                m = re.search(r'(?P<user_host>[\w\-]+@[\w\.\-]+)', argument)
                if m:
                    user_host = m.group("user_host")
                    thread_user_map[thread_id] = user_host  # <-- guardamos el usuario

                query=argument
                was_error=False
                error_message=None
            elif command_type=="Quit":
                query=argument
                was_error=False
                error_message=None
                user_host = thread_user_map.get(thread_id)  # <-- asignar usuario actual
                thread_user_map.pop(thread_id, None)

                # Obtener el último registro "Connect" con mismo thread_id
                last_connect = MysqlLogLine.objects.filter(      # pylint: disable=no-member
                    thread_id=thread_id,
                    command_type="Connect"
                ).order_by("-timestamp").first()

                if last_connect:
                    duration = timestamp - last_connect.timestamp

                    # Guardar duración en el registro "Connect"
                    last_connect.connection_duration = duration
                    last_connect.save()


            elif command_type == "Query":
                query = argument
                user_host = thread_user_map.get(thread_id)  # <-- asignamos usuario

                # 1️⃣ Validación básica de sintaxis
                error_message = validate_sql(query)
                was_error = error_message is not None

                # 2️⃣ Validación de tablas y columnas solo si no hubo error de sintaxis
                if not was_error:
                    is_valid, error_message_2 = is_valid_sql(query)
                    was_error = not is_valid
                    if error_message_2:
                        error_message = error_message_2

            
            # print(f"DEBUG: '{query}' | tablas extraídas: {extract_tables(query)} | was_error={was_error} | error_message={error_message}")


            #Crea el registro en la base de datos.
            #Con los campos del modelo
            MysqlLogLine.objects.create(    # pylint: disable=no-member
                timestamp=timestamp,
                thread_id=int(match.group('thread_id')),
                command_type=match.group('command_type'),
                user_host=user_host,
                query=query,
                raw=line,
                was_error=was_error,
                error_message=error_message,
            )

            parsed_lines += 1   #Contador de lineas parseadas

    return parsed_lines


