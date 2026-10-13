from datetime import datetime


class KaizenStep:
    """Internal model for a user-facing Chrono Step."""

    def __init__(self, description, scheduled_date=None, db_id=None):
        self._db_id = None
        self._description = ""
        self._completed = False
        self._scheduled_date = None
        self.db_id = db_id
        self.description = description
        self.scheduled_date = scheduled_date

    @property
    def db_id(self):
        return self._db_id

    @db_id.setter
    def db_id(self, value):
        if value is None:
            self._db_id = None
            return
        if isinstance(value, bool):
            raise ValueError("Chrono Step database ID must be a positive integer or None.")
        try:
            value = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Chrono Step database ID must be a positive integer or None.") from exc
        if value <= 0:
            raise ValueError("Chrono Step database ID must be greater than zero.")
        self._db_id = value

    @property
    def is_persisted(self):
        return self._db_id is not None

    @property
    def description(self): return self._description
    @description.setter
    def description(self, value):
        value = str(value).strip()
        if not value: raise ValueError("Chrono Step description cannot be empty.")
        self._description = value

    @property
    def completed(self): return self._completed
    @completed.setter
    def completed(self, value): self._completed = bool(value)
    def mark_completed(self): self._completed = True
    def mark_active(self): self._completed = False

    @property
    def scheduled_date(self): return self._scheduled_date
    @scheduled_date.setter
    def scheduled_date(self, value):
        if value in (None, ""):
            self._scheduled_date = None; return
        text = str(value).strip()
        try: datetime.strptime(text, "%Y-%m-%d")
        except ValueError as exc: raise ValueError("Scheduled date must use YYYY-MM-DD.") from exc
        self._scheduled_date = text
    def schedule_for(self, value): self.scheduled_date = value
    def unschedule(self): self._scheduled_date = None