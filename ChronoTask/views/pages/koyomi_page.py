from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets
from styles.theme import palette


class KoyomiPage(QtWidgets.QWidget):
    """Chrono Mate control page for Koyomi."""
    show_koyomi_requested = QtCore.Signal()
    hide_koyomi_requested = QtCore.Signal()
    celebration_sound_changed = QtCore.Signal(bool)
    climbing_enabled_changed = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("koyomiPage")
        self._build_ui()
        self.apply_theme()

    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(26, 24, 26, 24); root.setSpacing(16)

        header = QtWidgets.QHBoxLayout()
        header.setSpacing(14)
        text_col = QtWidgets.QVBoxLayout()
        text_col.setSpacing(4)
        title = QtWidgets.QLabel("Koyomi"); title.setObjectName("koyomiTitle")
        subtitle = QtWidgets.QLabel("Your ChronoTask Chrono Mate"); subtitle.setObjectName("koyomiSubtitle")
        text_col.addWidget(title); text_col.addWidget(subtitle)
        header.addLayout(text_col)
        header.addStretch(1)

        self.idlePreview = QtWidgets.QLabel()
        self.idlePreview.setObjectName("koyomiIdlePreview")
        self.idlePreview.setFixedSize(112, 112)
        self.idlePreview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        idle_path = Path(__file__).resolve().parents[2] / "desktop_mate" / "chibi_idle.gif"
        self.idlePreviewMovie = QtGui.QMovie(str(idle_path), parent=self)
        self.idlePreviewMovie.setCacheMode(QtGui.QMovie.CacheMode.CacheAll)
        self.idlePreviewMovie.setScaledSize(QtCore.QSize(108, 108))
        self.idlePreview.setMovie(self.idlePreviewMovie)
        self.idlePreviewMovie.start()
        header.addWidget(self.idlePreview, 0, QtCore.Qt.AlignmentFlag.AlignVCenter)
        root.addLayout(header)

        companion = QtWidgets.QFrame(); companion.setObjectName("koyomiCard")
        card = QtWidgets.QVBoxLayout(companion); card.setContentsMargins(20,18,20,18); card.setSpacing(12)
        name = QtWidgets.QLabel("Koyomi"); name.setObjectName("cardTitle"); name.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.statusLabel = QtWidgets.QLabel("Chrono Mate: Active"); self.statusLabel.setObjectName("bodyText"); self.statusLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        actions = QtWidgets.QHBoxLayout(); actions.addStretch(1)
        self.btnShow = QtWidgets.QPushButton("Show Koyomi"); self.btnHide = QtWidgets.QPushButton("Hide Koyomi")
        actions.addWidget(self.btnShow); actions.addWidget(self.btnHide); actions.addStretch(1)
        card.addWidget(name); card.addWidget(self.statusLabel); card.addLayout(actions)
        root.addWidget(companion)

        wisdom = self._section("KOYOMI WISDOM", "Koyomi occasionally shares reminders and ChronoTask wisdom while accompanying you.")
        self.chkSpeech = QtWidgets.QCheckBox("Show speech bubbles"); self.chkSpeech.setChecked(True)
        wisdom.layout().addWidget(self.chkSpeech); root.addWidget(wisdom)

        celebrations = self._section("CELEBRATIONS", "Choose when Koyomi celebrates your progress.")
        self.chkSteps = QtWidgets.QCheckBox("Celebrate completed Chrono Steps"); self.chkSteps.setChecked(True)
        self.chkTasks = QtWidgets.QCheckBox("Celebrate completed Tasks"); self.chkTasks.setChecked(True)
        self.chkSound = QtWidgets.QCheckBox("Play celebration sound"); self.chkSound.setChecked(True)
        celebrations.layout().addWidget(self.chkSteps); celebrations.layout().addWidget(self.chkTasks); celebrations.layout().addWidget(self.chkSound)
        root.addWidget(celebrations)

        behavior = self._section("BEHAVIOR", "Choose how Koyomi interacts with floating windows.")
        self.chkDisableClimbing = QtWidgets.QCheckBox("Disable climbing floating windows")
        self.chkDisableClimbing.setChecked(False)
        behavior.layout().addWidget(self.chkDisableClimbing)
        root.addWidget(behavior); root.addStretch(1)

        self.btnShow.clicked.connect(self.show_koyomi_requested.emit)
        self.btnHide.clicked.connect(self.hide_koyomi_requested.emit)
        self.chkSound.toggled.connect(self.celebration_sound_changed.emit)
        self.chkDisableClimbing.toggled.connect(
            lambda disabled: self.climbing_enabled_changed.emit(not disabled)
        )

    def _section(self, heading, description):
        box = QtWidgets.QFrame(); box.setObjectName("koyomiCard")
        layout = QtWidgets.QVBoxLayout(box); layout.setContentsMargins(18,16,18,16); layout.setSpacing(9)
        h = QtWidgets.QLabel(heading); h.setObjectName("sectionTitle")
        d = QtWidgets.QLabel(description); d.setObjectName("mutedText"); d.setWordWrap(True)
        layout.addWidget(h); layout.addWidget(d)
        return box

    def set_koyomi_active(self, active):
        self.statusLabel.setText("Chrono Mate: Active" if active else "Chrono Mate: Hidden")

    def apply_theme(self):
        c = palette(getattr(self.window(), "current_theme", "default"))
        self.setStyleSheet(f"""
            QWidget#koyomiPage {{ background: transparent; color: {c['text']}; }}
            QLabel#koyomiTitle {{ color: {c['text']}; font: 700 23px 'Segoe UI'; }}
            QLabel#koyomiSubtitle, QLabel#mutedText {{ color: {c['muted']}; font: 12px 'Segoe UI'; }}
            QLabel#cardTitle {{ color: {c['text']}; font: 700 17px 'Segoe UI'; }}
            QLabel#sectionTitle {{ color: {c['text']}; font: 700 12px 'Segoe UI'; }}
            QLabel#koyomiIdlePreview {{ background: transparent; border: none; }}
            QLabel#bodyText, QCheckBox {{ color: {c['text']}; font: 13px 'Segoe UI'; }}
            QFrame#koyomiCard {{ background: {c['surface']}; border: 1px solid {c['border_soft']}; border-radius: 14px; }}
            QPushButton {{ background: {c['accent']}; color: {c['text']}; border: 1px solid {c['accent_hover']}; border-radius: 9px; padding: 8px 14px; font: 600 12px 'Segoe UI'; }}
            QPushButton:hover {{ background: {c['accent_hover']}; }}
            QCheckBox {{ spacing: 8px; }}
        """)
