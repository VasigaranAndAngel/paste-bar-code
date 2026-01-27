import logging
import threading
from collections.abc import Callable
from functools import partial
from typing import override

import cv2
import pyautogui
from cv2.typing import MatLike
from PySide6.QtCore import QPoint, QRect, QSize, Qt, Signal
from PySide6.QtGui import QCloseEvent, QImage, QMouseEvent, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from configs import LOCK_INTERVAL, PRESS_ENTER, configs
from detect_code import detect_code
from ui.widgets import DetectionIndicator, FrameLabel, TimerLineEditWidget
from version import __version__

from .beep_sound import play_beep

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    _update_frame_signal: Signal = Signal(str, object)
    "To turn child thread's to main thread."

    def __init__(self) -> None:
        super().__init__()

        self._last_code: str = ""
        self._capture_option_change_callback: Callable[[str], None] | None = None
        self._mouse_pressed: QPoint | None = None

        self.setWindowTitle(f"Paste Bar Code - v{__version__}")

        win_geo = configs["window_geo"]
        if win_geo == "center":
            size = QSize(600, 400)
            screen_size = self.screen().size()
            pos = QPoint()
            pos.setX((screen_size.width() - size.width()) // 2)
            pos.setY((screen_size.height() - size.height()) // 2)
            rect = QRect()
            rect.setTopLeft(pos)
            rect.setSize(size)
            self.setGeometry(rect)
        else:
            self.setGeometry(*win_geo)

        self._image_widget: FrameLabel = FrameLabel(self)

        self._indicator_widget: DetectionIndicator = DetectionIndicator(self)

        self._interval_entry: TimerLineEditWidget = TimerLineEditWidget(self)
        self._interval_entry.setFixedSize(130, 40)
        _ = self._interval_entry.value_changed.connect(self._change_timer)
        _ = self._interval_entry.value_changed.connect(partial(self._update_config, LOCK_INTERVAL))

        self._press_enter: QCheckBox = QCheckBox(self)
        self._press_enter.setText("Press Enter")
        _ = self._press_enter.checkStateChanged.connect(
            lambda: self._update_config(PRESS_ENTER, self._press_enter.isChecked())
        )

        self._capture_options_combobox: QComboBox = QComboBox(self)
        _ = self._capture_options_combobox.currentTextChanged.connect(
            self._on_capture_option_change
        )

        self._buttons_layout: QHBoxLayout = QHBoxLayout()
        self._buttons_layout.addWidget(self._capture_options_combobox)
        self._buttons_layout.addWidget(self._press_enter)
        self._buttons_layout.addWidget(self._interval_entry)
        self._buttons_layout.addWidget(self._indicator_widget)

        self._main_layout: QVBoxLayout = QVBoxLayout()
        self._main_layout.addWidget(self._image_widget)
        self._main_layout.addLayout(self._buttons_layout)

        central_widget = QWidget(self)
        central_widget.setLayout(self._main_layout)

        self.setCentralWidget(central_widget)

        _ = self._update_frame_signal.connect(self._update_frame)

        self._update_options()

    def update_frame(self, frame: MatLike) -> None:
        code, _frame = detect_code(frame)
        if threading.get_ident() != threading.main_thread().ident:
            self._update_frame_signal.emit(code, _frame)
        else:
            self._update_frame(code, _frame)

    def update_capture_options(self, options: list[str]) -> None:
        capture_config = configs["capture"]
        self._capture_options_combobox.addItems(options)
        option_index = 0
        if capture_config != "auto" and capture_config in options:
            for option_index in range(self._capture_options_combobox.count()):
                if capture_config == self._capture_options_combobox.itemText(option_index):
                    break

        self._capture_options_combobox.setCurrentIndex(option_index)

    def set_capture_option_change_callback(self, func: Callable[[str], None] | None) -> None:
        self._capture_option_change_callback = func

    @override
    def closeEvent(self, event: QCloseEvent, /) -> None:
        geo_rect = self.geometry()
        geo = (geo_rect.x(), geo_rect.y(), geo_rect.width(), geo_rect.height())
        configs["window_geo"] = geo
        return super().closeEvent(event)

    @override
    def mousePressEvent(self, event: QMouseEvent, /) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._mouse_pressed = event.globalPos() - self.pos()
        else:
            return super().mousePressEvent(event)

    @override
    def mouseMoveEvent(self, event: QMouseEvent, /) -> None:
        if self._mouse_pressed is not None:
            self.move(event.globalPos() - self._mouse_pressed)
        else:
            return super().mouseMoveEvent(event)

    @override
    def mouseReleaseEvent(self, event: QMouseEvent, /) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._mouse_pressed = None
        else:
            return super().mouseReleaseEvent(event)

    def _on_capture_on(self) -> None:
        raise NotImplementedError

    def _on_capture_off(self) -> None:
        raise NotImplementedError

    def _update_frame(self, code: str, _frame: MatLike) -> None:
        rgb_img = cv2.cvtColor(_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape  # pyright: ignore[reportAny]
        bytes_per_line = ch * w  # pyright: ignore[reportAny]
        q_image = QImage(rgb_img.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)  # pyright: ignore[reportAny]
        pixmap = QPixmap.fromImage(q_image)
        self._image_widget.setPixmap(pixmap)
        if code and not (self._indicator_widget.locked and code == self._last_code):
            self._indicator_widget.code_detected(code)
            if configs["play_beep"]:
                play_beep()
            if configs["type_code"]:
                pyautogui.typewrite(code)
            if configs["press_enter"]:
                pyautogui.press("enter")
            self._last_code = code

    def _change_timer(self, time: float) -> None:
        """Changes the time of interval timer. (seconds)"""
        self._indicator_widget.change_timer(int(time * 1000))

    def _on_capture_option_change(self, option: str) -> None:
        if self._capture_option_change_callback is not None:
            self._capture_option_change_callback(option)
        configs["capture"] = option

    def _update_config(self, config: str, value: object) -> None:
        if config not in configs.keys():
            logger.error(
                f"Unknown configuration name: '{config}' provided to update configurations."
            )
        configs[config] = value

    def _update_options(self) -> None:
        "Updates the option widgets according to configs."
        self._interval_entry.setValue(configs["lock_interval"])
        self._press_enter.setChecked(configs["press_enter"])
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, configs["always_on_top"])
