
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/logs/', include('logs.urls'))  #nombre de la app "projects" y el archivo urls.py

]
