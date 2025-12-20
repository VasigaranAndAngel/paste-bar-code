import cv2
import pyautogui
from cv2.typing import MatLike
from PySide6.QtCore import Signal
from PySide6.QtGui import QImage, QPixmap, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from detect_code import detect_code
from ui.widgets import DetectionIndicator, TimerLineEditWidget


class MainWindow(QMainWindow):
    _update_frame_signal: Signal = Signal(str, object)
    "To turn child thread's to main thread."

    def __init__(self) -> None:
        super().__init__()

        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self._last_code: str = ""
        self._image_widget: QLabel = QLabel(self)
        self._image_widget.setMinimumSize(0, 0)
        self._image_widget.setScaledContents(True)
        self._image_widget.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)

        self._indicator_widget: DetectionIndicator = DetectionIndicator(self)

        self._interval_entry: TimerLineEditWidget = TimerLineEditWidget(self)
        self._interval_entry.setFixedSize(130, 40)
        _ = self._interval_entry.value_changed.connect(self._change_timer)
        self._interval_entry.setValue(1.5)

        self._press_enter: QCheckBox = QCheckBox(self)
        self._press_enter.setText("Press Enter")

        self._buttons_layout: QHBoxLayout = QHBoxLayout()
        self._buttons_layout.addWidget(self._interval_entry)
        self._buttons_layout.addWidget(self._press_enter)
        self._buttons_layout.addWidget(self._indicator_widget)

        self._main_layout: QVBoxLayout = QVBoxLayout()
        self._main_layout.addWidget(self._image_widget)
        self._main_layout.addLayout(self._buttons_layout)

        central_widget = QWidget(self)
        central_widget.setLayout(self._main_layout)

        self.setCentralWidget(central_widget)

        _ = self._update_frame_signal.connect(self._update_frame)

    def update_frame(self, frame: MatLike) -> None:
        code, _frame = detect_code(frame)
        self._update_frame_signal.emit(code, _frame)

    def _update_frame(self, code: str, _frame: MatLike) -> None:
        rgb_img = cv2.cvtColor(_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape  # pyright: ignore[reportAny]
        bytes_per_line = ch * w  # pyright: ignore[reportAny]
        q_image = QImage(rgb_img.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)  # pyright: ignore[reportAny]
        pixmap = QPixmap.fromImage(q_image)
        self._image_widget.setPixmap(pixmap)
        self._image_widget.setMinimumSize(0, 0)
        if code and not (self._indicator_widget.locked and code == self._last_code):
            self._indicator_widget.code_detected(code)
            pyautogui.typewrite(code)
            if self._press_enter.isChecked():
                pyautogui.press("enter")
            self._last_code = code

    def _change_timer(self, time: float) -> None:
        """Changes the time of interval timer. (seconds)"""
        self._indicator_widget.change_timer(int(time * 1000))
