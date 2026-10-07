"""Threaded serial client for the Main MCU.

Only one thread reads from the serial port: the RX loop. Every line it
receives is pushed into a response queue and also dispatched to the
registered listeners. The command() method waits on the queue for ok
or error responses.
"""

import threading
import time
from collections import deque
from typing import Callable, Optional

import serial

from config import SERIAL_PORT, SERIAL_BAUD
from protocol import (
    parse_position, parse_sensors, Position, Sensors,
    get_position, get_sensors,
)


# Response timeout for a single command, in seconds.
COMMAND_TIMEOUT = 15.0

# Serial port read timeout. Small so the RX loop wakes up regularly.
READ_TIMEOUT = 0.05

# Maximum number of unclaimed lines kept in the response queue.
RESPONSE_QUEUE_MAX = 200


class Machine:
    def __init__(self, dispatch: Callable[[Callable], None]):
        self.dispatch = dispatch
        self._ser: Optional[serial.Serial] = None
        self._lock = threading.RLock()
        self._rx_thread: Optional[threading.Thread] = None
        self._stop = threading.Event()

        self.position: Optional[Position] = None
        self.sensors: Optional[Sensors] = None
        self.alarm = False

        # Response queue for command() callers
        self._response_q: deque[str] = deque(maxlen=RESPONSE_QUEUE_MAX)
        self._response_event = threading.Event()
        self._command_lock = threading.Lock()

        # Listeners
        self._position_listeners: list[Callable[[Position], None]] = []
        self._sensor_listeners:   list[Callable[[Sensors], None]] = []

    # ---- Lifecycle ----

    def open(self):
        try:
            self._ser = serial.Serial(
                port=SERIAL_PORT,
                baudrate=SERIAL_BAUD,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=READ_TIMEOUT,
            )
        except serial.SerialException as exc:
            raise RuntimeError(f"Cannot open {SERIAL_PORT}: {exc}")

        self._stop.clear()
        self._rx_thread = threading.Thread(target=self._rx_loop, daemon=True)
        self._rx_thread.start()

        # Prime status. Use fire-and-forget; the RX thread will
        # populate position/sensors when responses arrive.
        self.fire(get_position())
        self.fire(get_sensors())

    def close(self):
        self._stop.set()
        if self._ser and self._ser.is_open:
            try:
                self._ser.close()
            except Exception:
                pass

    # ---- Listener registration ----

    def on_position(self, cb): self._position_listeners.append(cb)
    def on_sensors(self, cb):  self._sensor_listeners.append(cb)

    # ---- Sending ----

    def _send(self, cmd: str):
        if not self._ser or not self._ser.is_open:
            return
        with self._lock:
            try:
                self._ser.write((cmd + "\n").encode("ascii"))
                self._ser.flush()
            except serial.SerialException:
                pass

    def fire(self, cmd: str):
        """Send without waiting for a response."""
        self._send(cmd)

    def command(self, cmd: str, wait_ok: bool = True,
                timeout: float = COMMAND_TIMEOUT) -> bool:
        """Send a command and wait for ok or error. Returns True on ok."""
        with self._command_lock:
            # Drain any stale responses before sending
            with self._lock:
                self._response_q.clear()
                self._response_event.clear()

            self._send(cmd)

            if not wait_ok:
                return True

            deadline = time.time() + timeout
            while time.time() < deadline:
                line = self._pop_response(deadline)
                if line is None:
                    continue
                if line == "ok":
                    return True
                if line.startswith("error:"):
                    self.alarm = True
                    return False
                # Ignore [MSG:...], ack:..., <POS:...>, <SENSORS:...>
            return False

    def _pop_response(self, deadline: float) -> Optional[str]:
        with self._lock:
            if self._response_q:
                return self._response_q.popleft()
        # Wait for the RX thread to push something
        remaining = deadline - time.time()
        if remaining <= 0:
            return None
        self._response_event.wait(timeout=min(0.1, remaining))
        with self._lock:
            self._response_event.clear()
            if self._response_q:
                return self._response_q.popleft()
        return None

    # ---- Reading (only called from the RX thread) ----

    def _rx_loop(self):
        buf = b""
        while not self._stop.is_set():
            try:
                chunk = self._ser.read(256)
            except serial.SerialException:
                time.sleep(0.1)
                continue

            if not chunk:
                continue

            buf += chunk
            while b"\n" in buf:
                raw, buf = buf.split(b"\n", 1)
                line = raw.decode("ascii", errors="replace").strip("\r")
                if not line:
                    continue
                self._process_line(line)

    def _process_line(self, line: str):
        # 1) Update cached state
        pos = parse_position(line)
        if pos is not None:
            self.position = pos
            for cb in self._position_listeners:
                self.dispatch(lambda c=cb, p=pos: c(p))

        sen = parse_sensors(line)
        if sen is not None:
            self.sensors = sen
            for cb in self._sensor_listeners:
                self.dispatch(lambda c=cb, s=sen: c(s))

        if line.startswith("error:"):
            self.alarm = True

        # 2) Push to the response queue for command() waiters
        with self._lock:
            self._response_q.append(line)
            self._response_event.set()

    # ---- Convenience ----

    def refresh_status(self):
        self.fire(get_position())
        self.fire(get_sensors())