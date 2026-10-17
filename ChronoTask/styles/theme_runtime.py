from PySide6 import QtGui, QtWidgets
from styles.theme import THEMES, palette

# Base legacy colors mapped to semantic roles. Semantic warning/rest/priority colors excluded.
_BASE_ROLE = {
    "#151D2B":"window", "#182133":"surface_alt", "#1B2536":"surface_alt",
    "#202B3F":"surface", "#202C40":"input", "#222D42":"surface_alt",
    "#243149":"surface", "#253349":"surface", "#2B3851":"surface",
    "#2E3A52":"border_soft", "#31425D":"surface", "#34425D":"border_soft",
    "#344561":"border_soft", "#354760":"border", "#36445F":"border",
    "#40506C":"border", "#405273":"border", "#536784":"border",
    "#3E8AC4":"accent", "#4C9CD8":"accent", "#59B7FF":"accent_hover",
    "#79C5FF":"accent_hover", "#7CB4FF":"accent_hover", "#8FAEFF":"accent_hover",
    "#F4F7FF":"text", "#FFFFFF":"text", "#DCE5F7":"text",
    "#AAB6CF":"muted", "#AAB9D3":"muted", "#9AA9C3":"muted",
    "#93A3BF":"muted", "#91A1BD":"muted", "#8A9AB7":"muted",
    "#8291AE":"muted", "#8392AE":"muted", "#71809E":"muted",
    "#65738D":"muted", "#7F8DAA":"muted",
}

def _role_map():
    mapping = dict(_BASE_ROLE)
    # Critical fix: recognize colors already produced by an earlier theme.
    # This allows Yotsuba -> Lavender -> Nord without stale colors.
    for colors in THEMES.values():
        for role, value in colors.items():
            mapping.setdefault(value.upper(), role)
    return mapping

_ROLE_MAP = _role_map()

def themed_style(style, theme_name):
    target = palette(theme_name)
    # Longest keys first is defensive and deterministic.
    for old, role in _ROLE_MAP.items():
        if role in target:
            style = style.replace(old, target[role]).replace(old.lower(), target[role])
    return style

def apply_widget_tree(root, theme_name):
    root.current_theme = theme_name
    for widget in [root] + root.findChildren(QtWidgets.QWidget):
        current = widget.styleSheet()
        if current:
            widget.setStyleSheet(themed_style(current, theme_name))
    c = palette(theme_name)
    pal = root.palette()
    pal.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(c["window"]))
    pal.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(c["surface_alt"]))
    pal.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(c["surface"]))
    pal.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor(c["text"]))
    pal.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor(c["text"]))
    pal.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(c["accent"]))
    pal.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(c["text"]))
    root.setPalette(pal)
    root.update()