from PySide6 import QtCore, QtGui, QtWidgets


from styles.theme import palette
# ====================================================================
# SIDEBAR ICON BUTTON
# ====================================================================

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
        "#222D42": c["surface_alt"],
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


class SidebarIconButton(QtWidgets.QPushButton):
    """
    Custom ChronoTask sidebar button.

    The icon is drawn using QPainter instead of image files.

    Supported icons:
        home
        calendar
        tasks
        kaizen
        settings
    """

    def __init__(
        self,
        icon_name,
        parent=None
    ):
        super().__init__(parent)

        self.icon_name = icon_name

        self.setText("")

        self.setFixedSize(
            44,
            44
        )

        self.setCheckable(
            True
        )

        self.setCursor(
            QtGui.QCursor(
                QtCore.Qt.CursorShape.PointingHandCursor
            )
        )

    # =================================================================
    # PAINT
    # =================================================================

    def paintEvent(
        self,
        event
    ):
        # Draw the normal QPushButton first.
        super().paintEvent(event)

        painter = QtGui.QPainter(
            self
        )

        painter.setRenderHint(
            QtGui.QPainter.RenderHint.Antialiasing
        )

        # ============================================================
        # ICON COLOR
        # ============================================================

        if self.isChecked():
            color = QtGui.QColor(
                "#FFFFFF"
            )

        else:
            color = QtGui.QColor(
                "#AAB6CF"
            )

        # ============================================================
        # PEN
        # ============================================================

        pen = QtGui.QPen(
            color
        )

        pen.setWidthF(
            1.7
        )

        pen.setCapStyle(
            QtCore.Qt.PenCapStyle.RoundCap
        )

        pen.setJoinStyle(
            QtCore.Qt.PenJoinStyle.RoundJoin
        )

        painter.setPen(
            pen
        )

        painter.setBrush(
            QtCore.Qt.BrushStyle.NoBrush
        )

        # ============================================================
        # CENTER
        # ============================================================

        center_x = (
            self.width()
            / 2
        )

        center_y = (
            self.height()
            / 2
        )

        # ============================================================
        # DRAW CHOSEN ICON
        # ============================================================

        if self.icon_name == "home":
            self.draw_home(
                painter,
                center_x,
                center_y
            )

        elif self.icon_name == "calendar":
            self.draw_calendar(
                painter,
                center_x,
                center_y
            )

        elif self.icon_name == "tasks":
            self.draw_tasks(
                painter,
                center_x,
                center_y
            )

        elif self.icon_name == "kaizen":
            self.draw_kaizen(
                painter,
                center_x,
                center_y
            )

        elif self.icon_name == "settings":
            self.draw_settings(
                painter,
                center_x,
                center_y
            )

        painter.end()

    # =================================================================
    # HOME ICON
    # =================================================================

    @staticmethod
    def draw_home(
        painter,
        center_x,
        center_y
    ):
        path = QtGui.QPainterPath()

        # Roof.
        path.moveTo(
            center_x - 8,
            center_y - 1
        )

        path.lineTo(
            center_x,
            center_y - 8
        )

        path.lineTo(
            center_x + 8,
            center_y - 1
        )

        # House body.
        path.moveTo(
            center_x - 6,
            center_y - 2
        )

        path.lineTo(
            center_x - 6,
            center_y + 8
        )

        path.lineTo(
            center_x + 6,
            center_y + 8
        )

        path.lineTo(
            center_x + 6,
            center_y - 2
        )

        # Door.
        path.moveTo(
            center_x - 2,
            center_y + 8
        )

        path.lineTo(
            center_x - 2,
            center_y + 2
        )

        path.lineTo(
            center_x + 2,
            center_y + 2
        )

        path.lineTo(
            center_x + 2,
            center_y + 8
        )

        painter.drawPath(
            path
        )

    # =================================================================
    # CALENDAR ICON
    # =================================================================

    @staticmethod
    def draw_calendar(
        painter,
        center_x,
        center_y
    ):
        # Calendar outer body.
        rectangle = QtCore.QRectF(
            center_x - 8,
            center_y - 7,
            16,
            15
        )

        painter.drawRoundedRect(
            rectangle,
            2,
            2
        )

        # Divider below calendar header.
        painter.drawLine(
            QtCore.QPointF(
                center_x - 8,
                center_y - 2
            ),
            QtCore.QPointF(
                center_x + 8,
                center_y - 2
            )
        )

        # Calendar rings.
        painter.drawLine(
            QtCore.QPointF(
                center_x - 4,
                center_y - 9
            ),
            QtCore.QPointF(
                center_x - 4,
                center_y - 5
            )
        )

        painter.drawLine(
            QtCore.QPointF(
                center_x + 4,
                center_y - 9
            ),
            QtCore.QPointF(
                center_x + 4,
                center_y - 5
            )
        )

        # Date dots.
        painter.drawPoint(
            QtCore.QPointF(
                center_x - 4,
                center_y + 2
            )
        )

        painter.drawPoint(
            QtCore.QPointF(
                center_x,
                center_y + 2
            )
        )

        painter.drawPoint(
            QtCore.QPointF(
                center_x + 4,
                center_y + 2
            )
        )

        painter.drawPoint(
            QtCore.QPointF(
                center_x - 4,
                center_y + 5
            )
        )

        painter.drawPoint(
            QtCore.QPointF(
                center_x,
                center_y + 5
            )
        )

    # =================================================================
    # TASKS ICON
    # =================================================================

    @staticmethod
    def draw_tasks(
        painter,
        center_x,
        center_y
    ):
        # First checkbox.
        painter.drawRoundedRect(
            QtCore.QRectF(
                center_x - 8,
                center_y - 7,
                4,
                4
            ),
            1,
            1
        )

        # First task line.
        painter.drawLine(
            QtCore.QPointF(
                center_x - 1,
                center_y - 5
            ),
            QtCore.QPointF(
                center_x + 8,
                center_y - 5
            )
        )

        # Second checkbox.
        painter.drawRoundedRect(
            QtCore.QRectF(
                center_x - 8,
                center_y - 1,
                4,
                4
            ),
            1,
            1
        )

        # Second task line.
        painter.drawLine(
            QtCore.QPointF(
                center_x - 1,
                center_y + 1
            ),
            QtCore.QPointF(
                center_x + 8,
                center_y + 1
            )
        )

        # Third checkbox.
        painter.drawRoundedRect(
            QtCore.QRectF(
                center_x - 8,
                center_y + 5,
                4,
                4
            ),
            1,
            1
        )

        # Third task line.
        painter.drawLine(
            QtCore.QPointF(
                center_x - 1,
                center_y + 7
            ),
            QtCore.QPointF(
                center_x + 8,
                center_y + 7
            )
        )

    # =================================================================
    # KAIZEN ICON
    # =================================================================

    @staticmethod
    def draw_kaizen(
        painter,
        center_x,
        center_y
    ):
        """
        Draw a small sprout / growth icon representing Kaizen.
        """

        # Stem.
        painter.drawLine(
            QtCore.QPointF(
                center_x,
                center_y + 8
            ),
            QtCore.QPointF(
                center_x,
                center_y - 3
            )
        )

        # Left branch.
        painter.drawLine(
            QtCore.QPointF(
                center_x,
                center_y
            ),
            QtCore.QPointF(
                center_x - 5,
                center_y - 4
            )
        )

        # Right branch.
        painter.drawLine(
            QtCore.QPointF(
                center_x,
                center_y - 2
            ),
            QtCore.QPointF(
                center_x + 5,
                center_y - 7
            )
        )

        # Left leaf.
        left_leaf = QtGui.QPainterPath()

        left_leaf.moveTo(
            center_x - 5,
            center_y - 4
        )

        left_leaf.cubicTo(
            center_x - 9,
            center_y - 7,
            center_x - 9,
            center_y - 1,
            center_x - 5,
            center_y - 4
        )

        painter.drawPath(
            left_leaf
        )

        # Right leaf.
        right_leaf = QtGui.QPainterPath()

        right_leaf.moveTo(
            center_x + 5,
            center_y - 7
        )

        right_leaf.cubicTo(
            center_x + 9,
            center_y - 10,
            center_x + 10,
            center_y - 4,
            center_x + 5,
            center_y - 7
        )

        painter.drawPath(
            right_leaf
        )

        # Ground.
        painter.drawLine(
            QtCore.QPointF(
                center_x - 6,
                center_y + 8
            ),
            QtCore.QPointF(
                center_x + 6,
                center_y + 8
            )
        )

    # =================================================================
    # SETTINGS ICON
    # =================================================================

    @staticmethod
    def draw_settings(
        painter,
        center_x,
        center_y
    ):
        """
        Draw a simplified settings / gear icon.
        """

        # Outer circle.
        painter.drawEllipse(
            QtCore.QPointF(
                center_x,
                center_y
            ),
            7,
            7
        )

        # Inner circle.
        painter.drawEllipse(
            QtCore.QPointF(
                center_x,
                center_y
            ),
            2.5,
            2.5
        )

        # Top.
        painter.drawLine(
            QtCore.QPointF(
                center_x,
                center_y - 10
            ),
            QtCore.QPointF(
                center_x,
                center_y - 7
            )
        )

        # Bottom.
        painter.drawLine(
            QtCore.QPointF(
                center_x,
                center_y + 7
            ),
            QtCore.QPointF(
                center_x,
                center_y + 10
            )
        )

        # Left.
        painter.drawLine(
            QtCore.QPointF(
                center_x - 10,
                center_y
            ),
            QtCore.QPointF(
                center_x - 7,
                center_y
            )
        )

        # Right.
        painter.drawLine(
            QtCore.QPointF(
                center_x + 7,
                center_y
            ),
            QtCore.QPointF(
                center_x + 10,
                center_y
            )
        )

        # Top-left.
        painter.drawLine(
            QtCore.QPointF(
                center_x - 7,
                center_y - 7
            ),
            QtCore.QPointF(
                center_x - 5,
                center_y - 5
            )
        )

        # Top-right.
        painter.drawLine(
            QtCore.QPointF(
                center_x + 5,
                center_y - 5
            ),
            QtCore.QPointF(
                center_x + 7,
                center_y - 7
            )
        )

        # Bottom-left.
        painter.drawLine(
            QtCore.QPointF(
                center_x - 7,
                center_y + 7
            ),
            QtCore.QPointF(
                center_x - 5,
                center_y + 5
            )
        )

        # Bottom-right.
        painter.drawLine(
            QtCore.QPointF(
                center_x + 5,
                center_y + 5
            ),
            QtCore.QPointF(
                center_x + 7,
                center_y + 7
            )
        )