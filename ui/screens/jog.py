"""Jog screen — 4 arrows and a central home/zero button."""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QLabel, QDoubleSpinBox,
                             QSizePolicy)


from ui.scaling import px, size


class JogScreen(QWidget):
    back_clicked = pyqtSignal()
    jog = pyqtSignal(float, float)
    home_and_zero = pyqtSignal()
    set_step = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(px(16), px(12), px(16), px(16))
        root.setSpacing(px(10))

        header = QHBoxLayout()
        back = QPushButton("← Back")
        back.setObjectName("ghost")
        back.setMinimumHeight(px(44))
        back.clicked.connect(self.back_clicked.emit)
        header.addWidget(back)

        title = QLabel("Manual Jog")
        title.setObjectName("screen_title")
        header.addWidget(title)
        header.addStretch(1)
        root.addLayout(header)

        step_row = QHBoxLayout()
        step_row.addWidget(QLabel("Step:"))
        self.step_spin = QDoubleSpinBox()
        self.step_spin.setRange(0.1, 100.0)
        self.step_spin.setValue(1.0)
        self.step_spin.setSuffix(" mm")
        self.step_spin.setMinimumHeight(px(44))
        self.step_spin.valueChanged.connect(self.set_step.emit)
        step_row.addWidget(self.step_spin)
        step_row.addStretch(1)
        root.addLayout(step_row)

        # Arrow grid. Each cell expands to fill available space.
        grid = QGridLayout()
        grid.setSpacing(px(8))

        arrow_size = px(90)

        def arrow(text, dx, dy):
            b = QPushButton(text)
            b.setObjectName("arrow")
            b.setMinimumSize(arrow_size, arrow_size)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            b.clicked.connect(lambda: self._jog(dx, dy))
            return b

        grid.addWidget(arrow("▲", 0, +1), 0, 1)
        grid.addWidget(arrow("◀", -1, 0), 1, 0)
        grid.addWidget(arrow("▶", +1, 0), 1, 2)
        grid.addWidget(arrow("▼", 0, -1), 2, 1)

        center = QPushButton("⌂\nHome X\nZero Y/F")
        center.setObjectName("jog_center")
        center.setMinimumSize(arrow_size, arrow_size)
        center.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        center.clicked.connect(self.home_and_zero.emit)
        grid.addWidget(center, 1, 1)

        for c in range(3):
            grid.setColumnStretch(c, 1)
        for r in range(3):
            grid.setRowStretch(r, 1)

        root.addLayout(grid, stretch=1)

    def _jog(self, dx, dy):
        step = self.step_spin.value()
        self.jog.emit(dx * step, dy * step)