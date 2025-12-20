from abc import ABC, abstractmethod
from collections.abc import Callable

from cv2.typing import MatLike


class Capturer(ABC):
    @abstractmethod
    def start_capturing(self) -> None: ...

    @abstractmethod
    def stop_capturing(self) -> None: ...

    @abstractmethod
    def set_frame_callback(self, func: Callable[[MatLike], None]) -> None: ...

    @abstractmethod
    def available_options(self) -> list[str]: ...

    @abstractmethod
    def set_option(self, option: str): ...
