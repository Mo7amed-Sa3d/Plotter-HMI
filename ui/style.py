"""KlipperScreen-inspired QSS built from the current scale factor."""

from ui.scaling import px, s


_QSS_TEMPLATE = """
* {{
    font-family: "Roboto", "DejaVu Sans", sans-serif;
    font-size: {font_base}px;
    color: #E6E6E6;
}}

QMainWindow, QWidget {{
    background-color: #1C1C1C;
}}

QLabel#screen_title {{
    font-size: {font_title}px;
    font-weight: bold;
    color: #F0F0F0;
    padding: {pad_sm}px {pad_md}px;
}}

QLabel#screen_sub {{
    font-size: {font_sub}px;
    color: #A0A0A0;
    padding: 0 {pad_md}px {pad_sm}px {pad_md}px;
}}

QLabel#big_value {{
    font-size: {font_big}px;
    font-weight: bold;
    color: #F0F0F0;
}}

QPushButton {{
    background-color: #2E2E2E;
    border: 1px solid #3A3A3A;
    border-radius: {radius}px;
    padding: {pad_btn}px;
    font-size: {font_base}px;
    color: #E6E6E6;
    min-height: {btn_min_h}px;
}}
QPushButton:hover       {{ background-color: #383838; }}
QPushButton:pressed     {{ background-color: #242424; }}
QPushButton:disabled    {{ color: #666666; background-color: #232323; }}

QPushButton#primary {{
    background-color: #E8A33D;
    color: #1C1C1C;
    font-weight: bold;
    border: none;
}}
QPushButton#primary:hover {{ background-color: #F0B355; }}

QPushButton#danger {{
    background-color: #C0392B;
    color: #FFFFFF;
    font-weight: bold;
    border: none;
}}
QPushButton#danger:hover {{ background-color: #E0483A; }}

QPushButton#success {{
    background-color: #27AE60;
    color: #FFFFFF;
    font-weight: bold;
    border: none;
}}
QPushButton#success:hover {{ background-color: #2ECC71; }}

QPushButton#ghost {{
    background-color: transparent;
    border: 1px solid #3A3A3A;
}}

QPushButton#arrow {{
    font-size: {font_arrow}px;
    min-width: {arrow_size}px;
    min-height: {arrow_size}px;
}}

QPushButton#jog_center {{
    font-size: {font_sub}px;
    font-weight: bold;
    min-width: {arrow_size}px;
    min-height: {arrow_size}px;
}}

QGroupBox {{
    border: 1px solid #333333;
    border-radius: {radius}px;
    margin-top: {group_margin}px;
    padding-top: {pad_sm}px;
    font-weight: bold;
    color: #B0B0B0;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: {pad_md}px;
    padding: 0 {pad_xs}px;
}}

QSlider::groove:horizontal {{
    border: 1px solid #333333;
    height: {slider_h}px;
    background: #262626;
    border-radius: {slider_half}px;
}}
QSlider::handle:horizontal {{
    background: #E8A33D;
    width: {slider_handle}px;
    margin: -{slider_handle_off}px 0;
    border-radius: {slider_handle_half}px;
}}
QSlider::sub-page:horizontal {{
    background: #E8A33D;
    border-radius: {slider_half}px;
}}

QProgressBar {{
    border: 1px solid #333333;
    border-radius: {radius}px;
    background-color: #262626;
    height: {progress_h}px;
    text-align: center;
    color: #E6E6E6;
    font-size: {font_sub}px;
}}
QProgressBar::chunk {{
    background-color: #E8A33D;
    border-radius: {radius}px;
}}

QListWidget {{
    background-color: #222222;
    border: 1px solid #333333;
    border-radius: {radius}px;
    padding: {pad_xs}px;
    font-size: {font_base}px;
}}
QListWidget::item {{
    padding: {pad_list}px;
    border-bottom: 1px solid #2A2A2A;
    border-radius: {radius_sm}px;
}}
QListWidget::item:selected {{
    background-color: #E8A33D;
    color: #1C1C1C;
}}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
    background-color: #222222;
    border: 1px solid #333333;
    border-radius: {radius_sm}px;
    padding: {pad_input}px;
    color: #E6E6E6;
    font-size: {font_base}px;
    min-height: {input_min_h}px;
}}

QScrollBar:vertical {{
    background: #1C1C1C;
    width: {scrollbar}px;
    border-radius: {radius_sm}px;
}}
QScrollBar::handle:vertical {{
    background: #3A3A3A;
    border-radius: {radius_sm}px;
    min-height: {scrollbar_min}px;
}}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}

QStatusBar {{
    background-color: #161616;
    color: #9A9A9A;
    font-size: {font_sub}px;
}}

QDialog {{
    background-color: #1C1C1C;
}}

QFrame#virtual_keyboard {{
    background-color: #1A1A1A;
    border-top: 1px solid #333333;
}}

QPushButton#key {{
    background-color: #2E2E2E;
    border: 1px solid #3A3A3A;
    border-radius: {radius_sm}px;
    color: #E6E6E6;
    font-size: {font_base}px;
    font-weight: bold;
}}
QPushButton#key:pressed {{
    background-color: #E8A33D;
    color: #1C1C1C;
}}

QPushButton#key_action {{
    background-color: #3A3A3A;
    border: 1px solid #4A4A4A;
    border-radius: {radius_sm}px;
    color: #E6E6E6;
    font-size: {font_sub}px;
    font-weight: bold;
}}
QPushButton#key_action:pressed {{
    background-color: #E8A33D;
    color: #1C1C1C;
}}
"""


def build_qss() -> str:
    sc = s()

    # Derived numbers, all in reference pixels before scaling.
    base_font = sc.font_pt(10.0)          # actual pt size
    title_font = sc.font_pt(20.0)
    sub_font = sc.font_pt(11.0)
    big_font = sc.font_pt(24.0)
    arrow_font = sc.font_pt(26.0)

    return _QSS_TEMPLATE.format(
        font_base=base_font,
        font_title=title_font,
        font_sub=sub_font,
        font_big=big_font,
        font_arrow=arrow_font,

        pad_xs=px(4),
        pad_sm=px(8),
        pad_md=px(14),
        pad_btn=px(12),
        pad_list=px(14),
        pad_input=px(10),

        radius=px(10),
        radius_sm=px(6),

        btn_min_h=px(52),
        input_min_h=px(40),

        arrow_size=px(80),

        slider_h=px(8),
        slider_half=px(4),
        slider_handle=px(28),
        slider_handle_off=px(14),
        slider_handle_half=px(14),

        progress_h=px(26),

        group_margin=px(18),

        scrollbar=px(10),
        scrollbar_min=px(20),
    )


def apply_style(app):
    app.setStyleSheet(build_qss())