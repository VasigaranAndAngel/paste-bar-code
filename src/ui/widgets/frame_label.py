from typing import override

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPainterPath, QPaintEvent, QPixmap
from PySide6.QtWidgets import QCheckBox, QLabel, QWidget


class FrameLabel(QLabel):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._pixmap: QPixmap = QPixmap()

        self.setScaledContents(True)
        self.setMinimumSize(0, 0)

        self._flip_toggle: QCheckBox = QCheckBox(self)
        self._flip_toggle.setText("Flip")

    @override
    def setPixmap(self, arg__1: QPixmap, /) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        self._pixmap = arg__1
        self.repaint()

    @override
    def paintEvent(self, arg__1: QPaintEvent, /) -> None:
        image = self._pixmap.toImage()

        if (
            image.width() > self.contentsRect().width()
            or image.height() > self.contentsRect().height()
        ):
            image = image.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)

        if self._flip_toggle.isChecked():
            image.flip(Qt.Orientation.Horizontal)

        with QPainter(self) as p:
            p.setRenderHint(p.RenderHint.Antialiasing, True)

            image_pos = self.contentsRect().center() - image.rect().center()
            path = QPainterPath()
            path.addRoundedRect(
                image_pos.x(), image_pos.y(), image.size().width(), image.size().height(), 10, 10
            )
            p.setClipPath(path)
            p.drawImage(image_pos, image)
