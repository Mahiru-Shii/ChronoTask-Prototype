from PySide6 import QtCore, QtGui, QtWidgets


# ====================================================================
# CUSTOM DARK TIME EDIT
# ====================================================================

class DarkTimeEdit(QtWidgets.QTimeEdit):
    """
    ChronoTask time selector with custom visible up and down arrows.

    Qt's default spin-box arrows can be difficult to see against a
    custom dark stylesheet. This widget draws its own arrows while
    preserving the standard QTimeEdit behavior.
    """

    def paintEvent(self, event):
        # Draw the standard QTimeEdit control first.
        super().paintEvent(event)

        # Draw the custom arrows on top of the standard control.
        painter = QtGui.QPainter(self)

        painter.setRenderHint(
            QtGui.QPainter.RenderHint.Antialiasing
        )

        # Arrow color.
        pen = QtGui.QPen(
            QtGui.QColor("#B8C6DD")
        )

        pen.setWidthF(1.3)

        pen.setCapStyle(
            QtCore.Qt.PenCapStyle.RoundCap
        )

        pen.setJoinStyle(
            QtCore.Qt.PenJoinStyle.RoundJoin
        )

        painter.setPen(pen)

        # Horizontal position of both arrows.
        arrow_x = self.width() - 16

        # ============================================================
        # UP ARROW
        # ============================================================

        upper_y = self.height() / 2 - 7

        # Left side of the upper arrow.
        painter.drawLine(
            QtCore.QPointF(
                arrow_x - 4,
                upper_y + 3
            ),
            QtCore.QPointF(
                arrow_x,
                upper_y - 1
            )
        )

        # Right side of the upper arrow.
        painter.drawLine(
            QtCore.QPointF(
                arrow_x,
                upper_y - 1
            ),
            QtCore.QPointF(
                arrow_x + 4,
                upper_y + 3
            )
        )

        # ============================================================
        # DOWN ARROW
        # ============================================================

        lower_y = self.height() / 2 + 7

        # Left side of the lower arrow.
        painter.drawLine(
            QtCore.QPointF(
                arrow_x - 4,
                lower_y - 3
            ),
            QtCore.QPointF(
                arrow_x,
                lower_y + 1
            )
        )

        # Right side of the lower arrow.
        painter.drawLine(
            QtCore.QPointF(
                arrow_x,
                lower_y + 1
            ),
            QtCore.QPointF(
                arrow_x + 4,
                lower_y - 3
            )
        )

        painter.end()
