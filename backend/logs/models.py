from django.db import models

# Create your models here.

# app_logs/models.py
from django.db import models

class MysqlLogLine(models.Model):
    timestamp = models.DateTimeField(db_index=True, null=True, blank=True)   # cuándo ocurrió
    thread_id = models.IntegerField(null=True, blank=True, db_index=True)
    user_host = models.CharField(max_length=255, null=True, blank=True)     # "root[root] @ localhost [127.0.0.1]"
    command_type = models.CharField(max_length=50, db_index=True, null=True, blank=True)  # Query, Connect, Quit, etc.
    database = models.CharField(max_length=64, null=True, blank=True)
    query = models.TextField(null=True, blank=True)                        # texto SQL (si aplica)
    raw = models.TextField()                                                # línea completa
    parsed_at = models.DateTimeField(auto_now_add=True)
    was_error = models.BooleanField(default=False)                         # si la entrada indica error (opcional)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["command_type"]),
        ]

    def __str__(self):
        return f"{self.timestamp} {self.command_type} {self.thread_id}"
