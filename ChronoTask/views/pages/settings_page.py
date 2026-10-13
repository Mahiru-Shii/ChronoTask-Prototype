from PySide6 import QtCore, QtWidgets
from styles.theme import palette


class SettingsPage(QtWidgets.QWidget):
    theme_changed = QtCore.Signal(str)
    def __init__(self, database=None, parent=None):
        super().__init__(parent)
        self.database = database
        self.setObjectName("settingsPage")
        self._build_ui()
        self._apply_style()
        self._load_settings()
        self._connect_settings()

    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(0)

        title = QtWidgets.QLabel("Settings")
        title.setObjectName("settingsTitle")
        subtitle = QtWidgets.QLabel("Manage your ChronoTask preferences and defaults.")
        subtitle.setObjectName("settingsSubtitle")
        root.addWidget(title)
        root.addSpacing(5)
        root.addWidget(subtitle)
        root.addSpacing(22)

        scroll = QtWidgets.QScrollArea()
        scroll.setObjectName("settingsScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QtWidgets.QWidget()
        content.setObjectName("settingsContent")
        self.body = QtWidgets.QVBoxLayout(content)
        self.body.setContentsMargins(0, 0, 8, 8)
        self.body.setSpacing(20)

        self._build_general()
        self._build_appearance()
        self._build_chronok_defaults()
        self._build_data()
        self._build_about()
        self.body.addStretch(1)

        scroll.setWidget(content)
        root.addWidget(scroll, 1)

    def _section(self, heading):
        section = QtWidgets.QWidget()
        section.setObjectName("settingsSection")
        layout = QtWidgets.QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(9)

        label = QtWidgets.QLabel(heading.upper())
        label.setObjectName("settingsSectionLabel")
        layout.addWidget(label)

        card = QtWidgets.QFrame()
        card.setObjectName("settingsCard")
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(20, 4, 20, 4)
        card_layout.setSpacing(0)
        layout.addWidget(card)

        self.body.addWidget(section)
        return card_layout

    def _settings_row(self, title, description, control):
        row = QtWidgets.QWidget()
        row.setObjectName("settingsRow")
        layout = QtWidgets.QHBoxLayout(row)
        layout.setContentsMargins(0, 15, 0, 15)
        layout.setSpacing(24)

        text = QtWidgets.QWidget()
        text_layout = QtWidgets.QVBoxLayout(text)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)

        title_label = QtWidgets.QLabel(title)
        title_label.setObjectName("settingsItemTitle")
        description_label = QtWidgets.QLabel(description)
        description_label.setObjectName("settingsItemDescription")
        description_label.setWordWrap(True)

        text_layout.addWidget(title_label)
        text_layout.addWidget(description_label)
        layout.addWidget(text, 1)
        layout.addWidget(control, 0, QtCore.Qt.AlignmentFlag.AlignVCenter)
        return row

    def _divider(self):
        line = QtWidgets.QFrame()
        line.setObjectName("settingsDivider")
        line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        line.setFixedHeight(1)
        return line

    def _build_general(self):
        card = self._section("General")
        self.comboStartupPage = QtWidgets.QComboBox()
        self.comboStartupPage.setObjectName("settingsCombo")
        self.comboStartupPage.addItems(["Calendar", "Tasks", "ChronoK"])
        self.comboStartupPage.setMinimumWidth(150)
        card.addWidget(self._settings_row(
            "Startup page",
            "Choose where ChronoTask opens when the application starts.",
            self.comboStartupPage,
        ))

    def _build_appearance(self):
        card = self._section("Appearance")
        self.comboColorTheme = QtWidgets.QComboBox()
        self.comboColorTheme.setObjectName("settingsCombo")
        self._theme_keys = [
            "default", "lavender", "tokyo_night", "nord", "midnight_dusk",
            "tidal_wave", "teal", "yotsuba", "monochrome",
        ]
        labels = [
            "Default", "Lavender", "Tokyo Night", "Nord", "Midnight Dusk",
            "Tidal Wave", "Teal & Turquoise", "Yotsuba", "Monochrome",
        ]
        self.comboColorTheme.addItems(labels)
        self.comboColorTheme.setMinimumWidth(170)
        card.addWidget(self._settings_row(
            "Dark color palette",
            "Change ChronoTask's dark palette. System and light themes are intentionally disabled.",
            self.comboColorTheme,
        ))

    def _build_chronok_defaults(self):
        card = self._section("ChronoK defaults")

        self.spinDefaultDelay = QtWidgets.QSpinBox()
        self.spinDefaultDelay.setObjectName("settingsSpin")
        self.spinDefaultDelay.setRange(0, 365)
        self.spinDefaultDelay.setSuffix(" days")
        self.spinDefaultDelay.setMinimumWidth(150)
        card.addWidget(self._settings_row(
            "Default start delay",
            "Starting delay for newly created ChronoK plans.",
            self.spinDefaultDelay,
        ))
        card.addWidget(self._divider())

        self.checkDefaultRestDay = QtWidgets.QCheckBox()
        self.checkDefaultRestDay.setObjectName("settingsCheck")
        self.checkDefaultRestDay.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        card.addWidget(self._settings_row(
            "Midpoint rest day",
            "Include a midpoint rest day by default for new ChronoK plans.",
            self.checkDefaultRestDay,
        ))

    def _build_data(self):
        card = self._section("Data")
        database = QtWidgets.QLabel("data/chronotask.db")
        database.setObjectName("settingsValue")
        database.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        card.addWidget(self._settings_row(
            "Database",
            "Tasks, Chrono Steps, schedules, and rest-day data are stored locally.",
            database,
        ))

    def _build_about(self):
        card = self._section("About")
        application = QtWidgets.QWidget()
        value_layout = QtWidgets.QVBoxLayout(application)
        value_layout.setContentsMargins(0, 0, 0, 0)
        value_layout.setSpacing(2)
        name = QtWidgets.QLabel("ChronoTask")
        name.setObjectName("settingsValueStrong")
        product = QtWidgets.QLabel("Calendar  •  Tasks  •  ChronoK")
        product.setObjectName("settingsValueMuted")
        value_layout.addWidget(name, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        value_layout.addWidget(product, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        card.addWidget(self._settings_row(
            "Application",
            "A focused task planner with smart ChronoK scheduling.",
            application,
        ))

    def _load_settings(self):
        if self.database is None:
            return
        startup = str(self.database.get_setting("startup_page", "calendar")).lower()
        labels = {"calendar": "Calendar", "tasks": "Tasks", "chronok": "ChronoK"}
        self.comboStartupPage.setCurrentText(labels.get(startup, "Calendar"))
        self.spinDefaultDelay.setValue(max(0, self.database.get_int_setting("default_start_delay", 0)))
        self.checkDefaultRestDay.setChecked(
            self.database.get_bool_setting("default_midpoint_rest_day", False)
        )
        theme = str(self.database.get_setting("color_theme", "default")).lower()
        if hasattr(self, "comboColorTheme"):
            try:
                self.comboColorTheme.setCurrentIndex(self._theme_keys.index(theme))
            except ValueError:
                self.comboColorTheme.setCurrentIndex(0)

    def _connect_settings(self):
        self.comboStartupPage.currentTextChanged.connect(self._save_startup_page)
        self.spinDefaultDelay.valueChanged.connect(self._save_default_delay)
        self.checkDefaultRestDay.toggled.connect(self._save_default_rest_day)
        self.comboColorTheme.currentIndexChanged.connect(self._save_color_theme)

    def _save_startup_page(self, text):
        if self.database is not None:
            self.database.set_setting("startup_page", str(text).lower())

    def _save_default_delay(self, value):
        if self.database is not None:
            self.database.set_setting("default_start_delay", max(0, int(value)))

    def _save_default_rest_day(self, checked):
        if self.database is not None:
            self.database.set_setting("default_midpoint_rest_day", "1" if checked else "0")

    def _save_color_theme(self, index):
        if index < 0 or index >= len(self._theme_keys):
            return
        key = self._theme_keys[index]
        if self.database is not None:
            self.database.set_setting("color_theme", key)
        self._apply_style(key)
        self.theme_changed.emit(key)

    def _apply_style(self, theme_name=None):
        if theme_name is None:
            if self.database is None:
                theme_name = "default"
            else:
                theme_name = str(self.database.get_setting("color_theme", "default")).lower()
        c = palette(theme_name)
        style = r"""
            QWidget#settingsPage,
            QWidget#settingsContent,
            QWidget#settingsSection,
            QWidget#settingsRow {
                background: transparent;
            }

            QScrollArea#settingsScroll,
            QScrollArea#settingsScroll > QWidget,
            QScrollArea#settingsScroll QWidget#qt_scrollarea_viewport {
                background: transparent;
                border: none;
            }

            QLabel#settingsTitle {
                color: #F4F7FF;
                font-family: "Segoe UI";
                font-size: 24px;
                font-weight: 700;
            }

            QLabel#settingsSubtitle {
                color: #93A3BF;
                font-family: "Segoe UI";
                font-size: 10px;
            }

            QLabel#settingsSectionLabel {
                color: #8FAEFF;
                font-family: "Segoe UI";
                font-size: 9px;
                font-weight: 700;
            }

            QFrame#settingsCard {
                background-color: #202A3B;
                border: 1px solid #334563;
                border-radius: 12px;
            }

            QLabel#settingsItemTitle {
                color: #F4F7FF;
                font-family: "Segoe UI";
                font-size: 11px;
                font-weight: 600;
            }

            QLabel#settingsItemDescription {
                color: #91A1BD;
                font-family: "Segoe UI";
                font-size: 9px;
            }

            QLabel#settingsValue,
            QLabel#settingsValueMuted {
                color: #AAB9D3;
                font-family: "Segoe UI";
                font-size: 9px;
            }

            QLabel#settingsValueStrong {
                color: #F4F7FF;
                font-family: "Segoe UI";
                font-size: 10px;
                font-weight: 700;
            }

            QFrame#settingsDivider {
                background-color: #33415A;
                border: none;
                margin-left: 0px;
                margin-right: 0px;
            }

            QComboBox#settingsCombo,
            QSpinBox#settingsSpin {
                color: #F4F7FF;
                background-color: #151D2B;
                border: 1px solid #405273;
                border-radius: 8px;
                padding: 7px 10px;
                min-height: 20px;
                font-family: "Segoe UI";
                font-size: 10px;
            }

            QComboBox#settingsCombo:hover,
            QSpinBox#settingsSpin:hover,
            QComboBox#settingsCombo:focus,
            QSpinBox#settingsSpin:focus {
                border-color: #69A8FF;
            }

            QComboBox#settingsCombo QAbstractItemView {
                color: #F4F7FF;
                background-color: #1A2332;
                selection-background-color: #29476B;
                selection-color: #FFFFFF;
                border: 1px solid #405273;
                outline: none;
                padding: 4px;
            }

            QCheckBox#settingsCheck {
                spacing: 0px;
                padding: 3px;
                background: transparent;
            }

            QCheckBox#settingsCheck::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #60708C;
                border-radius: 6px;
                background-color: #161E2C;
            }

            QCheckBox#settingsCheck::indicator:hover {
                border-color: #7CB4FF;
            }

            QCheckBox#settingsCheck::indicator:checked {
                background-color: #4F91E8;
                border-color: #75B2FF;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background: #3A4A65;
                min-height: 28px;
                border-radius: 4px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
                border: none;
                height: 0px;
            }
        """
        replacements = {
            "#F4F7FF": c["text"],
            "#93A3BF": c["muted"],
            "#8FAEFF": c["accent_hover"],
            "#202A3B": c["surface"],
            "#334563": c["border_soft"],
            "#91A1BD": c["muted"],
            "#AAB9D3": c["muted"],
            "#33415A": c["border_soft"],
            "#151D2B": c["input"],
            "#405273": c["border"],
            "#69A8FF": c["accent_hover"],
            "#1A2332": c["surface_alt"],
            "#29476B": c["accent"],
            "#FFFFFF": c["text"],
            "#60708C": c["border"],
            "#161E2C": c["input"],
            "#7CB4FF": c["accent_hover"],
            "#4F91E8": c["accent"],
            "#75B2FF": c["accent_hover"],
            "#3A4A65": c["border"],
        }
        for old, new in replacements.items():
            style = style.replace(old, new)
        self.setStyleSheet(style)
