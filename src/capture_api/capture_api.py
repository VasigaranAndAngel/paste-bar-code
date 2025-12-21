import logging
from collections.abc import Callable, Sequence

from cv2.typing import MatLike

from .capturer_abc import Capturer
from .capturers import CAPTURERS

T_METHOD = type[Capturer]

logger = logging.getLogger(__name__)


# TODO: refactor capturer handling
class CaptureAPI:
    def __init__(self) -> None:
        self._frame_callback: Callable[[MatLike], None] | None = None
        self._capturer: Capturer | None = None
        self._lock_capture: bool = False
        self._option_maps: dict[str, tuple[T_METHOD, str]] = {}
        self._capturing: bool = False

    def set_frame_callback(self, func: Callable[[MatLike], None] | None) -> None:
        self._frame_callback = func

    def start_capturing(self) -> None:
        logger.info(f"Starting capture")
        if self._capturer is None:
            logger.error("Capturer not selected")
            raise Exception("Capturer not selected")
        self._capturer.start_capturing()
        self._capturing = True

    def stop_capturing(self) -> None:
        logger.info("Stopping capture")
        if self._capturer is not None:
            self._capturer.stop_capturing()
            self._capturing = False

    @staticmethod
    def get_available_capturing_methods() -> Sequence[T_METHOD]:
        # return Capturer.__subclasses__()
        return CAPTURERS

    def get_options(self) -> list[str]:
        options: list[str] = []
        for method in self.get_available_capturing_methods():
            name = method.name if method.name is not None else method.__name__
            available_options = method.available_options()
            if available_options:
                for opt in method.available_options():
                    option = f"{name}: {opt}"
                    self._option_maps[option] = (method, opt)
                    options.append(option)
            else:
                option = f"{name}"
                self._option_maps[option] = (method, "")
                options.append(option)
        return options

    def set_option(self, option: str) -> None:
        if option not in self._option_maps:
            raise Exception(f'Unexpectedly the option: "{option}" not found.')

        method, opt = self._option_maps[option]
        if self._capturer is None:
            self._capturer = method()
            if self._capturing:
                self._capturer.start_capturing()

        # check and change capture method
        elif not isinstance(self._capturer, method):
            self._capturer.stop_capturing()
            self._capturer = method()
            if self._capturing:
                self._capturer.start_capturing()

        self._capturer.set_frame_callback(self._handle_frame)

        # check and change capture option
        if opt in self._capturer.available_options():
            self._capturer.set_option(opt)
        else:
            raise Exception(f'Option: "{opt}" not found in "{method.name}"')

    def _handle_frame(self, frame: MatLike) -> None:
        if self._frame_callback is not None:
            self._frame_callback(frame)
