from string import ascii_letters
from typing import override
from random import choices

from PySide6.QtCore import QPoint, QPropertyAnimation, QRect, QTimer, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QEnterEvent,
    QGradient,
    QLinearGradient,
    QPainter,
    QPaintEvent,
    QPen,
    QPixmap,
    QTransform,
)
from PySide6.QtWidgets import (
    QAbstractButton,
    QGraphicsBlurEffect,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def draw_bulb(
    rect: QRect,
    color: QColor,
    outline_color: QColor,
) -> QPixmap:
    elipse_rect = rect.adjusted(10, 10, -10, -10)
    width, height = elipse_rect.size().width() / 2, elipse_rect.size().height() / 2

    pixmap = QPixmap(rect.size())
    pixmap.fill("Transparent")

    with QPainter(pixmap) as p:
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient()

        # Region outline
        dark_outline_color = outline_color.darker(160)
        gradient.setColorAt(0, dark_outline_color)
        gradient.setColorAt(1, outline_color)
        gradient.setCoordinateMode(gradient.CoordinateMode.ObjectMode)
        pen = QPen(Qt.PenStyle.SolidLine)
        pen.setWidth(int(0.15 * (rect.size().width() + rect.size().height()) / 2))
        pen.setBrush(gradient)
        p.setPen(pen)
        p.drawEllipse(elipse_rect.adjusted(1, 1, 1, 1).center(), width, height)
        # endregion

        # Region green gradient fill
        light_color = color.lighter(190)
        dark_color = color.darker(150)
        gradient.setColorAt(0, dark_color)
        gradient.setColorAt(1, light_color)
        gradient.setStart(0, 0)
        gradient.setFinalStop(0, 1.3)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(gradient)
        p.drawEllipse(elipse_rect.adjusted(1, 1, 1, 1).center(), width, height)
        # end region

        # Region
        gradient.setColorAt(0, QColor(255, 255, 255, 150))
        gradient.setColorAt(1, "transparent")
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(gradient)
        p.drawEllipse(
            elipse_rect.adjusted(1, int(-height * 0.8), 1, 1).center(), width * 0.8, height / 2
        )
        # endregion

    return pixmap


class DetectionIndicator(QWidget):
    BUTTONS_WIDTH: int = 40
    GREEN_LIGHT: QPixmap = draw_bulb(QRect(0, 0, 35, 35), QColor("green"), QColor("grey"))
    WHITE_LIGHT: QPixmap = draw_bulb(QRect(0, 0, 35, 35), QColor("white"), QColor("grey"))

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)

        self.setMaximumHeight(50)

        self._layout: QHBoxLayout = QHBoxLayout(self)
        self._layout.setContentsMargins(5, 5, 5 + DetectionIndicator.BUTTONS_WIDTH, 5)
        self._layout.setSpacing(5)
        self.setLayout(self._layout)

        self._code_label: QLabel = QLabel(self)
        self._audio_button: QAbstractButton = QPushButton("V", self)
        self._audio_button.setFixedSize(*[DetectionIndicator.BUTTONS_WIDTH] * 2)

        self._layout.addWidget(self._code_label, Qt.AlignmentFlag.AlignLeft)
        self._layout.addWidget(self._audio_button, Qt.AlignmentFlag.AlignRight)

        _ = self.setProperty("light_opacity", 0.0)

        self._light_opacity_anim: QPropertyAnimation = QPropertyAnimation(
            self, b"light_opacity", self
        )
        self._light_opacity_anim.setDuration(1500)
        _ = self._light_opacity_anim.valueChanged.connect(self.repaint)
        self._light_opacity_anim.setStartValue(0.0)
        self._light_opacity_anim.setEndValue(1.0)
        self._light_opacity_anim.setKeyValues([(0.0, 0.0), (0.1, 1.0), (1.0, 0.0)])

        # Region test
        # self.setStyleSheet("QWidget {border: 1px solid red}")
        self._code_label.setText("abcxyz")
        timer = QTimer(self)
        timer.timeout.connect(lambda: self.code_detected("".join(choices(ascii_letters, k=10))))
        timer.start(2000)
        # endregion

    def code_detected(self, code: str) -> None:
        self._code_label.setText(code)
        self._light_opacity_anim.stop()
        self._light_opacity_anim.start()
        # TODO: start timeout timer too

    @override
    def enterEvent(self, event: QEnterEvent, /) -> None:
        self.code_detected("")
        return super().enterEvent(event)

    @override
    def paintEvent(self, event: QPaintEvent, /) -> None:
        with QPainter(self) as p:
            # Region test TODO: should be removed
            # penC = QColor("red")
            # penC.setAlphaF(0.5)
            # p.setPen(penC)
            # p.drawRect(self.contentsRect().adjusted(0, 0, -1, -1))
            # endregion
            # Region Draw bult indicator
            p.drawPixmap(
                QPoint(self.contentsRect().width() - 44, 7), DetectionIndicator.WHITE_LIGHT
            )
            p.setOpacity(self.property("light_opacity") or 0.0)
            p.drawPixmap(
                QPoint(self.contentsRect().width() - 44, 7), DetectionIndicator.GREEN_LIGHT
            )
            # endregion


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


if __name__ == "__main__":
    import cv2
    from PIL import Image, ImageQt
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
