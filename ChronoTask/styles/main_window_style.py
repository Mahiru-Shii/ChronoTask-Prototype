from styles.theme import palette

_BASE_STYLE = r"""
QMainWindow#MainWindow {
    background-color: transparent;
    border: none;
}

QWidget#centralWidget {
    background-color: transparent;
    border: none;
}

QFrame#windowFrame {
    background-color: #151D2B;
    border: 1px solid #34425D;
    border-radius: 18px;
}

QWidget#contentArea {
    background-color: transparent;
    border: none;
}

QStackedWidget#contentStack {
    background-color: transparent;
    border: none;
}

QToolTip {
    background-color: #253349;
    color: #F4F7FF;
    border: 1px solid #40506C;
    padding: 5px 7px;
    font-family: "Segoe UI";
    font-size: 9px;
}

QMessageBox {
    background-color: #182133;
}

QMessageBox QLabel {
    background-color: transparent;
    color: #F4F7FF;
    font-family: "Segoe UI";
    font-size: 10px;
}

QMessageBox QPushButton {
    min-width: 74px;
    min-height: 30px;
    background-color: #253349;
    color: #F4F7FF;
    border: 1px solid #40506C;
    border-radius: 7px;
    padding: 2px 10px;
    font-family: "Segoe UI";
    font-size: 9px;
    font-weight: 600;
}

QMessageBox QPushButton:hover {
    background-color: #31425D;
    border-color: #536784;
}

QMessageBox QPushButton:default {
    background-color: #3E8AC4;
    border-color: #59B7FF;
}
"""

def build_main_window_style(theme_name="default"):
    c = palette(theme_name)
    replacements = {
        "#151D2B": c["window"],
        "#253349": c["surface"],
        "#182133": c["surface_alt"],
        "#40506C": c["border"],
        "#34425D": c["border_soft"],
        "#3E8AC4": c["accent"],
        "#59B7FF": c["accent_hover"],
        "#F4F7FF": c["text"],
    }
    style = _BASE_STYLE
    for old, new in replacements.items():
        style = style.replace(old, new)
    return style

MAIN_WINDOW_STYLE = build_main_window_style("default")