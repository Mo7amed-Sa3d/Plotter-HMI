"""Global scale engine.

The whole UI is laid out in "reference pixels" (800x480). At startup
this module reads the actual screen geometry and computes a scale
factor. Every widget in the app uses `scaled(px)` to convert reference
pixels to real pixels, so the same code renders correctly on a 3.5"
touch panel and a 27" monitor.
"""

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication


class Scale:
    """Holds the scale factor and orientation information."""

    def __init__(self):
        self.factor = 1.0
        self.orientation = "landscape"
        self.screen_w = 800
        self.screen_h = 480
        self._base_font_pt = 10.0

    # ---- Initialization ----

    def detect(self, ref_w: int, ref_h: int,
               min_scale: float, max_scale: float,
               portrait_threshold: float):
        screen = QApplication.primaryScreen()
        if screen is None:
            self.factor = 1.0
            return

        geo = screen.availableGeometry()
        self.screen_w = geo.width()
        self.screen_h = geo.height()

        if self.screen_h > self.screen_w:
            self.orientation = "portrait"
        else:
            self.orientation = "landscape"

        sx = self.screen_w / ref_w
        sy = self.screen_h / ref_h
        scale = min(sx, sy)

        if scale < min_scale:
            scale = min_scale
        elif scale > max_scale:
            scale = max_scale

        self.factor = scale

        dpi_scale = screen.logicalDotsPerInch() / 96.0
        self._base_font_pt = 10.0 * max(dpi_scale, 0.9)        
    # ---- Conversions ----

    def px(self, reference_px: float) -> int:
        """Reference pixels -> real pixels, never smaller than 1."""
        v = int(round(reference_px * self.factor))
        return max(v, 1)

    def size(self, w: float, h: float) -> QSize:
        return QSize(self.px(w), self.px(h))

    def font_pt(self, reference_pt: float) -> int:
        return max(int(round(reference_pt * self._base_font_pt / 10.0)), 6)

    def qfont(self, reference_pt: float, bold: bool = False) -> QFont:
        f = QFont()
        f.setPointSize(self.font_pt(reference_pt))
        f.setBold(bold)
        return f


# Module-level singleton
_SCALE = Scale()


def init(ref_w=800, ref_h=480,
         min_scale=0.75, max_scale=3.0,
         portrait_threshold=1.15):
    _SCALE.detect(ref_w, ref_h, min_scale, max_scale, portrait_threshold)
    return _SCALE


def s() -> Scale:
    return _SCALE


def px(reference_px: float) -> int:
    return _SCALE.px(reference_px)


def size(w: float, h: float) -> QSize:
    return _SCALE.size(w, h)


def font(reference_pt: float, bold: bool = False) -> QFont:
    return _SCALE.qfont(reference_pt, bold)


def is_portrait() -> bool:
    return _SCALE.orientation == "portrait"