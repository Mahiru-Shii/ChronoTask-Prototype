from datetime import date, datetime, timedelta
from PySide6 import QtCore

from models.kaizen_step import KaizenStep
from models.task import Task


class TaskController(QtCore.QObject):
    chrono_step_completed = QtCore.Signal(object, object)
    task_completed = QtCore.Signal(object)
    """Task/ChronoK business logic with optional SQLite persistence."""

    def __init__(self, repository=None):
        super().__init__()
        self.repository = repository
        if repository is not None:
            self._tasks = repository.load_tasks()
            loader = getattr(repository, "load_manual_rest_days", None)
            self._manual_rest_days = set(loader() if callable(loader) else [])
        else:
            self._tasks = []
            self._manual_rest_days = set()

    @property
    def tasks(self):
        return self._tasks

    def get_tasks(self):
        return list(self._tasks)

    def get_active_tasks(self):
        return [task for task in self._tasks if not task.completed]

    def get_overdue_tasks(self):
        """Return incomplete tasks whose deadline date/time has passed."""
        return [task for task in self._tasks if bool(getattr(task, "is_overdue", False))]

    def _require_task(self, task):
        if task not in self._tasks:
            raise ValueError("Task does not belong to this controller.")

    def _save_task_graph(self, task):
        if self.repository is not None:
            self.repository.save_task_graph(task)

    def _save_all(self):
        if self.repository is not None:
            for task in self._tasks:
                self.repository.save_task_graph(task)

    # -----------------------------------------------------------------
    # Task CRUD
    # -----------------------------------------------------------------

    def add_task(self, title, description, date, time, is_urgent, is_important,
                 created_date=None, include_rest_day=False, start_delay_days=0):
        task = Task(
            title, description, date, time, is_urgent, is_important,
            created_date=created_date,
            include_rest_day=include_rest_day,
            start_delay_days=start_delay_days,
        )
        self._tasks.append(task)
        self._save_task_graph(task)
        return task

    create_task = add_task

    def update_task(self, task, title=None, description=None, date=None, time=None,
                    is_urgent=None, is_important=None, include_rest_day=None,
                    start_delay_days=None):
        self._require_task(task)
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if date is not None:
            task.date = date
        if time is not None:
            task.time = time
        if is_urgent is not None or is_important is not None:
            task.set_priority(
                task.isUrgent if is_urgent is None else is_urgent,
                task.isImportant if is_important is None else is_important,
            )
        if include_rest_day is not None:
            task.include_rest_day = include_rest_day
        if start_delay_days is not None:
            task.start_delay_days = start_delay_days

        self.schedule_kaizen_steps(task)
        self._save_task_graph(task)
        return task

    def delete_task(self, task):
        self._require_task(task)
        if self.repository is not None and task.is_persisted:
            self.repository.delete_task(task)
        self._tasks.remove(task)
        self.reschedule_all_kaizen()
        return True

    def set_task_completed(self, task, completed=True):
        self._require_task(task)
        was_completed = bool(getattr(task, "completed", False))
        if completed:
            task.mark_completed()
        else:
            task.mark_active()
        self._save_task_graph(task)
        if completed and not was_completed:
            self.task_completed.emit(task)
        return task

    # -----------------------------------------------------------------
    # Priority
    # -----------------------------------------------------------------

    @staticmethod
    def priority_rank(task):
        if task.isUrgent and task.isImportant:
            return 0
        if task.isImportant:
            return 1
        if task.isUrgent:
            return 2
        return 3

    # -----------------------------------------------------------------
    # Chrono Steps (internal method names retained for compatibility)
    # -----------------------------------------------------------------

    def create_kaizen_steps(self, task, descriptions):
        self._require_task(task)
        created = []
        for value in descriptions:
            text = str(value).strip()
            if text:
                step = KaizenStep(text)
                task.add_kaizen_step(step)
                created.append(step)
        self.schedule_kaizen_steps(task)
        self._save_task_graph(task)
        return created

    def add_kaizen_step(self, task, description):
        self._require_task(task)
        step = KaizenStep(description)
        task.add_kaizen_step(step)
        self.schedule_kaizen_steps(task)
        self._save_task_graph(task)
        return step

    def update_kaizen_step(self, task, step, description):
        self._require_task(task)
        if step not in task.kaizen_steps:
            raise ValueError("Chrono Step does not belong to this task.")
        step.description = description
        self._save_task_graph(task)
        return step

    def delete_kaizen_step(self, task, step):
        self._require_task(task)
        if step not in task.kaizen_steps:
            raise ValueError("Chrono Step does not belong to this task.")
        task.remove_kaizen_step(step)
        self.schedule_kaizen_steps(task)
        self._save_task_graph(task)
        return True

    def set_kaizen_step_completed(self, task, step, completed=True):
        self._require_task(task)
        if step not in task.kaizen_steps:
            raise ValueError("Chrono Step does not belong to this task.")
        was_completed = bool(getattr(step, "completed", False))
        if completed:
            step.mark_completed()
        else:
            step.mark_active()
        self._save_task_graph(task)
        if completed and not was_completed:
            self.chrono_step_completed.emit(task, step)
        return step

    def get_progress(self, task):
        self._require_task(task)
        return task.kaizen_progress

    # -----------------------------------------------------------------
    # Scheduler
    # -----------------------------------------------------------------

    def schedule_kaizen_steps(self, task, persist=True):
        self._require_task(task)
        steps = list(task.kaizen_steps)
        if not steps:
            task.clear_rest_dates()
            if persist:
                self._save_task_graph(task)
            return {}

        start = self._normalize_date(task.created_date) or date.today()
        deadline = self._normalize_date(task.date)
        if deadline is None:
            return {}
        if deadline < start:
            start = deadline

        max_delay = max(0, (deadline - start).days)
        delay = min(max(0, int(getattr(task, "start_delay_days", 0))), max_delay)
        start = start + timedelta(days=delay)
        days = self._date_range(start, deadline) or [deadline]
        external_rest = self.get_rest_dates(exclude_task=task)
        task.clear_rest_dates()
        own_rest = set()

        if task.include_rest_day and len(days) >= 3:
            interior = [day for day in days[1:-1] if day not in external_rest]
            if interior:
                rest = interior[len(interior) // 2]
                task.add_rest_date(rest.isoformat())
                own_rest.add(rest)

        work_days = [day for day in days if day not in external_rest | own_rest]
        if not work_days:
            work_days = [deadline]

        base, extra = divmod(len(steps), len(work_days))
        index = 0
        result = {}

        for step in steps:
            step.unschedule()

        for day_index, work_day in enumerate(work_days):
            amount = base + (1 if day_index < extra else 0)
            batch = steps[index:index + amount]
            index += amount
            if not batch:
                continue
            result[work_day] = batch
            for step in batch:
                step.schedule_for(work_day.isoformat())

        if persist:
            self._save_task_graph(task)
        return {day.isoformat(): values for day, values in result.items()}

    def reschedule_all_kaizen(self):
        active = sorted(
            self.get_active_tasks(),
            key=lambda task: (
                self.priority_rank(task),
                self._normalize_date(task.date) or date.max,
            ),
        )
        for task in active:
            task.clear_rest_dates()
        for task in active:
            self.schedule_kaizen_steps(task, persist=False)
        self._save_all()

    # -----------------------------------------------------------------
    # Manual / global rest days
    # -----------------------------------------------------------------
    def get_manual_rest_days(self):
        result = set()
        for value in self._manual_rest_days:
            parsed = self._normalize_date(value)
            if parsed is not None: result.add(parsed)
        return result

    def is_manual_rest_day(self, value):
        target = self._normalize_date(value)
        return target is not None and target.isoformat() in self._manual_rest_days

    def add_manual_rest_day(self, value):
        target = self._normalize_date(value)
        if target is None: raise ValueError("Invalid rest day.")
        key = target.isoformat()
        if key in self._manual_rest_days: return False
        self._manual_rest_days.add(key)
        method = getattr(self.repository, "add_manual_rest_day", None) if self.repository else None
        if callable(method): method(key)
        self.reschedule_all_kaizen()
        return True

    def remove_manual_rest_day(self, value):
        target = self._normalize_date(value)
        if target is None: raise ValueError("Invalid rest day.")
        key = target.isoformat()
        if key not in self._manual_rest_days: return False
        self._manual_rest_days.remove(key)
        method = getattr(self.repository, "remove_manual_rest_day", None) if self.repository else None
        if callable(method): method(key)
        self.reschedule_all_kaizen()
        return True

    def toggle_manual_rest_day(self, value):
        if self.is_manual_rest_day(value):
            self.remove_manual_rest_day(value); return False
        self.add_manual_rest_day(value); return True

    # -----------------------------------------------------------------
    # Queries used by Calendar / Weekly Schedule
    # -----------------------------------------------------------------

    def get_rest_dates(self, exclude_task=None):
        result = self.get_manual_rest_days()
        for task in self.get_active_tasks():
            if task is exclude_task:
                continue
            for value in task.rest_dates:
                parsed = self._normalize_date(value)
                if parsed is not None:
                    result.add(parsed)
        return result

    def get_tasks_resting_on_date(self, value):
        target = self._normalize_date(value)
        if target is None:
            return []
        return [
            task for task in self.get_active_tasks()
            if target in {
                self._normalize_date(rest_date)
                for rest_date in task.rest_dates
            }
        ]

    def get_kaizen_steps_for_date(self, value, include_completed=False):
        target = self._normalize_date(value)
        if target is None:
            return []
        result = []
        for task in self.get_active_tasks():
            for step in task.kaizen_steps:
                if self._normalize_date(step.scheduled_date) != target:
                    continue
                if not include_completed and step.completed:
                    continue
                result.append((task, step))
        result.sort(key=lambda pair: (self.priority_rank(pair[0]), pair[0].time))
        return result

    @staticmethod
    def _normalize_date(value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        try:
            return datetime.strptime(str(value), "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def _date_range(start, end):
        if end < start:
            return []
        return [start + timedelta(days=index) for index in range((end - start).days + 1)]
