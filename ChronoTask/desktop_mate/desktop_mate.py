import sys
import random
import ctypes
from ctypes import wintypes
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets, QtMultimedia


class SpeechBubble(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
            | QtCore.Qt.WindowType.Tool
            | QtCore.Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.text = ""
        self.tail_on_top = False
        self.font = QtGui.QFont("Segoe UI", 9, QtGui.QFont.Weight.Bold)
        self.setFixedSize(150, 65)

    def set_text(self, text):
        self.text = text
        metrics = QtGui.QFontMetrics(self.font)
        max_inner_width = 205
        min_inner_width = 78
        natural_width = metrics.horizontalAdvance(text)
        inner_width = max(min_inner_width, min(max_inner_width, natural_width + 4))
        flags = int(QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.TextFlag.TextWordWrap)
        measured = metrics.boundingRect(QtCore.QRect(0, 0, inner_width, 1000), flags, text)
        # The paint rect removes 24 px horizontally and extra space vertically for the tail.
        width = max(112, min(245, inner_width + 34))
        # Add one full line spacing plus padding so bold descenders/last wrapped line never clip.
        height = max(62, min(165, measured.height() + metrics.lineSpacing() + 42))
        self.setFixedSize(width, height)
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        if self.tail_on_top:
            bubble = QtCore.QRectF(5, 18, self.width() - 10, self.height() - 22)
        else:
            bubble = QtCore.QRectF(5, 4, self.width() - 10, self.height() - 18)
        painter.setPen(QtGui.QPen(QtGui.QColor(45, 45, 45), 1.5))
        painter.setBrush(QtGui.QColor(255, 255, 255, 245))
        painter.drawRoundedRect(bubble, 11, 11)
        if self.tail_on_top:
            tail = QtGui.QPolygonF([
                QtCore.QPointF(self.width()/2 - 8, bubble.top()),
                QtCore.QPointF(self.width()/2, 3),
                QtCore.QPointF(self.width()/2 + 7, bubble.top()),
            ])
        else:
            tail = QtGui.QPolygonF([
                QtCore.QPointF(self.width()/2 - 7, bubble.bottom()),
                QtCore.QPointF(self.width()/2, self.height() - 3),
                QtCore.QPointF(self.width()/2 + 8, bubble.bottom()),
            ])
        painter.drawPolygon(tail)
        painter.setPen(QtGui.QColor(30, 30, 30))
        painter.setFont(self.font)
        painter.drawText(
            bubble.adjusted(11, 6, -11, -6),
            QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.TextFlag.TextWordWrap,
            self.text
        )


class DesktopMate(QtWidgets.QWidget):
    hidden_by_user = QtCore.Signal()
    def __init__(self):
        super().__init__()
        self.shutting_down = False
        self.setWindowTitle("Koyomi - Chrono Mate")
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
            | QtCore.Qt.WindowType.Tool
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(180, 180)
        self.setMouseTracking(True)

        base = Path(__file__).resolve().parent
        self.quotes_path = base / "quotes.txt"
        self.walk_path = base / "chibi_walk.gif"
        self.idle_path = base / "chibi_idle.gif"
        self.drag_path = base / "chibi_drag.png"
        self.run_path = base / "chibi_run.gif"
        self.stop_path = base / "chibi_stop.gif"
        self.sit_path = base / "chibi_sit.png"
        self.celebrate_path = base / "chibi_celebrate.png"
        self.yay_path = base / "chibi_yay.wav"
        self.fly_diagonal_path = base / "chibi_fly_diagonal.gif"
        self.fly_up_path = base / "chibi_fly_up.gif"
        self.climb_path = base / "chibi_climb.gif"
        self.petting_path = base / "chibi_petting.gif"
        self.sitting_petting_path = base / "chibi_sitting_petting.gif"
        self.falling_path = base / "chibi_falling.gif"
        self.falling_ground_hit_path = base / "chibi_falling_ground_hit.png"
        self.sitting_dizzy_path = base / "chibi_sitting_dizzy.gif"
        self.sitting_idle_path = base / "chibi_sitting_idle.gif"
        self.sitting_happy_path = base / "chibi_sitting_happy.gif"
        self.hanging_idle_path = base / "chibi_hanging_sit_idle.gif"
        self.hanging_petting_path = base / "chibi_hanging_sit_petting.gif"
        self.shamisen_path = base / "chibi_shamisen.gif"
        self.shamisen_track_paths = [base / f"shamisen_track_{i}.mp3" for i in range(1, 5)]
        for path in (self.walk_path, self.idle_path, self.drag_path,
                     self.run_path, self.stop_path, self.sit_path,
                     self.celebrate_path, self.yay_path, self.fly_diagonal_path,
                     self.fly_up_path, self.climb_path, self.petting_path,
                     self.sitting_petting_path,
                     self.falling_path, self.falling_ground_hit_path,
                     self.sitting_dizzy_path, self.sitting_idle_path,
                     self.sitting_happy_path, self.hanging_idle_path,
                     self.hanging_petting_path, self.shamisen_path,
                     *self.shamisen_track_paths):
            if not path.exists():
                raise FileNotFoundError(f"Missing required asset:\n{path}")

        self.character = QtWidgets.QLabel(self)
        self.character.setGeometry(0, 0, self.width(), self.height())
        self.character.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.character.setStyleSheet("background: transparent;")
        self.character.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.bubble = SpeechBubble()
        self.quotes = self.load_quotes()
        self.quote_visible = False
        self.quote_timer = QtCore.QTimer(self)
        self.quote_timer.setSingleShot(True)
        self.quote_timer.timeout.connect(self.show_random_quote)
        self.quote_hide_timer = QtCore.QTimer(self)
        self.quote_hide_timer.setSingleShot(True)
        self.quote_hide_timer.timeout.connect(self.hide_quote)
        self.schedule_quote()

        self.walk_movie = self.make_movie(self.walk_path)
        self.idle_movie = self.make_movie(self.idle_path)
        self.run_movie = self.make_movie(self.run_path)
        self.stop_movie = self.make_movie(self.stop_path)
        self.fly_diagonal_movie = self.make_movie(self.fly_diagonal_path)
        self.fly_up_movie = self.make_movie(self.fly_up_path)
        self.climb_movie = self.make_movie(self.climb_path)
        self.petting_movie = self.make_movie(self.petting_path)
        self.sitting_petting_movie = self.make_movie(self.sitting_petting_path)
        self.falling_movie = self.make_movie(self.falling_path)
        self.sitting_dizzy_movie = self.make_movie(self.sitting_dizzy_path)
        self.sitting_idle_movie = self.make_movie(self.sitting_idle_path)
        self.sitting_happy_movie = self.make_movie(self.sitting_happy_path)
        self.hanging_idle_movie = self.make_movie(self.hanging_idle_path)
        self.hanging_petting_movie = self.make_movie(self.hanging_petting_path)
        self.shamisen_movie = self.make_movie(self.shamisen_path)
        self.drag_pixmap = self.load_pixmap(self.drag_path)
        self.sit_pixmap = self.load_pixmap(self.sit_path)
        self.celebrate_pixmap = self.load_pixmap(self.celebrate_path)
        self.falling_ground_hit_pixmap = self.load_pixmap(self.falling_ground_hit_path)

        # Celebration sound
        self.yay_player = QtMultimedia.QMediaPlayer(self)
        self.yay_audio = QtMultimedia.QAudioOutput(self)
        self.yay_audio.setVolume(0.55)
        self.celebration_sound_enabled = True
        self.yay_player.setAudioOutput(self.yay_audio)
        self.yay_player.setSource(QtCore.QUrl.fromLocalFile(str(self.yay_path)))
        self.shamisen_player = QtMultimedia.QMediaPlayer(self)
        self.shamisen_audio = QtMultimedia.QAudioOutput(self)
        self.shamisen_audio.setVolume(0.75)
        self.shamisen_player.setAudioOutput(self.shamisen_audio)
        self.shamisen_player.mediaStatusChanged.connect(self._on_shamisen_media_status)
        self.shamisen_volume = 75
        self.shamisen_current_track = None

        self.movie = None
        self.state = "walk"
        self.direction = -1
        self.walk_speed = 2
        self.walking = True

        # Ground alignment. Increase this number to move the mate lower.
        self.FEET_OFFSET = 44
        # Separate adjustment in case the sitting art needs different alignment.
        self.SIT_FEET_OFFSET = 12

        # Drag + physics
        self.dragging = False
        self.active_menu = None
        self.active_menu_offset = QtCore.QPoint()
        self.MENU_ANCHOR_GAP = 6
        # Head-petting gesture detection. Move the cursor left/right repeatedly over the head.
        self.petting = False
        self.pet_last_x = None
        self.pet_last_sign = 0
        self.pet_strokes = 0
        self.pet_last_move_ms = 0
        self.PET_STROKES_NEEDED = 5
        self.PET_GESTURE_TIMEOUT_MS = 1100
        self.PETTING_KEEPALIVE_MS = 450
        self.petting_last_active_ms = 0
        # Head hitbox inside the 180x180 widget; deliberately does not include the body.
        self.PET_HEAD_RECT = QtCore.QRect(28, 8, 124, 92)
        self.manual_sitting = False
        self.drag_started_while_sitting = False
        self.MANUAL_SIT_GROUND_OFFSET = 14
        self.MANUAL_SIT_SWITCH_MIN_MS = 3500
        self.MANUAL_SIT_SWITCH_MAX_MS = 7000
        self.drag_offset = QtCore.QPoint()
        self.airborne = False
        self.velocity_y = 0.0
        self.gravity = 0.55
        self.max_fall_speed = 11.0

        # Hard-fall sequence: high drop -> falling -> impact -> dizzy -> silent recovery hop.
        self.hard_fall = False
        self.hard_fall_ground_y = 0
        self.recovery_jump = False
        self.recovery_ground_y = 0
        self.recovery_velocity_y = 0.0
        self.HARD_FALL_SCREEN_FRACTION = 0.50
        self.HARD_FALL_IMPACT_MS = 350
        self.HARD_FALL_DIZZY_MS = 1800
        self.RECOVERY_JUMP_VELOCITY = -8.5
        self.RECOVERY_GRAVITY = 0.72
        # Visual grounding offsets for the new crash/recovery artwork.
        self.FALLING_GROUND_HIT_OFFSET = 30
        self.SITTING_DIZZY_GROUND_OFFSET = 14
        self.RECOVERY_GROUND_OFFSET = 0

        # Drag swing
        self.last_drag_x = None
        self.drag_tilt = 0.0
        self.target_drag_tilt = 0.0

        # Floating-window climbing. Maximized windows are deliberately ignored.
        self.climb_target = None
        self.climb_side = None
        self.platform_hwnd = None
        self.platform_offset_x = 0
        self.fly_speed = 5
        self.climb_speed = 3
        # Alignment calibrated for transparent padding in the climb sprite.
        self.CLIMB_LEFT_INSET = 133
        self.CLIMB_RIGHT_INSET = 133
        self.CLIMB_BOTTOM_LIFT = 14
        self.TOP_JUMP_HEIGHT = 20
        self.TOP_JUMP_INWARD = 58
        self.top_jump = None
        self.climbing_enabled = True
        self.chrono_clock_window = None
        self.chrono_clock_attached = False
        self.chrono_clock_trip = False
        self.chrono_clock_phase = None
        self.chrono_clock_target_y = 0
        self.hanging_petting = False
        self.shamisen_playing = False
        self.window_scan_ticks = 0
        self.WINDOW_SCAN_EVERY = 18
        self.WINDOW_TARGET_DISTANCE = 420
        # Window-edge behavior: usually turn around, sometimes deliberately step off.
        self.EDGE_FALL_CHANCE = 0.20
        self.edge_fall_decision = None

        # Celebration jump
        self.celebrating = False
        self.celebrate_ground_y = 0
        self.celebrate_velocity_y = 0.0
        self.CELEBRATE_JUMP_VELOCITY = -11.5
        self.CELEBRATE_GRAVITY = 0.72

        # Run + braking momentum
        self.run_speed = 6.0
        self.stop_velocity = 0.0
        self.run_chance = 0.004
        self.run_timer = QtCore.QTimer(self)
        self.run_timer.setSingleShot(True)
        self.run_timer.timeout.connect(self.start_stopping)
        self.stop_timer = QtCore.QTimer(self)
        self.stop_timer.setSingleShot(True)
        self.stop_timer.timeout.connect(self.finish_stopping)

        # Sitting after landing
        self.sit_timer = QtCore.QTimer(self)
        self.sit_timer.setSingleShot(True)
        self.sit_timer.timeout.connect(self.finish_sitting)
        self.manual_sit_timer = QtCore.QTimer(self)
        self.manual_sit_timer.setSingleShot(True)
        self.manual_sit_timer.timeout.connect(self.change_manual_sit_pose)
        self.petting_stop_timer = QtCore.QTimer(self)
        self.petting_stop_timer.setSingleShot(True)
        self.petting_stop_timer.timeout.connect(self.finish_petting_if_inactive)

        self.motion_timer = QtCore.QTimer(self)
        self.motion_timer.timeout.connect(self.update_motion)
        self.motion_timer.start(16)

        # Reassert native topmost status so taskbar/task switching cannot cover Desktop Mate.
        self.topmost_timer = QtCore.QTimer(self)
        self.topmost_timer.timeout.connect(self.ensure_topmost)
        self.topmost_timer.start(750)
        QtCore.QTimer.singleShot(0, self.ensure_topmost)

        self.idle_timer = QtCore.QTimer(self)
        self.idle_timer.setSingleShot(True)
        self.idle_timer.timeout.connect(self.start_idle)
        self.resume_timer = QtCore.QTimer(self)
        self.resume_timer.setSingleShot(True)
        self.resume_timer.timeout.connect(self.finish_idle)

        # Koyomi startup entrance: fall in from the upper-right of the screen.
        self.startup_fall_from_top_right()

    def startup_fall_from_top_right(self):
        """Spawn Koyomi partially above the upper-right and use existing hard-fall physics."""
        screen = QtGui.QGuiApplication.primaryScreen()
        if screen is None:
            self.set_animation("walk")
            self.move_to_ground()
            self.schedule_idle()
            return

        area = screen.availableGeometry()
        right_margin = 70
        x = area.right() - self.width() - right_margin + 1
        x = max(area.left(), min(x, area.right() - self.width() + 1))
        y = area.top() - self.height() // 3

        self.move(x, y)
        self.direction = -1
        self.walking = True
        self.hard_fall = True
        self.recovery_jump = False
        self.hard_fall_ground_y = self.ground_y()
        self.airborne = True
        self.velocity_y = 1.0
        self.set_animation("falling")

    def load_quotes(self):
        if not self.quotes_path.exists():
            return []
        try:
            return [line.strip() for line in self.quotes_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        except (OSError, UnicodeError):
            return []

    def schedule_quote(self):
        if self.quotes:
            self.quote_timer.start(random.randint(20000, 60000))

    def show_random_quote(self):
        # Reload each time, so quotes.txt can be edited while Desktop Mate is running.
        latest = self.load_quotes()
        if latest:
            self.quotes = latest
        if not self.quotes:
            return
        self.bubble.set_text(random.choice(self.quotes))
        self.quote_visible = True
        self.position_bubble()
        self.bubble.show()
        self.quote_hide_timer.start(5000)

    def hide_quote(self):
        self.quote_visible = False
        self.bubble.hide()
        self.schedule_quote()

    def position_bubble(self):
        if not self.quote_visible:
            return
        screen = QtGui.QGuiApplication.screenAt(self.frameGeometry().center())
        area = screen.availableGeometry() if screen else QtGui.QGuiApplication.primaryScreen().availableGeometry()
        x = self.x() + self.width()//2 - self.bubble.width()//2
        y = self.y() - self.bubble.height() + 48
        x = max(area.left(), min(x, area.right() - self.bubble.width() + 1))
        # If there is no room above, place the bubble below and flip the tail upward
        # so the arrow still points at the Desktop Mate instead of toward empty space.
        below = y < area.top()
        if below:
            y = self.y() + self.height() - 20
        if self.bubble.tail_on_top != below:
            self.bubble.tail_on_top = below
            self.bubble.update()
        self.bubble.move(x, y)

    def make_movie(self, path):
        movie = QtGui.QMovie(str(path))
        movie.setScaledSize(QtCore.QSize(150, 150))
        movie.frameChanged.connect(lambda _frame, m=movie: self.update_movie_frame(m))
        return movie

    def load_pixmap(self, path):
        pixmap = QtGui.QPixmap(str(path)).scaled(
            150, 150,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation,
        )
        if pixmap.isNull():
            raise RuntimeError(f"Could not load {path.name}")
        return pixmap

    def set_animation(self, name):
        if name == "drag":
            if self.movie is not None:
                self.movie.stop()
            self.movie = None
            self.state = "drag"
            self.draw_drag_pose()
            return

        if name == "fall_ground_hit":
            if self.movie is not None:
                self.movie.stop()
            self.movie = None
            self.state = "fall_ground_hit"
            image = self.falling_ground_hit_pixmap
            if self.direction > 0:
                image = image.transformed(QtGui.QTransform().scale(-1, 1))
            self.character.setPixmap(image)
            return

        if name == "celebrate":
            if self.movie is not None:
                self.movie.stop()
            self.movie = None
            self.state = "celebrate"
            image = self.celebrate_pixmap
            if self.direction > 0:
                image = image.transformed(QtGui.QTransform().scale(-1, 1))
            self.character.setPixmap(image)
            return
        if name == "sit":
            if self.movie is not None:
                self.movie.stop()
            self.movie = None
            self.state = "sit"
            image = self.sit_pixmap
            if self.direction > 0:
                image = image.transformed(QtGui.QTransform().scale(-1, 1))
            self.character.setPixmap(image)
            return

        movies = {
            "walk": self.walk_movie,
            "idle": self.idle_movie,
            "run": self.run_movie,
            "stop": self.stop_movie,
            "fly_diagonal": self.fly_diagonal_movie,
            "fly_up": self.fly_up_movie,
            "climb": self.climb_movie,
            "petting": self.petting_movie,
            "sitting_petting": self.sitting_petting_movie,
            "falling": self.falling_movie,
            "sitting_dizzy": self.sitting_dizzy_movie,
            "sitting_idle": self.sitting_idle_movie,
            "sitting_happy": self.sitting_happy_movie,
            "hanging_idle": self.hanging_idle_movie,
            "hanging_petting": self.hanging_petting_movie,
            "shamisen": self.shamisen_movie,
        }
        wanted = movies[name]
        if self.movie is not None and self.movie is not wanted:
            self.movie.stop()
        self.movie = wanted
        self.state = name
        self.movie.start()
        self.update_movie_frame(self.movie)

    def update_movie_frame(self, movie):
        if getattr(self, "shutting_down", False):
            return
        if self.state in ("drag", "sit", "celebrate", "fall_ground_hit") or movie is None or movie is not self.movie:
            return
        frame = movie.currentPixmap()
        if frame.isNull():
            return
        if self.direction > 0:
            frame = frame.transformed(QtGui.QTransform().scale(-1, 1))
        self.character.setPixmap(frame)

    def draw_drag_pose(self):
        image = self.drag_pixmap
        if self.direction > 0:
            image = image.transformed(QtGui.QTransform().scale(-1, 1))
        transform = QtGui.QTransform()
        transform.rotate(self.drag_tilt)
        image = image.transformed(transform, QtCore.Qt.TransformationMode.SmoothTransformation)
        self.character.setPixmap(image)

    def ensure_topmost(self):
        self.raise_()
        if sys.platform == "win32":
            try:
                user32 = ctypes.windll.user32
                HWND_TOPMOST = -1
                SWP_NOMOVE = 0x0002
                SWP_NOSIZE = 0x0001
                SWP_NOACTIVATE = 0x0010
                SWP_SHOWWINDOW = 0x0040
                user32.SetWindowPos(
                    int(self.winId()), HWND_TOPMOST, 0, 0, 0, 0,
                    SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW
                )
                if self.quote_visible:
                    user32.SetWindowPos(
                        int(self.bubble.winId()), HWND_TOPMOST, 0, 0, 0, 0,
                        SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW
                    )
            except (AttributeError, OSError):
                pass

    def current_area(self):
        screen = QtGui.QGuiApplication.screenAt(self.frameGeometry().center())
        if screen is None:
            screen = QtGui.QGuiApplication.primaryScreen()
        return screen.availableGeometry() if screen else None

    def ground_y(self):
        area = self.current_area()
        if area is None:
            return self.y()
        extra = self.SIT_FEET_OFFSET if self.state == "sit" else 0
        return area.bottom() - self.height() + 1 + self.FEET_OFFSET + extra

    def move_to_ground(self):
        area = self.current_area()
        if area is not None:
            x = max(area.left(), min(self.x(), area.right() - self.width() + 1))
            self.move(x, self.ground_y())

    def schedule_idle(self):
        if self.walking and not self.dragging and not self.airborne and self.state == "walk":
            self.idle_timer.start(random.randint(3000, 7000))

    def start_idle(self):
        if self.walking and not self.dragging and not self.airborne and self.state == "walk":
            self.set_animation("idle")
            self.resume_timer.start(random.randint(1000, 2500))

    def finish_idle(self):
        if self.walking and not self.dragging and not self.airborne and self.state == "idle":
            self.set_animation("walk")
            self.schedule_idle()

    def start_running(self):
        if not self.walking or self.dragging or self.airborne or self.state != "walk":
            return
        self.idle_timer.stop()
        self.resume_timer.stop()
        self.set_animation("run")
        self.run_timer.start(random.randint(1200, 2600))

    def start_stopping(self):
        if self.dragging or self.airborne or self.state != "run":
            return
        self.stop_velocity = self.run_speed * self.direction
        self.set_animation("stop")
        # Let the stopping GIF play while momentum is being reduced.
        self.stop_timer.start(900)

    def finish_stopping(self):
        if self.state != "stop" or self.dragging or self.airborne:
            return
        # The animation can finish before the slide has completely decelerated.
        if abs(self.stop_velocity) <= 0.35:
            self.stop_velocity = 0.0
            self.set_animation("idle")
            self.resume_timer.start(random.randint(500, 1200))
        else:
            self.stop_timer.start(120)

    def land_and_sit(self):
        self.airborne = False
        self.velocity_y = 0.0
        self.run_timer.stop()
        self.stop_timer.stop()
        self.stop_velocity = 0.0
        self.set_animation("sit")
        self.move(self.x(), self.ground_y())
        self.sit_timer.start(1400)

    def finish_sitting(self):
        if self.state != "sit" or self.dragging or self.airborne:
            return
        if self.manual_sitting:
            self.walking = False
            self.change_manual_sit_pose()
            return
        self.set_animation("walk" if self.walking else "idle")
        self.move_to_ground()
        self.schedule_idle()

    def release_is_high_fall(self):
        area = self.current_area()
        if area is None:
            return False
        threshold = area.top() + int(area.height() * self.HARD_FALL_SCREEN_FRACTION)
        # Use the mate center so "above half the screen" matches what is seen visually.
        return self.frameGeometry().center().y() < threshold

    def start_hard_fall(self):
        self.hard_fall = True
        self.recovery_jump = False
        self.hard_fall_ground_y = self.ground_y()
        self.airborne = True
        self.velocity_y = 0.0
        self.set_animation("falling")

    def hard_fall_impact(self):
        self.airborne = False
        self.velocity_y = 0.0
        self.move(self.x(), self.hard_fall_ground_y + self.FALLING_GROUND_HIT_OFFSET)
        self.set_animation("fall_ground_hit")
        QtCore.QTimer.singleShot(self.HARD_FALL_IMPACT_MS, self.start_dizzy_recovery)

    def start_dizzy_recovery(self):
        if not self.hard_fall:
            return
        self.move(self.x(), self.hard_fall_ground_y + self.SITTING_DIZZY_GROUND_OFFSET)
        self.set_animation("sitting_dizzy")
        QtCore.QTimer.singleShot(self.HARD_FALL_DIZZY_MS, self.start_silent_recovery_jump)

    def start_silent_recovery_jump(self):
        if not self.hard_fall:
            return
        self.recovery_jump = True
        self.recovery_ground_y = self.ground_y() + self.RECOVERY_GROUND_OFFSET
        self.move(self.x(), self.recovery_ground_y)
        self.recovery_velocity_y = self.RECOVERY_JUMP_VELOCITY
        # Reuse celebration PNG, intentionally DO NOT call yay_player.play().
        self.set_animation("celebrate")

    def update_silent_recovery_jump(self):
        self.recovery_velocity_y += self.RECOVERY_GRAVITY
        new_y = self.y() + int(round(self.recovery_velocity_y))
        if new_y >= self.recovery_ground_y and self.recovery_velocity_y > 0:
            self.move(self.x(), self.recovery_ground_y)
            self.recovery_jump = False
            self.hard_fall = False
            self.recovery_velocity_y = 0.0
            if self.manual_sitting:
                self.walking = False
                self.change_manual_sit_pose()
            else:
                self.set_animation("walk" if self.walking else "idle")
                self.schedule_idle()
            return
        self.move(self.x(), new_y)

    @QtCore.Slot(bool)
    def set_celebration_sound_enabled(self, enabled):
        self.celebration_sound_enabled = bool(enabled)
        if not self.celebration_sound_enabled:
            self.yay_player.stop()

    def start_celebration(self):
        if self.chrono_clock_attached or self.chrono_clock_trip:
            return
        if self.dragging or self.airborne or self.celebrating:
            return
        self.idle_timer.stop()
        self.resume_timer.stop()
        self.run_timer.stop()
        self.stop_timer.stop()
        self.sit_timer.stop()
        self.manual_sit_timer.stop()
        self.stop_velocity = 0.0
        self.celebrating = True
        self.set_animation("walk")
        if self.platform_hwnd:
            rect = self.window_rect(self.platform_hwnd)
            if rect is not None:
                x = rect.left() + self.platform_offset_x
                x = max(rect.left(), min(x, rect.right() - self.width()))
                self.move(x, rect.top() - self.height() + self.FEET_OFFSET)
            else:
                self.platform_hwnd = None
                self.move_to_ground()
        else:
            self.move_to_ground()
        self.celebrate_ground_y = self.y()
        self.set_animation("celebrate")
        self.celebrate_velocity_y = self.CELEBRATE_JUMP_VELOCITY
        if self.celebration_sound_enabled:
            self.yay_player.setPosition(0)
            self.yay_player.play()

    def update_celebration(self):
        platform_x = self.x()
        if self.platform_hwnd:
            rect = self.window_rect(self.platform_hwnd)
            if rect is None:
                self.platform_hwnd = None
            else:
                platform_x = rect.left() + self.platform_offset_x
                platform_x = max(rect.left(), min(platform_x, rect.right() - self.width()))
                self.celebrate_ground_y = rect.top() - self.height() + self.FEET_OFFSET
        self.celebrate_velocity_y += self.CELEBRATE_GRAVITY
        new_y = self.y() + int(round(self.celebrate_velocity_y))
        if new_y >= self.celebrate_ground_y and self.celebrate_velocity_y > 0:
            self.move(platform_x, self.celebrate_ground_y)
            self.celebrating = False
            self.celebrate_velocity_y = 0.0
            self.set_animation("walk" if self.walking else "idle")
            self.schedule_idle()
            return
        self.move(platform_x, new_y)

    def window_rect(self, hwnd):
        if sys.platform != "win32" or not hwnd:
            return None
        u = ctypes.windll.user32
        if not u.IsWindow(hwnd) or not u.IsWindowVisible(hwnd) or u.IsIconic(hwnd) or u.IsZoomed(hwnd):
            return None
        r = wintypes.RECT()
        if not u.GetWindowRect(hwnd, ctypes.byref(r)):
            return None
        return QtCore.QRect(r.left, r.top, r.right-r.left, r.bottom-r.top)

    def desktop_windows(self):
        if sys.platform != "win32":
            return []
        u = ctypes.windll.user32
        own = int(self.winId())
        result = []
        CB = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        def each(hwnd, _):
            if int(hwnd) == own or not u.IsWindowVisible(hwnd) or u.IsIconic(hwnd) or u.IsZoomed(hwnd):
                return True
            # Ignore owned popup/tool windows.
            if u.GetWindow(hwnd, 4):
                return True
            r = wintypes.RECT()
            if not u.GetWindowRect(hwnd, ctypes.byref(r)):
                return True
            w, h = r.right-r.left, r.bottom-r.top
            if w < 240 or h < 140:
                return True
            # Extra maximized/full-work-area guard, including borderless windows.
            screen = QtGui.QGuiApplication.screenAt(QtCore.QPoint(r.left + w//2, r.top + h//2))
            if screen:
                a = screen.availableGeometry()
                if w >= a.width()-8 and h >= a.height()-8:
                    return True
            result.append((int(hwnd), QtCore.QRect(r.left, r.top, w, h)))
            return True
        callback = CB(each)
        u.EnumWindows(callback, 0)
        return result

    def climb_side_is_exposed(self, hwnd, rect, side):
        """Reject a side when another top-level window is actually in front of it."""
        if sys.platform != "win32":
            return True
        u = ctypes.windll.user32
        own = int(self.winId())
        target = int(hwnd)
        # Sample the intended lower side plus mid-side. WindowFromPoint respects Z-order.
        x = rect.left() + 3 if side == "left" else rect.right() - 4
        ys = [rect.bottom() - 12, rect.bottom() - min(70, max(20, rect.height()//4)),
              rect.top() + rect.height()//2]
        visible_hits = 0
        for y in ys:
            hit = int(u.WindowFromPoint(wintypes.POINT(x, y)))
            if hit == own:
                continue
            root = int(u.GetAncestor(hit, 2)) if hit else 0  # GA_ROOT
            if hit == target or root == target:
                visible_hits += 1
        return visible_hits >= 2

    @QtCore.Slot(bool)
    def set_climbing_enabled(self, enabled):
        self.climbing_enabled = bool(enabled)
        self.window_scan_ticks = 0
        if not self.climbing_enabled:
            self.climb_target = None
            self.climb_side = None

    def find_climb_target(self):
        if not self.climbing_enabled:
            return None
        if self.platform_hwnd or self.state not in ("walk", "idle"):
            return None
        cx = self.x() + self.width()//2
        feet_y = self.y() + self.height() - self.FEET_OFFSET
        best = None
        best_score = 10**9
        for hwnd, r in self.desktop_windows():
            # Need a real vertical side above the desktop mate.
            if r.top() >= feet_y - 35:
                continue
            left_dist = abs(r.left() - cx)
            right_dist = abs(r.right() - cx)
            choices = [(left_dist, "left"), (right_dist, "right")]
            choices.sort(key=lambda item: item[0])
            side = None
            dx = None
            for candidate_dist, candidate_side in choices:
                if candidate_dist <= self.WINDOW_TARGET_DISTANCE and self.climb_side_is_exposed(hwnd, r, candidate_side):
                    side = candidate_side
                    dx = candidate_dist
                    break
            if side is None:
                continue
            # Goal is the BOTTOM of the chosen side, not the top.
            bottom_attach_y = r.bottom() - self.height() + self.FEET_OFFSET
            vertical = abs(bottom_attach_y - self.y())
            score = dx + vertical * 0.65
            if score < best_score:
                best_score = score
                best = (hwnd, side)
        return best

    def begin_window_climb(self, target):
        if not self.climbing_enabled or not target:
            return
        self.climb_target, self.climb_side = target
        self.direction = -1 if self.climb_side == "left" else 1
        self.idle_timer.stop(); self.resume_timer.stop(); self.run_timer.stop()
        self.stop_timer.stop(); self.sit_timer.stop()
        self.stop_velocity = 0.0
        rect = self.window_rect(self.climb_target)
        if rect is None:
            self.climb_target = None
            return
        bottom_y = rect.bottom() - self.height() + self.FEET_OFFSET
        self.set_animation("fly_diagonal")

    def update_climb_trip(self):
        rect = self.window_rect(self.climb_target)
        if rect is None or not self.climb_side_is_exposed(self.climb_target, rect, self.climb_side):
            self.climb_target = None; self.climb_side = None
            self.airborne = True; self.velocity_y = 0.0; self.set_animation("idle")
            return

        # Flight faces its actual horizontal travel direction. Climbing itself is locked
        # to the selected wall side to avoid a one-frame wrong-side flash.
        attach_x = (rect.left() - self.width() + self.CLIMB_LEFT_INSET
                    if self.climb_side == "left"
                    else rect.right() - self.CLIMB_RIGHT_INSET)
        bottom_y = rect.bottom() - self.height() + self.FEET_OFFSET - self.CLIMB_BOTTOM_LIFT
        top_y = rect.top() - self.height() + self.FEET_OFFSET

        if self.state in ("fly_diagonal", "fly_up"):
            dx, dy = attach_x - self.x(), bottom_y - self.y()
            if self.state == "fly_diagonal" and abs(dx) > 1:
                wanted_direction = 1 if dx > 0 else -1
                if wanted_direction != self.direction:
                    self.direction = wanted_direction
                    self.update_movie_frame(self.movie)
            # Diagonal flight moves horizontal AND vertical together. Fly-up is used
            # only once the mate is nearly aligned horizontally and target is above.
            if abs(dx) > 30:
                wanted = "fly_diagonal"
                step_x = max(-self.fly_speed, min(self.fly_speed, dx))
                if abs(dy) > 3:
                    step_y = max(-self.fly_speed, min(self.fly_speed, dy))
                else:
                    step_y = 0
            elif dy < -6:
                wanted = "fly_up"
                step_x = max(-2, min(2, dx))
                step_y = max(-self.fly_speed, dy)
            else:
                wanted = "fly_diagonal"
                step_x = max(-self.fly_speed, min(self.fly_speed, dx))
                step_y = max(-self.fly_speed, min(self.fly_speed, dy))
            if self.state != wanted:
                if wanted == "fly_diagonal" and abs(dx) > 1:
                    self.direction = 1 if dx > 0 else -1
                self.set_animation(wanted)
            self.move(self.x()+step_x, self.y()+step_y)
            if abs(dx) <= self.fly_speed and abs(dy) <= self.fly_speed:
                self.move(attach_x, bottom_y)
                self.direction = -1 if self.climb_side == "left" else 1
                self.set_animation("climb")
            return

        if self.state == "climb":
            wall_direction = -1 if self.climb_side == "left" else 1
            if self.direction != wall_direction:
                self.direction = wall_direction
                self.update_movie_frame(self.movie)
            if self.y() - self.climb_speed <= top_y:
                self.start_top_jump(rect, top_y)
            else:
                self.move(attach_x, self.y()-self.climb_speed)

    def start_top_jump(self, rect, top_y):
        side = self.climb_side
        landing_x = (rect.left() + 18 if side == "left"
                     else rect.right() - self.width() - 18)
        landing_x = max(rect.left(), min(landing_x, rect.right()-self.width()))
        self.platform_hwnd = self.climb_target
        self.climb_target = None; self.climb_side = None
        self.top_jump = {"sx": self.x(), "sy": top_y, "lx": landing_x,
                         "ly": top_y, "frame": 0, "frames": 22}
        self.set_animation("idle")
        self.move(self.top_jump["sx"], top_y)

    def update_top_jump(self):
        j = self.top_jump
        j["frame"] += 1
        t = min(1.0, j["frame"] / j["frames"])
        x = round(j["sx"] + (j["lx"]-j["sx"])*t)
        y = round(j["ly"] - 4*self.TOP_JUMP_HEIGHT*t*(1-t))
        self.move(x, y)
        if t >= 1.0:
            rect = self.window_rect(self.platform_hwnd)
            self.platform_offset_x = j["lx"]-rect.left() if rect else 0
            self.top_jump = None
            self.set_animation("idle")
            QtCore.QTimer.singleShot(450, self.finish_window_landing)

    def finish_window_landing(self):
        if self.platform_hwnd and not self.dragging and not self.airborne and not self.top_jump:
            self.set_animation("walk" if self.walking else "idle")

    def platform_is_occluded(self, rect):
        """True when a higher Z-order window covers the mate's support point."""
        if sys.platform != "win32" or not self.platform_hwnd:
            return False
        u = ctypes.windll.user32
        # Test several pixels immediately above the supporting top edge.
        y = rect.top() + 2
        xs = [self.x()+self.width()//3, self.x()+self.width()//2,
              self.x()+(2*self.width())//3]
        own = int(self.winId())
        for x in xs:
            hwnd = int(u.WindowFromPoint(wintypes.POINT(x, y)))
            if hwnd not in (0, own, int(self.platform_hwnd)):
                root = int(u.GetAncestor(hwnd, 2))  # GA_ROOT
                if root not in (0, own, int(self.platform_hwnd)):
                    return True
        return False

    def sync_window_platform(self):
        if not self.platform_hwnd:
            return False
        rect = self.window_rect(self.platform_hwnd)
        if rect is None or self.platform_is_occluded(rect):
            platform_y = self.y()
            self.platform_hwnd = None
            self.top_jump = None
            area = self.current_area()
            if area is not None and (platform_y + self.height() // 2) < area.top() + int(area.height() * self.HARD_FALL_SCREEN_FRACTION):
                self.start_hard_fall()
            else:
                self.airborne = True
                self.velocity_y = 0.0
                self.set_animation("idle")
            return False
        y = rect.top() - self.height() + self.FEET_OFFSET
        x = rect.left() + self.platform_offset_x
        x = max(rect.left(), min(x, rect.right()-self.width()))
        self.move(x, y)
        self.platform_offset_x = x-rect.left()
        return True

    def set_chrono_clock_window(self, window):
        self.chrono_clock_window = window

    def clear_chrono_clock_window(self):
        self.chrono_clock_window = None
        if self.chrono_clock_attached or self.chrono_clock_trip:
            self.go_down_from_chrono_clock()

    def begin_chrono_clock_trip(self):
        clock = self.chrono_clock_window
        if clock is None or not clock.isVisible() or self.chrono_clock_attached or self.chrono_clock_trip:
            return
        self.manual_sitting = False
        self.drag_started_while_sitting = False
        self.manual_sit_timer.stop()
        self.sit_timer.stop()
        self.petting_stop_timer.stop()
        if self.petting:
            self.petting = False
            self.reset_pet_gesture()
        self.chrono_clock_trip = True
        self.chrono_clock_phase = "fly"
        self.walking = False
        self.platform_hwnd = None
        self.climb_target = None
        self.idle_timer.stop(); self.resume_timer.stop(); self.run_timer.stop(); self.stop_timer.stop()
        self.set_animation("fly_diagonal")

    def _clock_left_climb_x(self):
        clock = self.chrono_clock_window
        if clock is None:
            return None
        g = clock.frameGeometry()
        return g.left() - self.width() + self.CLIMB_LEFT_INSET

    def _clock_attach_point(self):
        clock = self.chrono_clock_window
        if clock is None:
            return None
        g = clock.frameGeometry()
        return QtCore.QPoint(g.left() - 35, g.top() - 113)

    def update_chrono_clock_trip(self):
        clock = self.chrono_clock_window
        if clock is None or not clock.isVisible():
            self.go_down_from_chrono_clock()
            return

        g = clock.frameGeometry()
        climb_x = self._clock_left_climb_x()

        if self.chrono_clock_phase == "fly":
            tx = climb_x
            ty = g.bottom() - self.height() + self.FEET_OFFSET - self.CLIMB_BOTTOM_LIFT
            dx = tx - self.x()
            dy = ty - self.y()
            if abs(dx) > 2:
                self.direction = 1 if dx > 0 else -1
            self.move(
                self.x() + max(-5, min(5, dx)),
                self.y() + max(-5, min(5, dy))
            )
            if abs(dx) <= 5 and abs(dy) <= 5:
                self.move(tx, ty)
                self.chrono_clock_phase = "climb"
                self.direction = -1
                self.set_animation("climb")
            return

        if self.chrono_clock_phase == "climb":
            target_y = g.top() - self.height() + self.FEET_OFFSET + 34
            self.direction = -1
            if self.y() - self.climb_speed <= target_y:
                self.move(climb_x, target_y)
                self.chrono_clock_phase = "jump"
                self.chrono_clock_target_y = target_y
                self.set_animation("idle")
                return
            self.move(climb_x, self.y() - self.climb_speed)
            return

        if self.chrono_clock_phase == "jump":
            point = self._clock_attach_point()
            if point is None:
                self.go_down_from_chrono_clock()
                return
            dx = point.x() - self.x()
            dy = point.y() - self.y()
            self.move(
                self.x() + max(-6, min(6, dx)),
                self.y() + max(-6, min(6, dy))
            )
            if abs(dx) <= 6 and abs(dy) <= 6:
                self.chrono_clock_trip = False
                self.chrono_clock_phase = None
                self.chrono_clock_attached = True
                self.walking = False
                self.airborne = False
                self.direction = -1
                self.move(point)
                self.set_animation("hanging_idle")

    def sync_chrono_clock_attachment(self):
        if not self.chrono_clock_attached:
            return
        point = self._clock_attach_point()
        if point is None:
            self.go_down_from_chrono_clock()
            return
        self.move(point)

    def play_shamisen(self):
        if not self.chrono_clock_attached:
            return
        if not self.shamisen_playing:
            self.shamisen_playing = True
            self.set_animation("shamisen")
        self._play_random_shamisen_track()

    def _play_random_shamisen_track(self):
        path = random.choice(self.shamisen_track_paths)
        self.shamisen_current_track = path
        self.shamisen_player.stop()
        self.shamisen_player.setSource(QtCore.QUrl.fromLocalFile(str(path)))
        self.shamisen_player.setPosition(0)
        self.shamisen_player.play()

    def _on_shamisen_media_status(self, status):
        if status == QtMultimedia.QMediaPlayer.MediaStatus.EndOfMedia and self.shamisen_playing and self.chrono_clock_attached:
            self._play_random_shamisen_track()

    def stop_shamisen(self):
        if not self.shamisen_playing:
            return
        self.shamisen_playing = False
        self.shamisen_player.stop()
        self.shamisen_current_track = None
        if self.chrono_clock_attached:
            self.set_animation("hanging_idle")

    def set_shamisen_volume(self, percent):
        percent = max(0, min(100, int(percent)))
        self.shamisen_volume = percent
        self.shamisen_audio.setVolume(percent / 100.0)

    def go_down_from_chrono_clock(self):
        self.shamisen_player.stop()
        self.chrono_clock_attached = False
        self.chrono_clock_trip = False
        self.chrono_clock_phase = None
        self.hanging_petting = False
        self.shamisen_playing = False
        self.walking = True
        self.airborne = True
        self.velocity_y = 0.0
        self.set_animation("falling")

    def update_motion(self):
        self.position_bubble()
        if self.chrono_clock_trip:
            self.update_chrono_clock_trip()
            return
        if self.chrono_clock_attached:
            self.sync_chrono_clock_attachment()
            return
        self.position_active_menu()
        if self.recovery_jump:
            self.update_silent_recovery_jump()
            return
        if self.top_jump:
            self.update_top_jump()
            return
        if self.state in ("fly_diagonal", "fly_up", "climb"):
            self.update_climb_trip()
            return
        if self.celebrating:
            self.update_celebration()
            return
        if self.platform_hwnd:
            if not self.sync_window_platform():
                return
        if self.petting:
            now = QtCore.QDateTime.currentMSecsSinceEpoch()
            if now - self.petting_last_active_ms >= self.PETTING_KEEPALIVE_MS:
                self.stop_petting()
            else:
                return
        # Manual sitting freezes autonomous behavior only while actually grounded.
        # If the mate was released in mid-air, gravity must run before sitting resumes.
        if self.manual_sitting and not self.airborne and not self.dragging:
            return
        if self.dragging:
            self.drag_tilt += (self.target_drag_tilt - self.drag_tilt) * 0.55
            self.target_drag_tilt *= 0.88
            if abs(self.target_drag_tilt) < 0.05:
                self.target_drag_tilt = 0.0
            if self.target_drag_tilt == 0.0:
                self.drag_tilt *= 0.88
            if abs(self.drag_tilt) < 0.05:
                self.drag_tilt = 0.0
            self.draw_drag_pose()
            return

        if self.airborne:
            self.apply_gravity()
            return

        if not self.walking:
            return

        if self.state == "walk":
            if self.climbing_enabled and not self.platform_hwnd and sys.platform == "win32":
                self.window_scan_ticks += 1
                if self.window_scan_ticks >= self.WINDOW_SCAN_EVERY:
                    self.window_scan_ticks = 0
                    target = self.find_climb_target()
                    if target and random.random() < 0.10:
                        self.begin_window_climb(target)
                        return
            if random.random() < self.run_chance:
                self.start_running()
            else:
                self.move_horizontal(float(self.walk_speed * self.direction))
        elif self.state == "run":
            self.move_horizontal(self.run_speed * self.direction)
        elif self.state == "stop":
            self.move_horizontal(self.stop_velocity)
            self.stop_velocity *= 0.90
            if abs(self.stop_velocity) < 0.35:
                self.stop_velocity = 0.0

    def should_fall_from_window_edge(self):
        if self.edge_fall_decision is None:
            self.edge_fall_decision = random.random() < self.EDGE_FALL_CHANCE
        return self.edge_fall_decision

    def start_platform_fall(self, x, platform_y):
        # A window can be high enough to count as a hard fall too.
        area = self.current_area()
        hard = False
        if area is not None:
            threshold = area.top() + int(area.height() * self.HARD_FALL_SCREEN_FRACTION)
            hard = (platform_y + self.height() // 2) < threshold
        self.platform_hwnd = None
        self.platform_offset_x = 0
        self.edge_fall_decision = None
        self.move(x, platform_y)
        if hard:
            self.start_hard_fall()
        else:
            self.airborne = True
            self.velocity_y = 0.0
            self.set_animation("idle")

    def move_horizontal(self, amount):
        # On a window top, never walk into empty space. Turn around at the real edges.
        if self.platform_hwnd:
            rect = self.window_rect(self.platform_hwnd)
            if rect is None:
                self.platform_hwnd = None
                self.airborne = True; self.velocity_y = 0.0; self.set_animation("idle")
                return
            x = self.x() + int(round(amount))
            left_limit = rect.left()
            right_limit = rect.right() - self.width()
            near_left = x <= left_limit
            near_right = x >= right_limit
            if near_left or near_right:
                old_platform_y = rect.top()-self.height()+self.FEET_OFFSET
                if self.should_fall_from_window_edge():
                    # Deliberately step just beyond the chosen edge, then use normal/high-fall physics.
                    fall_x = left_limit - 6 if near_left else right_limit + 6
                    self.start_platform_fall(fall_x, old_platform_y)
                    return
                # This time, choose not to fall and turn back across the window.
                x = left_limit if near_left else right_limit
                self.direction = 1 if near_left else -1
                if self.state == "stop":
                    self.stop_velocity = abs(self.stop_velocity) if near_left else -abs(self.stop_velocity)
                self.edge_fall_decision = None
                self.update_movie_frame(self.movie)
            else:
                # Only make a new random decision on the next edge encounter.
                self.edge_fall_decision = None
            self.platform_offset_x = x-rect.left()
            self.move(x, rect.top()-self.height()+self.FEET_OFFSET)
            return

        area = self.current_area()
        if area is None:
            return
        x = self.x() + int(round(amount))
        if x <= area.left():
            x = area.left(); self.direction = 1
            if self.state == "stop": self.stop_velocity = abs(self.stop_velocity)
            self.update_movie_frame(self.movie)
        elif x + self.width() >= area.right() + 1:
            x = area.right() - self.width() + 1; self.direction = -1
            if self.state == "stop": self.stop_velocity = -abs(self.stop_velocity)
            self.update_movie_frame(self.movie)
        self.move(x, self.ground_y())

    def apply_gravity(self):
        ground = self.ground_y()
        self.velocity_y = min(self.velocity_y + self.gravity, self.max_fall_speed)
        new_y = self.y() + max(1, int(self.velocity_y))
        if new_y >= ground:
            self.move(self.x(), ground)
            if self.hard_fall:
                self.hard_fall_impact()
            else:
                self.land_and_sit()
            return
        self.move(self.x(), new_y)

    def reset_pet_gesture(self):
        self.pet_last_x = None
        self.pet_last_sign = 0
        self.pet_strokes = 0
        self.pet_last_move_ms = 0

    def can_be_petted(self):
        if self.chrono_clock_attached and not self.shamisen_playing:
            return True
        return (not self.dragging and not self.airborne and not self.celebrating
                and not self.hard_fall and not self.recovery_jump
                and not self.top_jump and self.state not in ("fly_diagonal", "fly_up", "climb", "drag"))

    def start_petting(self):
        if self.petting or not self.can_be_petted():
            return
        if self.chrono_clock_attached:
            self.petting = True
            self.hanging_petting = True
            self.set_animation("hanging_petting")
            self.petting_last_active_ms = QtCore.QDateTime.currentMSecsSinceEpoch()
            return
        self.petting = True
        self.idle_timer.stop(); self.resume_timer.stop(); self.run_timer.stop()
        self.stop_timer.stop(); self.sit_timer.stop()
        if self.manual_sitting:
            self.manual_sit_timer.stop()
        self.stop_velocity = 0.0
        self.set_animation("sitting_petting" if self.manual_sitting else "petting")
        self.petting_last_active_ms = QtCore.QDateTime.currentMSecsSinceEpoch()
        # Keep direction history alive so continued left/right strokes refresh the loop.
        self.pet_strokes = 0

    def stop_petting(self):
        if not self.petting:
            return
        self.petting = False
        self.petting_stop_timer.stop()
        self.reset_pet_gesture()
        if self.chrono_clock_attached:
            self.hanging_petting = False
            self.set_animation("hanging_idle")
            return
        if not self.dragging and not self.airborne:
            if self.manual_sitting:
                self.manual_sit_timer.stop()
                # petting is already False, so this immediately replaces sitting_petting
                # with a fresh 60/40 idle/happy sitting pose.
                self.change_manual_sit_pose()
            else:
                self.set_animation("walk" if self.walking else "idle")
                self.schedule_idle()

    def finish_petting_if_inactive(self):
        if not self.petting:
            return
        now = QtCore.QDateTime.currentMSecsSinceEpoch()
        remaining = self.PETTING_KEEPALIVE_MS - (now - self.petting_last_active_ms)
        if remaining > 0:
            self.petting_stop_timer.start(int(remaining))
            return
        self.stop_petting()

    def detect_petting(self, local_pos, global_x):
        if not self.can_be_petted() and not self.petting:
            self.reset_pet_gesture()
            return
        if not self.PET_HEAD_RECT.contains(local_pos):
            if self.petting:
                self.stop_petting()
            else:
                self.reset_pet_gesture()
            return
        now = QtCore.QDateTime.currentMSecsSinceEpoch()
        if self.pet_last_move_ms and now - self.pet_last_move_ms > self.PET_GESTURE_TIMEOUT_MS and not self.petting:
            self.reset_pet_gesture()
        self.pet_last_move_ms = now
        if self.pet_last_x is None:
            self.pet_last_x = global_x
            return
        dx = global_x - self.pet_last_x
        if abs(dx) < 4:
            return
        sign = 1 if dx > 0 else -1
        direction_changed = bool(self.pet_last_sign and sign != self.pet_last_sign)
        if direction_changed:
            self.pet_strokes += 1
            if self.petting:
                # Keep the petting GIF alive only while genuine left/right strokes continue.
                self.petting_last_active_ms = now
            elif self.pet_strokes >= self.PET_STROKES_NEEDED:
                self.start_petting()
                self.pet_last_sign = sign
                self.pet_last_x = global_x
                return
        self.pet_last_sign = sign
        self.pet_last_x = global_x

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            if self.chrono_clock_attached:
                event.accept()
                return
            if self.celebrating or self.hard_fall or self.recovery_jump or self.state in ("fly_diagonal", "fly_up", "climb", "falling", "fall_ground_hit", "sitting_dizzy"):
                event.accept()
                return
            # Repositioning does not exit manual sitting. Only Resume Walking does.
            self.drag_started_while_sitting = self.manual_sitting
            if self.manual_sitting:
                self.manual_sit_timer.stop()
                self.sit_timer.stop()
            self.platform_hwnd = None
            self.dragging = True
            self.airborne = False
            self.velocity_y = 0.0
            self.stop_velocity = 0.0
            self.idle_timer.stop()
            self.resume_timer.stop()
            self.run_timer.stop()
            self.stop_timer.stop()
            self.sit_timer.stop()

            cursor = event.globalPosition().toPoint()
            self.drag_offset = cursor - self.frameGeometry().topLeft()
            self.last_drag_x = cursor.x()
            self.drag_tilt = 0.0
            self.target_drag_tilt = 0.0
            self.set_animation("drag")
            event.accept()
            return

        if event.button() == QtCore.Qt.MouseButton.RightButton:
            self.show_menu(event.globalPosition().toPoint())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.chrono_clock_attached:
            if not self.dragging:
                self.detect_petting(event.position().toPoint(), event.globalPosition().toPoint().x())
            event.accept()
            return
        if not self.dragging:
            self.detect_petting(event.position().toPoint(), event.globalPosition().toPoint().x())
            if self.petting:
                event.accept()
                return
        if self.dragging and event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            cursor = event.globalPosition().toPoint()
            dx = cursor.x() - self.last_drag_x if self.last_drag_x is not None else 0
            self.last_drag_x = cursor.x()

            if dx != 0:
                self.direction = 1 if dx > 0 else -1
                self.target_drag_tilt = max(-22.0, min(22.0, dx * 2.4))
            else:
                self.target_drag_tilt = 0.0

            self.move(cursor - self.drag_offset)
            self.draw_drag_pose()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        if self.petting:
            self.stop_petting()
        else:
            self.reset_pet_gesture()
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.chrono_clock_attached and event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()
            return
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.dragging = False
            self.last_drag_x = None
            self.drag_tilt = 0.0
            self.target_drag_tilt = 0.0

            ground = self.ground_y()
            if self.drag_started_while_sitting:
                self.drag_started_while_sitting = False
                self.walking = False
                if self.y() < ground:
                    # Preserve manual-sit mode, but gravity/fall reactions still apply.
                    if self.release_is_high_fall():
                        self.start_hard_fall()
                    else:
                        self.airborne = True
                        self.velocity_y = 0.0
                        self.set_animation("idle")
                else:
                    self.move(self.x(), ground)
                    self.land_and_sit()
            elif self.y() < ground:
                if self.release_is_high_fall():
                    self.start_hard_fall()
                else:
                    self.airborne = True
                    self.velocity_y = 0.0
                    self.set_animation("idle")
            else:
                self.move(self.x(), ground)
                self.land_and_sit()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def start_manual_sit(self):
        if self.dragging or self.airborne or self.celebrating or self.hard_fall or self.recovery_jump:
            return
        self.manual_sitting = True
        self.walking = False
        self.idle_timer.stop(); self.resume_timer.stop(); self.run_timer.stop()
        self.stop_timer.stop(); self.sit_timer.stop()
        self.stop_velocity = 0.0
        self.change_manual_sit_pose()

    def change_manual_sit_pose(self):
        if not self.manual_sitting or self.dragging or self.airborne or self.petting:
            return
        # Permanent sitting: randomly alternate 60% idle / 40% happy.
        self.set_animation("sitting_idle" if random.random() < 0.60 else "sitting_happy")
        self.move(self.x(), self.ground_y() + self.MANUAL_SIT_GROUND_OFFSET)
        self.manual_sit_timer.start(random.randint(
            self.MANUAL_SIT_SWITCH_MIN_MS, self.MANUAL_SIT_SWITCH_MAX_MS))

    def resume_from_manual_sit(self):
        self.drag_started_while_sitting = False
        self.manual_sitting = False
        self.manual_sit_timer.stop()
        self.walking = True
        self.move_to_ground()
        self.set_animation("walk")
        self.schedule_idle()

    @QtCore.Slot()
    def hide_koyomi(self):
        """Fully stop this Koyomi instance without leaving movie callbacks alive."""
        if getattr(self, "shutting_down", False):
            return
        self.shutting_down = True

        if self.active_menu is not None:
            self.active_menu.close()
            self.active_menu = None

        # Stop timers first so nothing schedules new UI work during shutdown.
        for timer in self.findChildren(QtCore.QTimer):
            timer.stop()

        # QMovie frameChanged callbacks can continue after QLabel teardown unless
        # every movie is stopped and disconnected first.
        for movie in (
            self.walk_movie, self.idle_movie, self.run_movie, self.stop_movie,
            self.fly_diagonal_movie, self.fly_up_movie, self.climb_movie,
            self.petting_movie, self.sitting_petting_movie, self.falling_movie,
            self.sitting_dizzy_movie, self.sitting_idle_movie, self.sitting_happy_movie,
            self.hanging_idle_movie, self.hanging_petting_movie, self.shamisen_movie,
        ):
            if movie is not None:
                movie.stop()
                try:
                    movie.frameChanged.disconnect()
                except (RuntimeError, TypeError):
                    pass

        self.movie = None
        self.quote_visible = False
        self.yay_player.stop()
        self.shamisen_player.stop()
        self.bubble.hide()
        self.bubble.close()
        self.character.clear()
        self.hidden_by_user.emit()
        self.close()
        self.deleteLater()

    def closeEvent(self, event):
        self.bubble.close()
        super().closeEvent(event)

    def position_active_menu(self):
        if self.active_menu is None or not self.active_menu.isVisible():
            return
        # Fixed anchor: menu's top-left sits just to the right of Desktop Mate's top-right.
        if self.chrono_clock_attached:
            anchor = QtCore.QPoint(
                self.x() - self.active_menu.width() + 72,
                self.y() + 92
            )
        else:
            anchor = QtCore.QPoint(
                self.x() + self.width() + self.MENU_ANCHOR_GAP,
                self.y()
            )
        screen = QtGui.QGuiApplication.screenAt(self.frameGeometry().center())
        if screen is not None:
            area = screen.availableGeometry()
            x = max(area.left(), min(anchor.x(), area.right() - self.active_menu.width() + 1))
            y = max(area.top(), min(anchor.y(), area.bottom() - self.active_menu.height() + 1))
            anchor = QtCore.QPoint(x, y)
        self.active_menu.move(anchor)

    def show_menu(self, position):
        if self.active_menu is not None:
            self.active_menu.close()

        menu = QtWidgets.QMenu()
        if self.chrono_clock_attached:
            menu.setWindowFlag(
                QtCore.Qt.WindowType.WindowStaysOnTopHint,
                True
            )

            go_down = menu.addAction("Go Down")
            shamisen = None
            stop_playing = None
            volume_menu = None
            volume_actions = {}
            if self.shamisen_playing:
                stop_playing = menu.addAction("Stop Playing")
                volume_menu = menu.addMenu("Volume")
                for percent in (100, 75, 50, 25, 0):
                    action = volume_menu.addAction(f"{percent}%")
                    action.setCheckable(True)
                    action.setChecked(percent == self.shamisen_volume)
                    volume_actions[action] = percent
            else:
                shamisen = menu.addAction("Shamisen")

            self.active_menu = menu
            self.topmost_timer.stop()

            def handle_attached_action(chosen):
                if chosen == go_down:
                    self.go_down_from_chrono_clock()
                elif shamisen is not None and chosen == shamisen:
                    self.play_shamisen()
                elif stop_playing is not None and chosen == stop_playing:
                    self.stop_shamisen()
                elif chosen in volume_actions:
                    self.set_shamisen_volume(volume_actions[chosen])

            def attached_menu_closed():
                if self.active_menu is menu:
                    self.active_menu = None

                self.topmost_timer.start(750)
                QtCore.QTimer.singleShot(
                    0,
                    self.ensure_topmost
                )

                menu.deleteLater()

            menu.triggered.connect(handle_attached_action)
            menu.aboutToHide.connect(attached_menu_closed)

            menu.popup(position)
            self.position_active_menu()

            return
        menu.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, True)
        pause = menu.addAction("Pause Walking" if self.walking else "Resume Walking")
        menu.addSeparator()
        turn = menu.addAction("Turn Around")
        menu.addSeparator()
        manual_sit = menu.addAction("Sit")
        celebrate = menu.addAction("Celebrate!")
        clock_action = None
        if self.chrono_clock_window is not None and self.chrono_clock_window.isVisible():
            menu.addSeparator()
            clock_action = menu.addAction("Chrono Clock")
        menu.addSeparator()
        exit_action = menu.addAction("Hide Koyomi")

        self.active_menu = menu
        self.active_menu_offset = QtCore.QPoint(self.width() + self.MENU_ANCHOR_GAP, 0)
        self.topmost_timer.stop()

        def handle_action(chosen):
            if chosen == pause:
                if self.manual_sitting:
                    self.resume_from_manual_sit()
                else:
                    self.walking = not self.walking
                    if not self.dragging and not self.airborne and self.state != "sit":
                        self.run_timer.stop(); self.stop_timer.stop(); self.stop_velocity = 0.0
                        self.set_animation("walk" if self.walking else "idle")
                    self.schedule_idle()
            elif chosen == turn:
                self.direction *= -1
                if self.state == "drag":
                    self.draw_drag_pose()
                elif self.state == "sit":
                    self.set_animation("sit")
                else:
                    self.update_movie_frame(self.movie)
            elif chosen == manual_sit:
                self.start_manual_sit()
            elif chosen == celebrate:
                self.start_celebration()
            elif clock_action is not None and chosen == clock_action:
                self.begin_chrono_clock_trip()
            elif chosen == exit_action:
                self.hide_koyomi()

        def menu_closed():
            if self.active_menu is menu:
                self.active_menu = None
            self.topmost_timer.start(750)
            QtCore.QTimer.singleShot(0, self.ensure_topmost)
            menu.deleteLater()

        menu.triggered.connect(handle_action)
        menu.aboutToHide.connect(menu_closed)
        menu.popup(position)
        self.position_active_menu()
