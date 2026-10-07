"""Tool forces screen."""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QSlider, QPushButton, QGroupBox, QSizePolicy)

from ui.scaling import px


class ToolsScreen(QWidget):
    back_clicked = pyqtSignal()
    force_changed = pyqtSignal(int, int)

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
        title = QLabel("Tool Forces")
        title.setObjectName("screen_title")
        header.addWidget(title)
        header.addStretch(1)
        root.addLayout(header)

        root.addWidget(self._channel_group(0, "Solenoid P0"), stretch=1)
        root.addWidget(self._channel_group(1, "Solenoid P1"), stretch=1)

    def _channel_group(self, channel: int, label: str):
        box = QGroupBox(label)
        box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(box)
        layout.setSpacing(px(8))

        value_label = QLabel("0")
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setObjectName("big_value")

        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 255)
        slider.setValue(0)
        slider.setMinimumHeight(px(40))

        def on_change(v):
            value_label.setText(str(v))
            self.force_changed.emit(channel, v)

        slider.valueChanged.connect(on_change)

        layout.addWidget(value_label)
        layout.addWidget(slider)

        if channel == 0:
            self.slider0 = slider
            self.label0 = value_label
        else:
            self.slider1 = slider
            self.label1 = value_label

        return box