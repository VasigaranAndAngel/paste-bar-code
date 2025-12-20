import threading
from collections.abc import Callable
from typing import override

import cv2
from cv2.typing import MatLike

from .capturer_abc import Capturer

# Source - https://stackoverflow.com/a
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
            is_reading, img = camera.read()
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


class LocalCapturer(Capturer):
    def __init__(self) -> None:
        self._selected_port: int = 0
        self._video_capture: cv2.VideoCapture | None = None
        self._option_to_port_map: dict[str, int] = {}
        self._callback: Callable[[MatLike], None] | None = None
        self._run_capturing: bool = False
        self._thread: threading.Thread | None = None

    @override
    def start_capturing(self) -> None:
        self._video_capture = cv2.VideoCapture(self._selected_port)
        self._run_capturing = True
        self._thread = threading.Thread(target=self._read_camera)
        self._thread.start()

    @override
    def stop_capturing(self) -> None:
        self._run_capturing = False
        thread = self._thread
        if thread is not None:
            thread.join()
        capture = self._video_capture
        if capture is not None:
            capture.release()

    @override
    def set_frame_callback(self, func: Callable[[MatLike], None]) -> None:
        self._callback = func

    @override
    def available_options(self) -> list[str]:
        available_ports = _list_ports()
        for port in available_ports[1]:
            option = f"Port {port}"
            self._option_to_port_map[option] = port

        return list(self._option_to_port_map.keys())

    @override
    def set_option(self, option: str):
        if option not in self._option_to_port_map.keys():
            print("error. unknown option")
            return
        self._selected_port = self._option_to_port_map[option]

    def _read_camera(self) -> None:
        camera = self._video_capture
        if camera is None:
            print("camera not set.")
            return

        while self._run_capturing:
            is_reading, img = camera.read()
            if is_reading:
                if self._callback is not None:
                    self._callback(img)
