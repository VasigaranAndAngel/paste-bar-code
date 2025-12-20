from pathlib import Path

from .app import app, set_callback, socketio

__all__ = ["set_callback", "start_app"]


def start_app() -> None:
    parent_path = Path(__file__).parent
    cert_path = parent_path.joinpath("cert.pem").absolute()
    key_path = parent_path.joinpath("key.pem").absolute()
    socketio.run(  # pyright: ignore[reportUnknownMemberType]
        app,
        host="0.0.0.0",
        port=5000,
        certfile=cert_path,
        keyfile=key_path,
    )
