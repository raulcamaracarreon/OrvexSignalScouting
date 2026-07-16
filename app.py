from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request


PROJECT_ROOT = Path(__file__).resolve().parent
ENV_PATH = PROJECT_ROOT / ".env"

DENUE_BASE_URL = (
    "https://www.inegi.org.mx/app/api/denue/v1/consulta"
)

ENTITY_OPTIONS = [
    {
        "code": "09",
        "name": "Ciudad de México",
    },
]

MUNICIPALITY_OPTIONS = [
    {
        "code": "0",
        "name": "Todas las alcaldías",
    },
    {
        "code": "002",
        "name": "Azcapotzalco",
    },
    {
        "code": "003",
        "name": "Coyoacán",
    },
    {
        "code": "004",
        "name": "Cuajimalpa de Morelos",
    },
    {
        "code": "005",
        "name": "Gustavo A. Madero",
    },
    {
        "code": "006",
        "name": "Iztacalco",
    },
    {
        "code": "007",
        "name": "Iztapalapa",
    },
    {
        "code": "008",
        "name": "La Magdalena Contreras",
    },
    {
        "code": "009",
        "name": "Milpa Alta",
    },
    {
        "code": "010",
        "name": "Álvaro Obregón",
    },
    {
        "code": "011",
        "name": "Tláhuac",
    },
    {
        "code": "012",
        "name": "Tlalpan",
    },
    {
        "code": "013",
        "name": "Xochimilco",
    },
    {
        "code": "014",
        "name": "Benito Juárez",
    },
    {
        "code": "015",
        "name": "Cuauhtémoc",
    },
    {
        "code": "016",
        "name": "Miguel Hidalgo",
    },
    {
        "code": "017",
        "name": "Venustiano Carranza",
    },
]

STRATUM_OPTIONS = [
    {
        "code": "0",
        "name": "Todos los tamaños",
    },
    {
        "code": "1",
        "name": "0 a 5 personas",
    },
    {
        "code": "2",
        "name": "6 a 10 personas",
    },
    {
        "code": "3",
        "name": "11 a 30 personas",
    },
    {
        "code": "4",
        "name": "31 a 50 personas",
    },
    {
        "code": "5",
        "name": "51 a 100 personas",
    },
    {
        "code": "6",
        "name": "101 a 250 personas",
    },
    {
        "code": "7",
        "name": "251 y más personas",
    },
]

NORMALIZED_FIELDS = (
    "Nombre",
    "Razon_social",
    "Clase_actividad",
    "Estrato",
    "Tipo_vialidad",
    "Calle",
    "Num_Exterior",
    "Num_Interior",
    "Colonia",
    "CP",
    "Ubicacion",
    "Telefono",
    "Correo_e",
    "Sitio_internet",
    "Longitud",
    "Latitud",
)

load_dotenv(ENV_PATH)

app = Flask(__name__)


def get_default_form() -> dict[str, object]:
    return {
        "entity": "09",
        "municipality": "007",
        "activity_class": "468213",
        "stratum": "0",
        "maximum_records": "100",
        "only_with_phone": True,
        "only_without_website": True,
    }


def get_valid_codes(
    options: list[dict[str, str]],
) -> set[str]:
    return {
        option["code"]
        for option in options
    }


def get_option_name(
    options: list[dict[str, str]],
    selected_code: str,
) -> str:
    for option in options:
        if option["code"] == selected_code:
            return option["name"]

    return selected_code


