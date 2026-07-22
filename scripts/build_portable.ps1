Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PythonPath = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$SpecPath = Join-Path $ProjectRoot "OrvexSignalScouting.spec"
$RequirementsPath = Join-Path $ProjectRoot "requirements-desktop.txt"
$DistFolder = Join-Path $ProjectRoot "dist\OrvexSignalScouting"
$SourceEnv = Join-Path $ProjectRoot ".env"
$ExampleEnv = Join-Path $ProjectRoot ".env.example"
$TargetEnv = Join-Path $DistFolder ".env"

if (-not (Test-Path $PythonPath)) {
    throw (
        "No se encontró el entorno virtual en " +
        "$ProjectRoot\.venv. Créalo antes de construir el portable."
    )
}

Set-Location $ProjectRoot

Write-Host ""
Write-Host "Instalando dependencias de escritorio..."
& $PythonPath -m pip install -r $RequirementsPath

Write-Host ""
Write-Host "Construyendo OrvexSignal Scouting portable..."
& $PythonPath -m PyInstaller `
    --clean `
    --noconfirm `
    $SpecPath

if (-not (Test-Path $DistFolder)) {
    throw "PyInstaller no creó la carpeta esperada: $DistFolder"
}

if (Test-Path $SourceEnv) {
    Copy-Item `
        -Path $SourceEnv `
        -Destination $TargetEnv `
        -Force

    Write-Host ""
    Write-Host "Se copió el archivo .env local al portable."
}
else {
    Copy-Item `
        -Path $ExampleEnv `
        -Destination $TargetEnv `
        -Force

    Write-Warning (
        "No existe .env en el proyecto. Se copió .env.example. " +
        "Agrega DENUE_TOKEN antes de ejecutar el portable."
    )
}

Write-Host ""
Write-Host "Portable creado correctamente:"
Write-Host $DistFolder
Write-Host ""
Write-Host "Ejecutable:"
Write-Host (
    Join-Path $DistFolder "OrvexSignalScouting.exe"
)
