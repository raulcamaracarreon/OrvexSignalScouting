# OrvexSignal Scouting portable para Windows

La versión portable se construye desde el mismo repositorio que la
versión de desarrollo. No existe un segundo código fuente.

## Resultado esperado

```text
dist/
└── OrvexSignalScouting/
    ├── OrvexSignalScouting.exe
    ├── .env
    └── _internal/
```

Al abrir `OrvexSignalScouting.exe`:

1. Se carga el token del DENUE desde `.env`.
2. Se inicia el servidor local con Waitress.
3. Se selecciona un puerto disponible desde el 5000.
4. Se abre automáticamente el navegador.
5. La consola permanece abierta mientras se utiliza Scouting.

## Construcción en Windows PowerShell 5.1

Ubica el repositorio:

```powershell
Set-Location E:\Proyectos\OrvexSignalScouting
```

Confirma que existe el entorno virtual:

```powershell
Test-Path .\.venv\Scripts\python.exe
```

El resultado esperado es:

```text
True
```

Habilita temporalmente la ejecución de scripts:

```powershell
Set-ExecutionPolicy `
  -Scope Process `
  -ExecutionPolicy Bypass `
  -Force
```

Construye el portable:

```powershell
& .\scripts\build_portable.ps1
```

El script:

- instala las dependencias de `requirements-desktop.txt`;
- limpia construcciones anteriores;
- ejecuta PyInstaller en modo carpeta;
- incluye `templates` y `static`;
- copia el `.env` local a la carpeta portable;
- muestra la ruta final del ejecutable.

## Ejecución

Abre directamente:

```text
E:\Proyectos\OrvexSignalScouting\dist\OrvexSignalScouting\OrvexSignalScouting.exe
```

No es necesario:

- abrir VS Code;
- activar manualmente `.venv`;
- ejecutar `python app.py`;
- instalar Python en el equipo que recibe la carpeta portable.

## Archivo `.env`

El archivo `.env` debe permanecer junto al ejecutable:

```text
OrvexSignalScouting/
├── OrvexSignalScouting.exe
├── .env
└── _internal/
```

Su contenido esperado es:

```text
DENUE_TOKEN=TU_TOKEN_DEL_DENUE
```

Nunca debe subirse `.env`, `dist` ni las exportaciones comerciales a
GitHub.

## Pruebas obligatorias

Después de construir el portable, verifica:

1. Apertura automática del navegador.
2. Carga de entidades y municipios.
3. Búsqueda de actividad SCIAN.
4. Consulta real al DENUE.
5. Filtro por teléfono.
6. Filtro por ausencia de sitio web.
7. Filtro por colonia.
8. Apertura de Google Maps.
9. Descarga CSV.
10. Descarga Excel con hipervínculos.
11. Cierre del servidor al cerrar la consola.

## Desarrollo normal

La versión Python continúa funcionando como antes:

```powershell
Set-Location E:\Proyectos\OrvexSignalScouting

& .\.venv\Scripts\Activate.ps1

python .\app.py
```

`app.py` no se modifica para construir el portable. El ejecutable usa
`desktop_launcher.py` como punto de entrada independiente.
