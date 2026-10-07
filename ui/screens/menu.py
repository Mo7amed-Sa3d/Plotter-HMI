"""Main menu — 6 large buttons, portrait-friendly."""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGridLayout,
                             QPushButton, QLabel, QSizePolicy)

from PyQt5.QtCore import pyqtSignal
from ui.scaling import px


class MenuScreen(QWidget):
    tools_clicked = pyqtSignal()
    speed_clicked = pyqtSignal()
    estop_clicked = pyqtSignal()
    test_cut_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    usb_clicked = pyqtSignal()
    jog_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(px(12), px(12), px(12), px(12))
        outer.setSpacing(px(10))

        title = QLabel("Label Cutter")
        title.setObjectName("screen_title")
        outer.addWidget(title)

        sub = QLabel("Main Menu")
        sub.setObjectName("screen_sub")
        outer.addWidget(sub)

        grid = QGridLayout()
        grid.setSpacing(px(10))

        def mk(text, slot, name=None):
            b = QPushButton(text)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            b.setMinimumHeight(px(100))
            b.clicked.connect(slot)
            if name:
                b.setObjectName(name)
            return b

        # 2 columns × 3 rows
        grid.addWidget(mk("Tool Forces",   self.tools_clicked.emit),   0, 0)
        grid.addWidget(mk("Speed",         self.speed_clicked.emit),   0, 1)
        grid.addWidget(mk("Test Cut",      self.test_cut_clicked.emit), 1, 0)
        grid.addWidget(mk("E-Stop",        self.estop_clicked.emit,
                          name="danger"),                               1, 1)
        grid.addWidget(mk("Settings",      self.settings_clicked.emit), 2, 0)
        grid.addWidget(mk("Cut from USB",  self.usb_clicked.emit,
                          name="primary"),                              2, 1)

        for c in range(2):
            grid.setColumnStretch(c, 1)
        for r in range(3):
            grid.setRowStretch(r, 1)

        outer.addLayout(grid, stretch=1)

        jog_btn = QPushButton("Manual Jog")
        jog_btn.setObjectName("ghost")
        jog_btn.setMinimumHeight(px(72))
        jog_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        jog_btn.clicked.connect(self.jog_clicked.emit)
        outer.addWidget(jog_btn)