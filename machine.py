"""Threaded serial client for the Main MCU."""

import threading
import time
from typing import Callable, Optional

import serial

from config import SERIAL_PORT, SERIAL_BAUD, SERIAL_TIMEOUT
from protocol import (
    parse_position, parse_sensors, Position, Sensors,
    get_position, get_sensors,
)
class Machine:
    """Owns the serial link. Thread-safe. Calls callbacks on the Qt thread
    through the provided `dispatch` callable."""

    def __init__(self, dispatch: Callable[[Callable], None]):
        self.dispatch = dispatch
        self._ser: Optional[serial.Serial] = None
        self._lock = threading.RLock()
        self._rx_thread: Optional[threading.Thread] = None
        self._stop = threading.Event()

        self.position: Optional[Position] = None
        self.sensors: Optional[Sensors] = None
        self.alarm = False

        # Listeners
        self._position_listeners: list[Callable[[Position], None]] = []
        self._sensor_listeners: list[Callable[[Sensors], None]] = []

    # ---- Lifecycle ----

    def open(self):
        try:
            self._ser = serial.Serial(
                port=SERIAL_PORT,
                baudrate=SERIAL_BAUD,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=SERIAL_TIMEOUT,
            )
        except serial.SerialException as exc:
            raise RuntimeError(f"Cannot open {SERIAL_PORT}: {exc}")

        self._stop.clear()
        self._rx_thread = threading.Thread(target=self._rx_loop, daemon=True)
        self._rx_thread.start()
        self._send(get_position())
        self._send(get_sensors())

    def close(self):
        self._stop.set()
        if self._ser and self._ser.is_open:
            self._ser.close()

    # ---- Listener registration ----

    def on_position(self, cb): self._position_listeners.append(cb)
    def on_sensors(self, cb):  self._sensor_listeners.append(cb)

    # ---- Sending ----

    def _send(self, cmd: str):
        if not self._ser or not self._ser.is_open:
            return
        with self._lock:
            self._ser.write((cmd + "\n").encode("ascii"))
            self._ser.flush()

    def command(self, cmd: str, wait_ok: bool = True) -> bool:
        """Send a command and optionally wait for ok/error. Returns True on
        ok, False on error or timeout."""
        self._send(cmd)
        if not wait_ok:
            return True
        deadline = time.time() + SERIAL_TIMEOUT
        while time.time() < deadline:
            line = self._readline()
            if line is None:
                continue
            if line == "ok":
                return True
            if line.startswith("error:"):
                self.alarm = True
                return False
        return False

    def fire(self, cmd: str):
        """Fire-and-forget. No response expected."""
        self._send(cmd)

    # ---- Reading ----

    def _readline(self) -> Optional[str]:
        if not self._ser or not self._ser.is_open:
            return None
        try:
            raw = self._ser.readline()
        except serial.SerialException:
            return None
        if not raw:
            return None
        return raw.decode("ascii", errors="replace").strip("\r\n")

    def _rx_loop(self):
        while not self._stop.is_set():
            line = self._readline()
            if line is None:
                continue
            self._handle_line(line)

    def _handle_line(self, line: str):
        pos = parse_position(line)
        if pos is not None:
            self.position = pos
            for cb in self._position_listeners:
                self.dispatch(lambda c=cb, p=pos: c(p))
            return

        sen = parse_sensors(line)
        if sen is not None:
            self.sensors = sen
            for cb in self._sensor_listeners:
                self.dispatch(lambda c=cb, s=sen: c(s))
            return

        if line.startswith("error:"):
            self.alarm = True

    # ---- Convenience ----

    def refresh_status(self):
        self.fire(get_position())
        self.fire(get_sensors())