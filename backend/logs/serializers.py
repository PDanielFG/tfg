from rest_framework import serializers
from .models import MysqlLogLine

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MysqlLogLine
        fields = "__all__"
