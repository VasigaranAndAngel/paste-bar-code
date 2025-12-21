import threading
from collections.abc import Callable
from typing import override

from cv2.typing import MatLike

from flask_app import set_callback, start_app

from .capturer_abc import Capturer


class FlaskCapturer(Capturer):
    name: str | None = "Local Network Web"

    def __init__(self) -> None:
        self._frame_callback: Callable[[MatLike], None] | None = None
        self._thread: threading.Thread = threading.Thread(target=start_app)
        set_callback(self._handle_frame)

    def _handle_frame(self, frame: MatLike) -> None:
        func = self._frame_callback
        if func is not None:
            func(frame)

    @override
    def start_capturing(self) -> None:
        self._thread.start()

    @override
    def stop_capturing(self) -> None:
        if self._thread.is_alive():
            self._thread.join(5)
            if self._thread.is_alive():
                print(f"error stopping flask thread: {self._thread}")  # TODO: use logging instead

    @override
    def set_frame_callback(self, func: Callable[[MatLike], None]) -> None:
        self._frame_callback = func

    @staticmethod
    @override
    def available_options() -> list[str]:
        return []

    @override
    def set_option(self, option: str) -> None:
        pass
