from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget

from ui.widgets import DetectionIndicator


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self._image_widget: QLabel = QLabel(self)
        self._image_widget.setMinimumSize(0, 0)

        self.setCentralWidget(central_widget := QWidget(self))

        central_widget.setLayout(main_layout := QVBoxLayout(self))

        main_layout.addWidget(self._image_widget)
        main_layout.addLayout(buttons_layout := QHBoxLayout())

        self._main_layout: QVBoxLayout = main_layout
        self._buttons_layout: QHBoxLayout = buttons_layout

        # Region test
        self._image_widget.setStyleSheet("QLabel {border: 2px solid red; border-radius: 10px;}")
        self._buttons_layout.addWidget(QPushButton("button 1", parent=self))
        self._buttons_layout.addWidget(QPushButton("button 2", parent=self))
        self._buttons_layout.addWidget(QPushButton("button 3", parent=self))
        # endregion
        self._indicator_widget: DetectionIndicator = DetectionIndicator(self)
        self._buttons_layout.addWidget(self._indicator_widget)


# Region test # TODO: should be removed
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