from abc import ABC, abstractmethod
from collections.abc import Callable

from cv2.typing import MatLike


class Capturer(ABC):
    # TODO: implement to emit signals on available options change
    name: str | None = None
    "Name of the capturer method."

    @abstractmethod
    def start_capturing(self) -> None: ...

    @abstractmethod
    def stop_capturing(self) -> None: ...

    @abstractmethod
    def set_frame_callback(self, func: Callable[[MatLike], None]) -> None: ...

    @staticmethod
    @abstractmethod
    def available_options() -> list[str]: ...

    @abstractmethod
    def set_option(self, option: str) -> None: ...
