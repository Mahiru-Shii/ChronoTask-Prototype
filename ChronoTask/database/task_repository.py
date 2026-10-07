from models.kaizen_step import KaizenStep
from models.task import Task


class TaskRepository:
    """Persistence boundary between TaskController and SQLite."""

    def __init__(self, database):
        self.database = database
        self.database.create_tables()

    @property
    def connection(self):
        return self.database.connect()

    def load_tasks(self):
        tasks = []
        rows = self.connection.execute(
            "SELECT * FROM tasks ORDER BY id"
        ).fetchall()

        for row in rows:
            task = Task(
                row["title"],
                row["description"],
                row["deadline_date"],
                row["deadline_time"],
                bool(row["is_urgent"]),
                bool(row["is_important"]),
                created_date=row["created_date"],
                include_rest_day=bool(row["include_rest_day"]),
            )
            task.completed = bool(row["completed"])
            task.db_id = row["id"]

            step_rows = self.connection.execute(
                """
                SELECT * FROM chrono_steps
                WHERE task_id = ?
                ORDER BY position, id
                """,
                (row["id"],),
            ).fetchall()
            for step_row in step_rows:
                step = KaizenStep(
                    step_row["description"],
                    scheduled_date=step_row["scheduled_date"],
                )
                step.completed = bool(step_row["completed"])
                step.db_id = step_row["id"]
                task.add_kaizen_step(step)

            rest_rows = self.connection.execute(
                "SELECT rest_date FROM rest_dates WHERE task_id = ? ORDER BY rest_date",
                (row["id"],),
            ).fetchall()
            task.rest_dates = [item["rest_date"] for item in rest_rows]
            tasks.append(task)
        return tasks

    def insert_task(self, task):
        cursor = self.connection.execute(
            """
            INSERT INTO tasks (
                title, description, deadline_date, deadline_time,
                is_urgent, is_important, completed, created_date,
                include_rest_day
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task.title, task.description, task.date, task.time,
                int(task.isUrgent), int(task.isImportant), int(task.completed),
                task.created_date, int(task.include_rest_day),
            ),
        )
        task.db_id = cursor.lastrowid
        self.connection.commit()
        return task.db_id

    def update_task(self, task):
        task_id = self._task_id(task)
        self.connection.execute(
            """
            UPDATE tasks SET
                title = ?, description = ?, deadline_date = ?, deadline_time = ?,
                is_urgent = ?, is_important = ?, completed = ?, created_date = ?,
                include_rest_day = ?
            WHERE id = ?
            """,
            (
                task.title, task.description, task.date, task.time,
                int(task.isUrgent), int(task.isImportant), int(task.completed),
                task.created_date, int(task.include_rest_day), task_id,
            ),
        )
        self.connection.commit()

    def delete_task(self, task):
        self.connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (self._task_id(task),),
        )
        self.connection.commit()

    def insert_chrono_step(self, task, step, position=None):
        task_id = self._task_id(task)
        if position is None:
            position = len(task.kaizen_steps) - 1
        cursor = self.connection.execute(
            """
            INSERT INTO chrono_steps (
                task_id, description, completed, scheduled_date, position
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                task_id, step.description, int(step.completed),
                step.scheduled_date, int(position),
            ),
        )
        step.db_id = cursor.lastrowid
        self.connection.commit()
        return step.db_id

    def update_chrono_step(self, task, step, position=None):
        self._task_id(task)
        step_id = self._step_id(step)
        if position is None:
            position = task.kaizen_steps.index(step)
        self.connection.execute(
            """
            UPDATE chrono_steps SET
                description = ?, completed = ?, scheduled_date = ?, position = ?
            WHERE id = ?
            """,
            (step.description, int(step.completed), step.scheduled_date, position, step_id),
        )
        self.connection.commit()

    def delete_chrono_step(self, step):
        self.connection.execute(
            "DELETE FROM chrono_steps WHERE id = ?",
            (self._step_id(step),),
        )
        self.connection.commit()

    def sync_chrono_steps(self, task):
        task_id = self._task_id(task)
        persisted = self.connection.execute(
            "SELECT id FROM chrono_steps WHERE task_id = ?",
            (task_id,),
        ).fetchall()
        persisted_ids = {row["id"] for row in persisted}
        current_ids = {
            step.db_id
            for step in task.kaizen_steps
            if step.db_id is not None
        }

        for step_id in persisted_ids - current_ids:
            self.connection.execute("DELETE FROM chrono_steps WHERE id = ?", (step_id,))

        for position, step in enumerate(task.kaizen_steps):
            step_id = step.db_id
            if step_id is None:
                cursor = self.connection.execute(
                    """
                    INSERT INTO chrono_steps
                        (task_id, description, completed, scheduled_date, position)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (task_id, step.description, int(step.completed), step.scheduled_date, position),
                )
                step.db_id = cursor.lastrowid
            else:
                self.connection.execute(
                    """
                    UPDATE chrono_steps SET
                        description = ?, completed = ?, scheduled_date = ?, position = ?
                    WHERE id = ? AND task_id = ?
                    """,
                    (step.description, int(step.completed), step.scheduled_date,
                     position, step_id, task_id),
                )
        self.connection.commit()

    def replace_rest_dates(self, task):
        task_id = self._task_id(task)
        self.connection.execute("DELETE FROM rest_dates WHERE task_id = ?", (task_id,))
        self.connection.executemany(
            "INSERT INTO rest_dates (task_id, rest_date) VALUES (?, ?)",
            [(task_id, value) for value in task.rest_dates],
        )
        self.connection.commit()

    def save_task_graph(self, task):
        if task.db_id is None:
            self.insert_task(task)
        else:
            self.update_task(task)
        self.sync_chrono_steps(task)
        self.replace_rest_dates(task)

    @staticmethod
    def _task_id(task):
        value = task.db_id
        if value is None:
            raise ValueError("Task has not been persisted yet.")
        return value

    @staticmethod
    def _step_id(step):
        value = step.db_id
        if value is None:
            raise ValueError("Chrono Step has not been persisted yet.")
        return value

