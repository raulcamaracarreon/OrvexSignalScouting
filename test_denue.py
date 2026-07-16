from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.parse import quote

import requests
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent
ENV_PATH = PROJECT_ROOT / ".env"

DENUE_BASE_URL = "https://www.inegi.org.mx/app/api/denue/v1/consulta"

# Consulta oficial de ejemplo del INEGI.
SEARCH_TERM = "camiones"
COORDINATES = "21.85717833,-102.28487238"
DISTANCE_METERS = 250


def main() -> int:
    load_dotenv(ENV_PATH)

    token = os.getenv("DENUE_TOKEN", "").strip()

    if not token:
        print("ERROR: DENUE_TOKEN no está disponible.")
        return 1

    encoded_search = quote(SEARCH_TERM, safe="")

    request_url = (
        f"{DENUE_BASE_URL}/Buscar/"
        f"{encoded_search}/"
        f"{COORDINATES}/"
        f"{DISTANCE_METERS}/"
        f"{token}"
    )

    print("Consultando la API del DENUE...")
    print(f"TOKEN_CARGADO={bool(token)}")
    print(f"LONGITUD_TOKEN={len(token)}")

    try:
        response = requests.get(
            request_url,
            timeout=30,
            headers={
                "Accept": "application/json",
                "User-Agent": "OrvexSignalScouting/0.1",
            },
        )
    except requests.RequestException as error:
        print(f"ERROR_DE_CONEXION={type(error).__name__}")
        return 1

    print(f"HTTP_STATUS={response.status_code}")

    if response.status_code != 200:
        print("La API respondió con un estado inesperado.")
        print("RESPUESTA:")
        print(response.text[:500])
        return 1

    try:
        data = response.json()
    except json.JSONDecodeError:
        print("ERROR: La respuesta no es JSON válido.")
        print("RESPUESTA:")
        print(response.text[:500])
        return 1

    print(f"TIPO_RESPUESTA={type(data).__name__}")

    if not isinstance(data, list):
        print("ERROR: Se esperaba una lista de establecimientos.")
        print(data)
        return 1

    print(f"REGISTROS_RECIBIDOS={len(data)}")

    if not data:
        print("La consulta funcionó, pero no devolvió establecimientos.")
        return 0

    first_record = data[0]

    if not isinstance(first_record, dict):
        print("ERROR: El primer registro no tiene la estructura esperada.")
        return 1

    print("\nCLAVES_DEL_PRIMER_REGISTRO:")

    for key in first_record.keys():
        print(f"- {key}")

    print("\nPRIMEROS_ESTABLECIMIENTOS:")

    for index, record in enumerate(data[:3], start=1):
        print(f"\nESTABLECIMIENTO_{index}")
        print(f"Nombre: {record.get('Nombre', '')}")
        print(f"Actividad: {record.get('Clase_actividad', '')}")
        print(f"Ubicación: {record.get('Ubicacion', '')}")
        print(f"Teléfono: {record.get('Telefono', '')}")
        print(f"Sitio web: {record.get('Sitio_internet', '')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())