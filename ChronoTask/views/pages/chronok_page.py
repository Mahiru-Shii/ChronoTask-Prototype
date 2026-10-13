from PySide6 import QtCore, QtGui, QtWidgets

from views.dialogs.chronok_dialog import ChronoKDialog


class ChronoKPage(QtWidgets.QWidget):
    """Eisenhower priority matrix combined with readable ChronoK progress."""

    tasks_changed = QtCore.Signal()

    QUADRANTS = (
        (
            "urgent_important",
            "DO FIRST",
            "Urgent + Important",
            "Handle immediately, then improve through small steps.",
            "#E06C75",
        ),
        (
            "important",
            "SCHEDULE",
            "Not Urgent + Important",
            "Protect time for important work before it becomes urgent.",
            "#59B7FF",
        ),
        (
            "urgent",
            "DELEGATE",
            "Urgent + Not Important",
            "Resolve quickly and minimize repeated effort.",
            "#E6B86A",
        ),
        (
            "normal",
            "IMPROVE",
            "Not Urgent + Not Important",
            "Use ChronoK only when the task still supports a useful goal.",
            "#8A8FB8",
        ),
    )

    def __init__(self, task_controller, parent=None):
        super().__init__(parent)
        self.task_controller = task_controller
        self.quadrant_layouts = {}
        self.quadrant_counts = {}

        self.setObjectName("kaizenPage")
        self._build_ui()
        self._apply_style()
        self.refresh()

    # =================================================================
    # UI
    # =================================================================

    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        header = QtWidgets.QHBoxLayout()
        header.setSpacing(12)

        heading = QtWidgets.QVBoxLayout()
        heading.setSpacing(5)

        self.lblTitle = QtWidgets.QLabel("ChronoK Matrix", self)
        self.lblTitle.setObjectName("pageTitle")

        self.lblSubtitle = QtWidgets.QLabel(
            "Use Eisenhower priority to decide what matters, then use ChronoK to make steady daily progress.",
            self,
        )
        self.lblSubtitle.setObjectName("pageSubtitle")
        self.lblSubtitle.setWordWrap(True)

        heading.addWidget(self.lblTitle)
        heading.addWidget(self.lblSubtitle)
        header.addLayout(heading, 1)

        self.lblSummary = QtWidgets.QLabel("0 active tasks", self)
        self.lblSummary.setObjectName("summary")
        self.lblSummary.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight
            | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        header.addWidget(self.lblSummary)
        root.addLayout(header)

        matrix = QtWidgets.QGridLayout()
        matrix.setHorizontalSpacing(14)
        matrix.setVerticalSpacing(14)

        for position, data in enumerate(self.QUADRANTS):
            row, column = divmod(position, 2)
            key, action, priority, description, color = data
            panel, tasks_layout, count_label = self._build_quadrant(
                key,
                action,
                priority,
                description,
                color,
            )
            self.quadrant_layouts[key] = tasks_layout
            self.quadrant_counts[key] = count_label
            matrix.addWidget(panel, row, column)
            matrix.setRowStretch(row, 1)
            matrix.setColumnStretch(column, 1)

        root.addLayout(matrix, 1)

    def _build_quadrant(
        self,
        key,
        action,
        priority,
        description,
        color,
    ):
        panel = QtWidgets.QFrame(self)
        panel.setObjectName("quadrant")
        panel.setProperty("quadrant", key)
        panel.setStyleSheet(
            f"""
            QFrame#quadrant {{
                background-color: #1B2536;
                border: 1px solid #34425D;
                border-top: 4px solid {color};
                border-radius: 13px;
            }}
            """
        )

        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(16, 14, 16, 15)
        layout.setSpacing(9)

        top = QtWidgets.QHBoxLayout()
        top.setSpacing(8)

        action_label = QtWidgets.QLabel(action, panel)
        action_label.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                background: transparent;
                font-family: "Segoe UI";
                font-size: 12px;
                font-weight: 700;
            }}
            """
        )
        top.addWidget(action_label)
        top.addStretch(1)

        count_label = QtWidgets.QLabel("0 tasks", panel)
        count_label.setObjectName("quadrantCount")
        top.addWidget(count_label)
        layout.addLayout(top)

        priority_label = QtWidgets.QLabel(priority, panel)
        priority_label.setObjectName("quadrantPriority")
        layout.addWidget(priority_label)

        description_label = QtWidgets.QLabel(description, panel)
        description_label.setObjectName("quadrantDescription")
        description_label.setWordWrap(True)
        layout.addWidget(description_label)

        scroll = QtWidgets.QScrollArea(panel)
        scroll.setObjectName("quadrantScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

        content = QtWidgets.QWidget()
        content.setObjectName("quadrantContent")
        tasks_layout = QtWidgets.QVBoxLayout(content)
        tasks_layout.setContentsMargins(0, 5, 4, 0)
        tasks_layout.setSpacing(9)
        tasks_layout.addStretch(1)

        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
        return panel, tasks_layout, count_label

    # =================================================================
    # DATA
    # =================================================================

    def get_tasks(self):
        getter = getattr(self.task_controller, "get_tasks", None)
        if callable(getter):
            return list(getter())
        return list(getattr(self.task_controller, "tasks", []) or [])

    @QtCore.Slot()
    def refresh(self):
        for layout in self.quadrant_layouts.values():
            while layout.count() > 1:
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        active = [
            task
            for task in self.get_tasks()
            if not bool(getattr(task, "completed", False))
        ]

        self.lblSummary.setText(
            f"{len(active)} active task"
            if len(active) == 1
            else f"{len(active)} active tasks"
        )

        grouped = {key: [] for key, *_ in self.QUADRANTS}
        for task in active:
            grouped[self._priority_key(task)].append(task)

        for key, tasks in grouped.items():
            tasks.sort(key=self._task_sort_key)
            self.quadrant_counts[key].setText(
                f"{len(tasks)} task" if len(tasks) == 1 else f"{len(tasks)} tasks"
            )

            layout = self.quadrant_layouts[key]
            if not tasks:
                empty = QtWidgets.QLabel("No tasks in this quadrant")
                empty.setObjectName("emptyQuadrant")
                empty.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                empty.setMinimumHeight(90)
                layout.insertWidget(0, empty)
                continue

            for task in tasks:
                layout.insertWidget(
                    layout.count() - 1,
                    self._build_task_card(task),
                )

    # =================================================================
    # TASK CARD
    # =================================================================

    def _build_task_card(self, task):
        card = QtWidgets.QFrame(self)
        card.setObjectName("kaizenTask")
        overdue = bool(getattr(task, "is_overdue", False))
        card.setProperty("overdue", overdue)

        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(13, 11, 13, 12)
        layout.setSpacing(8)

        top = QtWidgets.QHBoxLayout()
        top.setSpacing(10)

        title = QtWidgets.QLabel(
            ("!  " if overdue else "") + str(getattr(task, "title", "Untitled Task")),
            card,
        )
        title.setObjectName("taskTitle")
        title.setWordWrap(True)
        top.addWidget(title, 1)
        if overdue:
            badge = QtWidgets.QLabel("OVERDUE", card)
            badge.setObjectName("overdueBadge")
            top.addWidget(badge)

        button = QtWidgets.QPushButton("Plan", card)
        button.setObjectName("planButton")
        button.setFixedSize(68, 32)
        button.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        button.clicked.connect(
            lambda checked=False, current=task: self.open_plan(current)
        )
        top.addWidget(button)
        layout.addLayout(top)

        steps = list(getattr(task, "kaizen_steps", []) or [])
        progress_value = self._progress(task)
        scheduled_days = len(
            {
                getattr(step, "scheduled_date", None)
                for step in steps
                if getattr(step, "scheduled_date", None)
            }
        )

        info_parts = [
            f"{len(steps)} step" if len(steps) == 1 else f"{len(steps)} steps",
            f"{progress_value}% complete",
        ]
        if scheduled_days:
            info_parts.append(
                f"{scheduled_days} scheduled day"
                if scheduled_days == 1
                else f"{scheduled_days} scheduled days"
            )
        if getattr(task, "include_rest_day", False):
            info_parts.append("rest day enabled")

        info = QtWidgets.QLabel("  •  ".join(info_parts), card)
        info.setObjectName("taskMeta")
        info.setWordWrap(True)
        layout.addWidget(info)

        progress = QtWidgets.QProgressBar(card)
        progress.setObjectName("taskProgress")
        progress.setRange(0, 100)
        progress.setValue(progress_value)
        layout.addWidget(progress)

        next_step = self._next_incomplete_step(task)
        if next_step is not None:
            description = str(getattr(next_step, "description", ""))
            scheduled_date = getattr(next_step, "scheduled_date", None)
            next_text = f"Next: {description}"
            if scheduled_date:
                next_text += f"  •  {self._short_date(scheduled_date)}"

            next_label = QtWidgets.QLabel(next_text, card)
            next_label.setObjectName("nextStep")
            next_label.setWordWrap(True)
            layout.addWidget(next_label)

        return card

    # =================================================================
    # KAIZEN PLAN
    # =================================================================

    def open_plan(self, task):
        dialog = ChronoKDialog(
            task,
            self.task_controller,
            self,
        )
        dialog.steps_changed.connect(self.refresh)
        dialog.exec()
        self.refresh()
        self.tasks_changed.emit()

    # =================================================================
    # HELPERS
    # =================================================================

    def _progress(self, task):
        method = getattr(self.task_controller, "get_progress", None)
        if callable(method):
            try:
                return method(task)
            except ValueError:
                pass

        steps = list(getattr(task, "kaizen_steps", []) or [])
        if not steps:
            return 0

        completed = sum(
            bool(getattr(step, "completed", False))
            for step in steps
        )
        return round(completed / len(steps) * 100)

    @staticmethod
    def _priority_key(task):
        urgent = bool(getattr(task, "isUrgent", False))
        important = bool(getattr(task, "isImportant", False))

        if urgent and important:
            return "urgent_important"
        if important:
            return "important"
        if urgent:
            return "urgent"
        return "normal"

    @staticmethod
    def _task_sort_key(task):
        return (
            str(getattr(task, "date", "9999-12-31")),
            str(getattr(task, "time", "23:59")),
            str(getattr(task, "title", "")).lower(),
        )

    @staticmethod
    def _next_incomplete_step(task):
        incomplete = [
            step
            for step in (getattr(task, "kaizen_steps", []) or [])
            if not bool(getattr(step, "completed", False))
        ]
        if not incomplete:
            return None

        incomplete.sort(
            key=lambda step: (
                getattr(step, "scheduled_date", None) or "9999-12-31",
                str(getattr(step, "description", "")).lower(),
            )
        )
        return incomplete[0]

    @staticmethod
    def _short_date(value):
        if not value:
            return ""
        try:
            parsed = QtCore.QDate.fromString(str(value), "yyyy-MM-dd")
            if parsed.isValid():
                return parsed.toString("MMM d")
        except (TypeError, ValueError):
            pass
        return str(value)

    # =================================================================
    # STYLE
    # =================================================================

    def _apply_style(self):
        self.setStyleSheet(
            """
            QWidget#kaizenPage {
                background-color: #151D2B;
            }

            QLabel#pageTitle {
                color: #F4F7FF;
                background: transparent;
                font-family: "Segoe UI";
                font-size: 24px;
                font-weight: 700;
            }

            QLabel#pageSubtitle {
                color: #9AA9C3;
                background: transparent;
                font-family: "Segoe UI";
                font-size: 11px;
            }

            QLabel#summary {
                color: #AAB6CF;
                background: transparent;
                font-family: "Segoe UI";
                font-size: 11px;
                font-weight: 600;
            }

            QLabel#quadrantCount {
                color: #AAB6CF;
                background: transparent;
                font-family: "Segoe UI";
                font-size: 10px;
                font-weight: 600;
            }

            QLabel#quadrantPriority {
                color: #DCE5F7;
                background: transparent;
                font-family: "Segoe UI";
                font-size: 11px;
                font-weight: 600;
            }

            QLabel#quadrantDescription {
                color: #8291AE;
                background: transparent;
                font-family: "Segoe UI";
                font-size: 10px;
            }

            QScrollArea#quadrantScroll,
            QWidget#quadrantContent {
                background: transparent;
                border: none;
            }

            QFrame#kaizenTask {
                background-color: #202B3F;
                border: 1px solid #34425D;
                border-radius: 10px;
            }

            QFrame#kaizenTask[overdue="true"] { background-color:#2B2634; border:1px solid #E06C75; }
            QLabel#overdueBadge { color:#FF8C94; background:#4B2831; border:1px solid #82404B; border-radius:6px; padding:3px 7px; font:700 8px "Segoe UI"; }
            QFrame#kaizenTask:hover {
                background-color: #243149;
                border-color: #40506C;
            }

            QLabel#taskTitle {
                color: #F4F7FF;
                background: transparent;
                font-family: "Segoe UI";
                font-size: 12px;
                font-weight: 600;
            }

            QLabel#taskMeta {
                color: #9AA9C3;
                background: transparent;
                font-family: "Segoe UI";
                font-size: 10px;
            }

            QLabel#nextStep {
                color: #DCE5F7;
                background-color: #253349;
                border: none;
                border-radius: 6px;
                padding: 6px 8px;
                font-family: "Segoe UI";
                font-size: 10px;
            }

            QLabel#emptyQuadrant {
                color: #65738D;
                background: transparent;
                font-family: "Segoe UI";
                font-size: 11px;
            }

            QPushButton#planButton {
                background-color: #253349;
                color: #DCE5F7;
                border: 1px solid #40506C;
                border-radius: 7px;
                font-family: "Segoe UI";
                font-size: 10px;
                font-weight: 600;
            }

            QPushButton#planButton:hover {
                background-color: #31425D;
                color: white;
                border-color: #59B7FF;
            }

            QProgressBar#taskProgress {
                background-color: #253349;
                border: none;
                border-radius: 5px;
                height: 9px;
                color: transparent;
            }

            QProgressBar#taskProgress::chunk {
                background-color: #59B7FF;
                border-radius: 5px;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 2px;
            }

            QScrollBar::handle:vertical {
                background: #40506C;
                min-height: 28px;
                border-radius: 4px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
            """
        )
