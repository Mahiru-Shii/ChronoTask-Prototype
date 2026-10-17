from PySide6 import QtCore, QtGui, QtWidgets

from views.widgets.sidebar_button import SidebarIconButton


from styles.theme import palette
def _theme_style(style, widget):
    win = widget.window() if widget is not None else None
    theme_name = getattr(win, "current_theme", "default")
    c = palette(theme_name)
    replacements = {
        "#151D2B": c["window"],
        "#182133": c["surface_alt"],
        "#1B2536": c["surface_alt"],
        "#202B3F": c["surface"],
        "#202C40": c["input"],
        "#222D42": c["surface_alt"],
        "#243149": c["surface"],
        "#253349": c["surface"],
        "#2B3851": c["surface"],
        "#2E3A52": c["border_soft"],
        "#31425D": c["surface"],
        "#34425D": c["border_soft"],
        "#344561": c["border_soft"],
        "#354760": c["border"],
        "#36445F": c["border"],
        "#40506C": c["border"],
        "#405273": c["border"],
        "#536784": c["border"],
        "#3E8AC4": c["accent"],
        "#4C9CD8": c["accent"],
        "#59B7FF": c["accent_hover"],
        "#79C5FF": c["accent_hover"],
        "#7CB4FF": c["accent_hover"],
        "#8FAEFF": c["accent_hover"],
        "#F4F7FF": c["text"],
        "#FFFFFF": c["text"],
        "#DCE5F7": c["text"],
        "#AAB6CF": c["muted"],
        "#AAB9D3": c["muted"],
        "#9AA9C3": c["muted"],
        "#93A3BF": c["muted"],
        "#91A1BD": c["muted"],
        "#8A9AB7": c["muted"],
        "#8291AE": c["muted"],
        "#8392AE": c["muted"],
        "#71809E": c["muted"],
        "#65738D": c["muted"],
        "#7F8DAA": c["muted"],
    }
    for old, new in replacements.items():
        style = style.replace(old, new)
    return style



class HourglassLogo(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(42, 42)
        self.setToolTip("ChronoTask")

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        theme_name = getattr(self.window(), "current_theme", "default")
        c = palette(theme_name)

        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QColor(c["accent"]))
        painter.drawRoundedRect(self.rect(), 14, 14)

        pen = QtGui.QPen(QtGui.QColor(c["text"]))
        pen.setWidthF(2.0)
        pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)

        left, right, top, bottom = 13.0, 29.0, 11.5, 30.5
        painter.drawLine(QtCore.QPointF(left, top), QtCore.QPointF(right, top))
        painter.drawLine(QtCore.QPointF(left, bottom), QtCore.QPointF(right, bottom))
        painter.drawLine(QtCore.QPointF(left + 1, top + 2), QtCore.QPointF(right - 1, bottom - 2))
        painter.drawLine(QtCore.QPointF(right - 1, top + 2), QtCore.QPointF(left + 1, bottom - 2))

        sand = QtGui.QColor(c["text"])
        sand.setAlpha(225)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(sand)
        upper = QtGui.QPolygonF([
            QtCore.QPointF(16, 15), QtCore.QPointF(26, 15), QtCore.QPointF(21, 20)
        ])
        lower = QtGui.QPolygonF([
            QtCore.QPointF(21, 23), QtCore.QPointF(16, 28), QtCore.QPointF(26, 28)
        ])
        painter.drawPolygon(upper)
        painter.drawPolygon(lower)


