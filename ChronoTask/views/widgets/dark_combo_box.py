from PySide6 import QtCore, QtGui, QtWidgets


class DarkComboBox(QtWidgets.QComboBox):
    """
    ChronoTask ComboBox with a custom visible dropdown arrow.
    """

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QtGui.QPainter(self)

        painter.setRenderHint(
            QtGui.QPainter.RenderHint.Antialiasing
        )

        pen = QtGui.QPen(
            QtGui.QColor("#B8C6DD")
        )

        pen.setWidthF(1.5)

        pen.setCapStyle(
            QtCore.Qt.PenCapStyle.RoundCap
        )

        pen.setJoinStyle(
            QtCore.Qt.PenJoinStyle.RoundJoin
        )

        painter.setPen(pen)

        arrow_x = self.width() - 16
        arrow_y = self.height() / 2

        painter.drawLine(
            QtCore.QPointF(
                arrow_x - 4,
                arrow_y - 2
            ),
            QtCore.QPointF(
                arrow_x,
                arrow_y + 2
            )
        )

        painter.drawLine(
            QtCore.QPointF(
                arrow_x,
                arrow_y + 2
            ),
            QtCore.QPointF(
                arrow_x + 4,
                arrow_y - 2
            )
        )

        painter.end()
