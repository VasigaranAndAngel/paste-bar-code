import logging
import threading
from collections import defaultdict
from collections.abc import Callable
from typing import override

import cv2
from cv2.typing import MatLike
from cv2_enumerate_cameras import enumerate_cameras
from cv2_enumerate_cameras.camera_info import CameraInfo

from .capturer_abc import Capturer

logger = logging.getLogger(__name__)


class LocalCapturer(Capturer):
    _option_to_cameras_map: dict[str, tuple[CameraInfo, ...]] | None = None
    name: str | None = "Local Camera"

    def __init__(self) -> None:
        self._selected_cameras: list[CameraInfo] = []
        self._selected_option: str | None = None
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
        if LocalCapturer._option_to_cameras_map is None:
            LocalCapturer._update_available_options()

        if LocalCapturer._option_to_cameras_map is not None:
            return list(LocalCapturer._option_to_cameras_map.keys())
        else:
            return []

    @override
    def set_option(self, option: str) -> None:
        if (
            LocalCapturer._option_to_cameras_map is None
            or option not in LocalCapturer._option_to_cameras_map.keys()
        ):
            print("error. unknown option")
            return

        self._selected_option = option
        self._selected_cameras = sorted(
            LocalCapturer._option_to_cameras_map[option],
            key=lambda x: 0 if x.backend == cv2.CAP_MSMF else 1,
        )
        # restart capturing to change the camera port
        if self._run_capturing:
            self.stop_capturing()
            self.start_capturing()

    def _read_camera(self) -> None:
        if not len(self._selected_cameras) > 0:
            logger.warning(f"Aborting reading camera. because there are no cameras selected.")
            return

        selected_index = 0
        while True:
            try:
                if not len(self._selected_cameras) >= selected_index - 1:
                    logger.warning(
                        f'Aborting reading camera. None of the cameras: "{self._selected_cameras}" worked.'
                    )
                    return
                camera = cv2.VideoCapture(self._selected_cameras[selected_index].index)
                break
            except:  # TODO: specify exceptions
                selected_index += 1

        logger.info(f'Starting capturing. Selected cam: "{self._selected_cameras[selected_index]}"')
        while self._run_capturing:
            is_reading, img = camera.read()
            if is_reading:  # TODO: implement falling back to other cameras if not is_reading.
                if self._callback is not None:
                    self._callback(img)

        camera.release()

    @staticmethod
    def _update_available_options() -> None:
        LocalCapturer._option_to_cameras_map = {}

        _map: dict[str, list[CameraInfo]] = defaultdict(list)
        for camera in enumerate_cameras():
            option = camera.name
            _map[option].append(camera)

        for option, cameras in _map.items():
            LocalCapturer._option_to_cameras_map[option] = tuple(cameras)
