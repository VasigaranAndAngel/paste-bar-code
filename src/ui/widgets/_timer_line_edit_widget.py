from typing import override

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import (
    QDoubleValidator,
    QPainter,
    QPaintEvent,
    QResizeEvent,
    QWheelEvent,
)
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QWidget

from ._button import Button


class TimeValidator(QDoubleValidator):
    @override
    def validate(self, arg__1: str, arg__2: int, /) -> object:
        if arg__1.startswith("-"):
            return self.State.Invalid
        if "," in arg__1:
            return self.State.Invalid
        return super().validate(arg__1, arg__2)


class TimerLineEditWidget(QWidget):
    value_changed: Signal = Signal(float)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._line_edit: QLineEdit = QLineEdit("0.0", self)
        self._line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        validator = TimeValidator(self._line_edit)
        validator.setNotation(TimeValidator.Notation.StandardNotation)
        self._line_edit.setValidator(validator)
        self._line_edit.setStyleSheet("QLineEdit {background: transparent; border: 0}")
        _ = self._line_edit.textChanged.connect(self._emit_value_change)
        self._line_edit.focusOutEvent = (
            lambda x: self._line_edit.setText("0") if not self._line_edit.text() else None
        )

        self._add_button: Button = Button("+", self)
        self._add_button.setText("+")
        font = self._add_button.font()
        font.setPointSize(15)
        self._add_button.setFont(font)
        _ = self._add_button.clicked_with_modifiers.connect(self._on_add)

        self._sub_button: Button = Button("-", self)
        font = self._sub_button.font()
        font.setPointSize(15)
        self._sub_button.setFont(font)
        _ = self._sub_button.clicked_with_modifiers.connect(self._on_sub)

        self._layout: QHBoxLayout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.addWidget(self._sub_button)
        self._layout.addWidget(self._line_edit)
        self._layout.addWidget(self._add_button)

        self.setLayout(self._layout)

    @staticmethod
    def _speed_for_modifiers(modifiers: Qt.KeyboardModifier) -> float:
        shift_pressed = modifiers & Qt.KeyboardModifier.ShiftModifier
        ctrl_pressed = modifiers & Qt.KeyboardModifier.ControlModifier

        speed = 1
        if bool(shift_pressed) != bool(ctrl_pressed):
            if shift_pressed:
                speed = 10
            if ctrl_pressed:
                speed = 0.1

        return speed

    def _on_add(self, modifiers: Qt.KeyboardModifier) -> None:
        speed = TimerLineEditWidget._speed_for_modifiers(modifiers)
        self._line_edit.setText(str(float(int(self.value() * 1000) + 100 * speed) / 1000))

    def _on_sub(self, modifiers: Qt.KeyboardModifier) -> None:
        speed = TimerLineEditWidget._speed_for_modifiers(modifiers)
        value = float(int(self.value() * 1000) - 100 * speed) / 1000

        if value < 0:
            self._line_edit.setText("0.0")
        else:
            self._line_edit.setText(str(value))

    def _emit_value_change(self, _: str) -> None:
        self.value_changed.emit(self.value())

    def value(self) -> float:
        """Returns the current value in seconds (float)."""
        value = self._line_edit.text()
        if value == "." or not value:
            value = "0"
        return float(value)

    def setValue(self, value: float) -> None:
        """Sets the value to given value"""
        self._line_edit.setText(str(value))

    @override
    def resizeEvent(self, event: QResizeEvent, /) -> None:
        width, height = event.size().toTuple()
        line_edit_width = width - height * 2
        self._add_button.setFixedSize(height, height)
        self._sub_button.setFixedSize(height, height)
        self._line_edit.setFixedSize(line_edit_width, height)
        return super().resizeEvent(event)

    @override
    def minimumSizeHint(self, /) -> QSize:
        return QSize(0, 0)

    @override
    def wheelEvent(self, event: QWheelEvent, /) -> None:
        modifiers = event.modifiers()

        if event.angleDelta().y() > 0:
            self._on_add(modifiers)
        elif event.angleDelta().y() < 0:
            self._on_sub(modifiers)
        else:
            return super().wheelEvent(event)

    @override
    def paintEvent(self, event: QPaintEvent, /) -> None:
        with QPainter(self) as p:
            p.setRenderHint(p.RenderHint.Antialiasing, True)
            p.setPen(self.palette().button().color())
            p.setBrush(self.palette().base())
            p.drawRoundedRect(self.contentsRect().adjusted(0, 0, -1, -1), 5, 5)
