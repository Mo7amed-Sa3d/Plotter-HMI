"""Entry point for the HMI application."""

import sys
import signal

from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication

from config import (FULLSCREEN, REF_WIDTH, REF_HEIGHT,
                    MIN_SCALE, MAX_SCALE, PORTRAIT_THRESHOLD)
from machine import Machine
from job import Job
from ui import scaling
from ui.style import apply_style
from ui.main_window import MainWindow
from web_server import start_server


class Dispatcher(QObject):
    call = pyqtSignal(object)


def main():
    app = QApplication(sys.argv)

    # Compute the scale BEFORE anything else is constructed.
    scaling.init(
        ref_w=REF_WIDTH,
        ref_h=REF_HEIGHT,
        min_scale=MIN_SCALE,
        max_scale=MAX_SCALE,
        portrait_threshold=PORTRAIT_THRESHOLD,
    )

    # Now build and apply the stylesheet with the correct scale.
    apply_style(app)

    dispatcher = Dispatcher()
    def run_on_qt(fn):
        dispatcher.call.emit(fn)
    dispatcher.call.connect(lambda fn: fn())

    machine = Machine(dispatch=run_on_qt)
    try:
        machine.open()
    except RuntimeError as e:
        print(e, file=sys.stderr)

    job = Job(machine, dispatch=run_on_qt)
    start_server(machine, job)

    win = MainWindow(machine, job)

    if FULLSCREEN:
        win.showFullScreen()
    else:
        # Size the window to 80% of the screen, centered, for desktop use
        screen = app.primaryScreen().availableGeometry()
        w = int(screen.width() * 0.8)
        h = int(screen.height() * 0.8)
        win.resize(w, h)
        win.move(
            screen.x() + (screen.width() - w) // 2,
            screen.y() + (screen.height() - h) // 2,
        )
        win.show()

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    timer = QTimer()
    timer.timeout.connect(machine.refresh_status)
    timer.start(1000)

    rc = app.exec_()
    machine.close()
    return rc


if __name__ == "__main__":
    sys.exit(main())