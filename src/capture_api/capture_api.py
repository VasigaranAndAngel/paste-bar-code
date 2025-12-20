from collections.abc import Callable
from enum import Enum

from cv2.typing import MatLike

from .capturer_abc import Capturer

# region # TODO: remove
local_capturer = None
flask_capturer = None
ip_cam_capturer = None


class CaptureMethod(Enum):
    LOCAL_CAMERA = local_capturer
    LOCAL_WIFI_THROUGH_WEB_SITE = flask_capturer
    LOCAL_WIFI_THROUGH_IP_CAM = ip_cam_capturer


# endregion

T_METHOD = type[Capturer]


# TODO: refactor capturer handling
class CaptureAPI:
    def __init__(self) -> None:
        self._frame_callbacks: list[Callable[[MatLike], None]] = []
        self._code_detection_callbacks: list[Callable[[str], None]] = []
        self._capturer: Capturer | None = None
        self._lock_capture: bool = False

    def set_frame_callback(self, func: Callable[[MatLike], None]) -> None:
        self._frame_callbacks.append(func)

    def set_code_detection_callback(self, func: Callable[[str], None]) -> None:
        self._code_detection_callbacks.append(func)

    def start_capturing(self, capturer: T_METHOD) -> None:
        self._capturer = capturer()
        self._capturer.set_frame_callback(self._handle_frame)
        self._capturer.start_capturing()

    def stop_capturing(self) -> None:
        func = self._capturer
        if func is not None:
            func.stop_capturing()

    def change_capturing(self, capturer: T_METHOD) -> None:
        self._capturer = capturer()

    def set_capture_lock(self, lock: bool) -> None:
        pass

    @staticmethod
    def get_available_capturing_methods() -> list[T_METHOD]:
        return Capturer.__subclasses__()

    def _handle_frame(self, frame: MatLike) -> None:
        for func in self._frame_callbacks:
            func(frame)
