import json
from typing import Literal, TypedDict, TypeVar, override

from file_system import CONFIG_FILE


# NOTE: below is just a TypedDict for type hinting. The actual Config dict is `Config`
class T_CONFIG_DATA(TypedDict):
    window_geo: Literal["center"] | tuple[int, int, int, int]
    always_on_top: bool
    lock_interval: float
    type_code: bool
    press_enter: bool
    play_beep: bool
    capture: Literal["auto"] | str
    flip_frames: bool


WINDOW_GEO = "window_geo"
ALWAYS_ON_TOP = "always_on_top"
LOCK_INTERVAL = "lock_interval"
TYPE_CODE = "type_code"
PRESS_ENTER = "press_enter"
PLAY_BEEP = "play_beep"
CAPTURE = "capture"
FLIP_FRAMES = "flip_frames"

DEFAULT_VALUES: T_CONFIG_DATA = {
    WINDOW_GEO: "center",
    ALWAYS_ON_TOP: True,
    LOCK_INTERVAL: 1.5,
    TYPE_CODE: True,
    PRESS_ENTER: True,
    PLAY_BEEP: True,
    CAPTURE: "auto",
    FLIP_FRAMES: False,
}


_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


if not CONFIG_FILE.parent.exists():
    CONFIG_FILE.parent.mkdir()

if not CONFIG_FILE.exists():
    _ = CONFIG_FILE.write_text(json.dumps(DEFAULT_VALUES, indent=4))


class Config(dict[_KT, _VT]):
    _instance: "Config[_KT, _VT] | None" = None
    _data: T_CONFIG_DATA

    def __new__(cls) -> T_CONFIG_DATA:
        "To make this singleton and type hint instance of 'Config' as 'T_CONFIG_DATA'"
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance  # pyright: ignore[reportReturnType]

    def __init__(self) -> None:
        try:
            # TODO: test the configs has no issues.
            data = json.loads(CONFIG_FILE.read_text("utf-8"))
        except json.JSONDecodeError as e:
            raise NotImplementedError
        super().__init__(data)

    @override
    def __setitem__(self, key: _KT, value: _VT, /) -> None:
        super().__setitem__(key, value)
        self._save_config()

    def _save_config(self) -> None:
        _ = CONFIG_FILE.write_text(json.dumps(self, indent=4), "utf-8")


configs = Config()
