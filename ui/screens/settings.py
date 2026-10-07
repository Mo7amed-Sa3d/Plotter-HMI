"""Settings screen for Wi-Fi and Ethernet."""

import subprocess
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QListWidget, QListWidgetItem,
                             QGroupBox, QLineEdit, QFormLayout, QMessageBox,
                             QSizePolicy, QScrollArea)

from ui.scaling import px


class SettingsScreen(QWidget):
    back_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(px(16), px(12), px(16), px(16))
        outer.setSpacing(px(10))

        header = QHBoxLayout()
        back = QPushButton("← Back")
        back.setObjectName("ghost")
        back.setMinimumHeight(px(44))
        back.clicked.connect(self.back_clicked.emit)
        header.addWidget(back)
        title = QLabel("Settings")
        title.setObjectName("screen_title")
        header.addWidget(title)
        header.addStretch(1)
        outer.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setSpacing(px(12))

        # Wi-Fi
        wifi_box = QGroupBox("Wi-Fi")
        wifi_layout = QVBoxLayout(wifi_box)
        wifi_layout.setSpacing(px(8))

        self.wifi_list = QListWidget()
        self.wifi_list.setMinimumHeight(px(140))
        wifi_layout.addWidget(self.wifi_list, stretch=1)

        scan_btn = QPushButton("Scan")
        scan_btn.setMinimumHeight(px(44))
        scan_btn.clicked.connect(self._scan_wifi)
        wifi_layout.addWidget(scan_btn)

        form = QFormLayout()
        form.setSpacing(px(8))
        self.wifi_ssid = QLineEdit()
        self.wifi_pass = QLineEdit()
        self.wifi_pass.setEchoMode(QLineEdit.Password)
        form.addRow("SSID", self.wifi_ssid)
        form.addRow("Password", self.wifi_pass)
        wifi_layout.addLayout(form)

        connect_btn = QPushButton("Connect")
        connect_btn.setObjectName("primary")
        connect_btn.setMinimumHeight(px(48))
        connect_btn.clicked.connect(self._connect_wifi)
        wifi_layout.addWidget(connect_btn)
        body_layout.addWidget(wifi_box)

        # Ethernet
        eth_box = QGroupBox("Ethernet")
        eth_layout = QVBoxLayout(eth_box)
        self.eth_status = QLabel("—")
        self.eth_status.setWordWrap(True)
        refresh_eth = QPushButton("Refresh")
        refresh_eth.setMinimumHeight(px(44))
        refresh_eth.clicked.connect(self._refresh_eth)
        eth_layout.addWidget(self.eth_status)
        eth_layout.addWidget(refresh_eth)
        body_layout.addWidget(eth_box)

        body_layout.addStretch(1)
        scroll.setWidget(body)
        outer.addWidget(scroll, stretch=1)

        self._refresh_eth()

    def _scan_wifi(self):
        self.wifi_list.clear()
        try:
            out = subprocess.check_output(
                ["nmcli", "-t", "-f", "SSID,SIGNAL", "device", "wifi"],
                timeout=10).decode()
            for line in out.splitlines():
                parts = line.rsplit(":", 1)
                if len(parts) != 2:
                    continue
                ssid, signal = parts
                item = QListWidgetItem(f"{ssid}   ({signal}%)")
                item.setData(Qt.UserRole, ssid)
                self.wifi_list.addItem(item)
        except Exception as e:
            QMessageBox.warning(self, "Wi-Fi", f"Scan failed: {e}")

    def _connect_wifi(self):
        item = self.wifi_list.currentItem()
        ssid = item.data(Qt.UserRole) if item else self.wifi_ssid.text()
        pwd = self.wifi_pass.text()
        if not ssid:
            QMessageBox.warning(self, "Wi-Fi", "Select or type an SSID.")
            return
        try:
            subprocess.check_call(
                ["nmcli", "device", "wifi", "connect", ssid, "password", pwd],
                timeout=30)
            QMessageBox.information(self, "Wi-Fi", f"Connected to {ssid}.")
        except Exception as e:
            QMessageBox.warning(self, "Wi-Fi", f"Connect failed: {e}")

    def _refresh_eth(self):
        try:
            out = subprocess.check_output(
                ["ip", "-brief", "addr", "show"], timeout=5).decode()
            lines = [l for l in out.splitlines()
                     if l.startswith(("eth", "en"))]
            self.eth_status.setText("\n".join(lines) if lines else "No Ethernet")
        except Exception:
            self.eth_status.setText("Unable to query interfaces")