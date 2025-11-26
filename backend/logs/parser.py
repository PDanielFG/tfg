# logs/parser.py
import re
from datetime import datetime
from logs.models import MysqlLogLine    

import sqlparse

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

SQL_KEYWORDS = (
    "select", "insert", "update", "delete", "create", "drop", "alter",
    "from", "where", "join", "on", "group", "order", "limit", "use", "show", "describe"
)


def is_valid_sql(query: str):
    """
    Valida SQL de forma permisiva pero detectando errores comunes.
    Devuelve (is_valid: bool, error_message: str|None)
    """
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

        # Comprobación de FROM
        if "from" not in query:
            # pero permitimos "select 1", "select database()" etc
            if not re.match(r"select\s+[\w\(\)\*]+", query):
                return False, "Missing FROM clause"

        # Detectar palabras sospechosas
        words = re.findall(r"[a-z_]+", query)
        for w in words:
            if w not in SQL_KEYWORDS and not re.match(r"[a-z_][a-z0-9_]*", w):
                return False, f"Unknown token '{w}'"

        return True, None

    # Otros comandos normales
    if query.startswith(("insert", "update", "delete", "create", "drop", "alter")):
        return True, None

    return False, f"Unknown or unsupported SQL command ({original})"


def parse_mysql_log(filepath):
    parsed_lines = 0

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

            argument= match.group("argument").strip()
            user_host = None
            query = ''
            was_error=False
            error_message=None

            command_type = match.group('command_type')

            # Extraer user@host si es Connect
            if match.group('command_type') == "Connect":
                m = re.search(r'(?P<user_host>[\w\-]+@[\w\.\-]+)', argument)
                if m:
                    user_host = m.group("user_host")
                query=argument
                was_error=False
                error_message=None
            elif command_type=="Quit":
                query=argument
                was_error=False
                error_message=None
            elif command_type=="Query":
                query=argument
                is_valid, error_message=is_valid_sql(query)
                was_error=not is_valid


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


