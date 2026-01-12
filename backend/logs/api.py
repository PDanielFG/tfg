from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import connection
from datetime import datetime, timedelta
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth

import csv  # para poder usar csv.writer
from django.http import HttpResponse  # para poder devolver HttpResponse
from django.db.models import Count, Q  # para Count y Q
from .models import MysqlLogLine  # o la ruta correcta a tu modelo






from .models import MysqlLogLine
from rest_framework import viewsets, permissions
from .serializers import LogSerializer
from .parser import parse_mysql_log     #Poner . para referirnos al archivo
from django.db.models import Max
from .utils import queryset_to_csv_response



class MysqlLogLineViewSet(viewsets.ReadOnlyModelViewSet):
    
    #Est se muestra al visitar la url de la API
    """
    ViewSet que permite:
    - Listar logs ya parseados (GET /api/logs/)
    - Obtener un log concreto     (GET /api/logs/<id>/)
    - Subir un archivo log        (POST /api/logs/upload/)
    """

    queryset = MysqlLogLine.objects.all()   # pylint: disable=no-member
    serializer_class = LogSerializer
    parser_classes = (MultiPartParser, FormParser)

    #En upload o en delete, como son operaciones que no devuelven nada no se usa el serializer
    @action(detail=False, methods=["post"], url_path="upload")
    def upload(self, request):

        # DEBUG opcional
        print("FILES:", request.FILES)
        print("DATA:", request.data)

        if "file" not in request.FILES:
            return Response(
                {"error": "Debes enviar un archivo con la clave 'file'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file = request.FILES["file"]
        print("Nombre archivo:", file.name)
        print("Tipo:", file.content_type)

        # Guardar archivo
        path = default_storage.save(f"uploads/{file.name}", file)

        # Parsear archivo
        parsed = parse_mysql_log(path)

        return Response(
            {"status": "ok", "filename": file.name, "parsed_lines": parsed},
            status=status.HTTP_200_OK,
        )
    
    @action(detail=False, methods=['delete'], url_path='delete_all')
    def delete_all(self, request):
        count, _ = MysqlLogLine.objects.all().delete()  # pylint: disable=no-member


        table_name=MysqlLogLine._meta.db_table  # pylint: disable=no-member
        if 'sqlite' in connection.vendor:  # Solo si estamos usando SQLite
            with connection.cursor() as cursor:
                #Django usa sqlite, no usa mysql, CUIDADO
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}';")

        return Response(
            {"status": "deleted", "deleted_records": count},
            status=status.HTTP_200_OK
        )
    
    #En desuso, por el endpoint connected_users_summary

    # @action(detail=False, methods=['get'], url_path='connected-users')
    # def connected_users(self, request):
    #     """
    #     Devuelve los usuarios únicos que se han conectado, con la última conexión.
    #     """
    #     users = (
    #         MysqlLogLine.objects  # pylint: disable=no-member
    #         .filter(command_type='Connect', user_host__isnull=False)
    #         .values('user_host')    #Selecciona solo la columna de la bd user_host root@localhost o ana@localhost
    #         .annotate(last_connected=Max('timestamp'))  #campo extra calculado, con la ultima fecha de conexion
    #         .order_by('user_host')  #ordena en funcion del noombre
    #     )

    #     #Para extraer solo el usuario, en vez de usuario@host
    #     result = [
    #         {
    #             'user': u['user_host'].split('@')[0],  # solo la parte antes de @
    #             'last_connected': u['last_connected']
    #         }
    #         for u in users
    #     ]

    #     return Response(result)
    
    #Aqui si se usa el serializdor porque nos interesa devolver todos los campos, y luego seleccionar en el frontend
    #cual mostramos
    @action(detail=False, methods=['get'], url_path='queryList')
    def query_list(self, request):
        """
        Devuelve todos los logs en formato JSON.
        """
        logs = self.get_queryset()  # MysqlLogLine.objects.all()
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    
    #ESTO AÑADE A NUESTRA URL POR DEFECTO /api/logs/ el final de "user/userName"
    #De momento no llama al serializer, porque devolvemos el diccionario con las dos claves, 
    #no usamos el serializer porque usa todos los campos del log, y solo nos interesa el usuario

    #El comentario anterior era de este mismo endpoint pero solo sacando el nombre de usuario a modo de prueba.
    #Ahora lo hemos modificado, siguiendo una logica parecida
    @action(detail=False, methods=['get'], url_path='user/(?P<username>[^/.]+)')
    def user_detail(self, request, username=None):
        """
        Devuelve usuario, su última conexión y todas sus queries.
        """

        # Obtener CONEXIONES del usuario
        connections = MysqlLogLine.objects.filter(  # pylint: disable=no-member
            command_type='Connect',
            #filtra los registros que empiecen por username@, por ejemplo root@...
            user_host__startswith=username + '@'    #username lo capturamos de la url dinamica y lo unimos a @
                                                    #lo que va despues del @ es desde donde se conectan a nuestro servidor de bd, @localhost, desde la maquina, @office-> desde la oficina...
                                                    #el servidor de bd será siempre el mismo, en este caso mi pc, pero puede ser cualqueira
        ).order_by('-timestamp')

        if not connections:
            return Response({'error': 'Usuario no encontrado'}, status=404)

        last_connection = connections[0].timestamp

        # Obtener QUERIES del usuario
        queries = MysqlLogLine.objects.filter(  # pylint: disable=no-member
            command_type='Query',
            user_host__startswith=username + '@'    #Igual, pero en vez de devolver las conexiones de x usuario, devuelve todas las queries que hace
        ).order_by('-timestamp')

        #Transformamos los objetos de django de nuestra bd (registro de cada logs) a formato json para devolverlo y usarlos
        query_serializer = LogSerializer(queries, many=True)

        # convierte de objeto django a json, los registros de mi bd de django filtrados anteriormente
        connection_serializer = LogSerializer(connections, many=True)


        #diccionario que devuelve toda la info.
        #Esto es para llamarlo en el frontend
        response_data = {
            "user": username,
            "last_connected": last_connection,
            "connections": connection_serializer.data,
            "queries": query_serializer.data
        }

        return Response(response_data)
    

    #Endpoint para ahorrar trabajo al front
    #Es concretamente para el grafico de complejidad de consultas y simples.
    #Para cuando haya muchisimas no sature
    @action(detail=False, methods=['get'], url_path='user/(?P<username>[^/.]+)/complexity')
    def user_complexity_queries(self, request, username=None):
        # Filtrar todas las queries del usuario
        queries = MysqlLogLine.objects.filter(      #pylint: disable=no-member
            command_type='Query',
            user_host__startswith=username + '@',   #Para saber las consultas que hace un determinado usuario
            was_error=False     #Para ignorar las consultas erroneas
        )

        total = queries.count()
        complejas = queries.filter(is_complex=True).count()
        simples = total - complejas

        # Devolver solo los datos necesarios
        #no hace falta devolver el usuario, porque para el grafico de front ya sabe el usuario por props selectedUSer que se le pasa al grafico
        response_data = {
            "total": total,
            "complejas": complejas,
            "simples": simples
        }

        return Response(response_data)
    
    #Errores de sintaxis o logicos
    @action(detail=False, methods=['get'], url_path='user/(?P<username>[^/.]+)/errors')
    def user_error_summary(self, request, username=None):
        
        # Filtrar todas las queries del usuario
        queries = MysqlLogLine.objects.filter(      #pylint: disable=no-member
            command_type='Query',
            user_host__startswith=username + '@', 
            # was_error=False       Error estoy contando los errores precisamente
        )

        # Contar errores por tipo
        syntax_errors = queries.filter(syntax_error=True).count()
        logic_errors = queries.filter(logic_error=True).count()

        return Response({
            "syntax_errors": syntax_errors,
            "logic_errors": logic_errors
        })
    
    #Queries correctas vs incorrecas
    @action(detail=False, methods=['get'], url_path='user/(?P<username>[^/.]+)/query-summary')
    def user_query_summary(self, request, username=None):

        # Filtrar todas las queries del usuario
        queries = MysqlLogLine.objects.filter(      #pylint: disable=no-member
            command_type='Query',
            user_host__startswith=username + '@', 
        )

        # Contar queries erróneas y correctas
        errores = queries.filter(was_error=True).count()
        correctas = queries.count() - errores

        return Response({
            "correctas": correctas,
            "erroneas": errores
        })
    
    
    # Gráfico de duración de conexión de sesión y queries por sesión
    @action(detail=False, methods=['get'], url_path='user/(?P<username>[^/.]+)/sessions-summary')
    def user_sessions_summary(self, request, username=None):
        group_by = request.query_params.get("group_by", "session")
        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")

        # Filtrar conexiones y queries del usuario
        connections = MysqlLogLine.objects.filter(
            command_type='Connect',
            user_host__startswith=username + '@'
        )
        queries = MysqlLogLine.objects.filter(
            command_type='Query',
            user_host__startswith=username + '@'
        )

        # Filtrar por rango de fechas
        if from_date:
            connections = connections.filter(timestamp__gte=from_date)
            queries = queries.filter(timestamp__gte=from_date)
        if to_date:
            to_dt = datetime.strptime(to_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            connections = connections.filter(timestamp__lte=to_dt)
            queries = queries.filter(timestamp__lte=to_dt)

        # --------------------------
        # Agrupación por sesión
        # --------------------------
        if group_by == "session":
            data = []
            for conn in connections.order_by('timestamp'):
                # Duración de la sesión
                duration_seconds = int(conn.connection_duration.total_seconds()) if conn.connection_duration else 0
                end_time = conn.timestamp + timedelta(seconds=duration_seconds)

                # Queries estrictamente dentro de la sesión y rango de fechas
                queries_in_session = queries.filter(
                    timestamp__gte=conn.timestamp,
                    timestamp__lte=end_time
                )

                queries_ok = queries_in_session.filter(was_error=False).count()
                queries_error = queries_in_session.filter(was_error=True).count()

                data.append({
                    "label": conn.timestamp.strftime("%Y-%m-%d %H:%M"),
                    "duration": duration_seconds,
                    "queries": queries_in_session.count(),
                    "queries_correct": queries_ok,
                    "queries_incorrect": queries_error
                })
            return Response(data)

        # --------------------------
        # Agrupación por día, semana o mes
        # --------------------------
        if group_by == "day":
            trunc = TruncDay("timestamp")
            date_format = "%Y-%m-%d"
        elif group_by == "week":
            trunc = TruncWeek("timestamp")
            date_format = "%Y-%m-%d"
        elif group_by == "month":
            trunc = TruncMonth("timestamp")
            date_format = "%Y-%m"
        else:
            return Response({"error": "group_by inválido"}, status=status.HTTP_400_BAD_REQUEST)

        # Agregación de duración
        connections_agg = (
            connections
            .annotate(period=trunc)
            .values("period")
            .annotate(duration=Sum("connection_duration"))
            .order_by("period")
        )

        # Agregación de queries
        queries_agg = (
            queries
            .annotate(period=trunc)
            .values("period")
            .annotate(
                queries_total=Count("id"),
                queries_correct=Count("id", filter=Q(was_error=False)),
                queries_incorrect=Count("id", filter=Q(was_error=True))
            )
        )

        # Crear mapa completo
        queries_map = { q["period"].strftime(date_format): q for q in queries_agg }

        # Construir lista final
        data = []
        for c in connections_agg:
            seconds = int(c["duration"].total_seconds()) if c["duration"] else 0
            period_str = c["period"].strftime(date_format)
            q_info = queries_map.get(period_str, {"queries_correct":0, "queries_incorrect":0, "queries_total":0})

            data.append({
                "label": period_str,
                "duration": seconds,
                "queries": q_info["queries_total"],
                "queries_correct": q_info["queries_correct"],
                "queries_incorrect": q_info["queries_incorrect"]
            })

        return Response(data)



    @action(detail=False, methods=['get'], url_path='user/(?P<username>[^/.]+)')
    def user_queries_summary(self, request, username=None):

        # Filtrar solo las queries correctas del usuario
        queries = MysqlLogLine.objects.filter(             #pylint: disable=no-member
            command_type='Query',
            user_host__startswith=username + '@',
            was_error=False
        ).values('sql_type', 'timestamp', 'command_text')  # Puedes devolver más campos si quieres

        # Convertir queryset a lista de diccionarios
        queries_list = list(queries)

        return Response({
            "queries": queries_list
        })
    
    
    @action(detail=False, methods=['get'], url_path='user/(?P<username>[^/.]+)/tablesAndColumns')
    def user_columns_summary(self, request, username=None):

        # Filtrar queries del usuario
        queries = MysqlLogLine.objects.filter(  #pylint: disable=no-member
            command_type='Query',
            user_host__startswith=username + '@',
            was_error=False
        )

        # Serializamos los resultados
        serializer = LogSerializer(queries, many=True)
        serialized_data = serializer.data  # Esto ya tiene 'columns' y 'tables'

        # Filtramos las que tienen columnas y tablas
        # data = [q for q in serialized_data if q.get("columns") and q.get("tables") and len(q["columns"]) == len(q["tables"])]

        data=serialized_data
        return Response({"queries": data})
    

    #Endpoint para el filtro de la pregunta de 
    # "Cuantos usuarios han hecho X consultas en X dias?"
    @action(detail=False, methods=['get'], url_path='connected-users-summary')
    def connected_users_summary(self, request):
        """
        Devuelve usuarios con:
        - última conexión
        - número de consultas
        - número de conexiones
        Permite filtrar por últimos X días (?days=7)
        """

        # Parámetro opcional ?days=7
        #Con esta modificación, al hacer hace X dias, incluye el dia entero, antes era dia y hora.
        #Hace 7 dias, el jueves pasado desde las 00:00 en vez desde las 19:01
        days = request.query_params.get("days")
        from_date = None

        if days:
            from_date = (
                datetime.now() - timedelta(days=int(days))
            ).replace(hour=0, minute=0, second=0, microsecond=0)

        # ---------------------------
        # Conexiones (última conexión + cantidad)
        # ---------------------------
        connections = MysqlLogLine.objects.filter(      #pylint: disable=no-member
            command_type='Connect',
            user_host__isnull=False
        )
        if from_date:
            connections = connections.filter(timestamp__gte=from_date)

        connections = (
            connections
            .values('user_host')
            .annotate(
                last_connected=Max('timestamp'),
                connections_count=Count('id')   # ← aquí agregamos conteo de conexiones
            )
        )

        # ---------------------------
        # Queries (conteo por usuario)
        # ---------------------------
        queries = MysqlLogLine.objects.filter(      #pylint: disable=no-member
            command_type='Query',
            user_host__isnull=False
        )
        if from_date:
            queries = queries.filter(timestamp__gte=from_date)

        queries = (
            queries
            .values('user_host')
            .annotate(queries_count=Count('id'))
        )

        # Crear un mapa de username → queries_count
        queries_map = {q['user_host'].split('@')[0]: q['queries_count'] for q in queries}

        # ---------------------------
        # Construir resultado final
        # ---------------------------
        result = []
        for c in connections:
            username = c['user_host'].split('@')[0]
            result.append({
                "user": username,
                "last_connected": c['last_connected'],
                "connections_count": c['connections_count'],  # nuevo campo
                "queries_count": queries_map.get(username, 0)
            })

        return Response(result)
    
    @action(detail=False, methods=["get"], url_path="export/csv")
    def export_all_csv(self, request):
        logs = MysqlLogLine.objects.exclude(user_host="test@localhost")

        fields = [
            "timestamp",
            "user_host",
            "command_type",
            "query",
            "was_error",
            "error_message",
            "syntax_error",
            "logic_error",

            "sql_type",
            "is_complex",
            "thread_id",
        ]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="mysql_logs.csv"'

        writer = csv.writer(response)

        # Cabecera
        writer.writerow(fields)

        # Campos de texto a limpiar
        text_fields = {"query", "error_message"}

        for log in logs:
            row = []
            for field in fields:
                value = getattr(log, field, "")

                # 🔥 LIMPIEZA DE SALTOS DE LÍNEA
                if field in text_fields and value:
                    value = str(value).replace("\r", " ").replace("\n", " ")

                if field == "timestamp" and value:
                    # Convertir a string sin zona horaria
                    value = value.strftime("%Y-%m-%d %H:%M:%S")

                row.append(value)

            writer.writerow(row)

        return response

    #endpoint de prueba del BACKEND (8000) para ver si se refresca con los contenedores levantados, para llamarlo en script en frontend 
    #cuando en mi naveagdor (front) aparece localhost:8080/#/... es vue, por eso no aparece, habria que modificar el router/index.js de frontent
    @action(detail=False, methods=["get"], url_path="pruebita")
    def prueba(self, request):
        mensaje = {"mensaje": "¡Endpoint de prueba funcionando!"}
        return Response(mensaje)