from PySide6 import QtCore, QtGui, QtWidgets


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


class TaskCard(QtWidgets.QFrame):
    """Reusable task card used by the ChronoTask Tasks page."""

    completion_changed = QtCore.Signal(object, bool)
    edit_requested = QtCore.Signal(object)
    delete_requested = QtCore.Signal(object)
    kaizen_requested = QtCore.Signal(object)  # Internal compatibility name.

    PRIORITY_COLORS = {
        "Urgent + Important": "#E06C75",
        "Not Urgent + Important": "#59B7FF",
        "Urgent + Not Important": "#E6B86A",
        "Not Urgent + Not Important": "#7F8DAA",
    }

    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.setObjectName("taskCard")
        self.setProperty("completed", False)
        self.setProperty("overdue", False)
        self._build_ui()
        self._apply_style()
        self._connect_signals()
        self.refresh()

    def _build_ui(self):
        self.mainLayout = QtWidgets.QHBoxLayout(self)
        self.mainLayout.setContentsMargins(16, 14, 14, 14)
        self.mainLayout.setSpacing(12)

        self.chkComplete = QtWidgets.QCheckBox(self)
        self.chkComplete.setObjectName("chkComplete")
        self.chkComplete.setToolTip("Mark task as complete")
        self.chkComplete.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        self.mainLayout.addWidget(
            self.chkComplete,
            0,
            QtCore.Qt.AlignmentFlag.AlignTop,
        )

        self.infoLayout = QtWidgets.QVBoxLayout()
        self.infoLayout.setContentsMargins(0, 0, 0, 0)
        self.infoLayout.setSpacing(5)

        self.titleLayout = QtWidgets.QHBoxLayout()
        self.titleLayout.setContentsMargins(0, 0, 0, 0)
        self.titleLayout.setSpacing(7)

        self.lblOverdueIcon = QtWidgets.QLabel("!", self)
        self.lblOverdueIcon.setObjectName("overdueIcon")
        self.lblOverdueIcon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lblOverdueIcon.setFixedSize(18, 18)
        self.lblOverdueIcon.setToolTip("This task is overdue")

        self.lblTitle = QtWidgets.QLabel("", self)
        self.lblTitle.setObjectName("taskTitle")
        self.lblTitle.setWordWrap(True)

        self.lblOverdueBadge = QtWidgets.QLabel("OVERDUE", self)
        self.lblOverdueBadge.setObjectName("overdueBadge")
        self.lblOverdueBadge.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.titleLayout.addWidget(self.lblOverdueIcon)
        self.titleLayout.addWidget(self.lblTitle, 1)
        self.titleLayout.addWidget(self.lblOverdueBadge)
        self.infoLayout.addLayout(self.titleLayout)

        self.metadataLayout = QtWidgets.QHBoxLayout()
        self.metadataLayout.setContentsMargins(0, 0, 0, 0)
        self.metadataLayout.setSpacing(7)

        self.lblDeadline = self._create_metadata_label()
        self.lblSeparatorOne = self._create_separator()
        self.lblTime = self._create_metadata_label()
        self.lblSeparatorTwo = self._create_separator()
        self.lblPriority = QtWidgets.QLabel("", self)
        self.lblPriority.setObjectName("taskPriority")

        self.metadataLayout.addWidget(self.lblDeadline)
        self.metadataLayout.addWidget(self.lblSeparatorOne)
        self.metadataLayout.addWidget(self.lblTime)
        self.metadataLayout.addWidget(self.lblSeparatorTwo)
        self.metadataLayout.addWidget(self.lblPriority)
        self.metadataLayout.addStretch(1)
        self.infoLayout.addLayout(self.metadataLayout)

        # Compact ChronoK summary. This makes the card useful without making
        # it excessively tall.
        self.lblChronoSummary = QtWidgets.QLabel("", self)
        self.lblChronoSummary.setObjectName("chronoSummary")
        self.lblChronoSummary.setWordWrap(True)
        self.infoLayout.addWidget(self.lblChronoSummary)

        self.mainLayout.addLayout(self.infoLayout, 1)

        self.actionsLayout = QtWidgets.QHBoxLayout()
        self.actionsLayout.setContentsMargins(0, 0, 0, 0)
        self.actionsLayout.setSpacing(5)

        # This button was previously connected but never created, which caused
        # the AttributeError when a TaskCard was constructed.
        self.btnChronoK = self._create_action_button(
            "ChronoK",
            "taskChronoKButton",
            "Open ChronoK plan",
        )
        self.btnEdit = self._create_action_button(
            "Edit", "taskEditButton", "Edit task"
        )
        self.btnDelete = self._create_action_button(
            "Delete", "taskDeleteButton", "Delete task"
        )

        self.actionsLayout.addWidget(self.btnChronoK)
        self.actionsLayout.addWidget(self.btnEdit)
        self.actionsLayout.addWidget(self.btnDelete)
        self.mainLayout.addLayout(self.actionsLayout)

    def _create_metadata_label(self):
        label = QtWidgets.QLabel("", self)
        label.setObjectName("taskMetadata")
        return label

    def _create_separator(self):
        label = QtWidgets.QLabel("•", self)
        label.setObjectName("taskSeparator")
        return label

    def _create_action_button(self, text, object_name, tooltip):
        button = QtWidgets.QPushButton(text, self)
        button.setObjectName(object_name)
        button.setFixedHeight(30)
        button.setToolTip(tooltip)
        button.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        return button

    def _connect_signals(self):
        self.chkComplete.toggled.connect(self._completion_toggled)
        self.btnChronoK.clicked.connect(self._chronok_clicked)
        self.btnEdit.clicked.connect(self._edit_clicked)
        self.btnDelete.clicked.connect(self._delete_clicked)

    @QtCore.Slot(bool)
    def _completion_toggled(self, checked):
        self.update_completed_appearance(checked)
        self.completion_changed.emit(self.task, checked)

    @QtCore.Slot()
    def _chronok_clicked(self):
        self.kaizen_requested.emit(self.task)

    @QtCore.Slot()
    def _edit_clicked(self):
        self.edit_requested.emit(self.task)

    @QtCore.Slot()
    def _delete_clicked(self):
        self.delete_requested.emit(self.task)

    def refresh(self):
        self.lblTitle.setText(
            str(getattr(self.task, "title", "Untitled Task"))
        )
        self.lblDeadline.setText(
            self.format_date(getattr(self.task, "date", ""))
        )
        self.lblTime.setText(
            self.format_time(getattr(self.task, "time", ""))
        )

        priority = self.get_priority_text()
        self.lblPriority.setText(priority)
        self.update_priority_style(priority)
        self._refresh_chrono_summary()

        completed = bool(getattr(self.task, "completed", False))
        self.chkComplete.blockSignals(True)
        self.chkComplete.setChecked(completed)
        self.chkComplete.blockSignals(False)
        self.update_overdue_appearance()
        self.update_completed_appearance(completed)

    def _refresh_chrono_summary(self):
        steps = list(getattr(self.task, "kaizen_steps", []) or [])
        if not steps:
            self.lblChronoSummary.setText("ChronoK: No plan")
            return

        done = sum(
            bool(getattr(step, "completed", False))
            for step in steps
        )
        progress = round(done / len(steps) * 100)
        remaining = len(steps) - done
        self.lblChronoSummary.setText(
            f"ChronoK: {progress}%  •  {done}/{len(steps)} completed"
            f"  •  {remaining} remaining"
        )

    def get_priority_text(self):
        urgent = bool(getattr(self.task, "isUrgent", False))
        important = bool(getattr(self.task, "isImportant", False))

        if urgent and important:
            return "Urgent + Important"
        if not urgent and important:
            return "Not Urgent + Important"
        if urgent and not important:
            return "Urgent + Not Important"
        return "Not Urgent + Not Important"

    def update_priority_style(self, priority):
        color = self.PRIORITY_COLORS.get(priority, "#8A9AB7")
        self.lblPriority.setStyleSheet(_theme_style(
            f"""
            QLabel#taskPriority {{
                background-color: transparent;
                color: {color};
                border: none;
                font-family: "Segoe UI";
                font-size: 9px;
                font-weight: 600;
            }}
            """
        , self))

    def update_overdue_appearance(self):
        overdue = bool(getattr(self.task, "is_overdue", False))
        self.setProperty("overdue", overdue)
        self.lblOverdueIcon.setVisible(overdue)
        self.lblOverdueBadge.setVisible(overdue)

        metadata_color = "#FF717A" if overdue else "#8392AE"
        self.lblDeadline.setStyleSheet(_theme_style(
            f'color:{metadata_color}; background:transparent; border:none; font:600 9px "Segoe UI";'
        , self))
        self.lblTime.setStyleSheet(_theme_style(
            f'color:{metadata_color}; background:transparent; border:none; font:600 9px "Segoe UI";'
        , self))
        self.style().unpolish(self)
        self.style().polish(self)

    def update_completed_appearance(self, completed):
        self.setProperty("completed", completed)
        if completed:
            self.setProperty("overdue", False)
            self.lblOverdueIcon.hide()
            self.lblOverdueBadge.hide()
        title_color = "#65738D" if completed else "#F4F7FF"
        decoration = "text-decoration: line-through;" if completed else ""
        self.lblTitle.setStyleSheet(_theme_style(
            f"""
            QLabel#taskTitle {{
                background-color: transparent;
                color: {title_color};
                border: none;
                font-family: "Segoe UI";
                font-size: 12px;
                font-weight: 600;
                {decoration}
            }}
            """
        , self))
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    @staticmethod
    def format_date(value):
        if isinstance(value, QtCore.QDate):
            date = value
        else:
            date = QtCore.QDate.fromString(str(value), "yyyy-MM-dd")
        if date.isValid():
            return date.toString("MMM d, yyyy")
        return str(value) if value else "No deadline"

    @staticmethod
    def format_time(value):
        if isinstance(value, QtCore.QTime):
            time = value
        else:
            time = QtCore.QTime.fromString(str(value), "HH:mm")
        if time.isValid():
            return time.toString("h:mm AP")
        return str(value) if value else "No time"

    def _apply_style(self):
        self.setStyleSheet(_theme_style(
            """
            QFrame#taskCard {
                background-color: #202B3F;
                border: 1px solid #34425D;
                border-radius: 12px;
            }
            QFrame#taskCard[overdue="true"] {
                background-color: #2B2634;
                border: 1px solid #B84E59;
            }
            QFrame#taskCard[overdue="true"]:hover {
                background-color: #332936;
                border-color: #E06C75;
            }
            QLabel#overdueIcon {
                background-color: #E54852;
                color: #FFFFFF;
                border: 1px solid #FF717A;
                border-radius: 9px;
                font: 800 12px "Segoe UI";
            }
            QLabel#overdueBadge {
                background-color: #4B2831;
                color: #FF8C94;
                border: 1px solid #82404B;
                border-radius: 6px;
                padding: 3px 7px;
                font: 700 8px "Segoe UI";
            }
            QFrame#taskCard:hover {
                background-color: #243149;
                border-color: #40506C;
            }
            QFrame#taskCard[completed="true"] {
                background-color: #1D2738;
                border-color: #2E3A52;
            }
            QLabel#taskTitle {
                background: transparent;
                color: #F4F7FF;
                border: none;
                font: 600 12px "Segoe UI";
            }
            QLabel#taskMetadata, QLabel#taskSeparator {
                background: transparent;
                color: #8392AE;
                border: none;
                font: 9px "Segoe UI";
            }
            QLabel#chronoSummary {
                background: transparent;
                color: #9AA9C3;
                border: none;
                font: 9px "Segoe UI";
            }
            QCheckBox#chkComplete {
                background: transparent;
                spacing: 0px;
            }
            QCheckBox#chkComplete::indicator {
                width: 18px;
                height: 18px;
                background-color: #253349;
                border: 1px solid #536784;
                border-radius: 5px;
            }
            QCheckBox#chkComplete::indicator:hover {
                border-color: #59B7FF;
            }
            QCheckBox#chkComplete::indicator:checked {
                background-color: #3E8AC4;
                border-color: #59B7FF;
            }
            QPushButton#taskChronoKButton,
            QPushButton#taskEditButton {
                background-color: transparent;
                color: #AAB6CF;
                border: 1px solid #40506C;
                border-radius: 7px;
                padding-left: 10px;
                padding-right: 10px;
                font: 600 9px "Segoe UI";
            }
            QPushButton#taskChronoKButton:hover {
                background-color: #243A50;
                color: #59B7FF;
                border-color: #59B7FF;
            }
            QPushButton#taskEditButton:hover {
                background-color: #2B3851;
                color: #FFFFFF;
                border-color: #536784;
            }
            QPushButton#taskDeleteButton {
                background-color: transparent;
                color: #D68087;
                border: 1px solid #5B3A46;
                border-radius: 7px;
                padding-left: 10px;
                padding-right: 10px;
                font: 600 9px "Segoe UI";
            }
            QPushButton#taskDeleteButton:hover {
                background-color: #4A2D39;
                color: #FFFFFF;
                border-color: #E06C75;
            }
            """
        , self))