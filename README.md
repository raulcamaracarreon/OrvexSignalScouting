# OrvexSignal Scouting

Aplicación web local en Flask para localizar, filtrar y exportar
establecimientos de México mediante la API del Directorio Estadístico
Nacional de Unidades Económicas (DENUE) del INEGI.

OrvexSignal Scouting fue creada como una herramienta de exploración
comercial para identificar negocios que podrían beneficiarse de
soluciones digitales de atención, captación de prospectos y
automatización.

## Estado

**Versión estable: 1.0.0**

El alcance funcional planeado está completo y validado mediante
búsquedas reales, filtros territoriales y comerciales, revisión en
Google Maps y exportaciones CSV y Excel.

## Funciones principales

- Cobertura de las 32 entidades federativas de México.
- Selección dinámica de municipios, alcaldías o demarcaciones.
- Opción para consultar todos los municipios de una entidad.
- Catálogo de 1,086 clases SCIAN México 2023.
- Búsqueda de actividades económicas por código o nombre.
- Búsqueda tolerante a mayúsculas, minúsculas y acentos.
- Consulta del DENUE por bloques acumulados de hasta 500 registros.
- Coberturas configurables de hasta 500, 1,000, 2,000 o 5,000
  establecimientos.
- Filtro para mostrar únicamente negocios con teléfono.
- Filtro para mostrar únicamente negocios sin sitio web registrado.
- Filtro local por colonia con coincidencias parciales.
- Visualización de nombre, actividad, estrato, teléfono, sitio web,
  colonia y ubicación.
- Enlace de verificación de cada negocio en Google Maps.
- Exportación del conjunto filtrado a CSV compatible con Excel.
- Exportación a XLSX con formato, filtros e hipervínculos.
- Interfaz adaptable a escritorio y dispositivos móviles.
- Tema visual oscuro de OrvexSignal.

## Flujo de trabajo

```text
Seleccionar entidad y municipio
→ buscar o indicar una clase SCIAN
→ elegir la cobertura de búsqueda
→ aplicar filtros comerciales y de colonia
→ revisar prospectos
→ verificar negocios en Google Maps
→ exportar CSV o Excel
```

## Cobertura DENUE

La aplicación consulta el DENUE en bloques consecutivos de hasta
500 registros y combina automáticamente los resultados.

Ejemplo:

```text
Cobertura 500   → hasta 1 consulta
Cobertura 1,000 → hasta 2 consultas
Cobertura 2,000 → hasta 4 consultas
Cobertura 5,000 → hasta 10 consultas
```

La recuperación se detiene antes cuando el DENUE devuelve un bloque
incompleto. Alcanzar la cobertura seleccionada no garantiza que se
hayan agotado todos los establecimientos disponibles.

## Tecnologías

- Python 3.12
- Flask
- Requests
- python-dotenv
- openpyxl
- HTML
- CSS
- JavaScript sin dependencias de frontend

## Requisitos

- Python 3.12 o una versión compatible.
- Token gratuito de la API del DENUE.
- Conexión a internet para consultar el DENUE y abrir Google Maps.

El token puede solicitarse en el sitio oficial del INEGI:

https://www.inegi.org.mx/servicios/api_denue.html

## Instalación en Windows PowerShell

Clona el repositorio:

```powershell
git clone https://github.com/raulcamaracarreon/OrvexSignalScouting.git

Set-Location .\OrvexSignalScouting
```

Crea y activa el entorno virtual:

```powershell
py -m venv .venv

Set-ExecutionPolicy `
  -Scope Process `
  -ExecutionPolicy Bypass `
  -Force

& .\.venv\Scripts\Activate.ps1
```

Instala las dependencias:

```powershell
python -m pip install -r requirements.txt
```

## Configuración

Copia el archivo de ejemplo:

```powershell
Copy-Item '.env.example' '.env'
```

Abre `.env` y agrega el token:

```text
DENUE_TOKEN=TU_TOKEN_DEL_DENUE
```

El archivo `.env` está excluido de Git y no debe compartirse.

## Ejecución

Con el entorno virtual activo:

```powershell
python .\app.py
```

Abre en el navegador:

```text
http://127.0.0.1:5000
```

La aplicación está configurada para uso local.

## Catálogos incluidos

### SCIAN México 2023

El catálogo compacto de clases SCIAN está en:

```text
static/data/scian_classes.json
```

Contiene código y título oficial de 1,086 clases económicas.

### Catálogo territorial

El catálogo de entidades y municipios está en:

```text
static/data/inegi_geo_catalog.json
```

Fue generado a partir del Servicio Web del Catálogo Único de Claves
Geoestadísticas del INEGI.

Para reconstruir o actualizar este catálogo:

```powershell
python .\scripts\build_geo_catalog.py
```

Después valida el archivo antes de publicarlo:

```powershell
python -c "import json, pathlib; p=pathlib.Path(r'.\static\data\inegi_geo_catalog.json'); d=json.loads(p.read_text(encoding='utf-8')); assert d['entity_count']==32; assert d['municipality_count']>=2400; print('GEO_CATALOG_OK', d['entity_count'], d['municipality_count'])"
```

## Exportaciones

Las exportaciones incluyen los prospectos que cumplen todos los
filtros seleccionados dentro de la cobertura examinada.

### CSV

- Codificación UTF-8 con BOM.
- Compatible con Excel.
- Protección básica contra fórmulas en celdas.

### Excel

- Archivo XLSX.
- Encabezados con formato.
- Filtros automáticos.
- Columnas ajustadas.
- Hipervínculos para sitios web y Google Maps.

## Interpretación de los datos

Los datos provienen del DENUE del INEGI.

La ausencia de teléfono, correo o sitio web en el DENUE no demuestra
que el negocio carezca actualmente de esos medios. Los datos pueden
estar incompletos o desactualizados y deben verificarse antes de tomar
decisiones comerciales.

El filtro “sin sitio web” significa únicamente que el DENUE no tiene
un sitio registrado para ese establecimiento.

El enlace de Google Maps facilita la verificación, pero no garantiza
una coincidencia exacta en todos los casos.

## Seguridad y privacidad

No deben incluirse en el repositorio:

- Tokens.
- Archivos `.env`.
- Entornos virtuales.
- Bases de prospectos.
- Teléfonos recopilados.
- Exportaciones comerciales.
- Información privada.
- URLs completas del DENUE que contengan el token.

El repositorio excluye mediante `.gitignore` los archivos locales y
comerciales sensibles.

## Alcance de la versión 1.0

La versión 1.0 está orientada a exploración y exportación de
prospectos. No incluye:

- CRM.
- Envío de mensajes.
- Automatización de campañas.
- Base de datos de contactos trabajados.
- Seguimiento de respuestas.
- Clasificación automática de prospectos.

Estas funciones solo deberían añadirse después de validar una
necesidad operativa real.

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo
`LICENSE`.
