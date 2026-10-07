#!/bin/bash
# HMI install script for Raspberry Pi OS Lite (64-bit)

set -e

echo "==> Installing system packages"
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-pyqt5 \
    python3-serial python3-opencv python3-picamera2 \
    libgl1 libglib2.0-0 network-manager

echo "==> Enabling UART on GPIO 14/15"
CONFIG=/boot/firmware/config.txt
if ! grep -q "^enable_uart=1" "$CONFIG"; then
    echo "enable_uart=1" | sudo tee -a "$CONFIG"
fi
if ! grep -q "^dtoverlay=disable-bt" "$CONFIG"; then
    echo "dtoverlay=disable-bt" | sudo tee -a "$CONFIG"
fi

# Remove serial console from cmdline
CMDLINE=/boot/firmware/cmdline.txt
sudo sed -i 's/console=serial0,[0-9]*//g; s/console=ttyAMA0,[0-9]*//g' "$CMDLINE"

echo "==> Installing Python dependencies"
pip3 install --upgrade pip
pip3 install flask opencv-python-headless pyserial

echo "==> Installing systemd service"
SERVICE=/etc/systemd/system/hmi.service
sudo tee "$SERVICE" > /dev/null <<EOF
[Unit]
Description=Label Cutter HMI
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=DISPLAY=:0
ExecStart=/usr/bin/python3 $(pwd)/main.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=graphical.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable hmi.service

echo
echo "==> Installation complete."
echo "Reboot the Raspberry Pi to activate the UART and start the service."
echo "  sudo reboot"