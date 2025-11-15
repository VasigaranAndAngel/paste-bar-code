from random import choices
from string import ascii_letters
from typing import override

from PySide6.QtCore import QPoint, QPropertyAnimation, QRect, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QEnterEvent, QLinearGradient, QPainter, QPaintEvent, QPen, QPixmap
from PySide6.QtWidgets import QAbstractButton, QHBoxLayout, QLabel, QPushButton, QWidget


def draw_bulb(rect: QRect, color: QColor, outline_color: QColor) -> QPixmap:
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

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)

        self.GREEN_LIGHT: QPixmap = draw_bulb(QRect(0, 0, 35, 35), QColor("green"), QColor("grey"))
        self.WHITE_LIGHT: QPixmap = draw_bulb(QRect(0, 0, 35, 35), QColor("white"), QColor("grey"))

        self.setMaximumHeight(50)

        self._layout: QHBoxLayout = QHBoxLayout(self)
        self._layout.setContentsMargins(5, 5, 5 + DetectionIndicator.BUTTONS_WIDTH, 5)
        self._layout.setSpacing(5)

        self._code_label: QLabel = QLabel(self)
        self._audio_button: QAbstractButton = QPushButton("V", self)
        self._audio_button.setFixedSize(*[DetectionIndicator.BUTTONS_WIDTH] * 2)

        self._layout.addWidget(self._code_label, Qt.AlignmentFlag.AlignLeft)
        self._layout.addWidget(self._audio_button, Qt.AlignmentFlag.AlignRight)

        self._layout.addLayout(self._layout)

        self.setLayout(self._layout)

        _ = self.setProperty("light_opacity", 0.0)

        self._light_opacity_anim: QPropertyAnimation = QPropertyAnimation(
            self, b"light_opacity", self
        )
        self._light_opacity_anim.setDuration(1000)
        _ = self._light_opacity_anim.valueChanged.connect(self.repaint)
        self._light_opacity_anim.setStartValue(0.0)
        self._light_opacity_anim.setEndValue(1.0)
        self._light_opacity_anim.setKeyValues([(0.0, 0.0), (0.1, 1.0), (1.0, 0.0)])

        _ = self.setProperty("timer", 0.0)
        self._timer_anim: QPropertyAnimation = QPropertyAnimation(self, b"timer", self)
        self._timer_anim.setDuration(2000)
        self._timer_anim.setStartValue(0.0)
        self._timer_anim.setEndValue(1.0)
        _ = self._timer_anim.valueChanged.connect(self.repaint)

        _ = self.setProperty("timer_opacity", 0.0)
        self._timer_opacity_anim: QPropertyAnimation = QPropertyAnimation(
            self, b"timer_opacity", self
        )
        self._timer_opacity_anim.setDuration(250)
        self._timer_opacity_anim.setStartValue(0.0)
        self._timer_opacity_anim.setEndValue(1.0)
        _ = self._timer_opacity_anim.valueChanged.connect(self.repaint)

        # Region test TODO: remove
        # self.setStyleSheet("QWidget {border: 1px solid red}")
        self._code_label.setText("abcxyz")
        timer = QTimer(self)
        _ = timer.timeout.connect(lambda: self.code_detected("".join(choices(ascii_letters, k=10))))
        timer.start(2000)
        # endregion

    def code_detected(self, code: str) -> None:
        self._code_label.setText(code)
        self._light_opacity_anim.stop()
        self._light_opacity_anim.start()
        self._timer_anim.stop()
        self._timer_anim.start()
        self._timer_opacity_anim.stop()
        self._timer_opacity_anim.start()

    @override
    def enterEvent(self, event: QEnterEvent, /) -> None:
        self.code_detected("")
        return super().enterEvent(event)

    @override
    def paintEvent(self, event: QPaintEvent, /) -> None:
        timer: float = self.property("timer")
        opacity: float = self.property("timer_opacity")
        middle = (wid := self.width()) / 2
        width = wid * (1 - timer)
        pos_x = middle - width / 2
        with QPainter(self) as p:
            # Region test TODO: should be removed
            penC = QColor("red")
            penC.setAlphaF(0.5)
            p.setPen(penC)
            # p.drawRect(self.contentsRect().adjusted(0, 0, -1, -1))
            # endregion

            # Region Draw timer indicator
            p.setPen(Qt.PenStyle.NoPen)
            brush = QColor("lightgreen")
            brush.setAlphaF(opacity)
            p.setBrush(brush)
            p.drawRect(QRectF(pos_x, self.height() - 2, width, 2))
            # endregion

            # Region Draw bulb indicator
            p.drawPixmap(QPoint(self.contentsRect().width() - 44, 7), self.WHITE_LIGHT)
            p.setOpacity(self.property("light_opacity") or 0.0)
            p.drawPixmap(QPoint(self.contentsRect().width() - 44, 7), self.GREEN_LIGHT)
            # endregion
