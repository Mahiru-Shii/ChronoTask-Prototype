from PySide6 import QtCore, QtGui, QtWidgets
from styles.main_window_style import build_main_window_style
from styles.theme_runtime import apply_widget_tree
from views.pages.calendar_page import CalendarPage
from views.pages.chronok_page import ChronoKPage
from views.pages.settings_page import SettingsPage
from views.pages.tasks_page import TasksPage
from views.sidebar import Sidebar
from views.title_bar import TitleBar


class MainWindow(QtWidgets.QMainWindow):
    """Main frameless application window for ChronoTask."""

    def __init__(self, task_controller, database=None, parent=None):
        super().__init__(parent)
        self.task_controller = task_controller
        self.database = database
        self._setup_window()
        self._build_ui()
        self.current_theme = self._saved_theme()
        self.setStyleSheet(build_main_window_style(self.current_theme))
        self._connect_navigation()
        self._connect_page_signals()
        self.apply_theme(self.current_theme)
        self.show_startup_page()

    def _setup_window(self):
        self.setObjectName("MainWindow")
        self.setWindowTitle("ChronoTask")
        self.resize(1200, 760)
        self.setMinimumSize(960, 640)
        self.setWindowFlags(QtCore.Qt.WindowType.Window | QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def _build_ui(self):
        self.centralWidget = QtWidgets.QWidget(self)
        self.centralWidget.setObjectName("centralWidget")
        self.centralWidget.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setCentralWidget(self.centralWidget)

        outer_layout = QtWidgets.QVBoxLayout(self.centralWidget)
        outer_layout.setContentsMargins(10, 10, 10, 10)
        outer_layout.setSpacing(0)

        self.windowFrame = QtWidgets.QFrame(self.centralWidget)
        self.windowFrame.setObjectName("windowFrame")
        self.windowFrame.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        outer_layout.addWidget(self.windowFrame)

        self.windowLayout = QtWidgets.QVBoxLayout(self.windowFrame)
        self.windowLayout.setContentsMargins(0, 0, 0, 0)
        self.windowLayout.setSpacing(0)

        self.titleBar = TitleBar(parent_window=self, parent=self.windowFrame)
        self.windowLayout.addWidget(self.titleBar)

        self.contentArea = QtWidgets.QWidget(self.windowFrame)
        self.contentArea.setObjectName("contentArea")
        self.contentArea.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        body_layout = QtWidgets.QHBoxLayout(self.contentArea)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        self.windowLayout.addWidget(self.contentArea, 1)

        self.sidebar = Sidebar(self.contentArea)
        body_layout.addWidget(self.sidebar)

        self.contentStack = QtWidgets.QStackedWidget(self.contentArea)
        self.contentStack.setObjectName("contentStack")
        body_layout.addWidget(self.contentStack, 1)
        self._build_pages()

    def _build_pages(self):
        self.calendarPage = CalendarPage(task_controller=self.task_controller, parent=self.contentStack)
        self.tasksPage = TasksPage(task_controller=self.task_controller, database=self.database, parent=self.contentStack)
        self.kaizenPage = ChronoKPage(task_controller=self.task_controller, parent=self.contentStack)
        self.settingsPage = SettingsPage(database=self.database, parent=self.contentStack)

        self.contentStack.addWidget(self.calendarPage)
        self.contentStack.addWidget(self.tasksPage)
        self.contentStack.addWidget(self.kaizenPage)
        self.contentStack.addWidget(self.settingsPage)

    def _connect_navigation(self):
        self.sidebar.calendar_clicked.connect(self.show_calendar_page)
        self.sidebar.tasks_clicked.connect(self.show_tasks_page)
        self.sidebar.kaizen_clicked.connect(self.show_kaizen_page)
        self.sidebar.settings_clicked.connect(self.show_settings_page)

    def _connect_page_signals(self):
        self.tasksPage.tasks_changed.connect(self.calendarPage.refresh)
        self.tasksPage.tasks_changed.connect(self.kaizenPage.refresh)
        self.kaizenPage.tasks_changed.connect(self.calendarPage.refresh)
        self.kaizenPage.tasks_changed.connect(self.tasksPage.refresh_tasks)
        self.calendarPage.add_task_requested.connect(self.tasksPage.open_add_task)
        self.calendarPage.tasks_changed.connect(self.tasksPage.refresh_tasks)
        self.calendarPage.tasks_changed.connect(self.kaizenPage.refresh)
        self.settingsPage.theme_changed.connect(self.apply_theme)

    def _saved_theme(self):
        if self.database is None:
            return "default"
        return str(self.database.get_setting("color_theme", "default")).lower()

    @QtCore.Slot(str)
    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        # Rebuild the root stylesheet from its pristine default source, then
        # translate every child stylesheet from whatever theme it currently has.
        self.setStyleSheet(build_main_window_style(theme_name))
        apply_widget_tree(self, theme_name)

    def show_startup_page(self):
        startup = "calendar"
        if self.database is not None:
            startup = str(self.database.get_setting("startup_page", "calendar")).lower()

        pages = {
            "calendar": self.show_calendar_page,
            "tasks": self.show_tasks_page,
            "chronok": self.show_kaizen_page,
        }
        pages.get(startup, self.show_calendar_page)()

    @QtCore.Slot()
    def show_calendar_page(self):
        self.calendarPage.refresh()
        self.contentStack.setCurrentWidget(self.calendarPage)
        self.sidebar.set_active_page("calendar")

    @QtCore.Slot()
    def show_tasks_page(self):
        self.tasksPage.refresh_tasks()
        self.contentStack.setCurrentWidget(self.tasksPage)
        self.sidebar.set_active_page("tasks")

    @QtCore.Slot()
    def show_kaizen_page(self):
        self.kaizenPage.refresh()
        self.contentStack.setCurrentWidget(self.kaizenPage)
        self.sidebar.set_active_page("kaizen")

    @QtCore.Slot()
    def show_settings_page(self):
        self.contentStack.setCurrentWidget(self.settingsPage)
        self.sidebar.set_active_page("settings")

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QtCore.QEvent.Type.WindowStateChange:
            self.titleBar.sync_window_state()
            QtCore.QTimer.singleShot(0, self._update_window_mask)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_window_mask()

    def showEvent(self, event):
        super().showEvent(event)
        QtCore.QTimer.singleShot(0, self._update_window_mask)

    def _update_window_mask(self):
        if not hasattr(self, "windowFrame"):
            return
        if self.isMaximized():
            self.clearMask()
            return
        frame_geometry = self.windowFrame.geometry()
        if frame_geometry.width() <= 0 or frame_geometry.height() <= 0:
            return
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(frame_geometry), 18.0, 18.0)
        self.setMask(QtGui.QRegion(path.toFillPolygon().toPolygon()))

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape and self.isMaximized():
            self.showNormal()
            self.titleBar.sync_window_state()
            QtCore.QTimer.singleShot(0, self._update_window_mask)
            event.accept()
            return

        shortcuts = {
            QtCore.Qt.Key.Key_1: self.show_calendar_page,
            QtCore.Qt.Key.Key_2: self.show_tasks_page,
            QtCore.Qt.Key.Key_3: self.show_kaizen_page,
        }
        if event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
            action = shortcuts.get(event.key())
            if action is not None:
                action()
                event.accept()
                return
        super().keyPressEvent(event)