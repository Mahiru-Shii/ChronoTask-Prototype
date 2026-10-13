# ====================================================================
# CHRONOTASK TASK DIALOG STYLESHEET
# ====================================================================

TASK_DIALOG_STYLE = r"""
QDialog#TaskDialog {
    background-color: transparent;
}

QFrame#backgroundFrame {
    background-color: #182133;
    border: 1px solid #34425D;
    border-radius: 20px;
}

QFrame#titleBar,
QFrame#contentFrame {
    background-color: transparent;
    border: none;
}

QLabel#lblTitle {
    background-color: transparent;
    color: #F4F7FF;
    border: none;
    font-family: "Segoe UI";
    font-size: 12px;
    font-weight: 600;
}

QPushButton#btnClose {
    background-color: transparent;
    color: #AAB6CF;
    border: none;
    border-radius: 7px;
    font-family: "Segoe UI";
    font-size: 16px;
    font-weight: 400;
}

QPushButton#btnClose:hover {
    background-color: #E05D68;
    color: #FFFFFF;
}

QPushButton#btnClose:pressed {
    background-color: #C94F59;
    color: #FFFFFF;
}

QLabel#lblHeading {
    background-color: transparent;
    color: #F4F7FF;
    border: none;
    font-family: "Segoe UI";
    font-size: 20px;
    font-weight: 700;
}

QLabel#lblSubtitle {
    background-color: transparent;
    color: #8291AE;
    border: none;
    font-family: "Segoe UI";
    font-size: 10px;
    font-weight: 400;
}

QLabel#lblFieldTitle {
    background-color: transparent;
    color: #8A9AB7;
    border: none;
    font-family: "Segoe UI";
    font-size: 9px;
    font-weight: 700;
}

QFrame#calendarFrame {
    background-color: #222D42;
    border: 1px solid #36445F;
    border-radius: 16px;
}

QLabel#lblSelectedDeadline {
    background-color: transparent;
    color: #F4F7FF;
    border: none;
    font-family: "Segoe UI";
    font-size: 13px;
    font-weight: 600;
}

QLineEdit#txtTaskName {
    background-color: #253349;
    color: #F4F7FF;
    border: 1px solid #40506C;
    border-radius: 10px;
    padding-left: 14px;
    padding-right: 14px;
    font-family: "Segoe UI";
    font-size: 10px;
    selection-background-color: #3E8AC4;
    selection-color: #FFFFFF;
}

QLineEdit#txtTaskName:hover {
    border-color: #536784;
}

QLineEdit#txtTaskName:focus {
    border-color: #59B7FF;
}

QLineEdit#txtTaskName:disabled {
    background-color: #202C40;
    color: #65738D;
    border-color: #34425D;
}

QTextEdit#txtDescription {
    background-color: #253349;
    color: #F4F7FF;
    border: 1px solid #40506C;
    border-radius: 10px;
    padding: 9px 12px;
    font-family: "Segoe UI";
    font-size: 10px;
    selection-background-color: #3E8AC4;
    selection-color: #FFFFFF;
}

QTextEdit#txtDescription:hover {
    border-color: #536784;
}

QTextEdit#txtDescription:focus {
    border-color: #59B7FF;
}

QTextEdit#txtDescription:disabled {
    background-color: #202C40;
    color: #65738D;
    border-color: #34425D;
}

QComboBox#cmbPriority {
    background-color: #253349;
    color: #F4F7FF;
    border: 1px solid #40506C;
    border-radius: 10px;
    padding-left: 14px;
    padding-right: 40px;
    font-family: "Segoe UI";
    font-size: 10px;
    selection-background-color: #3E8AC4;
    selection-color: #FFFFFF;
}

QComboBox#cmbPriority:hover {
    border-color: #536784;
}

QComboBox#cmbPriority:focus {
    border-color: #59B7FF;
}

QComboBox#cmbPriority::drop-down {
    background-color: transparent;
    border: none;
    border-left: 1px solid #36445F;
    width: 34px;
}

QComboBox#cmbPriority::down-arrow {
    image: none;
    width: 0px;
    height: 0px;
}

QComboBox#cmbPriority QAbstractItemView {
    background-color: #253349;
    color: #F4F7FF;
    border: 1px solid #40506C;
    outline: none;
    selection-background-color: #354760;
    selection-color: #FFFFFF;
    padding: 6px;
    font-family: "Segoe UI";
    font-size: 10px;
}

QComboBox#cmbPriority QAbstractItemView::item {
    min-height: 30px;
    padding-left: 8px;
    padding-right: 8px;
}

QComboBox#cmbPriority QAbstractItemView::item:hover {
    background-color: #2B3851;
    color: #FFFFFF;
}

QComboBox#cmbPriority QAbstractItemView::item:selected {
    background-color: #3E8AC4;
    color: #FFFFFF;
}

QTimeEdit#timeEdit {
    background-color: #253349;
    color: #F4F7FF;
    border: 1px solid #40506C;
    border-radius: 10px;
    padding-left: 14px;
    padding-right: 40px;
    font-family: "Segoe UI";
    font-size: 10px;
    selection-background-color: #3E8AC4;
    selection-color: #FFFFFF;
}

QTimeEdit#timeEdit:hover {
    border-color: #536784;
}

QTimeEdit#timeEdit:focus {
    border-color: #59B7FF;
}

QTimeEdit#timeEdit::up-button {
    background-color: transparent;
    border: none;
    border-left: 1px solid #36445F;
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 32px;
    height: 20px;
}

QTimeEdit#timeEdit::down-button {
    background-color: transparent;
    border: none;
    border-left: 1px solid #36445F;
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 32px;
    height: 20px;
}

QTimeEdit#timeEdit::up-button:hover,
QTimeEdit#timeEdit::down-button:hover {
    background-color: #2B3851;
}

QTimeEdit#timeEdit::up-button:pressed,
QTimeEdit#timeEdit::down-button:pressed {
    background-color: #344561;
}

QTimeEdit#timeEdit::up-arrow,
QTimeEdit#timeEdit::down-arrow {
    image: none;
    width: 0px;
    height: 0px;
}

QPushButton#btnAddTask {
    background-color: #3E8AC4;
    color: #FFFFFF;
    border: 1px solid #59B7FF;
    border-radius: 11px;
    font-family: "Segoe UI";
    font-size: 11px;
    font-weight: 600;
}

QPushButton#btnAddTask:hover {
    background-color: #4C9CD8;
    border-color: #79C5FF;
}

QPushButton#btnAddTask:pressed {
    background-color: #347AAF;
    border-color: #4C9CD8;
}

QPushButton#btnAddTask:disabled {
    background-color: #2B3851;
    color: #65738D;
    border-color: #34425D;
}
"""