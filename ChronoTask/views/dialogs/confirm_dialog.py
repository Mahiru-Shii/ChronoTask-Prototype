from PySide6 import QtCore, QtGui, QtWidgets
from styles.theme import palette


class ConfirmDialog(QtWidgets.QDialog):
    """Animated ChronoTask confirmation dialog for destructive actions."""

    def __init__(
        self,
        parent=None,
        title="Delete task",
        message="Delete this task?",
        detail="This action cannot be undone.",
        confirm_text="Delete",
        cancel_text="Cancel",
    ):
        super().__init__(parent)
        self.dragging = False
        self.drag_position = QtCore.QPoint()
        self._deleting = False
        self._shown_once = False

        self._setup_window(title)
        self._build_ui(title, message, detail, confirm_text, cancel_text)
        self._apply_style()
        self._connect_signals()
        self._setup_animations()

    # =================================================================
    # WINDOW
    # =================================================================

    def _setup_window(self, title):
        self.setObjectName("ConfirmDialog")
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(440, 250)
        self.setWindowFlags(
            QtCore.Qt.WindowType.Dialog
            | QtCore.Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(
            QtCore.Qt.WidgetAttribute.WA_TranslucentBackground,
            True,
        )
        self.setWindowOpacity(0.0)

    # =================================================================
    # UI
    # =================================================================

    def _build_ui(self, title, message, detail, confirm_text, cancel_text):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(0)

        self.frame = QtWidgets.QFrame(self)
        self.frame.setObjectName("dialogFrame")
        root.addWidget(self.frame)

        layout = QtWidgets.QVBoxLayout(self.frame)
        layout.setContentsMargins(0, 0, 0, 20)
        layout.setSpacing(0)

        self.titleBar = QtWidgets.QFrame(self.frame)
        self.titleBar.setObjectName("titleBar")
        self.titleBar.setFixedHeight(48)
        title_layout = QtWidgets.QHBoxLayout(self.titleBar)
        title_layout.setContentsMargins(18, 0, 10, 0)

        self.lblTitle = QtWidgets.QLabel(title, self.titleBar)
        self.lblTitle.setObjectName("dialogTitle")
        title_layout.addWidget(self.lblTitle)
        title_layout.addStretch(1)

        self.btnClose = QtWidgets.QPushButton("×", self.titleBar)
        self.btnClose.setObjectName("closeButton")
        self.btnClose.setFixedSize(34, 30)
        self.btnClose.setToolTip("Close")
        self.btnClose.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        title_layout.addWidget(self.btnClose)
        layout.addWidget(self.titleBar)

        content = QtWidgets.QWidget(self.frame)
        content.setObjectName("content")
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(22, 14, 22, 0)
        content_layout.setSpacing(16)

        message_row = QtWidgets.QHBoxLayout()
        message_row.setSpacing(14)

        self.warningBadge = QtWidgets.QFrame(content)
        self.warningBadge.setObjectName("warningBadge")
        self.warningBadge.setFixedSize(46, 46)
        badge_layout = QtWidgets.QVBoxLayout(self.warningBadge)
        badge_layout.setContentsMargins(0, 0, 0, 0)

        self.lblWarning = QtWidgets.QLabel("!", self.warningBadge)
        self.lblWarning.setObjectName("warningIcon")
        self.lblWarning.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        badge_layout.addWidget(self.lblWarning)
        message_row.addWidget(
            self.warningBadge,
            0,
            QtCore.Qt.AlignmentFlag.AlignTop,
        )

        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setSpacing(6)

        self.lblMessage = QtWidgets.QLabel(message, content)
        self.lblMessage.setObjectName("message")
        self.lblMessage.setWordWrap(True)
        self.lblMessage.setMinimumHeight(28)
        text_layout.addWidget(self.lblMessage)

        self.lblDetail = QtWidgets.QLabel(detail, content)
        self.lblDetail.setObjectName("detail")
        self.lblDetail.setWordWrap(True)
        self.lblDetail.setMinimumHeight(38)
        text_layout.addWidget(self.lblDetail)

        message_row.addLayout(text_layout, 1)
        content_layout.addLayout(message_row)
        content_layout.addStretch(1)

        actions = QtWidgets.QHBoxLayout()
        actions.setSpacing(10)
        actions.addStretch(1)

        self.btnCancel = QtWidgets.QPushButton(cancel_text, content)
        self.btnCancel.setObjectName("cancelButton")
        self.btnCancel.setFixedSize(104, 40)
        self.btnCancel.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )

        self.btnConfirm = QtWidgets.QPushButton(confirm_text, content)
        self.btnConfirm.setObjectName("confirmButton")
        self.btnConfirm.setFixedSize(104, 40)
        self.btnConfirm.setDefault(True)
        self.btnConfirm.setAutoDefault(True)
        self.btnConfirm.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )

        actions.addWidget(self.btnCancel)
        actions.addWidget(self.btnConfirm)
        content_layout.addLayout(actions)
        layout.addWidget(content, 1)

    # =================================================================
    # SIGNALS
    # =================================================================

    def _connect_signals(self):
        self.btnClose.clicked.connect(self.reject)
        self.btnCancel.clicked.connect(self.reject)
        self.btnConfirm.clicked.connect(self.start_delete_animation)

    # =================================================================
    # ANIMATION
    # =================================================================

    def _setup_animations(self):
        self.fadeInAnimation = QtCore.QPropertyAnimation(self, b"windowOpacity", self)
        self.fadeInAnimation.setDuration(180)
        self.fadeInAnimation.setStartValue(0.0)
        self.fadeInAnimation.setEndValue(1.0)
        self.fadeInAnimation.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)

        self.fadeOutAnimation = QtCore.QPropertyAnimation(self, b"windowOpacity", self)
        self.fadeOutAnimation.setDuration(230)
        self.fadeOutAnimation.setStartValue(1.0)
        self.fadeOutAnimation.setEndValue(0.0)
        self.fadeOutAnimation.setEasingCurve(QtCore.QEasingCurve.Type.InCubic)
        self.fadeOutAnimation.finished.connect(self._finish_delete)

        self.badgeEffect = QtWidgets.QGraphicsOpacityEffect(self.warningBadge)
        self.warningBadge.setGraphicsEffect(self.badgeEffect)
        self.badgeEffect.setOpacity(1.0)

        self.badgePulse = QtCore.QSequentialAnimationGroup(self)
        for start, end, duration in (
            (1.0, 0.35, 85),
            (0.35, 1.0, 85),
            (1.0, 0.45, 70),
            (0.45, 1.0, 70),
        ):
            animation = QtCore.QPropertyAnimation(
                self.badgeEffect,
                b"opacity",
                self.badgePulse,
            )
            animation.setDuration(duration)
            animation.setStartValue(start)
            animation.setEndValue(end)
            animation.setEasingCurve(QtCore.QEasingCurve.Type.InOutQuad)
            self.badgePulse.addAnimation(animation)

        self.deleteSequence = QtCore.QSequentialAnimationGroup(self)
        pause = QtCore.QPauseAnimation(130, self.deleteSequence)
        self.deleteSequence.addAnimation(pause)
        self.deleteSequence.addAnimation(self.fadeOutAnimation)

    def showEvent(self, event):
        super().showEvent(event)
        if self._shown_once:
            return
        self._shown_once = True
        self.setWindowOpacity(0.0)
        QtCore.QTimer.singleShot(0, self.fadeInAnimation.start)

    @QtCore.Slot()
    def start_delete_animation(self):
        if self._deleting:
            return

        self._deleting = True
        self._set_controls_enabled(False)
        self.btnConfirm.setText("Deleting...")

        # A short pulse communicates the destructive action before the dialog
        # fades out. QGraphicsOpacityEffect is used so no layout geometry moves.
        self.badgePulse.start()
        self.deleteSequence.start()

    def _finish_delete(self):
        self.setWindowOpacity(1.0)
        super().accept()

    def _set_controls_enabled(self, enabled):
        self.btnConfirm.setEnabled(enabled)
        self.btnCancel.setEnabled(enabled)
        self.btnClose.setEnabled(enabled)

    # =================================================================
    # STYLE
    # =================================================================

    def _apply_style(self):
        parent_window = self.parent().window() if self.parent() is not None else None
        theme_name = getattr(parent_window, "current_theme", "default")
        c = palette(theme_name)
        self.current_theme = theme_name
        self.setStyleSheet(f"""
            QDialog#ConfirmDialog {{ background: transparent; }}
            QFrame#dialogFrame {{ background-color: {c['surface_alt']}; border: 1px solid {c['border']}; border-radius: 16px; }}
            QFrame#titleBar, QWidget#content {{ background: transparent; border: none; }}
            QLabel#dialogTitle {{ background: transparent; color: {c['text']}; border: none; font-family: 'Segoe UI'; font-size: 12px; font-weight: 600; }}
            QPushButton#closeButton {{ background: transparent; color: {c['muted']}; border: none; border-radius: 7px; font-size: 17px; }}
            QPushButton#closeButton:hover {{ background: {c['surface']}; color: {c['text']}; }}
            QFrame#warningBadge {{ background-color: #3A2734; border: 1px solid #75414D; border-radius: 13px; }}
            QLabel#warningIcon {{ background: transparent; color: #E06C75; border: none; font-size: 22px; font-weight: 800; }}
            QLabel#message {{ background: transparent; color: {c['text']}; border: none; font-size: 13px; font-weight: 600; }}
            QLabel#detail {{ background: transparent; color: {c['muted']}; border: none; font-size: 10px; }}
            QPushButton#cancelButton {{ background-color: {c['surface']}; color: {c['text']}; border: 1px solid {c['border']}; border-radius: 9px; font-size: 10px; font-weight: 600; }}
            QPushButton#cancelButton:hover {{ background-color: {c['input']}; border-color: {c['accent_hover']}; }}
            QPushButton#confirmButton {{ background-color: #C94F59; color: #FFFFFF; border: 1px solid #E06C75; border-radius: 9px; font-size: 10px; font-weight: 700; }}
            QPushButton#confirmButton:hover {{ background-color: #E05D68; border-color: #EE818A; }}
            QPushButton#confirmButton:pressed {{ background-color: #B5444F; }}
            QPushButton#confirmButton:disabled, QPushButton#cancelButton:disabled, QPushButton#closeButton:disabled {{ color: {c['muted']}; }}
        """)

    # =================================================================
    # INPUT / DRAGGING
    # =================================================================

    def reject(self):
        if self._deleting:
            return
        super().reject()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            if not self._deleting:
                self.reject()
            event.accept()
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if self._deleting:
            return
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            position = self.titleBar.mapFrom(
                self,
                event.position().toPoint(),
            )
            if self.titleBar.rect().contains(position):
                child = self.titleBar.childAt(position)
                if not isinstance(child, QtWidgets.QPushButton):
                    self.dragging = True
                    self.drag_position = (
                        event.globalPosition().toPoint()
                        - self.frameGeometry().topLeft()
                    )
                    event.accept()
                    return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._deleting:
            return
        if (
            self.dragging
            and event.buttons() & QtCore.Qt.MouseButton.LeftButton
        ):
            self.move(
                event.globalPosition().toPoint()
                - self.drag_position
            )
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        super().mouseReleaseEvent(event)