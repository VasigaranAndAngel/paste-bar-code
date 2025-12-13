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
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents)
        QApplication.setAttribute(
            Qt.ApplicationAttribute.AA_SynthesizeMouseForUnhandledTabletEvents, True
        )
        QApplication.setAttribute(
            Qt.ApplicationAttribute.AA_SynthesizeMouseForUnhandledTouchEvents, True
        )

        if text is None:  # TODO: remove
            self.setText("test TEXT")  # TODO: remove
        self.setMaximumSize(10_000, 10_000)

        _ = self.setProperty("background_color", self.palette().button().color())
        self._hover_anim: QPropertyAnimation = QPropertyAnimation(self, b"background_color", self)
        self._hover_anim.setDuration(300)
        self._hover_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        _ = self._hover_anim.valueChanged.connect(self.repaint)

    def _change_color(self, color: QColor) -> None:
        self._hover_anim.stop()
        self._hover_anim.setEndValue(color)
        self._hover_anim.start()

    @override
    def enterEvent(self, event: QEnterEvent, /) -> None:
        self._change_color(self.palette().base().color())

    @override
    def leaveEvent(self, event: QEvent, /) -> None:
        self._change_color(self.palette().button().color())

    @override
    def mousePressEvent(self, e: QMouseEvent, /) -> None:
        self._change_color(self.palette().accent().color())

    @override
    def mouseReleaseEvent(self, e: QMouseEvent, /) -> None:
        if self.rect().contains(e.pos()):
            self._change_color(self.palette().base().color())
            self.click()
            self.clicked_with_modifiers.emit(e.modifiers())
        else:
            self._change_color(self.palette().button().color())

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
                pass
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
