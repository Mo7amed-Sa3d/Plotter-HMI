"""Main menu — 6 large buttons, laid out responsively."""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QHBoxLayout,
                             QPushButton, QLabel, QSizePolicy)

from ui.scaling import px, is_portrait


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
        outer.setContentsMargins(px(16), px(12), px(16), px(16))
        outer.setSpacing(px(10))

        title = QLabel("Label Cutter")
        title.setObjectName("screen_title")
        outer.addWidget(title)

        sub = QLabel("Main Menu")
        sub.setObjectName("screen_sub")
        outer.addWidget(sub)

        grid = QGridLayout()
        grid.setSpacing(px(12))

        def mk(text, slot, name=None):
            b = QPushButton(text)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            b.setMinimumHeight(px(90))
            b.clicked.connect(slot)
            if name:
                b.setObjectName(name)
            return b

        # Portrait and landscape both use a 3-column grid, but the
        # rows differ. In portrait the labels are still readable
        # because font size scales with width.
        grid.addWidget(mk("Tool Forces",   self.tools_clicked.emit),   0, 0)
        grid.addWidget(mk("Speed",         self.speed_clicked.emit),   0, 1)
        grid.addWidget(mk("E-Stop",        self.estop_clicked.emit,
                          name="danger"),                               0, 2)
        grid.addWidget(mk("Test Cut",      self.test_cut_clicked.emit), 1, 0)
        grid.addWidget(mk("Settings",      self.settings_clicked.emit), 1, 1)
        grid.addWidget(mk("Cut from USB",  self.usb_clicked.emit,
                          name="primary"),                              1, 2)

        for c in range(3):
            grid.setColumnStretch(c, 1)
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)

        outer.addLayout(grid, stretch=1)

        jog_btn = QPushButton("Manual Jog")
        jog_btn.setObjectName("ghost")
        jog_btn.setMinimumHeight(px(64))
        jog_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        jog_btn.clicked.connect(self.jog_clicked.emit)
        outer.addWidget(jog_btn)