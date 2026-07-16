from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request


PROJECT_ROOT = Path(__file__).resolve().parent
ENV_PATH = PROJECT_ROOT / ".env"

DENUE_BASE_URL = "https://www.inegi.org.mx/app/api/denue/v1/consulta"

load_dotenv(ENV_PATH)

app = Flask(__name__)


def get_default_form() -> dict[str, object]:
    return {
        "condition": "llantas",
        "latitude": "19.432608",
        "longitude": "-99.133209",
        "distance": "5000",
        "only_with_phone": True,
        "only_without_website": True,
    }


def query_denue(
    condition: str,
    latitude: float,
    longitude: float,
    distance: int,
) -> list[dict[str, object]]:
    token = os.getenv("DENUE_TOKEN", "").strip()

    if not token:
        raise RuntimeError(
            "No se encontró DENUE_TOKEN en el archivo .env."
        )

    encoded_condition = quote(condition, safe="")

    request_url = (
        f"{DENUE_BASE_URL}/Buscar/"
        f"{encoded_condition}/"
        f"{latitude},{longitude}/"
        f"{distance}/"
        f"{token}"
    )

    response = requests.get(
        request_url,
        timeout=30,
        headers={
            "Accept": "application/json",
            "User-Agent": "OrvexSignalScouting/0.1",
        },
    )

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list):
        raise RuntimeError(
            "La API del DENUE devolvió una estructura inesperada."
        )

    return [
        record
        for record in data
        if isinstance(record, dict)
    ]


def normalize_text(value: object) -> str:
    if value is None:
        return ""

    return str(value).strip()


def filter_results(
    records: list[dict[str, object]],
    only_with_phone: bool,
    only_without_website: bool,
) -> list[dict[str, object]]:
    filtered_records: list[dict[str, object]] = []

    for record in records:
        phone = normalize_text(record.get("Telefono"))
        website = normalize_text(record.get("Sitio_internet"))

        if only_with_phone and not phone:
            continue

        if only_without_website and website:
            continue

        filtered_records.append(record)

    return sorted(
        filtered_records,
        key=lambda item: normalize_text(item.get("Nombre")).lower(),
    )


@app.route("/", methods=["GET", "POST"])
def index():
    form_data = get_default_form()

    results: list[dict[str, object]] = []
    error_message = ""
    api_result_count = 0
    search_executed = False

    if request.method == "POST":
        search_executed = True

        form_data = {
            "condition": request.form.get(
                "condition",
                "",
            ).strip(),
            "latitude": request.form.get(
                "latitude",
                "",
            ).strip(),
            "longitude": request.form.get(
                "longitude",
                "",
            ).strip(),
            "distance": request.form.get(
                "distance",
                "",
            ).strip(),
            "only_with_phone": (
                request.form.get("only_with_phone") == "on"
            ),
            "only_without_website": (
                request.form.get("only_without_website") == "on"
            ),
        }

        try:
            condition = str(form_data["condition"]).strip()

            if not condition:
                raise ValueError(
                    "Escribe una actividad o palabra de búsqueda."
                )

            latitude = float(str(form_data["latitude"]))
            longitude = float(str(form_data["longitude"]))
            distance = int(str(form_data["distance"]))

            if not -90 <= latitude <= 90:
                raise ValueError(
                    "La latitud debe estar entre -90 y 90."
                )

            if not -180 <= longitude <= 180:
                raise ValueError(
                    "La longitud debe estar entre -180 y 180."
                )

            if not 1 <= distance <= 5000:
                raise ValueError(
                    "El radio debe estar entre 1 y 5000 metros."
                )

            raw_results = query_denue(
                condition=condition,
                latitude=latitude,
                longitude=longitude,
                distance=distance,
            )

            api_result_count = len(raw_results)

            results = filter_results(
                records=raw_results,
                only_with_phone=bool(
                    form_data["only_with_phone"]
                ),
                only_without_website=bool(
                    form_data["only_without_website"]
                ),
            )

        except ValueError as error:
            error_message = str(error)

        except requests.Timeout:
            error_message = (
                "La API del DENUE tardó demasiado en responder."
            )

        except requests.HTTPError as error:
            status_code = (
                error.response.status_code
                if error.response is not None
                else "desconocido"
            )

            error_message = (
                "La API del DENUE respondió con el estado HTTP "
                f"{status_code}."
            )

        except requests.RequestException:
            error_message = (
                "No fue posible conectarse con la API del DENUE."
            )

        except RuntimeError as error:
            error_message = str(error)

        except Exception:
            error_message = (
                "Ocurrió un error inesperado durante la consulta."
            )

    return render_template(
        "index.html",
        form_data=form_data,
        results=results,
        error_message=error_message,
        api_result_count=api_result_count,
        search_executed=search_executed,
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )