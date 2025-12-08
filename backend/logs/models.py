from django.db import models

# Create your models here.

# app_logs/models.py

#Guarda cada linea del log, ya procesado por el parser
from django.db import models

class MysqlLogLine(models.Model):
    timestamp = models.DateTimeField(db_index=True, null=True, blank=True)
    thread_id = models.IntegerField(null=True, blank=True, db_index=True)

    user_host = models.CharField(max_length=255, null=True, blank=True)
    database = models.CharField(max_length=64, null=True, blank=True)

    command_type = models.CharField(max_length=50, db_index=True, null=True, blank=True)
    sql_type = models.CharField(max_length=20, null=True, blank=True, db_index=True)

    query = models.TextField(null=True, blank=True)
    is_complex = models.BooleanField(default=False)

    was_error = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)

    raw = models.TextField()
    parsed_at = models.DateTimeField(auto_now_add=True)

    connection_duration = models.DurationField(null=True, blank=True)

    syntax_error = models.BooleanField(default=False)
    logic_error = models.BooleanField(default=False)


    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["command_type"]),
            models.Index(fields=["sql_type"]),
            models.Index(fields=["thread_id"]),
        ]
