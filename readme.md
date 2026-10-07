How to install and run
1. Prepare the Raspberry Pi

Flash Raspberry Pi OS Lite (64-bit) to a microSD card. Boot it, log in over SSH, and clone or copy the hmi/ folder to /home/pi/hmi.

2. Run the install script

bash
cd /home/pi/hmi
chmod +x install.sh
./install.sh
sudo reboot
3. Wire the UART to the Main MCU

Raspberry Pi	ESP32-S3
GPIO 14 (TXD, pin 8)	GPIO 44 (UART1 RX)
GPIO 15 (RXD, pin 10)	GPIO 43 (UART1 TX)
GND (pin 6)	GND
Both boards must share a common ground. The Main MCU must be running the production firmware with PROTOCOL_TRANSPORT = PROTOCOL_TRANSPORT_UART1.

4. Access the UI

Local touchscreen: Plug an HDMI display and USB touch panel into the Pi. The Qt app starts fullscreen on boot.

Remote web UI: Open http://<pi-ip>:5000 in any browser on the same network.

5. Test

From the local UI, tap Manual Jog, then press the arrows. The Main MCU should move the axes. Tap Home X on the jog screen to run the homing sequence.

From the web UI, click Home, Jog, Feed 100 mm, Eject. Both interfaces share the same serial link and the same job state.

What is implemented
Feature	Status
Home X, zero Y/F	Done
Jog arrows + central button	Done
Tool forces screen with sliders	Done
Speed control	Done
E-Stop	Done
Test cut screen with two patterns	Done
Settings screen (Wi-Fi + Ethernet)	Done
Cut from USB with file browser	Done
Cutting screen: filename, %, preview, pause/resume	Done
Cutting settings dialog (speed + forces)	Done
G-code parser with preview rendering	Done
Registration mark detection module	Done (camera wiring pending)
HTTP server with web UI	Done
KlipperScreen-style QSS	Done
systemd auto-start	Done
What still needs hardware
The camera wiring for registration. The registration.py module is complete; it just needs a picamera2 or USB camera handle. Add a capture call in MainWindow._run_registration.

The serial port tuning. If your Main MCU uses different UART pins or if /dev/ttyAMA0 is not the right device, change SERIAL_PORT in config.py.

The Ethernet setup. The settings screen calls nmcli; on Raspberry Pi OS this works out of the box after NetworkManager is installed (apt install network-manager).

