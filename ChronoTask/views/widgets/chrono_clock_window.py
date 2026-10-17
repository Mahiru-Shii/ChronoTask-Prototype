from PySide6 import QtCore, QtGui, QtWidgets
from styles.theme import palette


class ChronoClockWindow(QtWidgets.QWidget):
    return_requested = QtCore.Signal()
    queue_completed = QtCore.Signal(object)
    geometry_changed = QtCore.Signal()
    closing = QtCore.Signal()

    def __init__(self, mode="clock", duration_seconds=0, queue=None, parent=None):
        super().__init__(parent)
        self.mode = mode
        self.remaining_seconds = max(0, int(duration_seconds))
        self.queue = list(queue or [])
        self._returning = False
        self._drag_offset = None
        self._resize_start_global = None
        self._resize_start_geometry = None
        self._resize_margin = 12
        self.resizeHandle = None
        self.setObjectName("chronoClockWindow")
        self.setWindowFlags(
            QtCore.Qt.WindowType.Window
            | QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
            | QtCore.Qt.WindowType.Tool
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.setMinimumSize(380, 135)
        self.setMaximumSize(550, 160)
        self.resize(380, 115)
        self._build_ui()
        self._tick_timer = QtCore.QTimer(self)
        self._tick_timer.timeout.connect(self._tick)
        self._tick_timer.start(250 if self.mode == "clock" else 1000)
        self._tick()
        self._apply_theme()
        self._show_front()
        self._update_adaptive_layout()

    def _build_ui(self):
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)
        self.frame = QtWidgets.QFrame(self)
        self.frame.setObjectName("clockFrame")
        self.frame.setMouseTracking(True)
        outer.addWidget(self.frame)

        layout = QtWidgets.QVBoxLayout(self.frame)
        layout.setContentsMargins(18, 5, 18, 12)
        layout.setSpacing(4)

        top = QtWidgets.QHBoxLayout()
        top.addStretch(1)
        self.closeButton = QtWidgets.QPushButton("×")
        self.closeButton.setObjectName("clockClose")
        self.closeButton.setFixedSize(22, 22)
        self.closeButton.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.closeButton.clicked.connect(self._return_to_chronotask)
        top.addWidget(self.closeButton)
        layout.addLayout(top)

        layout.addStretch(1)
        self.centerGroup = QtWidgets.QWidget(self.frame)
        self.centerGroup.setObjectName("clockCenterGroup")
        centerLayout = QtWidgets.QVBoxLayout(self.centerGroup)
        centerLayout.setContentsMargins(0, 0, 0, 0)
        centerLayout.setSpacing(3)

        self.timeLabel = QtWidgets.QLabel()
        self.timeLabel.setObjectName("clockTime")
        self.timeLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.timeLabel.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        centerLayout.addWidget(self.timeLabel)

        self.queueCheck = QtWidgets.QCheckBox()
        self.queueCheck.setObjectName("clockQueueCheck")
        self.queueCheck.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.queueCheck.toggled.connect(self._complete_front)
        self.queueLabel = QtWidgets.QLabel()
        self.queueLabel.setObjectName("clockQueuePreview")
        self.queueLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.queueLabel.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        centerLayout.addWidget(self.queueCheck, 0, QtCore.Qt.AlignmentFlag.AlignCenter)
        centerLayout.addWidget(self.queueLabel)

        layout.addWidget(self.centerGroup)
        layout.addStretch(1)

        self.resizeHandle = QtWidgets.QFrame(self)
        self.resizeHandle.setObjectName("resizeHandle")
        self.resizeHandle.setFixedSize(20, 20)
        self.resizeHandle.setCursor(QtCore.Qt.CursorShape.SizeFDiagCursor)
        self.resizeHandle.setMouseTracking(True)
        self.resizeHandle.installEventFilter(self)
        self.resizeHandle.raise_()
        self.frame.installEventFilter(self)

    def _show_front(self):
        if not self.queue:
            self.queueCheck.hide()
            self.queueLabel.setText("Queue complete" if hasattr(self, "queueCheck") else "")
            return
        item=self.queue[0]
        self.queueCheck.blockSignals(True)
        self.queueCheck.setChecked(False)
        self.queueCheck.setText(item[4])
        self.queueCheck.blockSignals(False)
        self.queueCheck.show()
        self.queueLabel.setText(f"1 of {len(self.queue)}")

    def _complete_front(self, checked):
        if not checked or not self.queue:
            return
        item=self.queue.pop(0)
        self.queue_completed.emit(item)
        self._show_front()

    def _tick(self):
        if self.mode == "clock":
            self.timeLabel.setText(QtCore.QTime.currentTime().toString("hh:mm:ss AP"))
            return
        hours = self.remaining_seconds // 3600
        minutes = (self.remaining_seconds % 3600) // 60
        seconds = self.remaining_seconds % 60
        self.timeLabel.setText(
            f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            if hours else f"{minutes:02d}:{seconds:02d}"
        )
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
        else:
            self._tick_timer.stop()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_adaptive_layout()
        self.geometry_changed.emit()

    def moveEvent(self, event):
        super().moveEvent(event)
        self.geometry_changed.emit()

    def _update_adaptive_layout(self):
        if not hasattr(self, "timeLabel"):
            return
        usable_width = max(1, self.width() - 64)
        usable_height = max(1, self.height() - 76)
        point_size = max(35, min(70, int(min(usable_width / 12.4, usable_height / 1.60))))
        font = QtGui.QFont("Consolas", point_size, QtGui.QFont.Weight.Bold)
        self.timeLabel.setFont(font)
        queue_font = self.queueLabel.font()
        queue_font.setPointSize(max(8, min(13, int(self.height() / 20))))
        self.queueLabel.setFont(queue_font)
        if hasattr(self, "resizeHandle"):
            self.resizeHandle.move(self.width() - 25, self.height() - 25)
            self.resizeHandle.raise_()

    def _apply_theme(self):
        c = palette(getattr(self.parent(), "current_theme", "default"))
        self.setStyleSheet(f"""
            QFrame#clockFrame {{
                background: {c['surface']};
                border: 1px solid {c['border_soft']};
                border-radius: 18px;
            }}
            QWidget#clockCenterGroup {{
                background: transparent;
                border: none;
            }}
            QLabel#clockTime {{
                color: {c['text']};
                background: transparent;
                border: none;
            }}
            QCheckBox#clockQueueCheck {{
                color: {c['text']};
                spacing: 8px;
                font: 600 12px 'Segoe UI';
                background: transparent;
                border: none;
            }}
            QLabel#clockQueuePreview {{
                color: {c['muted']};
                background: transparent;
                border: none;
            }}
            QPushButton#clockClose {{
                color: {c['muted']};
                background: transparent;
                border: none;
                border-radius: 6px;
                font: 17px 'Segoe UI';
                padding: 0px;
            }}
            QPushButton#clockClose:hover {{
                color: {c['text']};
                background: {c['surface_alt']};
            }}
            QFrame#resizeHandle {{
                background: transparent;
                border: none;
            }}
        """)

    def eventFilter(self, watched, event):
        if self.resizeHandle is not None and watched is self.resizeHandle:
            if event.type() == QtCore.QEvent.Type.MouseButtonPress and event.button() == QtCore.Qt.MouseButton.LeftButton:
                self._resize_start_global = event.globalPosition().toPoint()
                self._resize_start_geometry = self.geometry()
                return True
            if event.type() == QtCore.QEvent.Type.MouseMove and self._resize_start_global is not None and event.buttons() & QtCore.Qt.MouseButton.LeftButton:
                delta = event.globalPosition().toPoint() - self._resize_start_global
                width = max(self.minimumWidth(), min(self.maximumWidth(), self._resize_start_geometry.width() + delta.x()))
                height = max(self.minimumHeight(), min(self.maximumHeight(), self._resize_start_geometry.height() + delta.y()))
                self.resize(width, height)
                return True
            if event.type() == QtCore.QEvent.Type.MouseButtonRelease:
                self._resize_start_global = None
                self._resize_start_geometry = None
                return True

        if watched is self.frame:
            if event.type() == QtCore.QEvent.Type.MouseButtonPress and event.button() == QtCore.Qt.MouseButton.LeftButton:
                self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                return True
            if event.type() == QtCore.QEvent.Type.MouseMove and self._drag_offset is not None and event.buttons() & QtCore.Qt.MouseButton.LeftButton:
                self.move(event.globalPosition().toPoint() - self._drag_offset)
                return True
            if event.type() == QtCore.QEvent.Type.MouseButtonRelease and event.button() == QtCore.Qt.MouseButton.LeftButton:
                self._drag_offset = None
                return True
        return super().eventFilter(watched, event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None and event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton and self._drag_offset is not None:
            self._drag_offset = None
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _return_to_chronotask(self):
        if self._returning:
            return
        self._returning = True
        self.closing.emit()
        self._tick_timer.stop()
        self.hide()
        self.return_requested.emit()
        self.deleteLater()

    def closeEvent(self, event):
        if self._returning:
            event.accept()
            return
        event.ignore()
        self._return_to_chronotask()
