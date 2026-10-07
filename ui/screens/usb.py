"""USB file browser."""

from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QListWidget, QListWidgetItem,
                             QMessageBox, QSizePolicy)

from config import USB_MOUNT_POINTS
from ui.scaling import px


class UsbScreen(QWidget):
    back_clicked = pyqtSignal()
    file_selected = pyqtSignal(str)

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
        title = QLabel("Cut from USB")
        title.setObjectName("screen_title")
        header.addWidget(title)
        header.addStretch(1)

        refresh = QPushButton("Refresh")
        refresh.setObjectName("ghost")
        refresh.setMinimumHeight(px(44))
        refresh.clicked.connect(self.refresh)
        header.addWidget(refresh)
        root.addLayout(header)

        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self._choose)
        root.addWidget(self.list, stretch=1)

        self.start_btn = QPushButton("Start Cutting")
        self.start_btn.setObjectName("primary")
        self.start_btn.setMinimumHeight(px(60))
        self.start_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.start_btn.clicked.connect(self._start)
        root.addWidget(self.start_btn)

        self.refresh()

    def _mount(self):
        for mp in USB_MOUNT_POINTS:
            p = Path(mp)
            if p.exists() and any(p.iterdir()):
                return p
        return None

    def refresh(self):
        self.list.clear()
        mp = self._mount()
        if mp is None:
            item = QListWidgetItem("No USB drive detected")
            item.setFlags(Qt.NoItemFlags)
            self.list.addItem(item)
            return
        for path in sorted(mp.rglob("*")):
            if path.is_file() and path.suffix.lower() in (
                    ".gcode", ".nc", ".txt", ".plt"):
                item = QListWidgetItem(str(path.relative_to(mp)))
                item.setData(Qt.UserRole, str(path))
                self.list.addItem(item)

    def _choose(self, item):
        path = item.data(Qt.UserRole)
        if path:
            self.file_selected.emit(path)

    def _start(self):
        item = self.list.currentItem()
        if item is None:
            QMessageBox.warning(self, "USB", "Select a file.")
            return
        path = item.data(Qt.UserRole)
        if path:
            self.file_selected.emit(path)