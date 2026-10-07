"""Widget that draws a G-code toolpath, scaling its content to fit."""

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QColor, QFont
from PyQt5.QtWidgets import QWidget, QSizePolicy

from gcode_parser import ParsedJob, arc_points
from ui.scaling import px, size


class GCodePreview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.job: ParsedJob = None
        self.progress_index = 0
        self.setMinimumHeight(px(140))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("background-color: #151515; border-radius: %dpx;"
                           % px(10))

    def set_job(self, job: ParsedJob):
        self.job = job
        self.progress_index = 0
        self.update()

    def set_progress(self, index: int):
        self.progress_index = index
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor("#151515"))

        if not self.job or not self.job.moves:
            p.setPen(QColor("#404040"))
            f = p.font()
            f.setPointSize(max(px(11), 6))
            p.setFont(f)
            p.drawText(self.rect(), Qt.AlignCenter, "No job loaded")
            return

        pad = px(12)
        w = self.width() - 2 * pad
        h = self.height() - 2 * pad
        if w <= 0 or h <= 0:
            return

        sx = w / self.job.width
        sy = h / self.job.height
        s = min(sx, sy)

        def tx(x):
            return pad + (x - self.job.min_x) * s
        def ty(y):
            return self.height() - pad - (y - self.job.min_y) * s

        line_w = max(px(2), 1)
        pen_width = line_w
        dash_pen = QPen(QColor("#404040"), max(px(1), 1), Qt.DashLine)
        done_pen = QPen(QColor("#E8A33D"), pen_width)
        todo_pen = QPen(QColor("#606060"), pen_width)

        for i, mv in enumerate(self.job.moves):
            if mv.kind == "rapid":
                p.setPen(dash_pen)
            elif i < self.progress_index:
                p.setPen(done_pen)
            else:
                p.setPen(todo_pen)

            if mv.kind in ("rapid", "linear"):
                p.drawLine(int(tx(mv.x0)), int(ty(mv.y0)),
                           int(tx(mv.x1)), int(ty(mv.y1)))
            else:
                px_, py_ = tx(mv.x0), ty(mv.y0)
                for (ax, ay) in arc_points(mv):
                    nx, ny = tx(ax), ty(ay)
                    p.drawLine(int(px_), int(py_), int(nx), int(ny))
                    px_, py_ = nx, ny