class PawIconButton(QtWidgets.QPushButton):
    """Koyomi navigation button with a simple paw icon."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setAutoExclusive(False)
        self.setFixedSize(44, 44)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Koyomi")

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        c = palette(getattr(self.window(), "current_theme", "default"))

        # Same selected/hover feel as the other sidebar buttons.
        if self.isChecked():
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.setBrush(QtGui.QColor(c["surface"]))
            painter.drawRoundedRect(self.rect(), 10, 10)
        elif self.underMouse():
            hover = QtGui.QColor(c["surface"])
            hover.setAlpha(190)
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.setBrush(hover)
            painter.drawRoundedRect(self.rect(), 10, 10)

        color = QtGui.QColor(c["accent_hover"] if self.isChecked() else c["muted"])
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(color)

        # Four toe beans.
        painter.drawEllipse(QtCore.QRectF(11.0, 10.0, 6.0, 7.5))
        painter.drawEllipse(QtCore.QRectF(18.0, 7.0, 6.0, 8.0))
        painter.drawEllipse(QtCore.QRectF(25.0, 8.0, 6.0, 8.0))
        painter.drawEllipse(QtCore.QRectF(31.0, 12.0, 5.5, 7.0))

        # Main paw pad.
        pad = QtGui.QPainterPath()
        pad.moveTo(22.0, 17.0)
        pad.cubicTo(15.0, 17.0, 11.5, 22.0, 13.0, 28.0)
        pad.cubicTo(14.5, 34.0, 19.0, 33.5, 22.0, 31.0)
        pad.cubicTo(25.0, 33.5, 30.0, 34.0, 32.0, 28.0)
        pad.cubicTo(34.0, 22.0, 29.0, 17.0, 22.0, 17.0)
        pad.closeSubpath()
        painter.drawPath(pad)

class Sidebar(QtWidgets.QFrame):
    """Main navigation sidebar for ChronoTask."""

    calendar_clicked = QtCore.Signal()
    tasks_clicked = QtCore.Signal()
    kaizen_clicked = QtCore.Signal()
    chrono_clock_clicked = QtCore.Signal()
    koyomi_clicked = QtCore.Signal()
    settings_clicked = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.navigation_buttons = []

        self.setObjectName("sidebar")

        self._setup_sidebar()
        self._build_ui()
        self._connect_signals()

        # Calendar Dashboard is the default page.
        self.set_active_button(self.btnCalendar)

    # =================================================================
    # SIDEBAR SETTINGS
    # =================================================================

    def _setup_sidebar(self):
        self.setFixedWidth(76)
        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.setAttribute(
            QtCore.Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        # The outer windowFrame provides the dark background. Keeping
        # the sidebar transparent prevents a square child background
        # from covering the bottom-left rounded outer corner.
        self.setStyleSheet(_theme_style(
            """
            QFrame#sidebar {
                background-color: transparent;
                border: none;
                border-right: 1px solid #2E3A52;
            }

            QLabel#logoLabel {
                background-color: #3E8AC4;
                color: #FFFFFF;
                border: 1px solid #59B7FF;
                border-radius: 14px;
                font-family: "Segoe UI";
                font-size: 12px;
                font-weight: 700;
            }

            SidebarIconButton {
                background-color: transparent;
                border: none;
                border-radius: 10px;
            }

            SidebarIconButton:hover {
                background-color: #253349;
            }

            SidebarIconButton:checked {
                background-color: #31425D;
            }

            QFrame#sidebarSeparator {
                background-color: #34425D;
                border: none;
            }
            """
        , self))

    # =================================================================
    # BUILD UI
    # =================================================================

    def _build_ui(self):
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 16, 0, 14)
        self.mainLayout.setSpacing(8)
        self.mainLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        self._build_logo()
        self.mainLayout.addSpacing(9)

        self.btnCalendar = self._create_button("calendar", "Calendar")
        self.btnTasks = self._create_button("tasks", "Tasks")
        self.btnKaizen = self._create_button("kaizen", "ChronoK")
        self.btnChronoClock = self._create_button("clock", "Chrono Clock")
        self.btnKoyomi = PawIconButton(self)
        self.navigation_buttons.append(self.btnKoyomi)

        for button in (
            self.btnCalendar,
            self.btnTasks,
            self.btnKaizen,
            self.btnChronoClock,
            self.btnKoyomi,
        ):
            self.mainLayout.addWidget(
                button,
                0,
                QtCore.Qt.AlignmentFlag.AlignHCenter,
            )

        self.mainLayout.addStretch(1)

        self.separator = QtWidgets.QFrame(self)
        self.separator.setObjectName("sidebarSeparator")
        self.separator.setFixedSize(36, 1)
        self.mainLayout.addWidget(
            self.separator,
            0,
            QtCore.Qt.AlignmentFlag.AlignHCenter,
        )
        self.mainLayout.addSpacing(4)

        self.btnSettings = self._create_button("settings", "Settings")
        self.mainLayout.addWidget(
            self.btnSettings,
            0,
            QtCore.Qt.AlignmentFlag.AlignHCenter,
        )

    # =================================================================
    # LOGO
    # =================================================================

    def _build_logo(self):
        self.logoLabel = HourglassLogo(self)
        self.logoLabel.setObjectName("logoLabel")

        self.mainLayout.addWidget(
            self.logoLabel,
            0,
            QtCore.Qt.AlignmentFlag.AlignHCenter,
        )

    # =================================================================
    # BUTTON FACTORY
    # =================================================================

    def _create_button(self, icon_name, tooltip):
        button = SidebarIconButton(icon_name, self)
        button.setToolTip(tooltip)
        button.setAutoExclusive(False)
        self.navigation_buttons.append(button)
        return button

    # =================================================================
    # SIGNAL CONNECTIONS
    # =================================================================

    def _connect_signals(self):
        self.btnCalendar.clicked.connect(self._handle_calendar)
        self.btnTasks.clicked.connect(self._handle_tasks)
        self.btnKaizen.clicked.connect(self._handle_kaizen)
        self.btnChronoClock.clicked.connect(self._handle_chrono_clock)
        self.btnKoyomi.clicked.connect(self._handle_koyomi)
        self.btnSettings.clicked.connect(self._handle_settings)

    # =================================================================
    # CLICK HANDLERS
    # =================================================================


    @QtCore.Slot()
    def _handle_calendar(self):
        self.set_active_button(self.btnCalendar)
        self.calendar_clicked.emit()

    @QtCore.Slot()
    def _handle_tasks(self):
        self.set_active_button(self.btnTasks)
        self.tasks_clicked.emit()

    @QtCore.Slot()
    def _handle_kaizen(self):
        self.set_active_button(self.btnKaizen)
        self.kaizen_clicked.emit()

    @QtCore.Slot()
    def _handle_chrono_clock(self):
        self.set_active_button(self.btnChronoClock)
        self.chrono_clock_clicked.emit()

    @QtCore.Slot()
    def _handle_koyomi(self):
        self.set_active_button(self.btnKoyomi)
        self.koyomi_clicked.emit()

    def _handle_settings(self):
        self.set_active_button(self.btnSettings)
        self.settings_clicked.emit()

    # =================================================================
    # ACTIVE STATE
    # =================================================================

    def set_active_button(self, active_button):
        """Ensure that only the active navigation button is checked."""

        for button in self.navigation_buttons:
            button.blockSignals(True)
            button.setChecked(button is active_button)
            button.blockSignals(False)
            button.update()

    def set_active_page(self, page_name):
        """Synchronize the selected sidebar button with a page name."""

        buttons = {
            "calendar": self.btnCalendar,
            "tasks": self.btnTasks,
            "kaizen": self.btnKaizen,
            "chrono_clock": self.btnChronoClock,
            "koyomi": self.btnKoyomi,
            "settings": self.btnSettings,
        }

        button = buttons.get(page_name)
        if button is not None:
            self.set_active_button(button)

