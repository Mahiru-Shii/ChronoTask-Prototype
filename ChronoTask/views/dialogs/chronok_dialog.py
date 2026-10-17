from collections import Counter
from datetime import datetime

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


class ChronoKDialog(QtWidgets.QDialog):
    """Create, schedule, and manage Chrono Steps for one task."""

    steps_changed = QtCore.Signal()
    step_completed = QtCore.Signal(object)

    PRIORITY_COLORS = {
        (True, True): "#E06C75",
        (False, True): "#59B7FF",
        (True, False): "#E6B86A",
        (False, False): "#8A8FB8",
    }

    def __init__(self, task, task_controller, parent=None):
        super().__init__(parent)
        self.task = task
        self.task_controller = task_controller
        self.dragging = False
        self.drag_position = QtCore.QPoint()

        self.setObjectName("ChronoKDialog")
        self._setup_window()
        self._build_ui()
        self._apply_style()
        self._connect_signals()
        self._load_task_options()
        self.refresh_all()

    # =================================================================
    # WINDOW
    # =================================================================

    def _setup_window(self):
        self.setWindowTitle("ChronoK Plan")
        self.setModal(True)
        self.resize(680, 700)
        self.setMinimumSize(620, 620)
        self.setWindowFlags(
            QtCore.Qt.WindowType.Dialog
            | QtCore.Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(
            QtCore.Qt.WidgetAttribute.WA_TranslucentBackground,
            True,
        )

    # =================================================================
    # BUILD UI
    # =================================================================

    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(0)

        self.frame = QtWidgets.QFrame(self)
        self.frame.setObjectName("dialogFrame")
        root.addWidget(self.frame)

        layout = QtWidgets.QVBoxLayout(self.frame)
        layout.setContentsMargins(22, 0, 22, 22)
        layout.setSpacing(14)

        self._build_title_bar(layout)
        self._build_task_header(layout)
        self._build_schedule_options(layout)
        self._build_add_step(layout)
        self._build_step_list(layout)
        self._build_footer(layout)

    def _build_title_bar(self, parent_layout):
        self.titleBar = QtWidgets.QFrame(self.frame)
        self.titleBar.setObjectName("titleBar")
        self.titleBar.setFixedHeight(52)

        bar = QtWidgets.QHBoxLayout(self.titleBar)
        bar.setContentsMargins(0, 0, 0, 0)

        self.lblWindowTitle = QtWidgets.QLabel("ChronoK Plan", self.titleBar)
        self.lblWindowTitle.setObjectName("windowTitle")
        bar.addWidget(self.lblWindowTitle)
        bar.addStretch(1)

        self.btnClose = QtWidgets.QPushButton("×", self.titleBar)
        self.btnClose.setObjectName("closeButton")
        self.btnClose.setFixedSize(34, 30)
        self.btnClose.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        bar.addWidget(self.btnClose)
        parent_layout.addWidget(self.titleBar)

    def _build_task_header(self, parent_layout):
        self.lblTask = QtWidgets.QLabel(
            str(getattr(self.task, "title", "Untitled Task")),
            self.frame,
        )
        self.lblTask.setObjectName("taskTitle")
        self.lblTask.setWordWrap(True)
        parent_layout.addWidget(self.lblTask)

        priority = self._priority_text()
        self.lblPriority = QtWidgets.QLabel(priority, self.frame)
        self.lblPriority.setObjectName("priority")
        color = self.PRIORITY_COLORS[
            (
                bool(getattr(self.task, "isUrgent", False)),
                bool(getattr(self.task, "isImportant", False)),
            )
        ]
        self.lblPriority.setStyleSheet(_theme_style(
            f'color:{color}; background:transparent; font:700 11px "Segoe UI";'
        , self))
        parent_layout.addWidget(self.lblPriority)

        self.lblHint = QtWidgets.QLabel(
            "Break the task into small improvements. ChronoTask spreads the steps across available days before the deadline.",
            self.frame,
        )
        self.lblHint.setObjectName("hint")
        self.lblHint.setWordWrap(True)
        parent_layout.addWidget(self.lblHint)

        progress_row = QtWidgets.QHBoxLayout()
        self.progress = QtWidgets.QProgressBar(self.frame)
        self.progress.setObjectName("progress")
        self.progress.setRange(0, 100)
        self.lblProgress = QtWidgets.QLabel("0%", self.frame)
        self.lblProgress.setObjectName("progressText")
        progress_row.addWidget(self.progress, 1)
        progress_row.addWidget(self.lblProgress)
        parent_layout.addLayout(progress_row)

    def _build_schedule_options(self, parent_layout):
        options = QtWidgets.QFrame(self.frame)
        options.setObjectName("scheduleOptions")
        options_layout = QtWidgets.QVBoxLayout(options)
        options_layout.setContentsMargins(14, 12, 14, 12)
        options_layout.setSpacing(8)

        top = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("SMART SCHEDULE", options)
        label.setObjectName("sectionLabel")
        top.addWidget(label)
        top.addStretch(1)

        self.chkRestDay = QtWidgets.QCheckBox("Include a rest day", options)
        self.chkRestDay.setObjectName("restCheck")
        self.chkRestDay.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        top.addWidget(self.chkRestDay)
        options_layout.addLayout(top)

        delay_row = QtWidgets.QHBoxLayout()
        delay_label = QtWidgets.QLabel("Days before starting", options)
        delay_label.setObjectName("sectionLabel")
        self.spinStartDelay = QtWidgets.QSpinBox(options)
        self.spinStartDelay.setObjectName("startDelaySpin")
        self.spinStartDelay.setSuffix(" days")
        self.spinStartDelay.setMinimumWidth(105)
        delay_row.addWidget(delay_label)
        delay_row.addStretch(1)
        delay_row.addWidget(self.spinStartDelay)
        options_layout.addLayout(delay_row)
        self.lblStartDelayInfo = QtWidgets.QLabel("", options)
        self.lblStartDelayInfo.setObjectName("restInfo")
        self.lblStartDelayInfo.setWordWrap(True)
        options_layout.addWidget(self.lblStartDelayInfo)

        self.lblScheduleSummary = QtWidgets.QLabel("", options)
        self.lblScheduleSummary.setObjectName("scheduleSummary")
        self.lblScheduleSummary.setWordWrap(True)
        options_layout.addWidget(self.lblScheduleSummary)

        self.lblRestInfo = QtWidgets.QLabel("", options)
        self.lblRestInfo.setObjectName("restInfo")
        self.lblRestInfo.setWordWrap(True)
        options_layout.addWidget(self.lblRestInfo)

        parent_layout.addWidget(options)

    def _build_add_step(self, parent_layout):
        label = QtWidgets.QLabel("CHRONO STEPS", self.frame)
        label.setObjectName("sectionLabel")
        parent_layout.addWidget(label)

        add_row = QtWidgets.QHBoxLayout()
        add_row.setSpacing(8)

        self.txtStep = QtWidgets.QLineEdit(self.frame)
        self.txtStep.setObjectName("stepInput")
        self.txtStep.setPlaceholderText("Add a small next step...")
        self.txtStep.setMinimumHeight(44)

        self.btnAdd = QtWidgets.QPushButton("+ Add Step", self.frame)
        self.btnAdd.setObjectName("addButton")
        self.btnAdd.setMinimumSize(116, 44)
        self.btnAdd.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )

        add_row.addWidget(self.txtStep, 1)
        add_row.addWidget(self.btnAdd)
        parent_layout.addLayout(add_row)

    def _build_step_list(self, parent_layout):
        self.scroll = QtWidgets.QScrollArea(self.frame)
        self.scroll.setObjectName("stepsScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

        self.stepsWidget = QtWidgets.QWidget()
        self.stepsWidget.setObjectName("stepsWidget")
        self.stepsLayout = QtWidgets.QVBoxLayout(self.stepsWidget)
        self.stepsLayout.setContentsMargins(0, 0, 4, 0)
        self.stepsLayout.setSpacing(9)
        self.stepsLayout.addStretch(1)

        self.scroll.setWidget(self.stepsWidget)
        parent_layout.addWidget(self.scroll, 1)

    def _build_footer(self, parent_layout):
        self.btnDone = QtWidgets.QPushButton("Done", self.frame)
        self.btnDone.setObjectName("doneButton")
        self.btnDone.setMinimumHeight(44)
        self.btnDone.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        parent_layout.addWidget(self.btnDone)

    # =================================================================
    # DATA / SIGNALS
    # =================================================================

    def _connect_signals(self):
        self.btnClose.clicked.connect(self.accept)
        self.btnDone.clicked.connect(self.accept)
        self.btnAdd.clicked.connect(self.add_step)
        self.txtStep.returnPressed.connect(self.add_step)
        self.chkRestDay.toggled.connect(self.rest_day_changed)
        self.spinStartDelay.valueChanged.connect(self.start_delay_changed)

    def _load_task_options(self):
        self.chkRestDay.blockSignals(True)
        self.chkRestDay.setChecked(
            bool(getattr(self.task, "include_rest_day", False))
        )
        self.chkRestDay.blockSignals(False)
        self._update_start_delay_limit()
        self.spinStartDelay.blockSignals(True)
        self.spinStartDelay.setValue(int(getattr(self.task, "start_delay_days", 0)))
        self.spinStartDelay.blockSignals(False)
        self._update_start_delay_info()

    def _update_start_delay_limit(self):
        today = QtCore.QDate.currentDate()
        deadline = QtCore.QDate.fromString(str(getattr(self.task, "date", "")), "yyyy-MM-dd")
        maximum = max(0, today.daysTo(deadline)) if deadline.isValid() else 0
        self.spinStartDelay.setMaximum(maximum)
        if self.spinStartDelay.value() > maximum:
            self.spinStartDelay.setValue(maximum)

    def _update_start_delay_info(self):
        value = self.spinStartDelay.value()
        maximum = self.spinStartDelay.maximum()
        if value == 0:
            text = f"Maximum: {maximum} days. Chrono Steps can start today."
        else:
            start = QtCore.QDate.currentDate().addDays(value)
            text = f"Maximum: {maximum} days. Chrono Steps will start {start.toString('MMM d, yyyy')}."
        self.lblStartDelayInfo.setText(text)

    @QtCore.Slot(int)
    def start_delay_changed(self, value):
        self.task.start_delay_days = int(value)
        self._reschedule()
        self._update_start_delay_info()
        self.refresh_all()
        self.steps_changed.emit()

    @QtCore.Slot(bool)
    def rest_day_changed(self, checked):
        self.task.include_rest_day = bool(checked)
        self._reschedule()
        self.refresh_all()
        self.steps_changed.emit()

    def refresh_all(self):
        self.refresh_steps()
        self.refresh_schedule_summary()

    def refresh_steps(self):
        while self.stepsLayout.count() > 1:
            item = self.stepsLayout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        steps = list(getattr(self.task, "kaizen_steps", []) or [])
        for index, step in enumerate(steps, 1):
            self.stepsLayout.insertWidget(
                self.stepsLayout.count() - 1,
                self._step_row(index, step),
            )

        if not steps:
            empty = QtWidgets.QLabel(
                "No Chrono Steps yet. Add the first small improvement above.",
                self.stepsWidget,
            )
            empty.setObjectName("emptySteps")
            empty.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            empty.setMinimumHeight(70)
            self.stepsLayout.insertWidget(0, empty)

        progress = self._progress_value()
        self.progress.setValue(progress)
        self.lblProgress.setText(f"{progress}%")

    def _step_row(self, index, step):
        frame = QtWidgets.QFrame(self.stepsWidget)
        frame.setObjectName("stepRow")
        row = QtWidgets.QHBoxLayout(frame)
        row.setContentsMargins(12, 9, 9, 9)
        row.setSpacing(10)

        check = QtWidgets.QCheckBox(frame)
        check.setObjectName("stepCheck")
        check.setChecked(bool(getattr(step, "completed", False)))
        check.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        check.toggled.connect(
            lambda checked, current=step: self.set_completed(current, checked)
        )
        row.addWidget(check)

        text_box = QtWidgets.QVBoxLayout()
        text_box.setSpacing(3)

        text = QtWidgets.QLabel(
            f"{index}. {getattr(step, 'description', '')}",
            frame,
        )
        text.setObjectName("stepText")
        text.setWordWrap(True)
        text.setProperty("done", bool(getattr(step, "completed", False)))
        text_box.addWidget(text)

        scheduled = getattr(step, "scheduled_date", None)
        schedule_text = self._format_schedule_date(scheduled)
        meta = QtWidgets.QLabel(schedule_text, frame)
        meta.setObjectName("stepDate")
        text_box.addWidget(meta)

        row.addLayout(text_box, 1)

        delete = QtWidgets.QPushButton("×", frame)
        delete.setObjectName("deleteStep")
        delete.setFixedSize(30, 30)
        delete.setToolTip("Delete step")
        delete.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        delete.clicked.connect(
            lambda checked=False, current=step: self.delete_step(current)
        )
        row.addWidget(delete)
        return frame

    # =================================================================
    # STEP ACTIONS
    # =================================================================

    @QtCore.Slot()
    def add_step(self):
        description = self.txtStep.text().strip()
        if not description:
            self.txtStep.setFocus()
            return

        method = getattr(self.task_controller, "add_kaizen_step", None)
        if callable(method):
            method(self.task, description)
        else:
            from models.kaizen_step import KaizenStep
            self.task.kaizen_steps.append(KaizenStep(description))
            self._reschedule()

        self.txtStep.clear()
        self.refresh_all()
        self.steps_changed.emit()

    def set_completed(self, step, checked):
        was_completed = bool(getattr(step, "completed", False))
        method = getattr(
            self.task_controller,
            "set_kaizen_step_completed",
            None,
        )
        if callable(method):
            try:
                method(self.task, step, checked)
            except ValueError:
                step.completed = checked
        else:
            step.completed = checked

        self.refresh_all()
        self.steps_changed.emit()
        if checked and not was_completed:
            self.step_completed.emit(step)

    def delete_step(self, step):
        method = getattr(self.task_controller, "delete_kaizen_step", None)
        if callable(method):
            try:
                method(self.task, step)
            except ValueError:
                return
        elif step in self.task.kaizen_steps:
            self.task.kaizen_steps.remove(step)
            self._reschedule()

        self.refresh_all()
        self.steps_changed.emit()

    def _reschedule(self):
        method = getattr(self.task_controller, "schedule_kaizen_steps", None)
        if callable(method):
            try:
                method(self.task)
            except ValueError:
                pass

    # =================================================================
    # SCHEDULE SUMMARY
    # =================================================================

    def refresh_schedule_summary(self):
        steps = list(getattr(self.task, "kaizen_steps", []) or [])
        counts = Counter(
            getattr(step, "scheduled_date", None)
            for step in steps
            if getattr(step, "scheduled_date", None)
        )

        if not steps:
            self.lblScheduleSummary.setText(
                "Add steps to generate an automatic daily schedule."
            )
        elif not counts:
            self.lblScheduleSummary.setText(
                "The current task dates do not provide a schedulable range."
            )
        else:
            busiest = max(counts.values())
            scheduled_days = len(counts)
            if busiest > 1:
                load_text = f"Up to {busiest} steps may be scheduled on one day."
            else:
                load_text = "At most 1 step is scheduled per work day."
            self.lblScheduleSummary.setText(
                f"{len(steps)} steps across {scheduled_days} work days. {load_text}"
            )

        own_rest = list(getattr(self.task, "rest_dates", []) or [])
        external = self._external_rest_dates()
        info = []

        if own_rest:
            formatted = ", ".join(self._short_date(value) for value in own_rest)
            info.append(f"Task rest day: {formatted}")
        elif bool(getattr(self.task, "include_rest_day", False)):
            info.append("A rest day could not be placed in this short schedule.")

        if external:
            formatted = ", ".join(
                self._short_date(value)
                for value in sorted(external)
            )
            info.append(f"Existing rest days respected: {formatted}")

        self.lblRestInfo.setText("  •  ".join(info))
        self.lblRestInfo.setVisible(bool(info))

    def _external_rest_dates(self):
        method = getattr(self.task_controller, "get_rest_dates", None)
        if not callable(method):
            return set()
        try:
            dates = method(exclude_task=self.task)
        except TypeError:
            dates = method()
        return {
            value.isoformat() if hasattr(value, "isoformat") else str(value)
            for value in dates
        }

    # =================================================================
    # HELPERS
    # =================================================================

    def _progress_value(self):
        method = getattr(self.task_controller, "get_progress", None)
        if callable(method):
            try:
                return method(self.task)
            except ValueError:
                pass

        steps = list(getattr(self.task, "kaizen_steps", []) or [])
        if not steps:
            return 0
        completed = sum(
            bool(getattr(step, "completed", False))
            for step in steps
        )
        return round(completed / len(steps) * 100)

    def _priority_text(self):
        urgent = bool(getattr(self.task, "isUrgent", False))
        important = bool(getattr(self.task, "isImportant", False))
        if urgent and important:
            return "Urgent + Important  •  DO FIRST"
        if important:
            return "Not Urgent + Important  •  SCHEDULE"
        if urgent:
            return "Urgent + Not Important  •  DELEGATE"
        return "Not Urgent + Not Important  •  IMPROVE"

    @staticmethod
    def _format_schedule_date(value):
        if not value:
            return "Not scheduled"
        try:
            formatted = datetime.strptime(
                str(value),
                "%Y-%m-%d",
            ).strftime("%a, %b %d")
            return f"Scheduled: {formatted}"
        except ValueError:
            return f"Scheduled: {value}"

    @staticmethod
    def _short_date(value):
        try:
            return datetime.strptime(
                str(value),
                "%Y-%m-%d",
            ).strftime("%b %d")
        except ValueError:
            return str(value)

    # =================================================================
    # STYLE
    # =================================================================

    def _apply_style(self):
        self.setStyleSheet(_theme_style(
            """
            QDialog#ChronoKDialog {
                background: transparent;
            }

            QFrame#dialogFrame {
                background: #182133;
                border: 1px solid #40506C;
                border-radius: 18px;
            }

            QFrame#titleBar {
                background: transparent;
                border: none;
            }

            QLabel#windowTitle {
                color: #F4F7FF;
                background: transparent;
                font-family: "Segoe UI";
                font-size: 13px;
                font-weight: 600;
            }

            QPushButton#closeButton {
                background: transparent;
                color: #AAB6CF;
                border: none;
                border-radius: 6px;
                font-family: "Segoe UI";
                font-size: 17px;
            }

            QPushButton#closeButton:hover {
                background: #253349;
                color: white;
            }

            QLabel#taskTitle {
                color: #F4F7FF;
                background: transparent;
                font-family: "Segoe UI";
                font-size: 22px;
                font-weight: 700;
            }

            QLabel#hint {
                color: #9AA9C3;
                background: transparent;
                font-family: "Segoe UI";
                font-size: 11px;
            }

            QProgressBar#progress {
                background: #253349;
                border: none;
                border-radius: 6px;
                height: 12px;
                color: transparent;
            }

            QProgressBar#progress::chunk {
                background: #59B7FF;
                border-radius: 6px;
            }

            QLabel#progressText {
                color: #59B7FF;
                background: transparent;
                font-family: "Segoe UI";
                font-size: 11px;
                font-weight: 700;
            }

            QFrame#scheduleOptions {
                background: #202B3F;
                border: 1px solid #34425D;
                border-radius: 10px;
            }

            QLabel#sectionLabel {
                color: #AAB6CF;
                background: transparent;
                font-family: "Segoe UI";
                font-size: 10px;
                font-weight: 700;
            }

            QLabel#scheduleSummary {
                color: #DCE5F7;
                background: transparent;
                font-family: "Segoe UI";
                font-size: 11px;
            }

            QLabel#restInfo {
                color: #E6B86A;
                background: transparent;
                font-family: "Segoe UI";
                font-size: 10px;
            }

            QSpinBox#startDelaySpin { background:#253349; color:#F4F7FF; border:1px solid #40506C; border-radius:7px; padding:5px 8px; font:9px "Segoe UI"; }
            QCheckBox#restCheck {
                color: #DCE5F7;
                background: transparent;
                spacing: 8px;
                font-family: "Segoe UI";
                font-size: 11px;
            }

            QCheckBox#restCheck::indicator,
            QCheckBox#stepCheck::indicator {
                width: 18px;
                height: 18px;
                background: #253349;
                border: 1px solid #536784;
                border-radius: 5px;
            }

            QCheckBox#restCheck::indicator:checked,
            QCheckBox#stepCheck::indicator:checked {
                background: #3E8AC4;
                border-color: #59B7FF;
            }

            QLineEdit#stepInput {
                background: #253349;
                color: #F4F7FF;
                border: 1px solid #40506C;
                border-radius: 9px;
                padding: 0 13px;
                selection-background-color: #3E8AC4;
                selection-color: white;
                font-family: "Segoe UI";
                font-size: 11px;
            }

            QLineEdit#stepInput:focus {
                border-color: #59B7FF;
            }

            QPushButton#addButton,
            QPushButton#doneButton {
                background: #3E8AC4;
                color: white;
                border: 1px solid #59B7FF;
                border-radius: 9px;
                font-family: "Segoe UI";
                font-size: 11px;
                font-weight: 600;
            }

            QPushButton#addButton:hover,
            QPushButton#doneButton:hover {
                background: #4C9CD8;
            }

            QScrollArea#stepsScroll,
            QWidget#stepsWidget {
                background: transparent;
                border: none;
            }

            QFrame#stepRow {
                background: #202B3F;
                border: 1px solid #34425D;
                border-radius: 9px;
            }

            QLabel#stepText {
                color: #DCE5F7;
                background: transparent;
                font-family: "Segoe UI";
                font-size: 11px;
                font-weight: 500;
            }

            QLabel#stepText[done="true"] {
                color: #65738D;
                text-decoration: line-through;
            }

            QLabel#stepDate {
                color: #8291AE;
                background: transparent;
                font-family: "Segoe UI";
                font-size: 10px;
            }

            QLabel#emptySteps {
                color: #71809E;
                background: transparent;
                font-family: "Segoe UI";
                font-size: 11px;
            }

            QPushButton#deleteStep {
                background: transparent;
                color: #D68087;
                border: none;
                border-radius: 6px;
                font-size: 15px;
            }

            QPushButton#deleteStep:hover {
                background: #4A2D39;
                color: white;
            }
            """
        , self))

    # =================================================================
    # DRAGGING
    # =================================================================

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            position = self.titleBar.mapFrom(
                self,
                event.position().toPoint(),
            )
            if self.titleBar.rect().contains(position):
                child = self.titleBar.childAt(position)
                if not isinstance(child, QtWidgets.QPushButton):
                    self.dragging = True
                    self.drag_position = (
                        event.globalPosition().toPoint()
                        - self.frameGeometry().topLeft()
                    )
                    event.accept()
                    return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            self.dragging
            and event.buttons() & QtCore.Qt.MouseButton.LeftButton
        ):
            self.move(
                event.globalPosition().toPoint()
                - self.drag_position
            )
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        super().mouseReleaseEvent(event)

