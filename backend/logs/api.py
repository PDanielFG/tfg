from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser, FormParser

from .models import MysqlLogLine
from rest_framework import viewsets, permissions
from .serializers import LogSerializer
from .parser import parse_mysql_log     #Poner . para referirnos al archivo

class MysqlLogLineViewSet(viewsets.ReadOnlyModelViewSet):
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
