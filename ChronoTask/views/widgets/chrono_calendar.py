from datetime import datetime

from PySide6 import QtCore, QtGui, QtWidgets


from styles.theme import palette
def _theme_style(style, widget):
    win = widget.window() if widget is not None else None
    theme_name = getattr(win, "current_theme", "default")
    c = palette(theme_name)
    replacements = {
        "#151D2B": c["window"],
        "#182133": c["surface_alt"],
        "#1B2536": c["surface_alt"],
        "#202B3F": c["surface"],
        "#202C40": c["input"],
        "#222D42": c["surface"],
        "#243149": c["surface"],
        "#253349": c["surface"],
        "#2B3851": c["surface"],
        "#2E3A52": c["border_soft"],
        "#31425D": c["surface"],
        "#34425D": c["border_soft"],
        "#344561": c["border_soft"],
        "#354760": c["border"],
        "#36445F": c["border"],
        "#40506C": c["border"],
        "#405273": c["border"],
        "#536784": c["border"],
        "#3E8AC4": c["accent"],
        "#4C9CD8": c["accent"],
        "#59B7FF": c["accent_hover"],
        "#79C5FF": c["accent_hover"],
        "#7CB4FF": c["accent_hover"],
        "#8FAEFF": c["accent_hover"],
        "#F4F7FF": c["text"],
        "#FFFFFF": c["text"],
        "#DCE5F7": c["text"],
        "#AAB6CF": c["muted"],
        "#AAB9D3": c["muted"],
        "#9AA9C3": c["muted"],
        "#93A3BF": c["muted"],
        "#91A1BD": c["muted"],
        "#8A9AB7": c["muted"],
        "#8291AE": c["muted"],
        "#8392AE": c["muted"],
        "#71809E": c["muted"],
        "#65738D": c["muted"],
        "#7F8DAA": c["muted"],
    }
    for old, new in replacements.items():
        style = style.replace(old, new)
    return style