def query_denue_area(
    entity: str,
    municipality: str,
    activity_class: str,
    stratum: str,
    maximum_records: int,
) -> list[dict[str, object]]:
    token = os.getenv("DENUE_TOKEN", "").strip()

    if not token:
        raise RuntimeError(
            "No se encontró DENUE_TOKEN en el archivo .env."
        )

    request_url = (
        f"{DENUE_BASE_URL}/BuscarAreaActEstr/"
        f"{entity}/"
        f"{municipality}/"
        "0/"
        "0/"
        "0/"
        "0/"
        "0/"
        "0/"
        f"{activity_class}/"
        "0/"
        "1/"
        f"{maximum_records}/"
        "0/"
        f"{stratum}/"
        f"{token}"
    )

    response = requests.get(
        request_url,
        timeout=30,
        headers={
            "Accept": "application/json",
            "User-Agent": "OrvexSignalScouting/0.2",
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

    return " ".join(str(value).split())

def build_google_maps_url(
    record: dict[str, object],
) -> str:
    query_parts = [
        normalize_text(record.get("Nombre")),
        normalize_text(record.get("Calle")),
        normalize_text(record.get("Num_Exterior")),
        normalize_text(record.get("Colonia")),
        normalize_text(record.get("Ubicacion")),
    ]

    query = ", ".join(
        part
        for part in query_parts
        if part
    )

    if not query:
        latitude = normalize_text(
            record.get("Latitud")
        )

        longitude = normalize_text(
            record.get("Longitud")
        )

        if latitude and longitude:
            query = f"{latitude},{longitude}"

    if not query:
        return ""

    parameters = urlencode(
        {
            "api": "1",
            "query": query,
        }
    )

    return (
        "https://www.google.com/maps/search/"
        f"?{parameters}"
    )

def normalize_record(
    record: dict[str, object],
) -> dict[str, object]:
    normalized_record = dict(record)

    for field_name in NORMALIZED_FIELDS:
        normalized_record[field_name] = normalize_text(
            record.get(field_name)
        )

    normalized_record["Google_Maps_URL"] = (
        build_google_maps_url(
            normalized_record
        )
    )

    return normalized_record


def filter_results(
    records: list[dict[str, object]],
    only_with_phone: bool,
    only_without_website: bool,
) -> list[dict[str, object]]:
    filtered_records: list[dict[str, object]] = []

    for record in records:
        normalized_record = normalize_record(record)

        phone = normalize_text(
            normalized_record.get("Telefono")
        )

        website = normalize_text(
            normalized_record.get("Sitio_internet")
        )

        if only_with_phone and not phone:
            continue

        if only_without_website and website:
            continue

        filtered_records.append(normalized_record)

    return sorted(
        filtered_records,
        key=lambda item: normalize_text(
            item.get("Nombre")
        ).lower(),
    )


def validate_form(
    form_data: dict[str, object],
) -> tuple[str, str, str, str, int]:
    entity = str(form_data["entity"]).strip()
    municipality = str(
        form_data["municipality"]
    ).strip()
    activity_class = str(
        form_data["activity_class"]
    ).strip()
    stratum = str(form_data["stratum"]).strip()

    maximum_records = int(
        str(form_data["maximum_records"])
    )

    valid_entities = get_valid_codes(
        ENTITY_OPTIONS
    )

    valid_municipalities = get_valid_codes(
        MUNICIPALITY_OPTIONS
    )

    valid_strata = get_valid_codes(
        STRATUM_OPTIONS
    )

    if entity not in valid_entities:
        raise ValueError(
            "Selecciona una entidad válida."
        )

    if municipality not in valid_municipalities:
        raise ValueError(
            "Selecciona una alcaldía válida."
        )

    if not (
        activity_class == "0"
        or (
            activity_class.isdigit()
            and len(activity_class) == 6
        )
    ):
        raise ValueError(
            "El código SCIAN debe contener seis dígitos "
            "o utilizar 0 para todas las actividades."
        )

    if stratum not in valid_strata:
        raise ValueError(
            "Selecciona un tamaño de negocio válido."
        )

    if not 1 <= maximum_records <= 500:
        raise ValueError(
            "La cantidad de registros debe estar "
            "entre 1 y 500."
        )

    return (
        entity,
        municipality,
        activity_class,
        stratum,
        maximum_records,
    )


@app.route("/", methods=["GET", "POST"])
def index():
    form_data = get_default_form()

    results: list[dict[str, object]] = []
    error_message = ""
    api_result_count = 0
    search_executed = False
    search_description = ""

    if request.method == "POST":
        search_executed = True

        form_data = {
            "entity": request.form.get(
                "entity",
                "",
            ).strip(),
            "municipality": request.form.get(
                "municipality",
                "",
            ).strip(),
            "activity_class": request.form.get(
                "activity_class",
                "",
            ).strip(),
            "stratum": request.form.get(
                "stratum",
                "",
            ).strip(),
            "maximum_records": request.form.get(
                "maximum_records",
                "",
            ).strip(),
            "only_with_phone": (
                request.form.get("only_with_phone")
                == "on"
            ),
            "only_without_website": (
                request.form.get(
                    "only_without_website"
                )
                == "on"
            ),
        }

        try:
            (
                entity,
                municipality,
                activity_class,
                stratum,
                maximum_records,
            ) = validate_form(form_data)

            raw_results = query_denue_area(
                entity=entity,
                municipality=municipality,
                activity_class=activity_class,
                stratum=stratum,
                maximum_records=maximum_records,
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

            entity_name = get_option_name(
                ENTITY_OPTIONS,
                entity,
            )

            municipality_name = get_option_name(
                MUNICIPALITY_OPTIONS,
                municipality,
            )

            stratum_name = get_option_name(
                STRATUM_OPTIONS,
                stratum,
            )

            search_description = (
                f"{municipality_name}, {entity_name} · "
                f"SCIAN {activity_class} · "
                f"{stratum_name}"
            )

        except ValueError as error:
            error_message = str(error)

        except requests.Timeout:
            error_message = (
                "La API del DENUE tardó demasiado "
                "en responder."
            )

        except requests.HTTPError as error:
            status_code = (
                error.response.status_code
                if error.response is not None
                else "desconocido"
            )

            error_message = (
                "La API del DENUE respondió con el "
                f"estado HTTP {status_code}."
            )

        except requests.RequestException:
            error_message = (
                "No fue posible conectarse con "
                "la API del DENUE."
            )

        except RuntimeError as error:
            error_message = str(error)

        except Exception:
            error_message = (
                "Ocurrió un error inesperado "
                "durante la consulta."
            )

    return render_template(
        "index.html",
        form_data=form_data,
        entity_options=ENTITY_OPTIONS,
        municipality_options=MUNICIPALITY_OPTIONS,
        stratum_options=STRATUM_OPTIONS,
        results=results,
        error_message=error_message,
        api_result_count=api_result_count,
        search_executed=search_executed,
        search_description=search_description,
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )