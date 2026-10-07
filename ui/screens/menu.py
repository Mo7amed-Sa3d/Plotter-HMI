"""Main menu — 6 buttons, jog pad, and step selector, portrait-friendly."""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QLabel, QComboBox, QSizePolicy,
                             QGroupBox, QFrame)

from ui.scaling import px


STEP_SIZES = ["0.1", "0.5", "1", "5", "10", "50", "100"]


class MenuScreen(QWidget):
    # Menu buttons
    tools_clicked = pyqtSignal()
    speed_clicked = pyqtSignal()
    estop_clicked = pyqtSignal()
    test_cut_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    usb_clicked = pyqtSignal()

    # Jog pad
    jog = pyqtSignal(float, float)
    home_and_zero = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(px(12), px(10), px(12), px(12))
        root.setSpacing(px(8))

        # ---- Title ----
        title = QLabel("Label Cutter")
        title.setObjectName("screen_title")
        root.addWidget(title)

        # ---- Menu buttons (2 columns x 3 rows) ----
        menu_grid = QGridLayout()
        menu_grid.setSpacing(px(8))

        def mk(text, slot, name=None):
            b = QPushButton(text)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            b.setMinimumHeight(px(58))
            b.clicked.connect(slot)
            if name:
                b.setObjectName(name)
            return b

        menu_grid.addWidget(mk("Tool Forces", self.tools_clicked.emit), 0, 0)
        menu_grid.addWidget(mk("Speed",       self.speed_clicked.emit), 0, 1)
        menu_grid.addWidget(mk("Test Cut",    self.test_cut_clicked.emit), 1, 0)
        menu_grid.addWidget(mk("E-Stop",      self.estop_clicked.emit,
                               name="danger"), 1, 1)
        menu_grid.addWidget(mk("Settings",    self.settings_clicked.emit), 2, 0)
        menu_grid.addWidget(mk("Cut from USB", self.usb_clicked.emit,
                               name="primary"), 2, 1)

        menu_grid.setColumnStretch(0, 1)
        menu_grid.setColumnStretch(1, 1)
        root.addLayout(menu_grid)

        # ---- Separator ----
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #333333; background-color: #333333;")
        sep.setFixedHeight(1)
        root.addWidget(sep)

        # ---- Step size selector ----
        step_row = QHBoxLayout()
        step_row.setSpacing(px(6))

        step_lbl = QLabel("Step")
        step_lbl.setObjectName("screen_sub")
        step_row.addWidget(step_lbl)

        self.step_combo = QComboBox()
        self.step_combo.addItems(STEP_SIZES)
        self.step_combo.setCurrentText("1")
        self.step_combo.setMinimumHeight(px(40))
        self.step_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        step_row.addWidget(self.step_combo, stretch=1)

        unit = QLabel("mm")
        unit.setObjectName("screen_sub")
        step_row.addWidget(unit)

        root.addLayout(step_row)

        # ---- Jog pad ----
        jog_box = QGroupBox("Manual Jog")
        jog_layout = QGridLayout(jog_box)
        jog_layout.setSpacing(px(6))
        jog_layout.setContentsMargins(px(8), px(8), px(8), px(8))

        def arrow(text, dx, dy):
            b = QPushButton(text)
            b.setObjectName("arrow")
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            b.setMinimumSize(px(70), px(60))
            b.clicked.connect(lambda: self._jog(dx, dy))
            return b

        jog_layout.addWidget(arrow("▲", 0, +1), 0, 1)
        jog_layout.addWidget(arrow("◀", -1, 0), 1, 0)
        jog_layout.addWidget(arrow("▶", +1, 0), 1, 2)
        jog_layout.addWidget(arrow("▼", 0, -1), 2, 1)

        center = QPushButton("⌂\nHome X\nZero Y/F")
        center.setObjectName("jog_center")
        center.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        center.setMinimumSize(px(70), px(60))
        center.clicked.connect(self.home_and_zero.emit)
        jog_layout.addWidget(center, 1, 1)

        for c in range(3):
            jog_layout.setColumnStretch(c, 1)
        for r in range(3):
            jog_layout.setRowStretch(r, 1)

        root.addWidget(jog_box, stretch=1)

    # ---- Helpers ----

    def _jog(self, dx: float, dy: float):
        try:
            step = float(self.step_combo.currentText())
        except ValueError:
            step = 1.0
        self.jog.emit(dx * step, dy * step)