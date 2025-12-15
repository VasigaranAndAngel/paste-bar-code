from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QVBoxLayout, QWidget

from ui.widgets import DetectionIndicator, TimerLineEditWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self._image_widget: QLabel = QLabel(self)
        self._image_widget.setMinimumSize(0, 0)

        self._indicator_widget: DetectionIndicator = DetectionIndicator(self)

        self._interval_entry: TimerLineEditWidget = TimerLineEditWidget(self)
        self._interval_entry.setFixedSize(130, 40)
        _ = self._interval_entry.value_changed.connect(self._change_timer)
        self._interval_entry.setValue(1.5)

        self._buttons_layout: QHBoxLayout = QHBoxLayout()
        self._buttons_layout.addWidget(self._interval_entry)
        self._buttons_layout.addWidget(self._indicator_widget)

        self._main_layout: QVBoxLayout = QVBoxLayout()
        self._main_layout.addWidget(self._image_widget)
        self._main_layout.addLayout(self._buttons_layout)

        central_widget = QWidget(self)
        central_widget.setLayout(self._main_layout)

        self.setCentralWidget(central_widget)

    def _change_timer(self, time: float) -> None:
        """Changes the time of interval timer. (seconds)"""
        self._indicator_widget.change_timer(int(time * 1000))
