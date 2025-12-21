import threading
from collections.abc import Callable
from typing import override

import cv2
from cv2.typing import MatLike

from .capturer_abc import Capturer

# region Source - https://stackoverflow.com/a
# Posted by G M, modified by community. See post 'Timeline' for change history
# Retrieved 2025-12-16, License - CC BY-SA 4.0


def _list_ports() -> tuple[list[int], list[int], list[int]]:
    """
    Test the ports and returns a tuple with the available ports and the ones that are working.
    """
    non_working_ports: list[int] = []
    dev_port: int = 0
    working_ports: list[int] = []
    available_ports: list[int] = []
    while len(non_working_ports) < 6:
        camera = cv2.VideoCapture(dev_port)
        if not camera.isOpened():
            non_working_ports.append(dev_port)
            print("Port %s is not working." % dev_port)
        else:
            is_reading, _ = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                print("Port %s is working and reads images (%s x %s)" % (dev_port, h, w))
                working_ports.append(dev_port)
            else:
                print(
                    "Port %s for camera ( %s x %s) is present but does not reads."
                    % (dev_port, h, w)
                )
                available_ports.append(dev_port)
        dev_port += 1
    return available_ports, working_ports, non_working_ports


# endregion


class LocalCapturer(Capturer):
    _option_to_port_map: dict[str, int] | None = None
    name: str | None = "Local Camera"

    def __init__(self) -> None:
        self._selected_port: int = 0
        self._callback: Callable[[MatLike], None] | None = None
        self._run_capturing: bool = False
        self._thread: threading.Thread | None = None

    @override
    def start_capturing(self) -> None:
        self._run_capturing = True
        self._thread = threading.Thread(target=self._read_camera)
        self._thread.start()

    @override
    def stop_capturing(self) -> None:
        self._run_capturing = False
        if self._thread is not None:
            self._thread.join()
        self._thread = None

    @override
    def set_frame_callback(self, func: Callable[[MatLike], None]) -> None:
        self._callback = func

    @staticmethod
    @override
    def available_options() -> list[str]:
        if LocalCapturer._option_to_port_map is None:
            LocalCapturer._update_available_options()

        if LocalCapturer._option_to_port_map is not None:
            return list(LocalCapturer._option_to_port_map.keys())
        else:
            return []

    @override
    def set_option(self, option: str) -> None:
        if (
            LocalCapturer._option_to_port_map is None
            or option not in LocalCapturer._option_to_port_map.keys()
        ):
            print("error. unknown option")
            return

        self._selected_port = LocalCapturer._option_to_port_map[option]
        # restart capturing to change the camera port
        if self._run_capturing:
            self.stop_capturing()
            self.start_capturing()

    def _read_camera(self) -> None:
        camera = cv2.VideoCapture(self._selected_port)

        while self._run_capturing:
            is_reading, img = camera.read()
            if is_reading:
                if self._callback is not None:
                    self._callback(img)

        camera.release()

    @staticmethod
    def _update_available_options() -> None:
        if LocalCapturer._option_to_port_map is None:
            LocalCapturer._option_to_port_map = {}

        # available_ports = _list_ports()[1]
        available_ports = [1, 2]
        for port in available_ports:
            option = f"Port {port}"
            LocalCapturer._option_to_port_map[option] = port - 1
