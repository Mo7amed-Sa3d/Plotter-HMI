#!/bin/bash
# HMI install script for Raspberry Pi OS Bookworm / Trixie (64-bit)

set -e

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$APP_DIR/venv"
USER_NAME="$(whoami)"

echo "==> Installing system packages"
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-full \
    python3-pyqt5 \
    python3-pyqt5.qtsvg \
    python3-serial \
    python3-opencv \
    python3-numpy \
    python3-picamera2 \
    python3-flask \
    python3-requests \
    libgl1 \
    libglib2.0-0 \
    network-manager

echo "==> Enabling UART on GPIO 14/15"
CONFIG=/boot/firmware/config.txt
if ! grep -q "^enable_uart=1" "$CONFIG"; then
    echo "enable_uart=1" | sudo tee -a "$CONFIG"
fi
if ! grep -q "^dtoverlay=disable-bt" "$CONFIG"; then
    echo "dtoverlay=disable-bt" | sudo tee -a "$CONFIG"
fi

CMDLINE=/boot/firmware/cmdline.txt
sudo sed -i 's/console=serial0,[0-9]*//g; s/console=ttyAMA0,[0-9]*//g' "$CMDLINE"

echo "==> Creating Python virtual environment"
# --system-site-packages is REQUIRED so picamera2, libcamera, RPi.GPIO
# and PyQt5 installed by apt are visible inside the venv.
python3 -m venv --system-site-packages "$VENV_DIR"

echo "==> Installing pure-Python packages inside the venv"
"$VENV_DIR/bin/pip" install --upgrade pip
# Only packages that are not available via apt, or that you need a
# newer version of, go here.
"$VENV_DIR/bin/pip" install --upgrade \
    flask \
    pyserial

echo "==> Installing systemd service"
SERVICE=/etc/systemd/system/hmi.service
sudo tee "$SERVICE" > /dev/null <<EOF
[Unit]
Description=Label Cutter HMI
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$APP_DIR
Environment=DISPLAY=:0
ExecStart=$VENV_DIR/bin/python $APP_DIR/main.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=graphical.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable hmi.service

echo
echo "==> Installation complete."
echo "Venv: $VENV_DIR"
echo "Reboot the Raspberry Pi to activate the UART and start the service."
echo "  sudo reboot"