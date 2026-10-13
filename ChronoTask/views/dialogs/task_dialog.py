from PySide6 import QtCore, QtGui, QtWidgets

from styles.task_dialog_style import build_task_dialog_style
from views.widgets.chrono_calendar import ChronoCalendar
from views.widgets.dark_combo_box import DarkComboBox
from views.widgets.dark_time_edit import DarkTimeEdit


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


class TaskDialog(QtWidgets.QDialog):
    """Add/Edit Task dialog with optional initial ChronoK planning."""

    MODE_ADD = "add"
    MODE_EDIT = "edit"

    def __init__(self, parent=None, task=None, database=None):
        super().__init__(parent)
        self.task = task
        self.database = database
        self.mode = self.MODE_EDIT if task is not None else self.MODE_ADD
        self.dragging = False
        self.drag_position = QtCore.QPoint()
        self.kaizen_step_edits = []

        self._setup_window()
        self._build_ui()
        theme_name = "default" if self.database is None else str(self.database.get_setting("color_theme", "default")).lower()
        self.current_theme = theme_name
        # Theme both the shared dialog stylesheet and the local ChronoK panel stylesheet.
        self.setStyleSheet(_theme_style(build_task_dialog_style(theme_name) + self._extra_style(), self))
        self._connect_signals()
        self.update_selected_date()
        self._update_start_delay_limit()

        if task is None:
            self._apply_add_defaults()
        else:
            self.load_task(task)

    def _apply_add_defaults(self):
        if self.database is None:
            return
        delay = max(0, self.database.get_int_setting("default_start_delay", 0))
        self._default_start_delay = delay
        self._apply_default_start_delay()
        self.chkRestDay.setChecked(
            self.database.get_bool_setting("default_midpoint_rest_day", False)
        )
        self._update_start_delay_info()

    def _apply_default_start_delay(self):
        if self.mode != self.MODE_ADD:
            return
        delay = max(0, int(getattr(self, "_default_start_delay", 0)))
        self.spinStartDelay.setValue(min(delay, self.spinStartDelay.maximum()))

    def _setup_window(self):
        self.setObjectName("TaskDialog")
        self.setWindowTitle("Add Task")
        self.resize(500, 900)
        self.setMinimumSize(460, 760)
        self.setWindowFlags(
            QtCore.Qt.WindowType.Dialog
            | QtCore.Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(0)

        self.backgroundFrame = QtWidgets.QFrame(self)
        self.backgroundFrame.setObjectName("backgroundFrame")
        root.addWidget(self.backgroundFrame)

        shell = QtWidgets.QVBoxLayout(self.backgroundFrame)
        shell.setContentsMargins(0, 0, 0, 14)
        shell.setSpacing(0)

        self._build_title_bar(shell)

        self.scrollArea = QtWidgets.QScrollArea(self.backgroundFrame)
        self.scrollArea.setObjectName("dialogScroll")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

        self.contentFrame = QtWidgets.QFrame()
        self.contentFrame.setObjectName("contentFrame")
        self.contentLayout = QtWidgets.QVBoxLayout(self.contentFrame)
        self.contentLayout.setContentsMargins(18, 8, 18, 8)
        self.contentLayout.setSpacing(9)

        self._build_heading()
        self._build_calendar()
        self._build_deadline()
        self._build_task_name()
        self._build_description()
        self._build_priority()
        self._build_time()
        self._build_kaizen_section()
        self._build_action_button()

        self.scrollArea.setWidget(self.contentFrame)
        shell.addWidget(self.scrollArea, 1)

    def _build_title_bar(self, parent_layout):
        self.titleBar = QtWidgets.QFrame(self.backgroundFrame)
        self.titleBar.setObjectName("titleBar")
        self.titleBar.setFixedHeight(42)
        layout = QtWidgets.QHBoxLayout(self.titleBar)
        layout.setContentsMargins(16, 0, 10, 0)

        self.lblTitle = QtWidgets.QLabel("Add Task", self.titleBar)
        self.lblTitle.setObjectName("lblTitle")
        layout.addWidget(self.lblTitle)
        layout.addStretch(1)

        self.btnClose = QtWidgets.QPushButton("×", self.titleBar)
        self.btnClose.setObjectName("btnClose")
        self.btnClose.setFixedSize(34, 28)
        self.btnClose.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        layout.addWidget(self.btnClose)
        parent_layout.addWidget(self.titleBar)

    def _build_heading(self):
        self.lblHeading = QtWidgets.QLabel("Create a new task", self.contentFrame)
        self.lblHeading.setObjectName("lblHeading")
        self.lblSubtitle = QtWidgets.QLabel(
            "Choose a deadline, priority, and optional ChronoK plan.",
            self.contentFrame,
        )
        self.lblSubtitle.setObjectName("lblSubtitle")
        self.lblSubtitle.setWordWrap(True)
        self.contentLayout.addWidget(self.lblHeading)
        self.contentLayout.addWidget(self.lblSubtitle)

    def _build_calendar(self):
        self.calendarFrame = QtWidgets.QFrame(self.contentFrame)
        self.calendarFrame.setObjectName("calendarFrame")
        layout = QtWidgets.QVBoxLayout(self.calendarFrame)
        layout.setContentsMargins(8, 8, 8, 8)
        self.calendarWidget = ChronoCalendar(self.calendarFrame)
        self.calendarWidget.setMinimumHeight(260)
        layout.addWidget(self.calendarWidget)
        self.contentLayout.addWidget(self.calendarFrame)

    def _build_deadline(self):
        self.contentLayout.addWidget(self._field_label("SELECTED DEADLINE"))
        self.lblSelectedDeadline = QtWidgets.QLabel("", self.contentFrame)
        self.lblSelectedDeadline.setObjectName("lblSelectedDeadline")
        self.contentLayout.addWidget(self.lblSelectedDeadline)

    def _build_task_name(self):
        self.contentLayout.addWidget(self._field_label("TASK NAME"))
        self.txtTaskName = QtWidgets.QLineEdit(self.contentFrame)
        self.txtTaskName.setObjectName("txtTaskName")
        self.txtTaskName.setPlaceholderText("What needs to be done?")
        self.txtTaskName.setMinimumHeight(42)
        self.contentLayout.addWidget(self.txtTaskName)

    def _build_description(self):
        self.contentLayout.addWidget(self._field_label("DESCRIPTION"))
        self.txtDescription = QtWidgets.QTextEdit(self.contentFrame)
        self.txtDescription.setObjectName("txtDescription")
        self.txtDescription.setPlaceholderText("Add some details about this task...")
        self.txtDescription.setMinimumHeight(68)
        self.txtDescription.setMaximumHeight(90)
        self.contentLayout.addWidget(self.txtDescription)

    def _build_priority(self):
        self.contentLayout.addWidget(self._field_label("PRIORITY"))
        self.cmbPriority = DarkComboBox(self.contentFrame)
        self.cmbPriority.setObjectName("cmbPriority")
        self.cmbPriority.setMinimumHeight(42)
        self.cmbPriority.addItems([
            "Urgent + Important",
            "Not Urgent + Important",
            "Urgent + Not Important",
            "Not Urgent + Not Important",
        ])
        self.contentLayout.addWidget(self.cmbPriority)

    def _build_time(self):
        self.contentLayout.addWidget(self._field_label("TIME"))
        self.timeEdit = DarkTimeEdit(self.contentFrame)
        self.timeEdit.setObjectName("timeEdit")
        self.timeEdit.setMinimumHeight(42)
        self.timeEdit.setDisplayFormat("h:mm AP")
        now = QtCore.QTime.currentTime()
        self.timeEdit.setTime(QtCore.QTime(now.hour(), 0))
        self.contentLayout.addWidget(self.timeEdit)

    def _build_kaizen_section(self):
        self.kaizenFrame = QtWidgets.QFrame(self.contentFrame)
        self.kaizenFrame.setObjectName("kaizenFrame")
        layout = QtWidgets.QVBoxLayout(self.kaizenFrame)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(9)

        top = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("CHRONOK PLAN", self.kaizenFrame)
        title.setObjectName("kaizenTitle")
        top.addWidget(title)
        top.addStretch(1)
        self.chkUseKaizen = QtWidgets.QCheckBox("Use ChronoK planning", self.kaizenFrame)
        self.chkUseKaizen.setObjectName("kaizenCheck")
        top.addWidget(self.chkUseKaizen)
        layout.addLayout(top)

        hint = QtWidgets.QLabel(
            "Add small steps now. ChronoTask will distribute them between today and the deadline.",
            self.kaizenFrame,
        )
        hint.setObjectName("kaizenHint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.kaizenOptions = QtWidgets.QWidget(self.kaizenFrame)
        options_layout = QtWidgets.QVBoxLayout(self.kaizenOptions)
        options_layout.setContentsMargins(0, 2, 0, 0)
        options_layout.setSpacing(8)

        self.chkRestDay = QtWidgets.QCheckBox("Include a midpoint rest day", self.kaizenOptions)
        self.chkRestDay.setObjectName("kaizenCheck")
        options_layout.addWidget(self.chkRestDay)

        delay_row = QtWidgets.QHBoxLayout()
        delay_row.setSpacing(8)
        self.lblStartDelay = QtWidgets.QLabel("Days before starting", self.kaizenOptions)
        self.lblStartDelay.setObjectName("kaizenHint")
        self.spinStartDelay = QtWidgets.QSpinBox(self.kaizenOptions)
        self.spinStartDelay.setObjectName("startDelaySpin")
        self.spinStartDelay.setRange(0, 0)
        self.spinStartDelay.setSuffix(" days")
        self.spinStartDelay.setMinimumWidth(105)
        delay_row.addWidget(self.lblStartDelay)
        delay_row.addStretch(1)
        delay_row.addWidget(self.spinStartDelay)
        options_layout.addLayout(delay_row)
        self.lblStartDelayInfo = QtWidgets.QLabel("", self.kaizenOptions)
        self.lblStartDelayInfo.setObjectName("kaizenHint")
        self.lblStartDelayInfo.setWordWrap(True)
        options_layout.addWidget(self.lblStartDelayInfo)

        self.kaizenStepsContainer = QtWidgets.QWidget(self.kaizenOptions)
        self.kaizenStepsLayout = QtWidgets.QVBoxLayout(self.kaizenStepsContainer)
        self.kaizenStepsLayout.setContentsMargins(0, 0, 0, 0)
        self.kaizenStepsLayout.setSpacing(6)
        options_layout.addWidget(self.kaizenStepsContainer)

        self.btnAddKaizenStep = QtWidgets.QPushButton("+ Add Chrono Step", self.kaizenOptions)
        self.btnAddKaizenStep.setObjectName("addKaizenStepButton")
        self.btnAddKaizenStep.setMinimumHeight(36)
        options_layout.addWidget(self.btnAddKaizenStep)

        layout.addWidget(self.kaizenOptions)
        self.contentLayout.addWidget(self.kaizenFrame)

        self.kaizenOptions.setVisible(False)

    def _build_action_button(self):
        self.btnAddTask = QtWidgets.QPushButton("+ Add Task", self.contentFrame)
        self.btnAddTask.setObjectName("btnAddTask")
        self.btnAddTask.setMinimumHeight(46)
        self.btnAddTask.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.contentLayout.addWidget(self.btnAddTask)

    def _field_label(self, text):
        label = QtWidgets.QLabel(text, self.contentFrame)
        label.setObjectName("lblFieldTitle")
        return label

    def _connect_signals(self):
        self.btnClose.clicked.connect(self.reject)
        self.btnAddTask.clicked.connect(self.validate_and_accept)
        self.calendarWidget.selectionChanged.connect(self.update_selected_date)
        self.calendarWidget.selectionChanged.connect(self._update_start_delay_limit)
        self.spinStartDelay.valueChanged.connect(self._update_start_delay_info)
        self.txtTaskName.textChanged.connect(self.clear_validation_error)
        self.chkUseKaizen.toggled.connect(self._toggle_kaizen)
        self.btnAddKaizenStep.clicked.connect(
            lambda checked=False: self.add_kaizen_step_field()
        )

    @QtCore.Slot(bool)
    def _toggle_kaizen(self, checked):
        self.kaizenOptions.setVisible(checked)
        if checked and not self.kaizen_step_edits:
            self.add_kaizen_step_field()

    def add_kaizen_step_field(self, text=""):
        # QPushButton.clicked emits a bool. Guard against any signal accidentally
        # forwarding that value into QLineEdit.setText().
        if not isinstance(text, str):
            text = ""

        row_widget = QtWidgets.QWidget(self.kaizenStepsContainer)
        row = QtWidgets.QHBoxLayout(row_widget)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)

        edit = QtWidgets.QLineEdit(row_widget)
        edit.setObjectName("kaizenStepEdit")
        edit.setPlaceholderText("Small improvement step...")
        edit.setMinimumHeight(36)
        edit.setText(text)
        row.addWidget(edit, 1)

        remove = QtWidgets.QPushButton("×", row_widget)
        remove.setObjectName("removeKaizenStep")
        remove.setFixedSize(32, 32)
        remove.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        row.addWidget(remove)

        self.kaizenStepsLayout.addWidget(row_widget)
        self.kaizen_step_edits.append((row_widget, edit))
        remove.clicked.connect(
            lambda checked=False: self._remove_kaizen_step_field(
                row_widget, edit
            )
        )

        row_widget.show()
        edit.show()
        remove.show()
        self.kaizenStepsContainer.updateGeometry()
        self.kaizenOptions.updateGeometry()
        self.contentFrame.updateGeometry()
        QtCore.QTimer.singleShot(0, edit.setFocus)

    def _remove_kaizen_step_field(self, row_widget, edit):
        self.kaizen_step_edits = [
            pair for pair in self.kaizen_step_edits if pair[0] is not row_widget
        ]
        row_widget.deleteLater()

    @QtCore.Slot()
    def update_selected_date(self):
        self.lblSelectedDeadline.setText(
            self.calendarWidget.selectedDate().toString("MMMM d, yyyy")
        )

    @QtCore.Slot()
    def _update_start_delay_limit(self):
        today = QtCore.QDate.currentDate()
        deadline = self.calendarWidget.selectedDate()
        maximum = max(0, today.daysTo(deadline))
        self.spinStartDelay.setMaximum(maximum)
        if self.spinStartDelay.value() > maximum:
            self.spinStartDelay.setValue(maximum)
        if self.mode == self.MODE_ADD and hasattr(self, "_default_start_delay"):
            self._apply_default_start_delay()
        self._update_start_delay_info()

    def _update_start_delay_info(self):
        value = self.spinStartDelay.value()
        maximum = self.spinStartDelay.maximum()
        if value == 0:
            text = f"Maximum: {maximum} days. Chrono Steps can start today."
        else:
            start = QtCore.QDate.currentDate().addDays(value)
            text = f"Maximum: {maximum} days. Chrono Steps will start {start.toString('MMM d, yyyy')}."
        self.lblStartDelayInfo.setText(text)

    def validate_and_accept(self):
        if not self.txtTaskName.text().strip():
            self.txtTaskName.setFocus()
            self.txtTaskName.setStyleSheet(_theme_style("border: 1px solid #E06C75;", self))
            return

        if self.chkUseKaizen.isChecked():
            if not self.get_kaizen_steps():
                for _, edit in self.kaizen_step_edits:
                    edit.setFocus()
                    break
                return

        self.accept()

    @QtCore.Slot()
    def clear_validation_error(self):
        self.txtTaskName.setStyleSheet(_theme_style("", self))

    def get_kaizen_steps(self):
        return [
            edit.text().strip()
            for _, edit in self.kaizen_step_edits
            if edit.text().strip()
        ]

    def get_task_data(self):
        return {
            "name": self.txtTaskName.text().strip(),
            "description": self.txtDescription.toPlainText().strip(),
            "priority": self.cmbPriority.currentText(),
            "date": self.calendarWidget.selectedDate(),
            "time": self.timeEdit.time(),
            "use_kaizen": self.chkUseKaizen.isChecked(),
            "include_rest_day": (
                self.chkUseKaizen.isChecked() and self.chkRestDay.isChecked()
            ),
            "start_delay_days": (
                self.spinStartDelay.value() if self.chkUseKaizen.isChecked() else 0
            ),
            "kaizen_steps": self.get_kaizen_steps(),
        }

    def load_task(self, task):
        self.task = task
        self.mode = self.MODE_EDIT
        self.setWindowTitle("Edit Task")
        self.lblTitle.setText("Edit Task")
        self.lblHeading.setText("Update task")
        self.lblSubtitle.setText("Update the task, priority, deadline, and ChronoK plan.")
        self.btnAddTask.setText("Save Changes")

        self.txtTaskName.setText(getattr(task, "title", ""))
        self.txtDescription.setPlainText(getattr(task, "description", ""))

        task_date = self._parse_date(getattr(task, "date", None))
        if task_date.isValid():
            self.calendarWidget.setSelectedDate(task_date)
            self.calendarWidget.showSelectedDate()

        task_time = self._parse_time(getattr(task, "time", None))
        if task_time.isValid():
            self.timeEdit.setTime(task_time)

        self.cmbPriority.setCurrentText(self._priority_from_task(task))

        existing_steps = list(getattr(task, "kaizen_steps", []) or [])
        use_kaizen = bool(existing_steps) or bool(getattr(task, "include_rest_day", False))
        self.chkUseKaizen.setChecked(use_kaizen)
        self.chkRestDay.setChecked(bool(getattr(task, "include_rest_day", False)))
        self._update_start_delay_limit()
        self.spinStartDelay.setValue(int(getattr(task, "start_delay_days", 0)))

        for row_widget, _ in self.kaizen_step_edits:
            row_widget.deleteLater()
        self.kaizen_step_edits.clear()

        if existing_steps:
            for step in existing_steps:
                self.add_kaizen_step_field(getattr(step, "description", ""))
        elif use_kaizen:
            self.add_kaizen_step_field()

        self.kaizenOptions.setVisible(use_kaizen)
        self.update_selected_date()

    @staticmethod
    def _parse_date(value):
        if isinstance(value, QtCore.QDate):
            return value
        if value is None:
            return QtCore.QDate()
        for fmt in ("yyyy-MM-dd", "MM/dd/yyyy", "M/d/yyyy"):
            parsed = QtCore.QDate.fromString(str(value), fmt)
            if parsed.isValid():
                return parsed
        return QtCore.QDate()

    @staticmethod
    def _parse_time(value):
        if isinstance(value, QtCore.QTime):
            return value
        if value is None:
            return QtCore.QTime()
        for fmt in ("HH:mm", "H:mm", "h:mm AP"):
            parsed = QtCore.QTime.fromString(str(value), fmt)
            if parsed.isValid():
                return parsed
        return QtCore.QTime()

    @staticmethod
    def _priority_from_task(task):
        urgent = bool(getattr(task, "isUrgent", False))
        important = bool(getattr(task, "isImportant", False))
        if urgent and important:
            return "Urgent + Important"
        if important:
            return "Not Urgent + Important"
        if urgent:
            return "Urgent + Not Important"
        return "Not Urgent + Not Important"

    def _extra_style(self):
        return """
            QScrollArea#dialogScroll, QScrollArea#dialogScroll > QWidget > QWidget {
                background: transparent; border: none;
            }
            QFrame#kaizenFrame {
                background: #202B3F; border: 1px solid #34425D; border-radius: 11px;
            }
            QLabel#kaizenTitle {
                color: #F4F7FF; background: transparent; font: 700 10px "Segoe UI";
            }
            QLabel#kaizenHint {
                color: #9AA9C3; background: transparent; font: 10px "Segoe UI";
            }
            QCheckBox#kaizenCheck {
                color: #DCE5F7; background: transparent; spacing: 7px; font: 10px "Segoe UI";
            }
            QCheckBox#kaizenCheck::indicator {
                width: 18px; height: 18px; background: #253349;
                border: 1px solid #536784; border-radius: 5px;
            }
            QCheckBox#kaizenCheck::indicator:checked {
                background: #3E8AC4; border-color: #59B7FF;
            }
            QSpinBox#startDelaySpin { background:#253349; color:#F4F7FF; border:1px solid #40506C; border-radius:7px; padding:5px 8px; font:9px "Segoe UI"; }
            QLineEdit#kaizenStepEdit {
                background: #253349; color: #F4F7FF; border: 1px solid #40506C;
                border-radius: 8px; padding: 0 11px; font: 10px "Segoe UI";
                selection-background-color: #3E8AC4;
            }
            QLineEdit#kaizenStepEdit:focus { border-color: #59B7FF; }
            QPushButton#removeKaizenStep {
                background: transparent; color: #D68087; border: none;
                border-radius: 6px; font-size: 15px;
            }
            QPushButton#removeKaizenStep:hover { background: #4A2D39; color: white; }
            QPushButton#addKaizenStepButton {
                background: #253349; color: #DCE5F7; border: 1px solid #40506C;
                border-radius: 8px; font: 600 10px "Segoe UI";
            }
            QPushButton#addKaizenStepButton:hover {
                background: #31425D; border-color: #59B7FF; color: white;
            }
        """

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            position = self.titleBar.mapFrom(self, event.position().toPoint())
            if self.titleBar.rect().contains(position):
                self.dragging = True
                self.drag_position = (
                    event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                )
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        super().mouseReleaseEvent(event)