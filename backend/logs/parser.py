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
    r'(?P<year>\d{2})(?P<month>\d{1,2})(?P<day>\d{1,2})\s+'
    r'(?P<time>\d{1,2}:\d{1,2}:\d{1,2})\s+'
    r'(?P<thread_id>\d+)\s+'
    r'(?P<command_type>\w+)\s*'
    r'(?P<argument>.*)'
)

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

            
            #Crea datetime real con todo lo anterior
            year = 2000 + int(match.group('year'))
            month = int(match.group('month'))
            day = int(match.group('day'))
            hour, minute, second = map(int, match.group('time').split(':'))

            timestamp = datetime(year, month, day, hour, minute, second)



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


