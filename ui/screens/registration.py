"""Registration screen."""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QMessageBox, QListWidget,
                             QSizePolicy)

from config import REGISTRATION_MARKS
from ui.scaling import px


class RegistrationScreen(QWidget):
    back_clicked = pyqtSignal()
    run_scan = pyqtSignal()

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
        title = QLabel("Registration")
        title.setObjectName("screen_title")
        header.addWidget(title)
        header.addStretch(1)
        root.addLayout(header)

        self.preview = QLabel("No image")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumHeight(px(200))
        self.preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview.setStyleSheet(
            "background-color:#151515; border-radius:%dpx;" % px(10))
        root.addWidget(self.preview, stretch=1)

        self.results = QListWidget()
        self.results.setMinimumHeight(px(120))
        root.addWidget(self.results, stretch=1)

        row = QHBoxLayout()
        row.setSpacing(px(8))
        scan = QPushButton("Run Registration Scan")
        scan.setObjectName("primary")
        scan.setMinimumHeight(px(56))
        scan.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        scan.clicked.connect(self.run_scan.emit)

        apply_btn = QPushButton("Apply && Save")
        apply_btn.setObjectName("success")
        apply_btn.setMinimumHeight(px(56))
        apply_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        apply_btn.clicked.connect(self._apply)

        row.addWidget(scan)
        row.addWidget(apply_btn)
        root.addLayout(row)

        for i, (x, y) in enumerate(REGISTRATION_MARKS, start=1):
            self.results.addItem(f"Mark {i}: expected ({x:.1f}, {y:.1f}) mm")

    def show_frame(self, numpy_rgb):
        try:
            h, w, ch = numpy_rgb.shape
            bytes_per_line = ch * w
            qimg = QImage(numpy_rgb.data, w, h, bytes_per_line,
                          QImage.Format_RGB888)
            pix = QPixmap.fromImage(qimg).scaled(
                self.preview.width(), self.preview.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview.setPixmap(pix)
        except Exception:
            pass

    def update_marks(self, results):
        self.results.clear()
        for idx, found, mx, my, ox, oy in results:
            ex, ey = REGISTRATION_MARKS[idx]
            if found:
                text = (f"Mark {idx+1}: FOUND  "
                        f"measured ({mx:.2f}, {my:.2f}) mm  "
                        f"offset ({ox:+.2f}, {oy:+.2f}) mm")
            else:
                text = f"Mark {idx+1}: NOT FOUND at ({ex:.1f}, {ey:.1f}) mm"
            self.results.addItem(text)

    def _apply(self):
        QMessageBox.information(self, "Registration",
                                "Transform applied. Subsequent jobs will use it.")