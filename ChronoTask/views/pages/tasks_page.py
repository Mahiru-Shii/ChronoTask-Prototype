from datetime import datetime

from PySide6 import QtCore, QtGui, QtWidgets

from models.task import Task
from views.dialogs.confirm_dialog import ConfirmDialog
from views.dialogs.chronok_dialog import ChronoKDialog
from views.dialogs.task_dialog import TaskDialog
from views.widgets.task_card import TaskCard


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


class TasksPage(QtWidgets.QWidget):
    """ChronoTask Tasks page with Stage 1 task functionality."""

    FILTER_ALL = "all"
    FILTER_TODAY = "today"
    FILTER_UPCOMING = "upcoming"
    FILTER_COMPLETED = "completed"

    tasks_changed = QtCore.Signal()
    chrono_step_completed = QtCore.Signal(object)

    def __init__(self, task_controller, database=None, parent=None):
        super().__init__(parent)
        self.task_controller = task_controller
        self.database = database
        self.current_filter = self.FILTER_ALL
        self.filter_buttons = {}
        self.task_cards = []
        self.setObjectName("tasksPage")
        self._build_ui()
        self._apply_style()
        self._connect_signals()
        self.set_filter(self.FILTER_ALL)
        self.refresh_tasks()

    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        header = QtWidgets.QHBoxLayout()
        heading_box = QtWidgets.QVBoxLayout()
        heading_box.setSpacing(3)

        self.lblTitle = QtWidgets.QLabel("All Tasks")
        self.lblTitle.setObjectName("tasksTitle")
        self.lblSubtitle = QtWidgets.QLabel("Organize work by deadline and priority.")
        self.lblSubtitle.setObjectName("tasksSubtitle")
        heading_box.addWidget(self.lblTitle)
        heading_box.addWidget(self.lblSubtitle)
        header.addLayout(heading_box)
        header.addStretch(1)

        self.btnAddTask = QtWidgets.QPushButton("+ Add Task")
        self.btnAddTask.setObjectName("addTaskButton")
        self.btnAddTask.setMinimumSize(112, 40)
        self.btnAddTask.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        header.addWidget(self.btnAddTask)
        root.addLayout(header)

        controls = QtWidgets.QHBoxLayout()
        controls.setSpacing(10)
        self.txtSearch = QtWidgets.QLineEdit()
        self.txtSearch.setObjectName("taskSearch")
        self.txtSearch.setPlaceholderText("Search tasks...")
        self.txtSearch.setClearButtonEnabled(True)
        self.txtSearch.setMinimumHeight(40)
        controls.addWidget(self.txtSearch, 1)

        for title, key in (
            ("All", self.FILTER_ALL),
            ("Today", self.FILTER_TODAY),
            ("Upcoming", self.FILTER_UPCOMING),
            ("Completed", self.FILTER_COMPLETED),
        ):
            button = QtWidgets.QPushButton(title)
            button.setObjectName("filterButton")
            button.setCheckable(True)
            button.setMinimumHeight(36)
            button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            self.filter_buttons[key] = button
            controls.addWidget(button)
        root.addLayout(controls)

        summary = QtWidgets.QHBoxLayout()
        self.lblTaskCount = QtWidgets.QLabel("0 tasks")
        self.lblTaskCount.setObjectName("taskCount")
        self.lblTaskProgress = QtWidgets.QLabel("0 completed • 0 remaining")
        self.lblTaskProgress.setObjectName("taskProgress")
        summary.addWidget(self.lblTaskCount)
        summary.addStretch(1)
        summary.addWidget(self.lblTaskProgress)
        root.addLayout(summary)

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setObjectName("tasksScrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

        self.scrollContent = QtWidgets.QWidget()
        self.scrollContent.setObjectName("tasksScrollContent")
        self.tasksLayout = QtWidgets.QVBoxLayout(self.scrollContent)
        self.tasksLayout.setContentsMargins(0, 0, 4, 0)
        self.tasksLayout.setSpacing(10)

        self.emptyState = QtWidgets.QFrame()
        self.emptyState.setObjectName("emptyState")
        self.emptyState.setMinimumHeight(145)

        empty_layout = QtWidgets.QVBoxLayout(self.emptyState)
        empty_layout.setContentsMargins(28, 30, 28, 30)
        empty_layout.setSpacing(8)
        empty_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.lblEmptyTitle = QtWidgets.QLabel("No tasks here yet")
        self.lblEmptyTitle.setObjectName("emptyTitle")
        self.lblEmptyTitle.setMinimumHeight(26)
        self.lblEmptyTitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lblEmptyTitle.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )

        self.lblEmptyText = QtWidgets.QLabel(
            "Create a task or change the current filter."
        )
        self.lblEmptyText.setObjectName("emptyText")
        self.lblEmptyText.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lblEmptyText.setWordWrap(False)
        self.lblEmptyText.setMinimumWidth(390)
        self.lblEmptyText.setMaximumWidth(600)
        self.lblEmptyText.setMinimumHeight(30)
        self.lblEmptyText.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )

        empty_layout.addWidget(
            self.lblEmptyTitle, 0, QtCore.Qt.AlignmentFlag.AlignHCenter
        )
        empty_layout.addWidget(
            self.lblEmptyText, 0, QtCore.Qt.AlignmentFlag.AlignHCenter
        )
        self.tasksLayout.addWidget(self.emptyState)
        self.tasksLayout.addStretch(1)

        self.scrollArea.setWidget(self.scrollContent)
        root.addWidget(self.scrollArea, 1)

    def _connect_signals(self):
        self.btnAddTask.clicked.connect(self.open_add_task)
        self.txtSearch.textChanged.connect(self.refresh_tasks)
        for key, button in self.filter_buttons.items():
            button.clicked.connect(lambda checked=False, value=key: self.set_filter(value))

    def get_tasks(self):
        tasks = getattr(self.task_controller, "tasks", None)
        return tasks if isinstance(tasks, list) else []

    def set_filter(self, filter_name):
        self.current_filter = filter_name
        for key, button in self.filter_buttons.items():
            button.blockSignals(True)
            button.setChecked(key == filter_name)
            button.blockSignals(False)
        self.refresh_tasks()

    @QtCore.Slot()
    def open_add_task(self):
        dialog = TaskDialog(self, database=self.database)
        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return
        data = dialog.get_task_data()
        urgent, important = self.priority_to_flags(data["priority"])
        task = self.task_controller.add_task(
            title=data["name"],
            description=data["description"],
            date=data["date"].toString("yyyy-MM-dd"),
            time=data["time"].toString("HH:mm"),
            is_urgent=urgent,
            is_important=important,
            include_rest_day=data.get("include_rest_day", False),
            start_delay_days=data.get("start_delay_days", 0),
        )
        if data.get("use_kaizen"):
            self.task_controller.create_kaizen_steps(task, data.get("kaizen_steps", []))
        self.task_controller.reschedule_all_kaizen()
        self.refresh_tasks(); self.tasks_changed.emit()

    @QtCore.Slot(object)
    def edit_task(self, task):
        dialog = TaskDialog(self, task=task, database=self.database)
        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return
        data = dialog.get_task_data()
        urgent, important = self.priority_to_flags(data["priority"])
        self.task_controller.update_task(
            task, title=data["name"], description=data["description"],
            date=data["date"].toString("yyyy-MM-dd"),
            time=data["time"].toString("HH:mm"),
            is_urgent=urgent, is_important=important,
            include_rest_day=data.get("include_rest_day", False),
            start_delay_days=data.get("start_delay_days", 0),
        )
        descriptions = data.get("kaizen_steps", []) if data.get("use_kaizen") else []
        self._sync_chrono_steps(task, descriptions)
        self.task_controller.reschedule_all_kaizen()
        self.refresh_tasks(); self.tasks_changed.emit()

    def _sync_chrono_steps(self, task, descriptions):
        descriptions=[str(x).strip() for x in descriptions if str(x).strip()]
        existing=list(task.kaizen_steps)
        common=min(len(existing),len(descriptions))
        for i in range(common): self.task_controller.update_kaizen_step(task, existing[i], descriptions[i])
        for step in list(existing[len(descriptions):]): self.task_controller.delete_kaizen_step(task, step)
        for text in descriptions[len(existing):]: self.task_controller.add_kaizen_step(task, text)
        self.task_controller.schedule_kaizen_steps(task)

    @QtCore.Slot(object)
    def open_chronok_plan(self, task):
        dialog=ChronoKDialog(task, self.task_controller, self)
        dialog.steps_changed.connect(self._chronok_changed)
        dialog.step_completed.connect(self.chrono_step_completed.emit)
        dialog.exec()
        self.refresh_tasks(); self.tasks_changed.emit()

    @QtCore.Slot()
    def _chronok_changed(self):
        self.refresh_tasks(); self.tasks_changed.emit()

    @QtCore.Slot(object)
    def delete_task(self, task):
        task_title = str(getattr(task, "title", "this task"))

        dialog = ConfirmDialog(
            parent=self,
            title="Delete task",
            message=f'Delete "{task_title}"?',
            detail=(
                "This task, its Chrono Steps, and its scheduled work "
                "will be permanently removed."
            ),
            confirm_text="Delete",
            cancel_text="Cancel",
        )

        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return

        delete_method = getattr(self.task_controller, "delete_task", None)
        if callable(delete_method):
            try:
                delete_method(task)
            except ValueError:
                return
        else:
            tasks = getattr(self.task_controller, "tasks", [])
            if task in tasks:
                tasks.remove(task)

        reschedule = getattr(
            self.task_controller,
            "reschedule_all_kaizen",
            None,
        )
        if callable(reschedule):
            reschedule()

        self.refresh_tasks()
        self.tasks_changed.emit()

    @QtCore.Slot(object, bool)
    def set_task_completed(self, task, completed):
        self.task_controller.set_task_completed(task, completed)
        self.refresh_tasks()
        self.tasks_changed.emit()

    @staticmethod
    def priority_to_flags(priority):
        return {
            "Urgent + Important": (True, True),
            "Not Urgent + Important": (False, True),
            "Urgent + Not Important": (True, False),
            "Not Urgent + Not Important": (False, False),
        }.get(priority, (False, False))

    def _matches_search(self, task):
        query = self.txtSearch.text().strip().lower()
        if not query:
            return True
        title = str(getattr(task, "title", "")).lower()
        description = str(getattr(task, "description", "")).lower()
        return query in title or query in description

    def _matches_filter(self, task):
        completed = bool(getattr(task, "completed", False))
        if self.current_filter == self.FILTER_COMPLETED:
            return completed
        if completed and self.current_filter in (self.FILTER_TODAY, self.FILTER_UPCOMING):
            return False
        if self.current_filter == self.FILTER_ALL:
            return True

        task_date = self._task_date(task)
        if task_date is None:
            return False
        today = datetime.now().date()
        if self.current_filter == self.FILTER_TODAY:
            return task_date == today
        if self.current_filter == self.FILTER_UPCOMING:
            return task_date > today
        return True

    @staticmethod
    def _task_date(task):
        try:
            return datetime.strptime(str(getattr(task, "date", "")), "%Y-%m-%d").date()
        except ValueError:
            return None

    @QtCore.Slot()
    def refresh_tasks(self):
        self._clear_cards()
        all_tasks = self.get_tasks()
        visible = [
            task for task in all_tasks
            if self._matches_search(task) and self._matches_filter(task)
        ]

        for task in visible:
            card = TaskCard(task, self.scrollContent)
            card.completion_changed.connect(self.set_task_completed)
            if hasattr(card, "kaizen_requested"):
                card.kaizen_requested.connect(self.open_chronok_plan)
            card.edit_requested.connect(self.edit_task)
            card.delete_requested.connect(self.delete_task)
            self.tasksLayout.insertWidget(self.tasksLayout.count() - 1, card)
            self.task_cards.append(card)

        self.emptyState.setVisible(len(visible) == 0)
        self._update_summary(all_tasks)

    def _clear_cards(self):
        for card in self.task_cards:
            self.tasksLayout.removeWidget(card)
            card.deleteLater()
        self.task_cards.clear()

    def _update_summary(self, tasks):
        total = len(tasks)
        completed = sum(bool(getattr(task, "completed", False)) for task in tasks)
        remaining = total - completed
        self.lblTaskCount.setText(f"{total} task" if total == 1 else f"{total} tasks")
        self.lblTaskProgress.setText(f"{completed} completed • {remaining} remaining")

    def _apply_style(self):
        self.setStyleSheet(_theme_style(
            """
            QWidget#tasksPage, QWidget#tasksScrollContent {
                background-color: #151D2B;
            }
            QLabel#tasksTitle {
                color: #F4F7FF; font: 700 22px "Segoe UI"; background: transparent;
            }
            QLabel#tasksSubtitle, QLabel#taskProgress {
                color: #8291AE; font: 10px "Segoe UI"; background: transparent;
            }
            QLabel#taskCount {
                color: #DCE5F7; font: 600 10px "Segoe UI"; background: transparent;
            }
            QPushButton#addTaskButton {
                background-color: #3E8AC4; color: white; border: 1px solid #59B7FF;
                border-radius: 10px; padding: 0 16px; font: 600 10px "Segoe UI";
            }
            QPushButton#addTaskButton:hover { background-color: #4C9CD8; }
            QLineEdit#taskSearch {
                background-color: #202B3F; color: #F4F7FF; border: 1px solid #34425D;
                border-radius: 10px; padding: 0 13px; font: 10px "Segoe UI";
                selection-background-color: #3E8AC4; selection-color: white;
            }
            QLineEdit#taskSearch:focus { border-color: #59B7FF; }
            QPushButton#filterButton {
                background-color: #202B3F; color: #8A9AB7; border: 1px solid #34425D;
                border-radius: 9px; padding: 0 13px; font: 600 9px "Segoe UI";
            }
            QPushButton#filterButton:hover { background-color: #253349; color: #DCE5F7; }
            QPushButton#filterButton:checked {
                background-color: #31425D; color: #FFFFFF; border-color: #536784;
            }
            QScrollArea#tasksScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                background: transparent; width: 9px; margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: #40506C; min-height: 30px; border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            QFrame#emptyState {
                background-color: #1B2536; border: 1px dashed #34425D; border-radius: 12px;
            }
            QLabel#emptyTitle {
                color: #DCE5F7; background: transparent; font: 600 12px "Segoe UI";
            }
            QLabel#emptyText {
                color: #8291AE;
                background: transparent;
                border: none;
                font: 10px "Segoe UI";
                padding: 2px 8px;
            }
            """
        , self))