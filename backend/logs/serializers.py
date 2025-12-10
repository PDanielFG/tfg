from rest_framework import serializers
from .models import MysqlLogLine
from .parser import extract_columns, extract_tables     #llamamos a las funciones declaradas en el parser

class LogSerializer(serializers.ModelSerializer):

    #Como mi modelo no guarda explicitamente tablas y columnas de consulta lo indicamos asi
    tables = serializers.SerializerMethodField()
    columns = serializers.SerializerMethodField()


    class Meta:
        model = MysqlLogLine
        fields = "__all__"

    #Esto es para añadir al serializador los campos nuevos de tables y columns que no tiene el modelo y que llamamos con 
    #las funciones, tambien podriamos poner en vez de all todos los campos a mano
    def get_fields(self):
        fields = super().get_fields()
        # Añadir campos extra
        fields['tables'] = serializers.SerializerMethodField()
        fields['columns'] = serializers.SerializerMethodField()
        return fields

    #Funciones del parser
    def get_tables(self, obj):
        return extract_tables(obj.query) if obj.query else []

    def get_columns(self, obj):
        return extract_columns(obj.query) if obj.query else []
