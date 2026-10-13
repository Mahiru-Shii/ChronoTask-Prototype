import sys
import ctypes
from pathlib import Path

from PySide6 import QtGui, QtWidgets

from controllers.task_controller import TaskController
from database.database import Database
from database.task_repository import TaskRepository
from views.main_window import MainWindow


def _database_path():
    """Keep the SQLite database in a stable app-local data folder."""
    project_root = Path(__file__).resolve().parent
    data_dir = project_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "chronotask.db"


def main():
    """Start ChronoTask with SQLite-backed task persistence."""
    # Give ChronoTask its own Windows taskbar identity when running through python.exe.
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "ChronoTask.Desktop.1"
        )

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("ChronoTask")
    app.setOrganizationName("ChronoTask")

    logo_path = Path(__file__).resolve().parent / "assets" / "chronotask_logo.ico"
    if logo_path.is_file():
        app.setWindowIcon(QtGui.QIcon(str(logo_path)))

    database = Database(_database_path())
    database.create_tables()
    repository = TaskRepository(database)
    task_controller = TaskController(repository=repository)

    window = MainWindow(task_controller=task_controller, database=database)
    if logo_path.is_file():
        window.setWindowIcon(QtGui.QIcon(str(logo_path)))
    app.aboutToQuit.connect(database.close)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())