class ChronoCalendarDelegate(QtWidgets.QStyledItemDelegate):
    """Responsive painter that keeps indicators away from the date number."""

    CURRENT = QtGui.QColor("#DCE5F7")
    OUTSIDE = QtGui.QColor("#65738D")
    HEADER = QtGui.QColor("#8A9AB7")
    SELECTED = QtGui.QColor("#3E8AC4")
    SELECTED_TEXT = QtGui.QColor("#FFFFFF")
    HOVER = QtGui.QColor("#2B3851")
    REST = QtGui.QColor("#60C6B2")

    def __init__(self, calendar, parent=None):
        super().__init__(parent)
        self.calendar = calendar

    def date_for_index(self, index):
        if not index.isValid() or index.row() == 0:
            return QtCore.QDate()
        first = QtCore.QDate(self.calendar.yearShown(), self.calendar.monthShown(), 1)
        first_weekday = self.calendar.firstDayOfWeek().value
        leading = (first.dayOfWeek() - first_weekday) % 7
        return first.addDays(-leading).addDays((index.row() - 1) * 7 + index.column())

    def paint(self, painter, option, index):
        opt = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        opt.state &= ~QtWidgets.QStyle.StateFlag.State_HasFocus
        if index.row() == 0:
            self._paint_header(painter, opt, index)
        else:
            self._paint_date(painter, opt, index)

    def _paint_header(self, painter, option, index):
        painter.save()
        font = QtGui.QFont("Segoe UI", 9)
        font.setWeight(QtGui.QFont.Weight.DemiBold)
        painter.setFont(font)
        painter.setPen(self.HEADER)
        painter.drawText(option.rect, QtCore.Qt.AlignmentFlag.AlignCenter, str(index.data()))
        painter.restore()

    def _paint_date(self, painter, option, index):
        day = self.date_for_index(index)
        info = self.calendar.day_info(day)
        selected = bool(option.state & QtWidgets.QStyle.StateFlag.State_Selected)
        hovered = bool(option.state & QtWidgets.QStyle.StateFlag.State_MouseOver)
        in_month = day.year() == self.calendar.yearShown() and day.month() == self.calendar.monthShown()

        painter.save()
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.fillRect(option.rect, QtGui.QColor(palette(getattr(self.calendar.window(), "current_theme", "default"))["surface"]))

        # This must work at the small normal-window row height as well as maximized.
        cell = option.rect.adjusted(5, 2, -5, -2)
        strongest = self.calendar.strongest_deadline_key(info)
        if selected:
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.setBrush(self.SELECTED)
            painter.drawRoundedRect(cell, 6, 6)
        elif info.get("overdue", 0):
            color = QtGui.QColor("#FF4D5A"); fill = QtGui.QColor(color); fill.setAlpha(58)
            painter.setPen(QtGui.QPen(color, 1.6)); painter.setBrush(fill); painter.drawRoundedRect(cell, 6, 6)
        elif strongest is not None:
            color = self.calendar.PRIORITY_COLORS_BY_KEY[strongest]
            fill = QtGui.QColor(color)
            fill.setAlpha(52)
            painter.setPen(QtGui.QPen(color, 1.2))
            painter.setBrush(fill)
            painter.drawRoundedRect(cell, 6, 6)
        elif hovered:
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.setBrush(self.HOVER)
            painter.drawRoundedRect(cell, 6, 6)

        # Date is drawn around the true cell center and lifted only one pixel.
        # Markers never enter this protected center strip.
        center_y = cell.center().y() - 1
        date_zone = QtCore.QRectF(
            cell.left() + 13,
            center_y - 7,
            max(10.0, cell.width() - 26),
            14,
        )
        date_font = QtGui.QFont("Segoe UI", 9)
        if day == QtCore.QDate.currentDate():
            date_font.setWeight(QtGui.QFont.Weight.Bold)
        painter.setFont(date_font)
        painter.setPen(self.SELECTED_TEXT if selected else self.CURRENT if in_month else self.OUTSIDE)
        painter.drawText(date_zone, QtCore.Qt.AlignmentFlag.AlignCenter, str(index.data()))

        # Kaizen circles live on the left/right edges, never above/below the number.
        if info["rest"]:
            self._paint_rest(painter, cell, selected)
        else:
            self._paint_side_kaizen(painter, cell, info["kaizen"], selected)

        if info.get("overdue", 0): self._paint_overdue(painter, cell, selected)
        # Deadline squares live in a tiny bottom lane. At normal window height
        # they remain below the date baseline instead of covering the number.
        self._paint_bottom_deadlines(painter, cell, info["deadlines"], selected)
        painter.restore()

    def _visible_counts(self, counts):
        return [(key, counts.get(key, 0)) for key in self.calendar.PRIORITY_ORDER if counts.get(key, 0)]

    def _paint_overdue(self, painter, cell, selected):
        color = QtGui.QColor("#FFFFFF") if selected else QtGui.QColor("#FF4D5A")
        cx, top = cell.center().x(), cell.top() + 1.5
        path = QtGui.QPainterPath(); path.moveTo(cx, top); path.lineTo(cx-5.5, top+9.5); path.lineTo(cx+5.5, top+9.5); path.closeSubpath()
        fill = QtGui.QColor(color); fill.setAlpha(60)
        painter.setPen(QtGui.QPen(color, 1.1)); painter.setBrush(fill); painter.drawPath(path)
        font = QtGui.QFont("Segoe UI", 5); font.setWeight(QtGui.QFont.Weight.Bold); painter.setFont(font); painter.setPen(color)
        painter.drawText(QtCore.QRectF(cx-4, top+2, 8, 7), QtCore.Qt.AlignmentFlag.AlignCenter, "!")

    def _paint_side_kaizen(self, painter, cell, counts, selected):
        visible = self._visible_counts(counts)
        if not visible:
            return

        # Priority slots: red/blue on upper sides, orange/purple on lower sides.
        # Sizes are deliberately compact because normal-window cells are shallow.
        r = 4.0
        x_left = cell.left() + 8
        x_right = cell.right() - 8
        y_upper = cell.center().y() - 7
        y_lower = cell.center().y() + 7
        slots = {
            "urgent_important": QtCore.QPointF(x_left, y_upper),
            "important": QtCore.QPointF(x_right, y_upper),
            "urgent": QtCore.QPointF(x_left, y_lower),
            "normal": QtCore.QPointF(x_right, y_lower),
        }

        for key, count in visible:
            c = slots[key]
            marker = QtCore.QRectF(c.x() - r, c.y() - r, r * 2, r * 2)
            color = QtGui.QColor("#FFFFFF") if selected else QtGui.QColor(self.calendar.PRIORITY_COLORS_BY_KEY[key])
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawEllipse(marker)
            if count > 1:
                self._paint_marker_count(painter, marker, count, selected, 5)

    def _paint_bottom_deadlines(self, painter, cell, counts, selected):
        visible = self._visible_counts(counts)
        if not visible:
            return

        amount = len(visible)
        size = 7.0 if amount <= 2 else 6.0
        gap = 3.0
        total = amount * size + max(0, amount - 1) * gap
        x = cell.center().x() - total / 2
        # Keep a guaranteed two-pixel margin from the bottom frame.
        y = cell.bottom() - size - 2

        for key, count in visible:
            marker = QtCore.QRectF(x, y, size, size)
            color = QtGui.QColor("#FFFFFF") if selected else QtGui.QColor(self.calendar.PRIORITY_COLORS_BY_KEY[key])
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawRoundedRect(marker, 1.8, 1.8)
            if count > 1:
                self._paint_marker_count(painter, marker, count, selected, 4)
            x += size + gap

    def _paint_marker_count(self, painter, marker, count, selected, point_size):
        font = QtGui.QFont("Segoe UI", point_size)
        font.setWeight(QtGui.QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QtGui.QColor("#3E8AC4") if selected else QtGui.QColor("#182133"))
        painter.drawText(marker, QtCore.Qt.AlignmentFlag.AlignCenter, str(count))

    def _paint_rest(self, painter, cell, selected):
        # A compact top-right pill leaves the centered date fully untouched.
        width = min(24.0, max(18.0, cell.width() * 0.30))
        height = 8.0
        marker = QtCore.QRectF(
            cell.right() - width - 3,
            cell.top() + 3,
            width,
            height,
        )
        color = QtGui.QColor("#FFFFFF") if selected else self.REST
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawRoundedRect(marker, 3.2, 3.2)
        font = QtGui.QFont("Segoe UI", 4)
        font.setWeight(QtGui.QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QtGui.QColor("#3E8AC4") if selected else QtGui.QColor("#182133"))
        painter.drawText(marker, QtCore.Qt.AlignmentFlag.AlignCenter, "REST")


