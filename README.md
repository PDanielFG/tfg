Para tener el software en funcionamiento hay que ejecutar los archivos de creacion de la base de datos y volcado de datos.
###estructura.sql y volcado.sql
Con el comando "mysql -u user -p database < archivo.sql"

Esto es debido a que la persona que usa el software es porque desea analizar las esadísticas de los usuarios que han accedido a la misma.

En caso de que se quiera cambiar la base de datos ir al archivo backend/core/settings.py en la sección databases, modificamos los datos de la base de datos.

El proyecto se inicia al poner localhost:8080
Hay dos opciones:
1.- Descargar el repositorio en tu equipo, y usar el archivo llamado docker-compose.env (el nombre debe de ser modificado por docker-compose.yml) 
frontend--> npm install, npm install -g @vue/cli, npm run serve

backend --> ir a la carpeta donde descargamos el proyecto, con la cmd entrar a la carpeta tfg (donde esta frontend y backend) y hacer "python -m venv env"
		activamos el ambiente en env/script/activate,
		vamos a la carpeta de backend con cd backend
		pip install -r requirements.txt
		python manage-py runserver

2.- Descargar el archivo original docker-compose.yml, simplemente ejecutar docker-compose up 
