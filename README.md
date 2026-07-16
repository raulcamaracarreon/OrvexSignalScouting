# OrvexSignal Scouting

Aplicación web en Flask para localizar y filtrar establecimientos de México mediante la API del Directorio Estadístico Nacional de Unidades Económicas (DENUE) del INEGI.

El proyecto nació como una herramienta de scouting comercial para identificar negocios locales que podrían beneficiarse de soluciones digitales de atención, captación de prospectos y automatización.

## Funciones actuales

- Consulta de establecimientos mediante la API del DENUE.
- Búsqueda por actividad o palabra clave.
- Búsqueda alrededor de coordenadas geográficas.
- Radio configurable de hasta 5,000 metros.
- Filtro de negocios con teléfono.
- Filtro de negocios sin sitio web registrado en DENUE.
- Visualización de nombre, actividad, estrato, teléfono, colonia y ubicación.
- Interfaz web adaptable a escritorio y dispositivos móviles.

## Tecnologías

- Python 3.12
- Flask
- Requests
- python-dotenv
- HTML
- CSS

## Requisitos

- Python 3.12 o una versión compatible.
- Token gratuito de la API del DENUE.

El token puede solicitarse en el sitio oficial del INEGI:

https://www.inegi.org.mx/servicios/api_denue.html

## Instalación

Clona el repositorio:

    git clone https://github.com/raulcamaracarreon/OrvexSignalScouting.git

    Set-Location .\OrvexSignalScouting

Crea el entorno virtual:

    py -m venv .venv

    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

    & .\.venv\Scripts\Activate.ps1

Instala las dependencias:

    python -m pip install -r requirements.txt

## Configuración

Copia el archivo de ejemplo:

    Copy-Item '.env.example' '.env'

Abre el archivo `.env` y agrega tu token:

    DENUE_TOKEN=TU_TOKEN_DEL_DENUE

El archivo `.env` está excluido de Git y no debe compartirse.

## Ejecución

Ejecuta la aplicación:

    python .\app.py

Después abre en el navegador:

    http://127.0.0.1:5000

## Estado del proyecto

Primera versión funcional:

- Conexión con DENUE validada.
- Búsqueda geográfica operativa.
- Filtros comerciales operativos.
- Tabla de resultados operativa.

## Próximas mejoras consideradas

- Selección de entidad y municipio.
- Búsqueda mediante códigos SCIAN.
- Exportación a CSV y Excel.
- Mapa de establecimientos.
- Clasificación de prospectos.
- Seguimiento de contactos.
- Almacenamiento local con SQLite.

## Fuente de datos

Los datos son consultados mediante la API del DENUE del Instituto Nacional de Estadística y Geografía de México.

La ausencia de teléfono, correo o sitio web en un registro del DENUE no garantiza que el establecimiento carezca actualmente de esos medios. La información debe verificarse antes de utilizarse para decisiones comerciales.

## Seguridad

No deben incluirse en el repositorio:

- Tokens.
- Archivos `.env`.
- Entornos virtuales.
- Bases de prospectos.
- Teléfonos recopilados.
- Exportaciones comerciales.
- Información privada.

## Licencia

Este proyecto se distribuye bajo la licencia MIT.