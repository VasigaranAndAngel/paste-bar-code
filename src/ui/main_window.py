from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget

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
        # region test # TODO: remove
        self._image_widget.setStyleSheet("QLabel {border: 2px solid red; border-radius: 10px;}")
        self._buttons_layout.addWidget(QPushButton("button 2", parent=self))
        self._buttons_layout.addWidget(QPushButton("button 3", parent=self))
        # endregion
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


# region test # TODO: should be removed
if __name__ == "__main__":
    import cv2
    from PIL import Image
    from PySide6.QtGui import QPixmap
    from PySide6.QtWidgets import QApplication

    def capture_frame() -> QPixmap:
        cam = cv2.VideoCapture(0)

        while True:
            success, frame = cam.read()
            if success:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                qt_pixmap = Image.fromarray(rgb_image).toqpixmap()
                break

        cam.release()
        return qt_pixmap

    app = QApplication([])
    win = MainWindow()
    win._image_widget.setPixmap(capture_frame())
    _ = win.show()
    _ = app.exec()
# endregion
