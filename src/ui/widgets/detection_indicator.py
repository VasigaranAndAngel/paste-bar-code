from typing import cast, override

from PySide6.QtCore import QPoint, QPropertyAnimation, QRect, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPaintEvent, QPen, QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from ._button import Button


def draw_bulb(rect: QRect, color: QColor, outline_color: QColor) -> QPixmap:
    ellipse_rect = rect.adjusted(10, 10, -10, -10)
    width, height = ellipse_rect.size().width() / 2, ellipse_rect.size().height() / 2

    pixmap = QPixmap(rect.size())
    pixmap.fill("Transparent")

    with QPainter(pixmap) as p:
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient()

        # region outline
        dark_outline_color = outline_color.darker(160)
        gradient.setColorAt(0, dark_outline_color)
        gradient.setColorAt(1, outline_color)
        gradient.setCoordinateMode(gradient.CoordinateMode.ObjectMode)
        pen = QPen(Qt.PenStyle.SolidLine)
        pen.setWidth(int(0.15 * (rect.size().width() + rect.size().height()) / 2))
        pen.setBrush(gradient)
        p.setPen(pen)
        p.drawEllipse(ellipse_rect.adjusted(1, 1, 1, 1).center(), width, height)
        # endregion

        # region green gradient fill
        light_color = color.lighter(190)
        dark_color = color.darker(150)
        gradient.setColorAt(0, dark_color)
        gradient.setColorAt(1, light_color)
        gradient.setStart(0, 0)
        gradient.setFinalStop(0, 1.3)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(gradient)
        p.drawEllipse(ellipse_rect.adjusted(1, 1, 1, 1).center(), width, height)
        # endregion

        # region
        gradient.setColorAt(0, QColor(255, 255, 255, 150))
        gradient.setColorAt(1, "transparent")
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(gradient)
        p.drawEllipse(
            ellipse_rect.adjusted(1, int(-height * 0.8), 1, 1).center(), width * 0.8, height / 2
        )
        # endregion

    return pixmap


class DetectionIndicator(QWidget):
    BUTTONS_WIDTH: int = 36
    lock_changed: Signal = Signal(bool)

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)

        self.GREEN_LIGHT: QPixmap = draw_bulb(QRect(0, 0, 35, 35), QColor("green"), QColor("grey"))
        self.WHITE_LIGHT: QPixmap = draw_bulb(QRect(0, 0, 35, 35), QColor("white"), QColor("grey"))
        self.locked: bool = False

        self.setMaximumHeight(40)

        self._code_label: QLabel = QLabel(self)
        self._audio_button: Button = Button("X", self)
        self._audio_button.setFixedSize(*[DetectionIndicator.BUTTONS_WIDTH] * 2)
        self._audio_button.set_custom_color(QColor("#ff5959"))

        self._layout: QHBoxLayout = QHBoxLayout(self)
        self._layout.setContentsMargins(10, 0, 0 + DetectionIndicator.BUTTONS_WIDTH, 0)
        self._layout.setSpacing(0)
        self._layout.addWidget(self._code_label, Qt.AlignmentFlag.AlignLeft)
        self._layout.addWidget(self._audio_button, Qt.AlignmentFlag.AlignRight)

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

    def code_detected(self, code: str) -> None:
        self._code_label.setText(code)
        self._light_opacity_anim.stop()
        self._light_opacity_anim.start()
        self._timer_anim.stop()
        self._timer_anim.start()
        self._timer_opacity_anim.stop()
        self._timer_opacity_anim.start()

    def change_timer(self, ms: int) -> None:
        self._timer_anim.setDuration(ms)
        if ms < 500:
            self._timer_opacity_anim.setDuration(int(0.25 * ms))
        elif ms < 1700:
            self._timer_opacity_anim.setDuration(250)
        else:
            self._timer_opacity_anim.setDuration(500)

    def _lock(self) -> None:
        self.locked = True
        self.lock_changed.emit(True)

    def _unlock(self) -> None:
        self.locked = False
        self.lock_changed.emit(False)

    @override
    def paintEvent(self, event: QPaintEvent, /) -> None:
        timer = cast(float, self.property("timer"))
        opacity = cast(float, self.property("timer_opacity"))
        middle = (wid := self.width()) / 2
        width = wid * (1 - timer)
        pos_x = middle - width / 2
        with QPainter(self) as p:
            p.setRenderHint(p.RenderHint.Antialiasing, True)
            # region Draw background
            color = self.palette().button().color()
            color.setAlphaF(0.5)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(color)
            p.drawRoundedRect(self.contentsRect(), 5, 5)
            # endregion

            # region Draw timer indicator
            p.setPen(Qt.PenStyle.NoPen)
            brush = QColor("lightgreen")
            brush.setAlphaF(opacity)
            p.setBrush(brush)
            p.drawRect(QRectF(pos_x, self.height() - 2, width, 2))
            # endregion

            # region Draw bulb indicator
            p.drawPixmap(QPoint(self.contentsRect().width() - 40, 3), self.WHITE_LIGHT)
            light_opacity = cast(float, self.property("light_opacity"))
            if light_opacity > 0:
                p.setOpacity(light_opacity)
                p.drawPixmap(QPoint(self.contentsRect().width() - 40, 3), self.GREEN_LIGHT)
            # endregion
