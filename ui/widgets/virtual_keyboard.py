"""On-screen QWERTY keyboard for touch input.

A QFrame that is a child of the main window, positioned along the
bottom. It attaches to a target QLineEdit (or the internal line edit
of a QSpinBox) and forwards keystrokes to it.

All keys use Qt.NoFocus so tapping them does not steal focus from the
line edit. That means the line edit stays the focus widget for the
whole typing session, and FocusOut is only triggered when the user
taps outside the keyboard.
"""

from PyQt5.QtCore import Qt, QEvent, QObject, pyqtSignal
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import (QFrame, QGridLayout, QHBoxLayout, QPushButton,
                             QApplication, QLineEdit, QTextEdit,
                             QSpinBox, QDoubleSpinBox, QSizePolicy)

from ui.scaling import px


ROWS = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
    ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
    ["a", "s", "d", "f", "g", "h", "j", "k", "l", "."],
    ["SHIFT", "z", "x", "c", "v", "b", "n", "m", "DEL"],
    ["SPACE", "ENTER"],
]


class VirtualKeyboard(QFrame):
    submitted = pyqtSignal()
    cancelled = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("virtual_keyboard")
        self.setFrameShape(QFrame.NoFrame)
        self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self._target = None
        self._caps = False
        self._keys: dict[str, QPushButton] = {}

        grid = QGridLayout(self)
        grid.setContentsMargins(px(6), px(6), px(6), px(6))
        grid.setSpacing(px(4))

        for row_idx, row in enumerate(ROWS):
            col = 0
            for label in row:
                btn = self._make_key(label)
                if label == "SPACE":
                    grid.addWidget(btn, row_idx, col, 1, 6)
                    col += 6
                elif label == "ENTER":
                    grid.addWidget(btn, row_idx, col, 1, 4)
                    col += 4
                elif label == "SHIFT":
                    grid.addWidget(btn, row_idx, col, 1, 2)
                    col += 2
                elif label == "DEL":
                    grid.addWidget(btn, row_idx, col, 1, 2)
                    col += 2
                else:
                    grid.addWidget(btn, row_idx, col, 1, 1)
                    col += 1

        for c in range(10):
            grid.setColumnStretch(c, 1)

        self.hide()

    # ---- Construction helpers ----

    def _make_key(self, label: str) -> QPushButton:
        btn = QPushButton(label)
        btn.setFocusPolicy(Qt.NoFocus)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn.setMinimumHeight(px(40))

        if label in ("SHIFT", "DEL", "ENTER", "SPACE"):
            btn.setObjectName("key_action")
        else:
            btn.setObjectName("key")

        btn.clicked.connect(lambda: self._on_key(label))
        self._keys[label] = btn
        return btn

    def _update_labels(self):
        for label, btn in self._keys.items():
            if label in ("SHIFT", "DEL", "ENTER", "SPACE"):
                continue
            btn.setText(label.upper() if self._caps else label.lower())
        self._keys["SHIFT"].setText("SHIFT▼" if self._caps else "SHIFT")

    # ---- Attach / detach ----

    def attach(self, target):
        """Bind to a QLineEdit-like widget and show."""
        self._target = target
        self._reposition()
        self.show()
        self.raise_()

    def detach(self):
        self._target = None
        self.hide()

    def target(self):
        return self._target

    # ---- Key handling ----

    def _on_key(self, label: str):
        if self._target is None:
            return

        if label == "DEL":
            self._target.backspace()
        elif label == "ENTER":
            self.submitted.emit()
            # Synthesize Return so QLineEdit emits returnPressed,
            # and QSpinBox commits its value.
            ev = QKeyEvent(QEvent.KeyPress, Qt.Key_Return, Qt.NoModifier, "\r")
            QApplication.sendEvent(self._target, ev)
            self.detach()
        elif label == "SPACE":
            self._target.insert(" ")
        elif label == "SHIFT":
            self._caps = not self._caps
            self._update_labels()
        else:
            ch = label.upper() if self._caps else label.lower()
            self._target.insert(ch)
            if self._caps:
                self._caps = False
                self._update_labels()

    # ---- Geometry ----

    def _reposition(self):
        parent = self.parentWidget()
        if parent is None:
            return
        h = self.sizeHint().height()
        self.setGeometry(0, parent.height() - h, parent.width(), h)

    def showEvent(self, event):
        super().showEvent(event)
        self._reposition()


class KeyboardFilter(QObject):
    """Installs on QApplication. Shows the keyboard when a text input
    receives focus, hides it when the focus leaves the keyboard region."""

    def __init__(self, keyboard: VirtualKeyboard):
        super().__init__()
        self.keyboard = keyboard

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusIn:
            target = self._as_text_target(obj)
            if target is not None:
                self.keyboard.attach(target)
        elif event.type() == QEvent.FocusOut:
            # The new focus widget is in obj.focusWidget() of the app.
            # If it belongs to the keyboard, do not hide.
            new_focus = QApplication.focusWidget()
            if new_focus is None or not self._inside_keyboard(new_focus):
                # Do not hide if the outgoing widget is being replaced
                # by another text target (FocusIn on the new one will
                # re-attach the keyboard anyway).
                if self._as_text_target(new_focus) is None:
                    self.keyboard.detach()
        return False

    @staticmethod
    def _as_text_target(obj):
        if obj is None:
            return None
        if isinstance(obj, (QLineEdit, QTextEdit)):
            return obj
        if isinstance(obj, (QSpinBox, QDoubleSpinBox)):
            return obj.lineEdit()
        return None

    def _inside_keyboard(self, widget) -> bool:
        p = widget
        while p is not None:
            if p is self.keyboard:
                return True
            p = p.parentWidget()
        return False