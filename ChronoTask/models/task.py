from datetime import date as system_date, datetime


class Task:
    """Encapsulated ChronoTask task model."""

    def __init__(self, title, description, date, time, isUrgent, isImportant,
                 created_date=None, include_rest_day=False, rest_dates=None,
                 start_delay_days=0, db_id=None):
        self._db_id = None
        self._title = ""
        self._description = ""
        self._date = ""
        self._time = ""
        self._is_urgent = False
        self._is_important = False
        self._completed = False
        self._kaizen_steps = []
        self._created_date = ""
        self._include_rest_day = False
        self._rest_dates = []
        self._start_delay_days = 0
        self.db_id = db_id
        self.title = title
        self.description = description
        self.date = date
        self.time = time
        self.isUrgent = isUrgent
        self.isImportant = isImportant
        self.created_date = created_date or system_date.today().isoformat()
        self.include_rest_day = include_rest_day
        self.rest_dates = rest_dates or []
        self.start_delay_days = start_delay_days

    @property
    def db_id(self):
        return self._db_id

    @db_id.setter
    def db_id(self, value):
        if value is None:
            self._db_id = None
            return
        if isinstance(value, bool):
            raise ValueError("Task database ID must be a positive integer or None.")
        try:
            value = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Task database ID must be a positive integer or None.") from exc
        if value <= 0:
            raise ValueError("Task database ID must be greater than zero.")
        self._db_id = value

    @property
    def is_persisted(self):
        return self._db_id is not None

    @property
    def title(self): return self._title
    @title.setter
    def title(self, value):
        value = str(value).strip()
        if not value: raise ValueError("Task title cannot be empty.")
        self._title = value

    @property
    def description(self): return self._description
    @description.setter
    def description(self, value): self._description = str(value or "").strip()

    @property
    def date(self): return self._date
    @date.setter
    def date(self, value): self._date = self._validate_date(value, "Task deadline")

    @property
    def time(self): return self._time
    @time.setter
    def time(self, value):
        text = str(value).strip()
        try: datetime.strptime(text, "%H:%M")
        except ValueError as exc: raise ValueError("Task time must use HH:MM.") from exc
        self._time = text

    @property
    def isUrgent(self): return self._is_urgent
    @isUrgent.setter
    def isUrgent(self, value): self._is_urgent = bool(value)

    @property
    def isImportant(self): return self._is_important
    @isImportant.setter
    def isImportant(self, value): self._is_important = bool(value)

    @property
    def priority(self):
        if self._is_urgent and self._is_important: return "Urgent + Important"
        if self._is_important: return "Not Urgent + Important"
        if self._is_urgent: return "Urgent + Not Important"
        return "Not Urgent + Not Important"

    def set_priority(self, urgent, important):
        self._is_urgent = bool(urgent); self._is_important = bool(important)

    @property
    def deadline_datetime(self):
        """Return the task deadline as a datetime, or None if invalid."""
        try:
            return datetime.strptime(
                f"{self._date} {self._time}",
                "%Y-%m-%d %H:%M",
            )
        except (TypeError, ValueError):
            return None

    @property
    def is_overdue(self):
        """True when an incomplete task is past its deadline."""
        if self._completed:
            return False
        deadline = self.deadline_datetime
        return deadline is not None and datetime.now() > deadline

    @property
    def completed(self): return self._completed
    @completed.setter
    def completed(self, value): self._completed = bool(value)
    def mark_completed(self): self._completed = True
    def mark_active(self): self._completed = False

    @property
    def kaizen_steps(self): return self._kaizen_steps
    def add_kaizen_step(self, step): self._kaizen_steps.append(step); return step
    def remove_kaizen_step(self, step): self._kaizen_steps.remove(step)
    def clear_kaizen_steps(self): self._kaizen_steps.clear()

    @property
    def kaizen_progress(self):
        if not self._kaizen_steps: return 0
        return round(sum(step.completed for step in self._kaizen_steps) / len(self._kaizen_steps) * 100)

    @property
    def created_date(self): return self._created_date
    @created_date.setter
    def created_date(self, value): self._created_date = self._validate_date(value, "Created date")

    @property
    def include_rest_day(self): return self._include_rest_day
    @include_rest_day.setter
    def include_rest_day(self, value): self._include_rest_day = bool(value)

    @property
    def start_delay_days(self): return self._start_delay_days
    @start_delay_days.setter
    def start_delay_days(self, value):
        if isinstance(value, bool): raise ValueError("Start delay must be a non-negative integer.")
        try: value = int(value)
        except (TypeError, ValueError) as exc: raise ValueError("Start delay must be a non-negative integer.") from exc
        if value < 0: raise ValueError("Start delay cannot be negative.")
        self._start_delay_days = value

    @property
    def rest_dates(self): return list(self._rest_dates)
    @rest_dates.setter
    def rest_dates(self, values):
        self._rest_dates = []
        for value in values or []: self.add_rest_date(value)
    def add_rest_date(self, value):
        value = self._validate_date(value, "Rest date")
        if value not in self._rest_dates: self._rest_dates.append(value); self._rest_dates.sort()
    def clear_rest_dates(self): self._rest_dates.clear()

    @staticmethod
    def _validate_date(value, label):
        text = str(value).strip()
        try: datetime.strptime(text, "%Y-%m-%d")
        except ValueError as exc: raise ValueError(f"{label} must use YYYY-MM-DD.") from exc
        return text