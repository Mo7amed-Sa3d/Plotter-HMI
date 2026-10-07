"""Test cut screen."""

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QComboBox, QSizePolicy)

from ui.scaling import px


TEST_PATTERNS = {
    "Square 20x20": """
G21
G90
G1 X20 Y0 F40
G1 X20 Y20
G1 X0 Y20
G1 X0 Y0
""",
    "Circle Ø20": """
G21
G90
G1 X20 Y10 F40
G1 X19.7 Y13.9
G1 X18.9 Y17.7
G1 X17.4 Y21.2
G1 X15.3 Y24.4
G1 X12.6 Y27.0
G1 X9.5 Y29.0
G1 X6.2 Y30.2
G1 X2.7 Y30.7
G1 X-0.8 Y30.3
G1 X-4.1 Y29.1
G1 X-7.1 Y27.2
G1 X-9.6 Y24.7
G1 X-11.5 Y21.6
G1 X-12.6 Y18.2
G1 X-13.0 Y14.7
G1 X-12.4 Y11.2
G1 X-11.1 Y7.9
G1 X-9.1 Y5.0
G1 X-6.5 Y2.6
G1 X-3.4 Y0.8
G1 X0 Y0
""",
}


class TestCutScreen(QWidget):
    back_clicked = pyqtSignal()
    run_test = pyqtSignal(str)

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
        title = QLabel("Test Cut")
        title.setObjectName("screen_title")
        header.addWidget(title)
        header.addStretch(1)
        root.addLayout(header)

        row = QHBoxLayout()
        row.addWidget(QLabel("Pattern:"))
        self.pattern = QComboBox()
        self.pattern.addItems(TEST_PATTERNS.keys())
        self.pattern.setMinimumHeight(px(46))
        row.addWidget(self.pattern, stretch=1)
        root.addLayout(row)

        run = QPushButton("Run Test Cut")
        run.setObjectName("primary")
        run.setMinimumHeight(px(80))
        run.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        run.clicked.connect(self._run)
        root.addWidget(run, stretch=1)

    def _run(self):
        name = self.pattern.currentText()
        self.run_test.emit(TEST_PATTERNS[name].strip())