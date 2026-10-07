"""Top-level window: stacked screens, wiring, job orchestration."""

import threading

from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtWidgets import (QMainWindow, QStackedWidget, QMessageBox,
                             QApplication)

from config import DEFAULT_FORCE_A, DEFAULT_FORCE_B, DEFAULT_SPEED
from gcode_parser import parse_file, parse_text
from job import Job, JobState
from machine import Machine
from protocol import home_x, zero_x, zero_y, move_linear, pwm_off

from ui.screens.menu import MenuScreen
from ui.screens.cutting import CuttingScreen, CuttingSettingsDialog
from ui.screens.tools import ToolsScreen
from ui.screens.speed import SpeedScreen
from ui.screens.settings import SettingsScreen
from ui.screens.usb import UsbScreen
from ui.screens.test_cut import TestCutScreen
from ui.screens.registration import RegistrationScreen
from ui.widgets.virtual_keyboard import VirtualKeyboard, KeyboardFilter


class MainWindow(QMainWindow):
    _dispatch = pyqtSignal(object)

    def __init__(self, machine: Machine, job: Job):
        super().__init__()
        self.machine = machine
        self.job = job

        self.setWindowTitle("Label Cutter HMI")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Screens
        self.menu = MenuScreen()
        self.cutting = CuttingScreen()
        self.tools = ToolsScreen()
        self.speed = SpeedScreen()
        self.settings = SettingsScreen()
        self.usb = UsbScreen()
        self.test_cut = TestCutScreen()
        self.registration = RegistrationScreen()

        for w in (self.menu, self.cutting, self.tools, self.speed,
                  self.settings, self.usb, self.test_cut, self.registration):
            self.stack.addWidget(w)

        self.stack.setCurrentWidget(self.menu)

        # Virtual keyboard
        self.keyboard = VirtualKeyboard(self.centralWidget())
        self.keyboard_filter = KeyboardFilter(self.keyboard)
        QApplication.instance().installEventFilter(self.keyboard_filter)

        # Status bar
        self.status = self.statusBar()
        self.status.showMessage("Idle")

        # Periodic status refresh
        self.poll = QTimer(self)
        self.poll.setInterval(1000)
        self.poll.timeout.connect(self.machine.refresh_status)
        self.poll.start()

        self._wire()

        machine.on_position(self._on_position)
        machine.on_sensors(self._on_sensors)
        job.on_state(self._on_job_state)
        job.on_progress(self._on_job_progress)

        self.job.set_speed(DEFAULT_SPEED)
        self.job.set_force(0, DEFAULT_FORCE_A)
        self.job.set_force(1, DEFAULT_FORCE_B)

    # ---- Signal wiring ----

    def _wire(self):
        # Menu buttons
        self.menu.tools_clicked.connect(
            lambda: self.stack.setCurrentWidget(self.tools))
        self.menu.speed_clicked.connect(
            lambda: self.stack.setCurrentWidget(self.speed))
        self.menu.settings_clicked.connect(
            lambda: self.stack.setCurrentWidget(self.settings))
        self.menu.usb_clicked.connect(
            lambda: self.stack.setCurrentWidget(self.usb))
        self.menu.test_cut_clicked.connect(
            lambda: self.stack.setCurrentWidget(self.test_cut))
        self.menu.estop_clicked.connect(self._do_estop)

        # Jog pad on the main menu
        self.menu.jog.connect(self._do_jog)
        self.menu.home_and_zero.connect(self._do_home_zero)

        # Tools
        self.tools.back_clicked.connect(
            lambda: self.stack.setCurrentWidget(self.menu))
        self.tools.force_changed.connect(self._do_force)

        # Speed
        self.speed.back_clicked.connect(
            lambda: self.stack.setCurrentWidget(self.menu))
        self.speed.speed_changed.connect(self.job.set_speed)

        # Settings / USB / Test cut / Registration
        self.settings.back_clicked.connect(
            lambda: self.stack.setCurrentWidget(self.menu))
        self.usb.back_clicked.connect(
            lambda: self.stack.setCurrentWidget(self.menu))
        self.usb.file_selected.connect(self._start_job)
        self.test_cut.back_clicked.connect(
            lambda: self.stack.setCurrentWidget(self.menu))
        self.test_cut.run_test.connect(self._run_test_cut)
        self.registration.back_clicked.connect(
            lambda: self.stack.setCurrentWidget(self.menu))
        self.registration.run_scan.connect(self._run_registration)

        # Cutting controls
        self.cutting.pause_clicked.connect(self.job.pause)
        self.cutting.resume_clicked.connect(self.job.resume)
        self.cutting.cancel_clicked.connect(self._cancel_job)
        self.cutting.settings_clicked.connect(self._open_cutting_settings)

    # ---- Callbacks from machine / job ----

    def _on_position(self, pos):
        self.status.showMessage(
            f"X={pos.x:.2f}  Y={pos.y:.2f}  F={pos.f:.2f}  "
            f"S1={int(pos.s1)} S2={int(pos.s2)} S3={int(pos.s3)}")

    def _on_sensors(self, s):
        pass

    def _on_job_state(self, job):
        if job.state == JobState.RUNNING:
            self.stack.setCurrentWidget(self.cutting)
            self.cutting.set_paused(False)
        elif job.state == JobState.PAUSED:
            self.cutting.set_paused(True)
        elif job.state in (JobState.FINISHED, JobState.IDLE):
            self.stack.setCurrentWidget(self.menu)
        elif job.state == JobState.ERROR:
            QMessageBox.warning(self, "Job", "Job failed.")

    def _on_job_progress(self, value):
        self.cutting.set_progress(value, self.job.current_index)

    # ---- Command handlers ----

    def _do_jog(self, dx, dy):
        p = self.machine.position
        base_x = p.qx if p else 0.0
        base_y = p.qy if p else 0.0
        self.machine.fire(
            move_linear(base_x + dx, base_y + dy, self.job.speed_override))

    def _do_home_zero(self):
        self.machine.command(home_x())
        self.machine.command(zero_x(0.0))
        self.machine.command(zero_y(0.0))

    def _do_force(self, channel, duty):
        self.job.set_force(channel, duty)

    def _do_estop(self):
        self.machine.fire("STOP")
        self.machine.fire(pwm_off(0))
        self.machine.fire(pwm_off(1))
        QMessageBox.warning(self, "E-Stop",
                            "Emergency stop sent. Power-cycle the machine if "
                            "the alarm persists.")

    def _start_job(self, path):
        try:
            job = parse_file(path)
            self.cutting.set_file(path)
            self.cutting.set_job(job)
            self.job.start(path)
        except Exception as e:
            QMessageBox.warning(self, "Job", f"Failed to load: {e}")

    def _cancel_job(self):
        self.job.cancel()
        self.stack.setCurrentWidget(self.menu)

    def _open_cutting_settings(self):
        dlg = CuttingSettingsDialog(self, self.job.speed_override,
                                    self.job.force_a, self.job.force_b)
        if dlg.exec_():
            self.job.set_speed(float(dlg.speed.value()))
            self.job.set_force(0, dlg.force_a.value())
            self.job.set_force(1, dlg.force_b.value())

    def _run_test_cut(self, gcode_text):
        job = parse_text(gcode_text)
        self.cutting.set_file("test_cut")
        self.cutting.set_job(job)
        self.job.job = job
        self.job.total_moves = len(job.moves)
        self.job.current_index = 0
        self.job.state = JobState.RUNNING
        self.stack.setCurrentWidget(self.cutting)
        threading.Thread(target=self.job._run, daemon=True).start()

    def _run_registration(self):
        QMessageBox.information(self, "Registration",
                                "Registration scan is not yet wired to a camera.")

    # ---- Layout ----

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "keyboard"):
            self.keyboard._reposition()