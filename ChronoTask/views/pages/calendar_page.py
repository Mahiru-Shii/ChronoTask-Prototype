from datetime import datetime, timedelta

from PySide6 import QtCore, QtGui, QtWidgets

from views.widgets.chrono_calendar import ChronoCalendar


class CalendarPage(QtWidgets.QWidget):
    """Calendar dashboard with deadlines, daily Chrono Step work, and rest days."""

    tasks_changed = QtCore.Signal()

    PRIORITY_COLORS = {
        (True, True): "#E06C75",
        (False, True): "#59B7FF",
        (True, False): "#E6B86A",
        (False, False): "#8A8FB8",
    }

    def __init__(self, task_controller=None, parent=None):
        super().__init__(parent)
        self.task_controller = task_controller
        self.week_offset = 0
        self.setObjectName("calendarPage")
        self._build_ui()
        self._apply_style()
        self._connect_signals()
        self.refresh()

    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 24)
        root.setSpacing(15)
        self._build_top_bar(root)
        self._build_dashboard(root)
        self._build_schedule(root)

    def _build_top_bar(self, root):
        frame = QtWidgets.QFrame(self)
        frame.setObjectName("topBarFrame")
        layout = QtWidgets.QHBoxLayout(frame)
        layout.setContentsMargins(2, 0, 2, 0)

        left = QtWidgets.QVBoxLayout()
        left.setSpacing(2)
        self.lblAppName = QtWidgets.QLabel("ChronoTask")
        self.lblAppName.setObjectName("appName")
        self.lblDate = QtWidgets.QLabel()
        self.lblDate.setObjectName("dateLabel")
        left.addWidget(self.lblAppName)
        left.addWidget(self.lblDate)
        layout.addLayout(left)
        layout.addStretch(1)

        card = QtWidgets.QFrame()
        card.setObjectName("deadlineCard")
        dl = QtWidgets.QVBoxLayout(card)
        dl.setContentsMargins(14, 8, 14, 8)
        dl.setSpacing(2)
        label = QtWidgets.QLabel("NEXT DEADLINE")
        label.setObjectName("smallLabel")
        self.lblNextDeadline = QtWidgets.QLabel("No upcoming deadlines")
        self.lblNextDeadline.setObjectName("nextDeadline")
        dl.addWidget(label)
        dl.addWidget(self.lblNextDeadline)
        layout.addWidget(card)
        root.addWidget(frame)

    def _build_dashboard(self, root):
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(15)

        calendar_card = QtWidgets.QFrame()
        calendar_card.setObjectName("calendarCard")
        calendar_layout = QtWidgets.QVBoxLayout(calendar_card)
        calendar_layout.setContentsMargins(16, 14, 16, 14)
        calendar_layout.setSpacing(10)
        heading = QtWidgets.QLabel("My Calendar")
        heading.setObjectName("sectionTitle")
        calendar_layout.addWidget(heading)
        self.calendarWidget = ChronoCalendar(calendar_card)
        calendar_layout.addWidget(self.calendarWidget, 1)
        row.addWidget(calendar_card, 3)

        self.focusCard = QtWidgets.QFrame()
        self.focusCard.setObjectName("focusCard")
        focus = QtWidgets.QVBoxLayout(self.focusCard)
        focus.setContentsMargins(18, 16, 18, 16)
        focus.setSpacing(8)

        focus_title_row = QtWidgets.QHBoxLayout()
        focus_title = QtWidgets.QLabel("Today's Focus")
        focus_title.setObjectName("sectionTitle")
        self.lblTodayCount = QtWidgets.QLabel("")
        self.lblTodayCount.setObjectName("todayCount")
        focus_title_row.addWidget(focus_title)
        focus_title_row.addStretch(1)
        focus_title_row.addWidget(self.lblTodayCount)
        focus.addLayout(focus_title_row)

        self.lblFocusTask = QtWidgets.QLabel("No task selected")
        self.lblFocusTask.setObjectName("focusTask")
        self.lblFocusTask.setWordWrap(True)
        self.lblFocusMeta = QtWidgets.QLabel("")
        self.lblFocusMeta.setObjectName("focusMeta")
        self.lblFocusMeta.setWordWrap(True)
        focus.addWidget(self.lblFocusTask)
        focus.addWidget(self.lblFocusMeta)

        self.lblChronoKHeading = QtWidgets.QLabel("CHRONO STEPS TODAY")
        self.lblChronoKHeading.setObjectName("smallLabel")
        focus.addWidget(self.lblChronoKHeading)

        self.todayStepsWidget = QtWidgets.QWidget()
        self.todayStepsLayout = QtWidgets.QVBoxLayout(self.todayStepsWidget)
        self.todayStepsLayout.setContentsMargins(0, 0, 0, 0)
        self.todayStepsLayout.setSpacing(5)
        focus.addWidget(self.todayStepsWidget)

        focus.addStretch(1)
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setObjectName("focusProgress")
        self.progressBar.setRange(0, 100)
        self.lblChronoK = QtWidgets.QLabel("")
        self.lblChronoK.setObjectName("mutedText")
        self.lblChronoK.setWordWrap(True)
        focus.addWidget(self.progressBar)
        focus.addWidget(self.lblChronoK)
        row.addWidget(self.focusCard, 2)
        root.addLayout(row, 3)

    def _build_schedule(self, root):
        panel = QtWidgets.QFrame()
        panel.setObjectName("schedulePanel")
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(12)

        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Weekly Schedule")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch(1)
        self.btnPreviousWeek = self._nav_button("‹")
        self.btnToday = self._nav_button("Today")
        self.btnNextWeek = self._nav_button("›")
        header.addWidget(self.btnPreviousWeek)
        header.addWidget(self.btnToday)
        header.addWidget(self.btnNextWeek)
        layout.addLayout(header)

        self.scheduleGridWidget = QtWidgets.QWidget()
        self.scheduleGrid = QtWidgets.QGridLayout(self.scheduleGridWidget)
        self.scheduleGrid.setContentsMargins(0, 0, 0, 0)
        self.scheduleGrid.setHorizontalSpacing(5)
        self.scheduleGrid.setVerticalSpacing(5)
        layout.addWidget(self.scheduleGridWidget)
        root.addWidget(panel, 2)

    def _nav_button(self, text):
        button = QtWidgets.QPushButton(text)
        button.setObjectName("weekButton")
        button.setMinimumHeight(30)
        button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        return button

    def _connect_signals(self):
        self.calendarWidget.selectionChanged.connect(self._calendar_selected)
        self.btnPreviousWeek.clicked.connect(lambda: self.change_week(-1))
        self.btnNextWeek.clicked.connect(lambda: self.change_week(1))
        self.btnToday.clicked.connect(self.show_current_week)

    def get_tasks(self):
        if self.task_controller is None:
            return []
        getter = getattr(self.task_controller, "get_tasks", None)
        if callable(getter):
            return list(getter())
        return list(getattr(self.task_controller, "tasks", []) or [])

    @QtCore.Slot()
    def refresh(self):
        tasks = self.get_tasks()
        self.calendarWidget.set_tasks(tasks)
        now = QtCore.QDateTime.currentDateTime()
        self.lblDate.setText(now.toString("dddd, MMMM d, yyyy  •  h:mm AP"))
        self._refresh_next_deadline(tasks)
        self._refresh_focus(tasks)
        self._refresh_schedule(tasks)

    def _refresh_next_deadline(self, tasks):
        now = datetime.now()
        future = []
        for task in tasks:
            if bool(getattr(task, "completed", False)):
                continue
            due = self._task_datetime(task)
            if due is not None and due >= now:
                future.append((due, task))
        future.sort(key=lambda item: item[0])
        if not future:
            self.lblNextDeadline.setText("No upcoming deadlines")
            return
        due, task = future[0]
        text = due.strftime("%b %d, %I:%M %p").replace(" 0", " ")
        self.lblNextDeadline.setText(f"{getattr(task, 'title', 'Untitled')}  •  {text}")

    # =================================================================
    # TODAY'S FOCUS
    # =================================================================

    def _refresh_focus(self, tasks):
        self._clear_layout(self.todayStepsLayout)
        today = datetime.now().date()
        rest_tasks = self._rest_tasks(today)
        scheduled = self._scheduled_steps(today)

        if rest_tasks and not scheduled:
            self.lblTodayCount.setText("REST DAY")
            self.lblFocusTask.setText("Recovery is part of the plan")
            self.lblFocusMeta.setText(
                "No Chrono Steps are scheduled today. Continue with the next scheduled improvement tomorrow."
            )
            self.lblChronoKHeading.setText("TODAY")
            rest = QtWidgets.QLabel("REST  •  Recharge and protect tomorrow's focus.")
            rest.setObjectName("restFocus")
            rest.setWordWrap(True)
            self.todayStepsLayout.addWidget(rest)
            self.progressBar.setValue(0)
            self.lblChronoK.setText(
                f"{len(rest_tasks)} task" + (" is" if len(rest_tasks) == 1 else "s are") + " observing a rest day."
            )
            return

        if scheduled:
            primary_task = scheduled[0][0]
            self.lblTodayCount.setText(
                f"{len(scheduled)} STEP" if len(scheduled) == 1 else f"{len(scheduled)} STEPS"
            )
            self.lblFocusTask.setText(str(getattr(primary_task, "title", "Untitled Task")))
            self.lblFocusMeta.setText(
                f"{self._priority_text(primary_task)}  •  Due {self._display_date(getattr(primary_task, 'date', ''))}"
            )
            self.lblChronoKHeading.setText("CHRONO STEPS TODAY")

            for task, step in scheduled[:5]:
                item = QtWidgets.QLabel(str(getattr(step, "description", "")))
                item.setObjectName("todayStep")
                item.setWordWrap(True)
                color = self._priority_color(task)
                item.setStyleSheet(
                    f"QLabel#todayStep {{ color:#DCE5F7; background:#253349; border:none; border-left:3px solid {color}; border-radius:6px; padding:6px 8px; font:10px 'Segoe UI'; }}"
                )
                self.todayStepsLayout.addWidget(item)

            if len(scheduled) > 5:
                more = QtWidgets.QLabel(f"+ {len(scheduled) - 5} more scheduled step(s)")
                more.setObjectName("mutedText")
                self.todayStepsLayout.addWidget(more)

            progress = self._progress(primary_task)
            self.progressBar.setValue(progress)
            completed = sum(
                bool(getattr(step, "completed", False))
                for step in getattr(primary_task, "kaizen_steps", []) or []
            )
            total = len(getattr(primary_task, "kaizen_steps", []) or [])
            self.lblChronoK.setText(
                f"{completed} of {total} total Chrono Steps completed  •  {progress}%"
            )
            return

        active = [task for task in tasks if not bool(getattr(task, "completed", False))]
        if not active:
            self.lblTodayCount.setText("")
            self.lblFocusTask.setText("No task selected")
            self.lblFocusMeta.setText("Create a task to begin planning today's focus.")
            self.lblChronoKHeading.setText("CHRONO STEPS TODAY")
            empty = QtWidgets.QLabel("No Chrono Steps scheduled today.")
            empty.setObjectName("mutedText")
            self.todayStepsLayout.addWidget(empty)
            self.progressBar.setValue(0)
            self.lblChronoK.setText("ChronoK progress will appear here.")
            return

        active.sort(key=self._focus_sort_key)
        task = active[0]
        self.lblTodayCount.setText("NO STEPS TODAY")
        self.lblFocusTask.setText(str(getattr(task, "title", "Untitled Task")))
        self.lblFocusMeta.setText(
            f"{self._priority_text(task)}  •  Due {self._display_date(getattr(task, 'date', ''))}"
        )
        empty = QtWidgets.QLabel("No Chrono Step from this task is scheduled today.")
        empty.setObjectName("mutedText")
        empty.setWordWrap(True)
        self.todayStepsLayout.addWidget(empty)
        progress = self._progress(task)
        self.progressBar.setValue(progress)
        self.lblChronoK.setText(f"ChronoK progress: {progress}%")

    # =================================================================
    # WEEKLY SCHEDULE
    # =================================================================

    def _refresh_schedule(self, tasks):
        self._clear_layout(self.scheduleGrid)
        today = datetime.now().date()
        monday = today - timedelta(days=today.weekday()) + timedelta(weeks=self.week_offset)
        days = [monday + timedelta(days=i) for i in range(7)]

        for column, day in enumerate(days):
            header = QtWidgets.QLabel(day.strftime("%a\n%b %d"))
            header.setObjectName("scheduleDay")
            header.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            header.setProperty("today", day == today)
            header.setMinimumHeight(38)
            self.scheduleGrid.addWidget(header, 0, column)
            self.scheduleGrid.setColumnStretch(column, 1)

            # The day frame itself stays a fixed size. Its contents scroll.
            cell = QtWidgets.QFrame()
            cell.setObjectName("scheduleCell")
            cell.setMinimumHeight(150)
            cell.setMaximumHeight(185)
            cell_layout = QtWidgets.QVBoxLayout(cell)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            cell_layout.setSpacing(0)

            day_scroll = QtWidgets.QScrollArea(cell)
            day_scroll.setObjectName("dayScheduleScroll")
            day_scroll.setWidgetResizable(True)
            day_scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
            day_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            day_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)

            day_content = QtWidgets.QWidget()
            day_content.setObjectName("dayScheduleContent")
            layout = QtWidgets.QVBoxLayout(day_content)
            layout.setContentsMargins(6, 7, 6, 7)
            layout.setSpacing(6)

            rest_tasks = self._rest_tasks(day)
            kaizen_steps = self._scheduled_steps(day)
            deadline_tasks = [
                task for task in tasks
                if not bool(getattr(task, "completed", False))
                and self._task_date(task) == day
            ]

            if rest_tasks:
                rest = QtWidgets.QLabel("REST DAY")
                rest.setObjectName("scheduleRest")
                rest.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                rest.setMinimumHeight(30)
                layout.addWidget(rest)

            # Interactive Chrono Steps. Checking one completes only that step.
            for task, step in kaizen_steps:
                description = str(getattr(step, "description", ""))
                event = self._schedule_checkbox(
                    title="CHRONOK",
                    text=description,
                    color=self._priority_color(task),
                    checked=bool(getattr(step, "completed", False)),
                )
                event.setToolTip(description)
                event.toggled.connect(
                    lambda checked, current_task=task, current_step=step:
                    self._set_weekly_step_completed(
                        current_task,
                        current_step,
                        checked,
                    )
                )
                layout.addWidget(event)

            # Interactive deadlines. Checking one completes the whole task.
            for task in deadline_tasks:
                title = str(getattr(task, "title", "Untitled"))
                deadline = self._schedule_checkbox(
                    title=f"DEADLINE {self._display_time(getattr(task, 'time', ''))}",
                    text=title,
                    color=self._priority_color(task),
                    checked=bool(getattr(task, "completed", False)),
                )
                deadline.setToolTip(title)
                deadline.toggled.connect(
                    lambda checked, current_task=task:
                    self._set_weekly_task_completed(current_task, checked)
                )
                layout.addWidget(deadline)

            if not rest_tasks and not kaizen_steps and not deadline_tasks:
                blank = QtWidgets.QLabel("No tasks")
                blank.setObjectName("scheduleEmpty")
                blank.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                blank.setMinimumHeight(40)
                layout.addWidget(blank)

            layout.addStretch(1)
            day_scroll.setWidget(day_content)
            cell_layout.addWidget(day_scroll)
            self.scheduleGrid.addWidget(cell, 1, column)

    def _schedule_checkbox(self, title, text, color, checked=False):
        checkbox = QtWidgets.QCheckBox()
        checkbox.setObjectName("scheduleCheck")
        checkbox.setText(f"{title}\n{text}")
        checkbox.setChecked(checked)
        checkbox.setMinimumHeight(52)
        checkbox.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        checkbox.setStyleSheet(
            f"""
            QCheckBox#scheduleCheck {{
                color: #F4F7FF;
                background: #253349;
                border: none;
                border-left: 3px solid {color};
                border-radius: 6px;
                padding: 6px 7px;
                spacing: 8px;
                font: 600 10px "Segoe UI";
            }}
            QCheckBox#scheduleCheck:hover {{
                background: #2B3A53;
            }}
            QCheckBox#scheduleCheck::indicator {{
                width: 17px;
                height: 17px;
                background: #182133;
                border: 1px solid #71809E;
                border-radius: 5px;
            }}
            QCheckBox#scheduleCheck::indicator:hover {{
                border-color: {color};
            }}
            QCheckBox#scheduleCheck::indicator:checked {{
                background: {color};
                border-color: {color};
            }}
            """
        )
        return checkbox

    def _set_weekly_step_completed(self, task, step, completed):
        method = getattr(
            self.task_controller,
            "set_kaizen_step_completed",
            None,
        )
        if callable(method):
            try:
                method(task, step, completed)
            except ValueError:
                return
        else:
            step.completed = bool(completed)

        self._refresh_after_weekly_change()

    def _set_weekly_task_completed(self, task, completed):
        method = getattr(self.task_controller, "set_task_completed", None)
        if callable(method):
            try:
                method(task, completed)
            except ValueError:
                return
        else:
            task.completed = bool(completed)

        reschedule = getattr(self.task_controller, "reschedule_all_kaizen", None)
        if callable(reschedule):
            reschedule()

        self._refresh_after_weekly_change()

    def _refresh_after_weekly_change(self):
        # Rebuild this page after the checkbox signal has finished dispatching.
        # The short delay avoids deleting the checkbox while its toggled signal
        # is still executing.
        self.tasks_changed.emit()
        QtCore.QTimer.singleShot(0, self.refresh)

    # =================================================================
    # SCHEDULER QUERIES
    # =================================================================

    def _scheduled_steps(self, day):
        method = getattr(self.task_controller, "get_kaizen_steps_for_date", None)
        if callable(method):
            return list(method(day))

        result = []
        key = day.isoformat()
        for task in self.get_tasks():
            if bool(getattr(task, "completed", False)):
                continue
            for step in getattr(task, "kaizen_steps", []) or []:
                if (
                    getattr(step, "scheduled_date", None) == key
                    and not bool(getattr(step, "completed", False))
                ):
                    result.append((task, step))
        result.sort(key=lambda pair: self._priority_rank(pair[0]))
        return result

    def _rest_tasks(self, day):
        method = getattr(self.task_controller, "get_tasks_resting_on_date", None)
        if callable(method):
            return list(method(day))

        key = day.isoformat()
        return [
            task for task in self.get_tasks()
            if key in (getattr(task, "rest_dates", []) or [])
            and not bool(getattr(task, "completed", False))
        ]

    # =================================================================
    # NAVIGATION
    # =================================================================

    @QtCore.Slot()
    def _calendar_selected(self):
        selected = self.calendarWidget.selectedDate()
        selected_day = datetime(selected.year(), selected.month(), selected.day()).date()
        selected_monday = selected_day - timedelta(days=selected_day.weekday())
        current = datetime.now().date()
        current_monday = current - timedelta(days=current.weekday())
        self.week_offset = (selected_monday - current_monday).days // 7
        self._refresh_schedule(self.get_tasks())

    def change_week(self, delta):
        self.week_offset += delta
        self._refresh_schedule(self.get_tasks())

    @QtCore.Slot()
    def show_current_week(self):
        self.week_offset = 0
        self.calendarWidget.setSelectedDate(QtCore.QDate.currentDate())
        self._refresh_schedule(self.get_tasks())

    # =================================================================
    # HELPERS
    # =================================================================

    @staticmethod
    def _clear_layout(layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                CalendarPage._clear_layout(child_layout)

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
        return round(
            sum(bool(getattr(s, "completed", False)) for s in steps)
            / len(steps) * 100
        )

    @staticmethod
    def _task_date(task):
        try:
            return datetime.strptime(str(getattr(task, "date", "")), "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def _task_datetime(task):
        try:
            return datetime.strptime(
                f"{getattr(task, 'date', '')} {getattr(task, 'time', '')}",
                "%Y-%m-%d %H:%M",
            )
        except ValueError:
            return None

    @staticmethod
    def _display_date(value):
        try:
            return datetime.strptime(str(value), "%Y-%m-%d").strftime("%b %d, %Y")
        except ValueError:
            return str(value) or "No deadline"

    @staticmethod
    def _display_time(value):
        try:
            return datetime.strptime(str(value), "%H:%M").strftime("%I:%M %p").lstrip("0")
        except ValueError:
            return str(value)

    @staticmethod
    def _priority_text(task):
        urgent = bool(getattr(task, "isUrgent", False))
        important = bool(getattr(task, "isImportant", False))
        if urgent and important:
            return "Urgent + Important"
        if important:
            return "Not Urgent + Important"
        if urgent:
            return "Urgent + Not Important"
        return "Not Urgent + Not Important"

    @staticmethod
    def _priority_rank(task):
        urgent = bool(getattr(task, "isUrgent", False))
        important = bool(getattr(task, "isImportant", False))
        if urgent and important:
            return 0
        if important:
            return 1
        if urgent:
            return 2
        return 3

    def _priority_color(self, task):
        return self.PRIORITY_COLORS[
            (
                bool(getattr(task, "isUrgent", False)),
                bool(getattr(task, "isImportant", False)),
            )
        ]

    def _focus_sort_key(self, task):
        return (
            self._priority_rank(task),
            self._task_datetime(task) or datetime.max,
        )

    # =================================================================
    # STYLE
    # =================================================================

    def _apply_style(self):
        self.setStyleSheet("""
            QWidget#calendarPage { background-color:#151D2B; }
            QFrame#topBarFrame { background:transparent; border:none; }
            QLabel#appName { color:#F4F7FF; font:700 20px "Segoe UI"; background:transparent; }
            QLabel#dateLabel, QLabel#mutedText { color:#8291AE; font:9px "Segoe UI"; background:transparent; }
            QLabel#smallLabel { color:#71809E; font:700 8px "Segoe UI"; background:transparent; }
            QLabel#nextDeadline { color:#DCE5F7; font:600 10px "Segoe UI"; background:transparent; }
            QFrame#deadlineCard, QFrame#calendarCard, QFrame#focusCard, QFrame#schedulePanel {
                background-color:#1B2536; border:1px solid #34425D; border-radius:14px;
            }
            QLabel#sectionTitle { color:#F4F7FF; font:700 14px "Segoe UI"; background:transparent; }
            QLabel#todayCount { color:#59B7FF; font:700 9px "Segoe UI"; background:transparent; }
            QLabel#focusTask { color:#F4F7FF; font:600 13px "Segoe UI"; background:transparent; }
            QLabel#focusMeta { color:#9AA9C3; font:10px "Segoe UI"; background:transparent; }
            QLabel#restFocus { color:#60C6B2; background:#203A3B; border:1px solid #36706A; border-radius:7px; padding:8px; font:600 10px "Segoe UI"; }
            QProgressBar#focusProgress { background:#253349; border:none; border-radius:5px; height:10px; color:transparent; }
            QProgressBar#focusProgress::chunk { background:#3E8AC4; border-radius:5px; }
            QPushButton#weekButton { background:#253349; color:#AAB6CF; border:1px solid #34425D; border-radius:7px; padding:4px 10px; font:600 9px "Segoe UI"; }
            QPushButton#weekButton:hover { background:#31425D; color:white; }
            QLabel#scheduleDay { color:#8A9AB7; background:transparent; font:600 9px "Segoe UI"; padding:5px; }
            QLabel#scheduleDay[today="true"] { color:#59B7FF; }
            QFrame#scheduleCell { background:#202B3F; border:1px solid #2E3A52; border-radius:9px; min-height:100px; }
            QLabel#scheduleRest { color:#182133; background:#60C6B2; border:none; border-radius:5px; padding:4px; font:700 8px "Segoe UI"; }
            QLabel#scheduleEmpty { color:#536078; background:transparent; font:8px "Segoe UI"; }
            QLabel#scheduleMore { color:#59B7FF; background:transparent; font:600 9px "Segoe UI"; }
            QScrollArea#dayScheduleScroll, QWidget#dayScheduleContent {
                background: transparent;
                border: none;
            }
            QScrollArea#dayScheduleScroll QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 3px 1px;
            }
            QScrollArea#dayScheduleScroll QScrollBar::handle:vertical {
                background: #536784;
                min-height: 24px;
                border-radius: 3px;
            }
            QScrollArea#dayScheduleScroll QScrollBar::add-line:vertical,
            QScrollArea#dayScheduleScroll QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)