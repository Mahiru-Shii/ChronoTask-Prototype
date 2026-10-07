from PySide6 import QtCore, QtWidgets

from views.widgets.sidebar_button import SidebarIconButton


class Sidebar(QtWidgets.QFrame):
    """Main navigation sidebar for ChronoTask."""

    calendar_clicked = QtCore.Signal()
    tasks_clicked = QtCore.Signal()
    kaizen_clicked = QtCore.Signal()
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
        self.setStyleSheet(
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
        )

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

        for button in (
            self.btnCalendar,
            self.btnTasks,
            self.btnKaizen,
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
        self.logoLabel = QtWidgets.QLabel("CT", self)
        self.logoLabel.setObjectName("logoLabel")
        self.logoLabel.setFixedSize(42, 42)
        self.logoLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.logoLabel.setToolTip("ChronoTask")

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
            "settings": self.btnSettings,
        }

        button = buttons.get(page_name)
        if button is not None:
            self.set_active_button(button)
