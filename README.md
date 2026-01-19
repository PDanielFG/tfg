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

> Nota: El archivo `docker-compose.env` debe renombrarse a `docker-compose.yml` si se va a usar Docker.

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
* Configurar la base de datos en `settings.py` si es necesario
* Acceder a la aplicación en `localhost:8080`
* Ejecutar con Docker o manualmente según preferencia
