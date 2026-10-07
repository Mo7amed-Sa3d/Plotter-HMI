"""Speed screen."""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QSlider, QPushButton, QSizePolicy)

from ui.scaling import px


class SpeedScreen(QWidget):
    back_clicked = pyqtSignal()
    speed_changed = pyqtSignal(float)

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
        title = QLabel("Speed")
        title.setObjectName("screen_title")
        header.addWidget(title)
        header.addStretch(1)
        root.addLayout(header)

        root.addStretch(1)
        self.value = QLabel("40 mm/s")
        self.value.setAlignment(Qt.AlignCenter)
        self.value.setObjectName("big_value")
        root.addWidget(self.value)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 200)
        self.slider.setValue(40)
        self.slider.setMinimumHeight(px(60))
        self.slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        def on_change(v):
            self.value.setText(f"{v} mm/s")
            self.speed_changed.emit(float(v))

        self.slider.valueChanged.connect(on_change)
        root.addWidget(self.slider)
        root.addStretch(1)