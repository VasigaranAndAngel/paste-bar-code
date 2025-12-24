from typing import cast, override

from PySide6.QtCore import QEasingCurve, QEvent, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QEnterEvent,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QTouchEvent,
)
from PySide6.QtWidgets import QAbstractButton, QApplication, QWidget


class Button(QAbstractButton):
    clicked_with_modifiers: Signal = Signal(Qt.KeyboardModifier)

    def __init__(
        self,
        text: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent, text=text)

        self._custom_color: QColor | None = None

        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents)
        QApplication.setAttribute(
            Qt.ApplicationAttribute.AA_SynthesizeMouseForUnhandledTabletEvents, True
        )
        QApplication.setAttribute(
            Qt.ApplicationAttribute.AA_SynthesizeMouseForUnhandledTouchEvents, True
        )

        self.setMaximumSize(10_000, 10_000)

        _ = self.setProperty("background_color", self.palette().base().color())
        self._hover_anim: QPropertyAnimation = QPropertyAnimation(self, b"background_color", self)
        self._hover_anim.setDuration(300)
        self._hover_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        _ = self._hover_anim.valueChanged.connect(self.repaint)

    def set_custom_color(self, color: QColor | None) -> None:
        self._custom_color = color
        _ = self.setProperty("background_color", color)
        self.repaint()

    def _change_color(self, color: QColor) -> None:
        self._hover_anim.stop()
        self._hover_anim.setEndValue(color)
        self._hover_anim.start()

    @override
    def enterEvent(self, event: QEnterEvent, /) -> None:
        color = (
            x.darker(120)
            if (x := self._custom_color) is not None
            else self.palette().button().color()
        )
        self._change_color(color)

    @override
    def leaveEvent(self, event: QEvent, /) -> None:
        color = x if (x := self._custom_color) is not None else self.palette().base().color()
        self._change_color(color)

    @override
    def mousePressEvent(self, e: QMouseEvent, /) -> None:
        if e.button() != Qt.MouseButton.LeftButton:
            return

        color = (
            x.lighter(110)
            if (x := self._custom_color) is not None
            else self.palette().accent().color()
        )
        self._change_color(color)

    @override
    def mouseReleaseEvent(self, e: QMouseEvent, /) -> None:
        if e.button() != Qt.MouseButton.LeftButton:
            return

        if self.rect().contains(e.pos()):
            color = (
                x.darker(120)
                if (x := self._custom_color) is not None
                else self.palette().button().color()
            )
            self.click()
            self.clicked_with_modifiers.emit(e.modifiers())
        else:
            color = x if (x := self._custom_color) else self.palette().base().color()

        self._change_color(color)

    @override
    def event(self, e: QEvent, /) -> bool:
        if isinstance(e, QTouchEvent):
            if e.type() == e.Type.TouchBegin:
                mouse_event = QMouseEvent(
                    QMouseEvent.Type.MouseButtonPress,
                    e.points()[0].pos(),
                    Qt.MouseButton.LeftButton,
                    Qt.MouseButton.LeftButton,
                    e.modifiers(),
                )
                self.mousePressEvent(mouse_event)
            elif e.type() == e.Type.TouchUpdate:
                pass
            elif e.type() == e.Type.TouchEnd:
                mouse_event = QMouseEvent(
                    QMouseEvent.Type.MouseButtonRelease,
                    e.points()[0].pos(),
                    Qt.MouseButton.LeftButton,
                    Qt.MouseButton.LeftButton,
                    e.modifiers(),
                )
                self.mouseReleaseEvent(mouse_event)
            e.accept()
            return True
        return super().event(e)

    @override
    def paintEvent(self, e: QPaintEvent, /) -> None:
        color = cast(QColor, self.property("background_color"))
        text = self.text()
        with QPainter(self) as p:
            p.setRenderHint(p.RenderHint.Antialiasing, True)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(color)
            p.drawRoundedRect(self.contentsRect().adjusted(0, 0, -1, -1), 5, 5)
            if text:
                p.setPen(self.palette().text().color())
                p.drawText(
                    self.contentsRect().adjusted(0, 0, -1, -1),
                    self.text(),
                    Qt.AlignmentFlag.AlignCenter,
                )
