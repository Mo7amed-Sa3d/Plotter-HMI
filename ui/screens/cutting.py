"""Cutting progress screen."""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QProgressBar, QDialog, QSpinBox,
                             QDialogButtonBox, QFormLayout, QSizePolicy)

from ui.scaling import px, size
from ui.widgets.gcode_preview import GCodePreview


class CuttingScreen(QWidget):
    pause_clicked = pyqtSignal()
    resume_clicked = pyqtSignal()
    cancel_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(px(16), px(12), px(16), px(16))
        root.setSpacing(px(8))

        self.title = QLabel("No file")
        self.title.setObjectName("screen_title")
        root.addWidget(self.title)

        self.preview = GCodePreview()
        root.addWidget(self.preview, stretch=1)

        self.percent = QLabel("0.0 %")
        self.percent.setObjectName("big_value")
        self.percent.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        root.addWidget(self.percent)

        self.bar = QProgressBar()
        self.bar.setRange(0, 1000)
        self.bar.setTextVisible(False)
        root.addWidget(self.bar)

        row = QHBoxLayout()
        row.setSpacing(px(8))
        self.pause_btn = QPushButton("Pause")
        self.resume_btn = QPushButton("Resume")
        self.settings_btn = QPushButton("Settings")
        self.cancel_btn = QPushButton("Cancel")
        self.pause_btn.setObjectName("primary")
        self.resume_btn.setObjectName("success")
        self.cancel_btn.setObjectName("danger")

        for b in (self.pause_btn, self.resume_btn,
                  self.settings_btn, self.cancel_btn):
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            b.setMinimumHeight(px(56))

        self.pause_btn.clicked.connect(self.pause_clicked.emit)
        self.resume_btn.clicked.connect(self.resume_clicked.emit)
        self.settings_btn.clicked.connect(self.settings_clicked.emit)
        self.cancel_btn.clicked.connect(self.cancel_clicked.emit)

        row.addWidget(self.pause_btn)
        row.addWidget(self.resume_btn)
        row.addWidget(self.settings_btn)
        row.addWidget(self.cancel_btn)
        root.addLayout(row)

        self.resume_btn.hide()

    def set_file(self, path: str):
        self.title.setText(path.split("/")[-1])

    def set_job(self, job):
        self.preview.set_job(job)

    def set_progress(self, value: float, index: int):
        self.bar.setValue(int(value * 1000))
        self.percent.setText(f"{value * 100:.1f} %")
        self.preview.set_progress(index)

    def set_paused(self, paused: bool):
        self.pause_btn.setVisible(not paused)
        self.resume_btn.setVisible(paused)


class CuttingSettingsDialog(QDialog):
    def __init__(self, parent, speed, force_a, force_b):
        super().__init__(parent)
        self.setWindowTitle("Cutting Settings")
        self.setMinimumWidth(px(380))
        layout = QVBoxLayout(self)
        layout.setContentsMargins(px(16), px(16), px(16), px(16))
        layout.setSpacing(px(10))

        form = QFormLayout()
        form.setSpacing(px(10))

        self.speed = QSpinBox()
        self.speed.setRange(1, 200)
        self.speed.setValue(int(speed))
        self.speed.setSuffix(" mm/s")
        self.speed.setMinimumHeight(px(44))
        form.addRow("Speed", self.speed)

        self.force_a = QSpinBox()
        self.force_a.setRange(0, 255)
        self.force_a.setValue(force_a)
        self.force_a.setMinimumHeight(px(44))
        form.addRow("Force P0", self.force_a)

        self.force_b = QSpinBox()
        self.force_b.setRange(0, 255)
        self.force_b.setValue(force_b)
        self.force_b.setMinimumHeight(px(44))
        form.addRow("Force P1", self.force_b)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        for b in buttons.buttons():
            b.setMinimumHeight(px(48))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)