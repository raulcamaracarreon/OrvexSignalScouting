from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_PATH = (
    PROJECT_ROOT
    / "static"
    / "data"
    / "inegi_geo_catalog.json"
)

ENTITY_URL = (
    "https://gaia.inegi.org.mx/"
    "wscatgeo/v2/mgee/"
)

MUNICIPALITY_URL_TEMPLATE = (
    "https://gaia.inegi.org.mx/"
    "wscatgeo/v2/mgem/{entity_code}"
)

REQUEST_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "OrvexSignalScouting/0.4",
}


def fetch_records(
    session: requests.Session,
    url: str,
) -> list[dict[str, object]]:
    response = session.get(
        url,
        timeout=60,
        headers=REQUEST_HEADERS,
    )

    response.raise_for_status()

    payload = response.json()

    if not isinstance(payload, dict):
        raise RuntimeError(
            "El servicio geográfico del INEGI devolvió "
            "una estructura inesperada."
        )

    records = payload.get("datos")

    if not isinstance(records, list):
        raise RuntimeError(
            "El servicio geográfico del INEGI no devolvió "
            "una lista de datos."
        )

    return [
        record
        for record in records
        if isinstance(record, dict)
    ]


def normalize_entity(
    record: dict[str, object],
) -> dict[str, str]:
    code = str(
        record.get("cve_ent")
        or record.get("cvegeo")
        or ""
    ).strip()

    name = " ".join(
        str(record.get("nomgeo") or "").split()
    )

    if len(code) != 2 or not code.isdigit():
        raise RuntimeError(
            f"Clave de entidad inválida: {code!r}."
        )

    if not name:
        raise RuntimeError(
            f"La entidad {code} no tiene nombre."
        )

    return {
        "code": code,
        "name": name,
    }


def normalize_municipality(
    record: dict[str, object],
    expected_entity_code: str,
) -> dict[str, str]:
    entity_code = str(
        record.get("cve_ent") or ""
    ).strip()

    municipality_code = str(
        record.get("cve_mun") or ""
    ).strip()

    name = " ".join(
        str(record.get("nomgeo") or "").split()
    )

    if entity_code != expected_entity_code:
        raise RuntimeError(
            "El servicio devolvió un municipio de una "
            "entidad distinta a la solicitada."
        )

    if (
        len(municipality_code) != 3
        or not municipality_code.isdigit()
    ):
        raise RuntimeError(
            "Clave municipal inválida para la entidad "
            f"{expected_entity_code}: "
            f"{municipality_code!r}."
        )

    if not name:
        raise RuntimeError(
            "El municipio "
            f"{expected_entity_code}{municipality_code} "
            "no tiene nombre."
        )

    return {
        "code": municipality_code,
        "name": name,
    }


def build_catalog() -> dict[str, object]:
    with requests.Session() as session:
        entity_records = fetch_records(
            session,
            ENTITY_URL,
        )

        entities = sorted(
            (
                normalize_entity(record)
                for record in entity_records
            ),
            key=lambda entity: entity["code"],
        )

        if len(entities) != 32:
            raise RuntimeError(
                "Se esperaban 32 entidades federativas y "
                f"se obtuvieron {len(entities)}."
            )

        entity_codes = [
            entity["code"]
            for entity in entities
        ]

        if len(entity_codes) != len(set(entity_codes)):
            raise RuntimeError(
                "El catálogo contiene claves de entidad "
                "duplicadas."
            )

        municipality_total = 0

        for entity in entities:
            entity_code = entity["code"]

            print(
                "Consultando municipios de "
                f"{entity_code} — {entity['name']}..."
            )

            municipality_records = fetch_records(
                session,
                MUNICIPALITY_URL_TEMPLATE.format(
                    entity_code=entity_code
                ),
            )

            municipalities = sorted(
                (
                    normalize_municipality(
                        record,
                        expected_entity_code=entity_code,
                    )
                    for record in municipality_records
                ),
                key=lambda municipality: (
                    municipality["name"].casefold(),
                    municipality["code"],
                ),
            )

            municipality_codes = [
                municipality["code"]
                for municipality in municipalities
            ]

            if len(municipality_codes) != len(
                set(municipality_codes)
            ):
                raise RuntimeError(
                    "La entidad "
                    f"{entity_code} contiene claves "
                    "municipales duplicadas."
                )

            if not municipalities:
                raise RuntimeError(
                    "La entidad "
                    f"{entity_code} no devolvió municipios."
                )

            entity["municipalities"] = municipalities
            municipality_total += len(municipalities)

    city_of_mexico = next(
        entity
        for entity in entities
        if entity["code"] == "09"
    )

    if len(city_of_mexico["municipalities"]) != 16:
        raise RuntimeError(
            "Ciudad de México debe contener "
            "16 demarcaciones territoriales."
        )

    if municipality_total < 2400:
        raise RuntimeError(
            "El total nacional de municipios parece "
            "incompleto."
        )

    return {
        "source": (
            "Servicio Web del Catálogo Único de "
            "Claves Geoestadísticas, INEGI"
        ),
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "entity_count": len(entities),
        "municipality_count": municipality_total,
        "entities": entities,
    }


def main() -> None:
    catalog = build_catalog()

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            catalog,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print(f"Archivo creado: {OUTPUT_PATH}")
    print(
        "Entidades: "
        f"{catalog['entity_count']}"
    )
    print(
        "Municipios y demarcaciones: "
        f"{catalog['municipality_count']}"
    )


if __name__ == "__main__":
    main()
