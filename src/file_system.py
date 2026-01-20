import sys
from pathlib import Path

if hasattr(sys, "frozen"):
    if hasattr(sys, "_MEIPASS"):  # check if build with `pyinstaller --onefile`
        app_dir = Path(getattr(sys, "_MEIPASS"))  # pyright: ignore[reportAny]
    else:
        app_dir = Path(sys.executable).parent
    resource_dir = app_dir.joinpath("resources")
else:
    resource_dir = "src/resources"

CONFIG_FILE = Path.home() / "appdata" / "Local" / "Paste Bar Code" / "config.json"

RESOURCES_DIR = Path(resource_dir).absolute()

BEEP_SOUND_WAV = sf if (sf := RESOURCES_DIR.joinpath("beep_sound.wav")).exists() else None