class ChronoCalendar(QtWidgets.QCalendarWidget):
    """Calendar with distinct deadline squares and Kaizen circles by priority."""

    PRIORITY_ORDER = (
        "urgent_important",
        "important",
        "urgent",
        "normal",
    )
    PRIORITY_COLORS_BY_KEY = {
        "urgent_important": QtGui.QColor("#E06C75"),
        "important": QtGui.QColor("#59B7FF"),
        "urgent": QtGui.QColor("#E6B86A"),
        "normal": QtGui.QColor("#8A8FB8"),
    }
    PRIORITY_RANK = {key: index for index, key in enumerate(PRIORITY_ORDER)}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.calendar_view = None
        self.calendar_delegate = None
        self._tasks = []
        self._manual_rest_days = set()
        self._day_data = {}
        self.setObjectName("chronoCalendar")
        self._setup()
        self._apply_style()
        self.currentPageChanged.connect(self._page_changed)
        self.selectionChanged.connect(self.refresh)
        QtCore.QTimer.singleShot(0, self._finish_setup)

    def _setup(self):
        self.setVerticalHeaderFormat(QtWidgets.QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.setHorizontalHeaderFormat(QtWidgets.QCalendarWidget.HorizontalHeaderFormat.ShortDayNames)
        self.setFirstDayOfWeek(QtCore.Qt.DayOfWeek.Monday)
        self.setNavigationBarVisible(True)
        self.setGridVisible(False)
        self.setSelectionMode(QtWidgets.QCalendarWidget.SelectionMode.SingleSelection)
        self.setSelectedDate(QtCore.QDate.currentDate())
        # Keep all six possible calendar weeks visible in compact windows.
        self.setMinimumHeight(252)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

    def _finish_setup(self):
        self._setup_view()
        self._remove_weekend_red()
        self._style_controls()
        self.refresh()

    def _setup_view(self):
        view = self.findChild(QtWidgets.QTableView, "qt_calendar_calendarview")
        if view is None:
            return
        self.calendar_view = view
        view.setShowGrid(False)
        view.setAlternatingRowColors(False)
        view.setMouseTracking(True)
        view.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        view.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        view.horizontalHeader().hide()
        view.verticalHeader().hide()
        view.setStyleSheet(_theme_style("""
            QTableView { background:#222D42; border:none; outline:none; gridline-color:transparent; selection-background-color:transparent; }
            QTableView::item { background:transparent; border:none; outline:none; padding:2px; }
            QTableView::item:selected, QTableView::item:hover, QTableView::item:focus { background:transparent; border:none; outline:none; }
        """, self))
        self.calendar_delegate = ChronoCalendarDelegate(self, view)
        view.setItemDelegate(self.calendar_delegate)
        view.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        view.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        view.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

    def set_tasks(self, tasks):
        self._tasks = list(tasks or [])
        self._rebuild_day_data()
        self.refresh()

    def set_manual_rest_days(self, rest_days):
        self._manual_rest_days = set()
        for value in rest_days or []:
            parsed = self._parse_date(value)
            if parsed.isValid(): self._manual_rest_days.add(self._date_key(parsed))
        self._rebuild_day_data(); self.refresh()

    def clear_tasks(self):
        self._tasks = []
        self._day_data.clear()
        self.refresh()

    def _empty_day_info(self):
        return {
            "deadlines": {key: 0 for key in self.PRIORITY_ORDER},
            "kaizen": {key: 0 for key in self.PRIORITY_ORDER},
            "rest": False,
            "overdue": 0,
        }

    def _rebuild_day_data(self):
        self._day_data.clear()
        for task in self._tasks:
            if bool(getattr(task, "completed", False)):
                continue
            key = self._priority_key(task)

            deadline = self._parse_date(getattr(task, "date", None))
            if deadline.isValid():
                info = self._day_data.setdefault(self._date_key(deadline), self._empty_day_info())
                info["deadlines"][key] += 1
                if bool(getattr(task, "is_overdue", False)): info["overdue"] += 1

            for value in getattr(task, "rest_dates", []) or []:
                rest = self._parse_date(value)
                if rest.isValid():
                    info = self._day_data.setdefault(self._date_key(rest), self._empty_day_info())
                    info["rest"] = True

            for step in getattr(task, "kaizen_steps", []) or []:
                if bool(getattr(step, "completed", False)):
                    continue
                scheduled = self._parse_date(getattr(step, "scheduled_date", None))
                if scheduled.isValid():
                    info = self._day_data.setdefault(self._date_key(scheduled), self._empty_day_info())
                    info["kaizen"][key] += 1

        for date_key in self._manual_rest_days:
            info = self._day_data.setdefault(date_key, self._empty_day_info())
            info["rest"] = True

    def day_info(self, value):
        parsed = self._parse_date(value)
        if not parsed.isValid():
            return self._empty_day_info()
        return self._day_data.get(self._date_key(parsed), self._empty_day_info())

    def strongest_deadline_key(self, info):
        for key in self.PRIORITY_ORDER:
            if info["deadlines"].get(key, 0):
                return key
        return None

    # Backward-compatible helpers used elsewhere.
    def task_color_for_date(self, value):
        strongest = self.strongest_deadline_key(self.day_info(value))
        return None if strongest is None else self.PRIORITY_COLORS_BY_KEY[strongest]

    def kaizen_info_for_date(self, value):
        info = self.day_info(value)
        total = sum(info["kaizen"].values())
        if not total:
            return None
        strongest = next((key for key in self.PRIORITY_ORDER if info["kaizen"].get(key)), None)
        return {"count": total, "color": self.PRIORITY_COLORS_BY_KEY[strongest]}

    def kaizen_count_for_date(self, value):
        return sum(self.day_info(value)["kaizen"].values())

    def is_rest_date(self, value):
        return self.day_info(value)["rest"]

    @staticmethod
    def _priority_key(task):
        urgent = bool(getattr(task, "isUrgent", False))
        important = bool(getattr(task, "isImportant", False))
        if urgent and important:
            return "urgent_important"
        if important:
            return "important"
        if urgent:
            return "urgent"
        return "normal"

    @staticmethod
    def _date_key(value):
        return value.year(), value.month(), value.day()

    @staticmethod
    def _parse_date(value):
        if isinstance(value, QtCore.QDate):
            return value
        if value is None:
            return QtCore.QDate()
        text = str(value).strip()
        parsed = QtCore.QDate.fromString(text, "yyyy-MM-dd")
        if parsed.isValid():
            return parsed
        try:
            native = datetime.strptime(text, "%Y-%m-%d")
            return QtCore.QDate(native.year, native.month, native.day)
        except ValueError:
            return QtCore.QDate()

    def _remove_weekend_red(self):
        fmt = QtGui.QTextCharFormat()
        fmt.setForeground(QtGui.QColor("#DCE5F7"))
        for day in QtCore.Qt.DayOfWeek:
            if day != QtCore.Qt.DayOfWeek(0):
                self.setWeekdayTextFormat(day, fmt)

    @QtCore.Slot(int, int)
    def _page_changed(self, year, month):
        QtCore.QTimer.singleShot(0, self.refresh)

    @QtCore.Slot()
    def refresh(self):
        if self.calendar_view is None:
            self._setup_view()
        if self.calendar_view is not None:
            self.calendar_view.viewport().update()
        self.updateCells()

    def _apply_style(self):
        self.setStyleSheet(_theme_style("""
            QCalendarWidget { background:#222D42; border:none; font-family:"Segoe UI"; }
            QWidget#qt_calendar_navigationbar { background:#222D42; border:none; }
            QCalendarWidget QToolButton { background:transparent; color:#F4F7FF; border:none; border-radius:6px; padding:3px 8px; font-size:10px; font-weight:600; }
            QCalendarWidget QToolButton:hover { background:#2B3851; }
            QCalendarWidget QToolButton:pressed { background:#344561; }
            QCalendarWidget QToolButton::menu-indicator { image:none; width:0; height:0; }
            QCalendarWidget QSpinBox { background:#253349; color:#F4F7FF; border:1px solid #40506C; border-radius:6px; padding:4px 8px; selection-background-color:#3E8AC4; selection-color:white; }
            QCalendarWidget QMenu { background:#222D42; color:#DCE5F7; border:1px solid #40506C; padding:5px; }
            QCalendarWidget QMenu::item { padding:6px 20px; }
            QCalendarWidget QMenu::item:selected { background:#3E8AC4; color:white; }
        """, self))

    def _style_controls(self):
        for name in ("qt_calendar_prevmonth", "qt_calendar_nextmonth"):
            button = self.findChild(QtWidgets.QToolButton, name)
            if button:
                button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        month = self.findChild(QtWidgets.QToolButton, "qt_calendar_monthbutton")
        if month:
            month.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextOnly)
        year = self.findChild(QtWidgets.QToolButton, "qt_calendar_yearbutton")
        if year:
            year.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextOnly)
        editor = self.findChild(QtWidgets.QSpinBox, "qt_calendar_yearedit")
        if editor:
            editor.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def showEvent(self, event):
        super().showEvent(event)
        QtCore.QTimer.singleShot(0, self._finish_setup)