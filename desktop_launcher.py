from __future__ import annotations

import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from dotenv import load_dotenv
from waitress import serve


HOST = "127.0.0.1"
PREFERRED_PORTS = range(5000, 5011)


def get_application_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


def load_application_environment() -> Path:
    env_path = get_application_root() / ".env"
    load_dotenv(env_path, override=False)
    return env_path


def find_available_port() -> int:
    for port in PREFERRED_PORTS:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as candidate:
            try:
                candidate.bind((HOST, port))
            except OSError:
                continue

            return port

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as candidate:
        candidate.bind((HOST, 0))
        return int(candidate.getsockname()[1])


def open_browser_when_ready(url: str) -> None:
    for _ in range(40):
        try:
            with urlopen(url, timeout=1):
                webbrowser.open(url, new=1)
                return
        except (OSError, URLError):
            time.sleep(0.25)

    webbrowser.open(url, new=1)


def pause_before_exit() -> None:
    try:
        input("\nPresiona Enter para cerrar.")
    except (EOFError, KeyboardInterrupt):
        pass


def main() -> int:
    env_path = load_application_environment()

    if not os.getenv("DENUE_TOKEN", "").strip():
        print("No se encontró el token del DENUE.")
        print(f"Ubica este archivo y agrega el token:\n{env_path}")
        print("\nFormato esperado:")
        print("DENUE_TOKEN=TU_TOKEN_DEL_DENUE")
        pause_before_exit()
        return 1

    from app import app

    port = find_available_port()
    url = f"http://{HOST}:{port}"

    print("=" * 62)
    print("ORVEXSIGNAL SCOUTING")
    print("=" * 62)
    print(f"\nLa aplicación está disponible en:\n{url}")
    print("\nEl navegador se abrirá automáticamente.")
    print("Mantén esta ventana abierta mientras uses Scouting.")
    print("Para terminar, cierra esta ventana o presiona Ctrl+C.\n")

    browser_thread = threading.Thread(
        target=open_browser_when_ready,
        args=(url,),
        daemon=True,
    )
    browser_thread.start()

    try:
        serve(
            app,
            host=HOST,
            port=port,
            threads=4,
        )
    except KeyboardInterrupt:
        print("\nOrvexSignal Scouting se cerró correctamente.")
    except Exception as error:
        print("\nNo fue posible iniciar OrvexSignal Scouting.")
        print(f"Detalle técnico: {error}")
        pause_before_exit()
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
