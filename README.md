# Puesta en funcionamiento del software

## Base de datos

Para que el software funcione correctamente es necesario ejecutar los archivos de **creación de la base de datos** y **volcado de datos**:

* `estructura.sql`
* `volcado.sql`

Ejecutar ambos archivos con el siguiente comando:

```bash
mysql -u user -p database < archivo.sql
```

Este paso es necesario porque el software está diseñado para **analizar las estadísticas de los usuarios que han accedido a la aplicación**.

---

## Logs de prueba

Para **probar el proyecto** y validar el correcto funcionamiento del sistema de análisis, se proporciona un archivo de logs de ejemplo:

* `general.log`

Este archivo contiene **registros de prueba** que simulan accesos y actividad de usuarios en la aplicación. El software utiliza estos logs para generar estadísticas y métricas.

Asegúrate de que el archivo `general.log` esté ubicado en la ruta configurada en el proyecto (o en la ruta por defecto definida en la aplicación) antes de iniciar el backend.

### Activación de los logs generales (`general.log`)

#### ✅ Con XAMPP (MySQL / MariaDB)

1. Abrir el archivo `my.ini` (ubicación típica: `xampp/mysql/bin/my.ini`).
2. Buscar la sección `[mysqld]`.
3. Añadir o descomentar las siguientes líneas:

```ini
general_log = 1
general_log_file = "ruta/a/general.log"

---

#### ✅ Sin XAMPP

##### Windows

1. Abrir el archivo de configuración de MySQL (`my.ini` o `my.cnf`).
2. Añadir o descomentar:

```ini
general_log = 1
general_log_file = "C:/ruta/a/general.log"

##### Linux

1. Abrir el archivo de configuración de MySQL (`my.cnf` o `my.ini`).  
   - Normalmente se encuentra en `/etc/mysql/my.cnf` o `/etc/my.cnf`.
2. Añadir o descomentar:

```ini
general_log = 1
general_log_file = /var/log/mysql/general.log

##### macOS

1. Abrir el archivo de configuración de MySQL (`my.cnf` o `my.ini`).
   - Normalmente se encuentra en `/usr/local/etc/my.cnf` o `/etc/my.cnf`.
2. Añadir o descomentar:

```ini
general_log = 1
general_log_file = /usr/local/var/mysql/general.log

En todos los casos, reiniciar el servicio mysql.

---

## Configuración de la base de datos

Si se desea modificar la base de datos utilizada por el proyecto, hay que editar el archivo:

```
backend/core/settings.py
```

Dentro de la sección `DATABASES`, actualizar los datos de conexión correspondientes.

---

## Inicio del proyecto

La aplicación estará disponible en:

```
http://localhost:8080
```

Existen **dos formas de ejecutar el proyecto**:

---

## Opción 1: Ejecución manual (sin Docker)

### 1. Descargar el repositorio

Clonar o descargar el repositorio en el equipo local.

> Nota: El archivo `docker-compose.env` debe renombrarse a `docker-compose.yml`.

---

### 2. Frontend

```bash
npm install
npm install -g @vue/cli
npm run serve
```

---

### 3. Backend

Desde la carpeta raíz del proyecto (donde están `frontend` y `backend`):

```bash
python -m venv env
```

Activar el entorno virtual:

```bash
env/Scripts/activate
```

Acceder al backend e instalar dependencias:

```bash
cd backend
pip install -r requirements.txt
```

Ejecutar el servidor:

```bash
python manage.py runserver
```

---

## Opción 2: Ejecución con Docker

1. Descargar el archivo original `docker-compose.yml`
2. Ejecutar el siguiente comando:

```bash
docker-compose up
```

---

## Resumen

* Ejecutar los scripts SQL antes de iniciar el proyecto
* Utilizar el archivo `general.log` como **log de prueba** para validar el análisis de estadísticas
* Configurar la base de datos en `settings.py` si es necesario
* Acceder a la aplicación en `localhost:8080`
* Ejecutar con Docker o manualmente según preferencia
