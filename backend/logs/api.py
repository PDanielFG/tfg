from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import connection


from .models import MysqlLogLine
from rest_framework import viewsets, permissions
from .serializers import LogSerializer
from .parser import parse_mysql_log     #Poner . para referirnos al archivo
from django.db.models import Max

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
        with connection.cursor() as cursor:
            #Django usa sqlite, no usa mysql, CUIDADO
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}';")

        return Response(
            {"status": "deleted", "deleted_records": count},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=False, methods=['get'], url_path='connected-users')
    def connected_users(self, request):
        """
        Devuelve los usuarios únicos que se han conectado, con la última conexión.
        """
        users = (
            MysqlLogLine.objects  # pylint: disable=no-member
            .filter(command_type='Connect', user_host__isnull=False)
            .values('user_host')    #Selecciona solo la columna de la bd user_host root@localhost o ana@localhost
            .annotate(last_connected=Max('timestamp'))  #campo extra calculado, con la ultima fecha de conexion
            .order_by('user_host')  #ordena en funcion del noombre
        )

        #Para extraer solo el usuario, en vez de usuario@host
        result = [
            {
                'user': u['user_host'].split('@')[0],  # solo la parte antes de @
                'last_connected': u['last_connected']
            }
            for u in users
        ]

        return Response(result)
    
    @action(detail=False, methods=['get'], url_path='queryList')
    def query_list(self, request):
        """
        Devuelve todos los logs en formato JSON.
        """
        logs = self.get_queryset()  # MysqlLogLine.objects.all()
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
