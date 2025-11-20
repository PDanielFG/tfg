# logs/parser.py
import re
from datetime import datetime
from logs.models import MysqlLogLine


#Lee cada linea del txt, y extrae la info util
#El parser es el que mira la caja de papeles arrugados, los lee, ordena y extrae lo importante
#El modelo es la estanteria donde se guardan luego en nuestra bd



#regex->define el formato de las líneas utiles.
#Tiene los campos que extraeremos: date, time, thread_id, command_type, argument

LOG_PATTERN = re.compile(
    r'(?P<date>\d{6})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+(?P<thread_id>\d+)\s+(?P<command_type>\w+)\s*(?P<argument>.*)'
)

#Hay que pulir detalles del parser, que parsee solo las consultas que hace el alumno, pero funciona bien
def parse_mysql_log(filepath):
    parsed_lines = 0

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:    #Abro el txt evitando posibles excepciones
        for raw_line in file:   #itero en cada linea
            line = raw_line.strip() #Elimino saltos de líneas y espacios al principio y fin

            # Saltar encabezados inútiles de XAMPP
            if line.startswith("C:\\xampp") or line.startswith("TCP Port") or line.startswith("Time"):
                continue

            #Si la linea no sigue el formato definido en el regex LOG_PATTERN la descarta
            match = LOG_PATTERN.match(line)     #???
            if not match:
                continue

            # Fecha YYMMDD
            date_raw = match.group('date')
            year = 2000 + int(date_raw[0:2])  # 25 → 2025
            month = int(date_raw[2:4])
            day = int(date_raw[4:6])

            #hora
            time_str = match.group('time')
            
            #Crea datetime real con todo lo anterior
            timestamp = datetime.strptime(f"{year}-{month}-{day} {time_str}", "%Y-%m-%d %H:%M:%S")


            #Crea el registro en la base de datos.
            #Con los campos del modelo
            MysqlLogLine.objects.create(    # pylint: disable=no-member
                timestamp=timestamp,
                thread_id=int(match.group('thread_id')),
                command_type=match.group('command_type'),
                query=match.group('argument').strip() if match.group('command_type') == "Query" else '',
                raw=line,
            )

            parsed_lines += 1   #Contador de lineas parseadas

    return parsed_lines


