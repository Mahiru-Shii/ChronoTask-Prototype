from PySide6 import QtCore, QtGui, QtWidgets


class TitleBar(QtWidgets.QFrame):
    """Custom title bar for the frameless ChronoTask window."""

    def __init__(self, parent_window, parent=None):
        super().__init__(parent)
        self.parent_window = parent_window
        self.dragging = False
        self.drag_position = QtCore.QPoint()

        self.setObjectName("titleBar")
        self._setup_title_bar()
        self._build_ui()
        self._connect_signals()
        self._start_clock()

    def _setup_title_bar(self):
        self.setFixedHeight(52)
        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)

        # Important for rounded main-window corners: this title bar does
        # not paint a square background over the outer windowFrame.
        self.setStyleSheet(
            """
            QFrame#titleBar {
                background-color: transparent;
                border: none;
                border-bottom: 1px solid #2E3A52;
            }

            QLabel#appTitle {
                background-color: transparent;
                color: #F4F7FF;
                border: none;
                font-family: "Segoe UI";
                font-size: 12px;
                font-weight: 700;
            }

            QLabel#clockLabel {
                background-color: transparent;
                color: #8A9AB7;
                border: none;
                font-family: "Segoe UI";
                font-size: 9px;
                font-weight: 500;
            }

            QPushButton#windowButton {
                background-color: transparent;
                color: #AAB6CF;
                border: none;
                border-radius: 6px;
                font-family: "Segoe UI";
                font-size: 13px;
            }

            QPushButton#windowButton:hover {
                background-color: #253349;
                color: #FFFFFF;
            }

            QPushButton#windowButton:pressed {
                background-color: #31425D;
            }

            QPushButton#closeButton {
                background-color: transparent;
                color: #AAB6CF;
                border: none;
                border-radius: 6px;
                font-family: "Segoe UI";
                font-size: 14px;
            }

            QPushButton#closeButton:hover {
                background-color: #E05D68;
                color: #FFFFFF;
            }

            QPushButton#closeButton:pressed {
                background-color: #C94F59;
                color: #FFFFFF;
            }
            """
        )

    def _build_ui(self):
        self.mainLayout = QtWidgets.QHBoxLayout(self)
        self.mainLayout.setContentsMargins(18, 0, 10, 0)
        self.mainLayout.setSpacing(6)

        self.appTitle = QtWidgets.QLabel("ChronoTask", self)
        self.appTitle.setObjectName("appTitle")
        self.mainLayout.addWidget(self.appTitle)
        self.mainLayout.addStretch(1)

        self.clockLabel = QtWidgets.QLabel("", self)
        self.clockLabel.setObjectName("clockLabel")
        self.clockLabel.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight
            | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.clockLabel.setMinimumWidth(90)
        self.mainLayout.addWidget(self.clockLabel)
        self.mainLayout.addSpacing(8)

        self.btnMinimize = self._create_window_button("−", "Minimize")
        self.btnMaximize = self._create_window_button("□", "Maximize")
        self.mainLayout.addWidget(self.btnMinimize)
        self.mainLayout.addWidget(self.btnMaximize)

        self.btnClose = QtWidgets.QPushButton("×", self)
        self.btnClose.setObjectName("closeButton")
        self.btnClose.setFixedSize(34, 30)
        self.btnClose.setToolTip("Close")
        self.btnClose.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        self.mainLayout.addWidget(self.btnClose)

    def _create_window_button(self, text, tooltip):
        button = QtWidgets.QPushButton(text, self)
        button.setObjectName("windowButton")
        button.setFixedSize(34, 30)
        button.setToolTip(tooltip)
        button.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        return button

    def _connect_signals(self):
        self.btnMinimize.clicked.connect(self.minimize_window)
        self.btnMaximize.clicked.connect(self.toggle_maximize)
        self.btnClose.clicked.connect(self.close_window)

    def _start_clock(self):
        self.clockTimer = QtCore.QTimer(self)
        self.clockTimer.timeout.connect(self.update_clock)
        self.clockTimer.start(1000)
        self.update_clock()

    @QtCore.Slot()
    def update_clock(self):
        self.clockLabel.setText(
            QtCore.QDateTime.currentDateTime().toString("h:mm AP")
        )

    @QtCore.Slot()
    def minimize_window(self):
        if self.parent_window is not None:
            self.parent_window.showMinimized()

    @QtCore.Slot()
    def toggle_maximize(self):
        if self.parent_window is None:
            return

        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
        else:
            self.parent_window.showMaximized()

        self.sync_window_state()
        self._request_mask_refresh()

    @QtCore.Slot()
    def close_window(self):
        if self.parent_window is not None:
            self.parent_window.close()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            child = self.childAt(event.position().toPoint())

            if isinstance(child, QtWidgets.QPushButton):
                super().mousePressEvent(event)
                return

            if self.parent_window is not None:
                self.dragging = True
                self.drag_position = (
                    event.globalPosition().toPoint()
                    - self.parent_window.frameGeometry().topLeft()
                )
                event.accept()
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (
            self.dragging
            and event.buttons() & QtCore.Qt.MouseButton.LeftButton
        ):
            super().mouseMoveEvent(event)
            return

        if self.parent_window is None:
            return

        global_position = event.globalPosition().toPoint()

        # Restore before dragging a maximized window.
        if self.parent_window.isMaximized():
            old_width = max(self.parent_window.width(), 1)
            relative_x = event.position().x() / old_width

            self.parent_window.showNormal()
            self.sync_window_state()

            new_width = self.parent_window.width()
            new_x = int(global_position.x() - new_width * relative_x)
            new_y = global_position.y() - 20
            self.parent_window.move(new_x, new_y)

            self.drag_position = (
                global_position
                - self.parent_window.frameGeometry().topLeft()
            )
            self._request_mask_refresh()

        self.parent_window.move(global_position - self.drag_position)
        event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            child = self.childAt(event.position().toPoint())
            if not isinstance(child, QtWidgets.QPushButton):
                self.toggle_maximize()
                event.accept()
                return

        super().mouseDoubleClickEvent(event)

    def sync_window_state(self):
        if self.parent_window is None:
            return

        if self.parent_window.isMaximized():
            self.btnMaximize.setText("❐")
            self.btnMaximize.setToolTip("Restore")
        else:
            self.btnMaximize.setText("□")
            self.btnMaximize.setToolTip("Maximize")

    def _request_mask_refresh(self):
        if self.parent_window is None:
            return

        refresh = getattr(self.parent_window, "_update_window_mask", None)
        if callable(refresh):
            QtCore.QTimer.singleShot(0, refresh)