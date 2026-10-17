from datetime import datetime
from PySide6 import QtCore, QtWidgets
from styles.theme import palette


class ChronoClockPage(QtWidgets.QWidget):
    launch_requested = QtCore.Signal(str, int, object)

    def __init__(self, task_controller, parent=None):
        super().__init__(parent)
        self.task_controller = task_controller
        self.queue = []
        self.item_checks = {}
        self.setObjectName("chronoClockPage")
        self._build_ui()
        self.refresh_items()
        self.apply_theme()

    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(26, 24, 26, 24)
        root.setSpacing(16)
        title = QtWidgets.QLabel("Chrono Clock"); title.setObjectName("clockPageTitle")
        subtitle = QtWidgets.QLabel("Focus on what's next."); subtitle.setObjectName("clockPageSubtitle")
        root.addWidget(title); root.addWidget(subtitle)
        body = QtWidgets.QHBoxLayout(); body.setSpacing(16); root.addLayout(body, 1)

        controls = QtWidgets.QFrame(); controls.setObjectName("clockCard")
        left = QtWidgets.QVBoxLayout(controls); left.setContentsMargins(20,18,20,18); left.setSpacing(14)
        heading = QtWidgets.QLabel("CLOCK"); heading.setObjectName("clockSectionTitle"); left.addWidget(heading)
        self.preview = QtWidgets.QLabel(); self.preview.setObjectName("clockPreview")
        self.preview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter); self.preview.setMinimumHeight(94); left.addWidget(self.preview)
        mode = QtWidgets.QHBoxLayout()
        self.clockRadio=QtWidgets.QRadioButton("Digital Clock"); self.timerRadio=QtWidgets.QRadioButton("Timer"); self.clockRadio.setChecked(True)
        mode.addWidget(self.clockRadio); mode.addWidget(self.timerRadio); mode.addStretch(1); left.addLayout(mode)
        timerBox=QtWidgets.QFrame(); timerBox.setObjectName("timerSetup"); tl=QtWidgets.QHBoxLayout(timerBox); tl.setContentsMargins(12,10,12,10)
        self.hours=QtWidgets.QSpinBox(); self.minutes=QtWidgets.QSpinBox(); self.seconds=QtWidgets.QSpinBox()
        for spin in (self.hours, self.minutes, self.seconds):
            spin.setRange(0, 59)
            spin.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
            spin.setKeyboardTracking(False)
            spin.installEventFilter(self)
        self.minutes.setValue(25)
        for spin in (self.hours, self.minutes, self.seconds):
            group = QtWidgets.QWidget()
            group.setObjectName("timeSpinGroup")
            gl = QtWidgets.QHBoxLayout(group)
            gl.setContentsMargins(0, 0, 0, 0)
            gl.setSpacing(4)
            minus = QtWidgets.QPushButton("−")
            plus = QtWidgets.QPushButton("+")
            minus.setObjectName("timeStepButton")
            plus.setObjectName("timeStepButton")
            minus.setFixedSize(24, 24)
            plus.setFixedSize(24, 24)
            minus.clicked.connect(lambda checked=False, sp=spin: sp.stepDown())
            plus.clicked.connect(lambda checked=False, sp=spin: sp.stepUp())
            gl.addWidget(minus)
            gl.addWidget(spin, 1)
            gl.addWidget(plus)
            tl.addWidget(group, 1)
            if spin is not self.seconds:
                colon = QtWidgets.QLabel(":")
                colon.setObjectName("timerColon")
                tl.addWidget(colon)
        left.addWidget(timerBox)
        self.launchButton=QtWidgets.QPushButton("Launch Digital Clock"); self.launchButton.setObjectName("clockLaunch"); left.addWidget(self.launchButton); left.addStretch(1)

        available=QtWidgets.QFrame(); available.setObjectName("clockCard")
        right=QtWidgets.QVBoxLayout(available); right.setContentsMargins(18,16,18,16); right.setSpacing(8)
        ah=QtWidgets.QLabel("AVAILABLE ITEMS"); ah.setObjectName("clockSectionTitle"); right.addWidget(ah)
        hint=QtWidgets.QLabel("Check items in the order you want to focus on them."); hint.setObjectName("clockMuted"); hint.setWordWrap(True); right.addWidget(hint)
        self.scroll=QtWidgets.QScrollArea(); self.scroll.setWidgetResizable(True); self.scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.itemsHost=QtWidgets.QWidget(); self.itemsHost.setObjectName("clockItemsHost"); self.itemsLayout=QtWidgets.QVBoxLayout(self.itemsHost); self.itemsLayout.setContentsMargins(0,4,0,4); self.itemsLayout.setSpacing(7); self.itemsLayout.addStretch(1)
        self.scroll.setWidget(self.itemsHost); right.addWidget(self.scroll,1)
        queueHeader = QtWidgets.QHBoxLayout()
        qh = QtWidgets.QLabel("FOCUS QUEUE")
        qh.setObjectName("clockSectionTitle")
        self.queueCount = QtWidgets.QLabel("0 items")
        self.queueCount.setObjectName("queueCount")
        queueHeader.addWidget(qh)
        queueHeader.addStretch(1)
        queueHeader.addWidget(self.queueCount)
        right.addLayout(queueHeader)

        self.queueList = QtWidgets.QListWidget()
        self.queueList.setObjectName("focusQueue")
        self.queueList.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.queueList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.queueList.setMaximumHeight(138)
        self.queueList.setMinimumHeight(72)
        right.addWidget(self.queueList)

        self.queueEmpty = QtWidgets.QLabel("Select items above to build your focus order.")
        self.queueEmpty.setObjectName("clockMuted")
        self.queueEmpty.setWordWrap(True)
        right.addWidget(self.queueEmpty)
        body.addWidget(controls,3); body.addWidget(available,2)

        self.pageClock=QtCore.QTimer(self); self.pageClock.timeout.connect(self._refresh_preview); self.pageClock.start(250)
        self.clockRadio.toggled.connect(self._mode_changed); self.timerRadio.toggled.connect(self._mode_changed)
        for spin in (self.hours,self.minutes,self.seconds): spin.valueChanged.connect(self._refresh_preview)
        self.launchButton.clicked.connect(self._launch); self._mode_changed()
        self.itemsRefreshTimer = QtCore.QTimer(self)
        self.itemsRefreshTimer.timeout.connect(self.refresh_items)
        self.itemsRefreshTimer.start(1000)

    def refresh_items(self):
        self._sync_queue_with_controller()
        while self.itemsLayout.count()>1:
            item=self.itemsLayout.takeAt(0); w=item.widget()
            if w: w.deleteLater()
        self.item_checks={}
        step_header=QtWidgets.QLabel("CHRONO STEPS"); step_header.setObjectName("itemGroup"); self.itemsLayout.insertWidget(self.itemsLayout.count()-1,step_header)
        tasks=list(self.task_controller.tasks)
        for task in tasks:
            for step in getattr(task,"kaizen_steps",[]):
                if getattr(step,"completed",False): continue
                date = getattr(step, "scheduled_date", None)
                date_text = self._format_date(date)
                detail = f"{task.title}" + (f"  •  {date_text}" if date_text else "")
                self._add_item("step", task, step, step.description, detail)
        task_header=QtWidgets.QLabel("TASKS"); task_header.setObjectName("itemGroup"); self.itemsLayout.insertWidget(self.itemsLayout.count()-1,task_header)
        for task in tasks:
            if getattr(task,"completed",False): continue
            deadline=getattr(task,"deadline_datetime",None)
            detail=deadline.strftime("Deadline: %b %d, %I:%M %p") if deadline else "No deadline"
            self._add_item("task",task,None,task.title,detail)

    def _sync_queue_with_controller(self):
        live = []
        tasks = list(self.task_controller.tasks)
        for item in self.queue:
            key, kind, queued_task, queued_step, title = item
            task = queued_task if queued_task in tasks else None
            if task is None:
                task_id = getattr(queued_task, "db_id", None)
                task = next((t for t in tasks if task_id is not None and getattr(t, "db_id", None) == task_id), None)
            if task is None or getattr(task, "completed", False):
                continue
            if kind == "step":
                steps = list(getattr(task, "kaizen_steps", []))
                step = queued_step if queued_step in steps else None
                if step is None:
                    step_id = getattr(queued_step, "db_id", None)
                    step = next((st for st in steps if step_id is not None and getattr(st, "db_id", None) == step_id), None)
                if step is None or getattr(step, "completed", False):
                    continue
                live.append((self._key(kind, task, step), kind, task, step, getattr(step, "description", title)))
            else:
                live.append((self._key(kind, task, None), kind, task, None, getattr(task, "title", title)))
        self.queue = live
        self._update_queue_summary()

    @staticmethod
    def _format_date(value):
        if value in (None, ""):
            return ""
        if hasattr(value, "strftime"):
            return value.strftime("%b %d")
        text = str(value).strip()
        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y", "%m/%d/%y"):
            try:
                return datetime.strptime(text, fmt).strftime("%b %d")
            except ValueError:
                pass
        return text

    def _key(self,kind,task,step):
        return (kind,id(task),id(step) if step is not None else 0)

    def _add_item(self,kind,task,step,title,detail):
        key=self._key(kind,task,step)
        box = QtWidgets.QCheckBox(f"{title}\n{detail}")
        box.setObjectName("queueChoice")
        box.setProperty("queued", any(x[0] == key for x in self.queue))
        box.setChecked(any(x[0] == key for x in self.queue))
        box.toggled.connect(lambda checked,k=key,a=kind,t=task,s=step,n=title:self._toggle_queue(checked,k,a,t,s,n))
        self.item_checks[key]=box; self.itemsLayout.insertWidget(self.itemsLayout.count()-1,box)

    def _toggle_queue(self,checked,key,kind,task,step,title):
        box = self.item_checks.get(key)
        if box is not None:
            box.setProperty("queued", checked)
            box.style().unpolish(box)
            box.style().polish(box)
        if checked:
            if not any(x[0]==key for x in self.queue): self.queue.append((key,kind,task,step,title))
        else:
            self.queue=[x for x in self.queue if x[0]!=key]
        self._update_queue_summary()

    def _update_queue_summary(self):
        self.queueList.clear()
        count = len(self.queue)
        self.queueCount.setText(f"{count} item" if count == 1 else f"{count} items")
        self.queueEmpty.setVisible(count == 0)
        self.queueList.setVisible(count > 0)
        for index, item in enumerate(self.queue, 1):
            list_item = QtWidgets.QListWidgetItem(f"{index:02d}   {item[4]}")
            list_item.setData(QtCore.Qt.ItemDataRole.UserRole, item[0])
            list_item.setSizeHint(QtCore.QSize(0, 32))
            self.queueList.addItem(list_item)

    def _mode_changed(self):
        timer=self.timerRadio.isChecked()
        for spin in (self.hours,self.minutes,self.seconds): spin.setEnabled(timer)
        self.launchButton.setText("Launch Timer" if timer else "Launch Digital Clock"); self._refresh_preview()

    def _refresh_preview(self):
        if self.clockRadio.isChecked(): self.preview.setText(QtCore.QTime.currentTime().toString("hh:mm:ss AP")); return
        total=self.hours.value()*3600+self.minutes.value()*60+self.seconds.value(); h=total//3600; m=(total%3600)//60; s=total%60
        self.preview.setText(f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}")

    def _launch(self):
        total=0 if self.clockRadio.isChecked() else self.hours.value()*3600+self.minutes.value()*60+self.seconds.value()
        if self.timerRadio.isChecked() and total<=0: return
        self.launch_requested.emit("clock" if self.clockRadio.isChecked() else "timer",total,list(self.queue))

    def remove_queue_key(self,key):
        self.queue=[x for x in self.queue if x[0]!=key]
        if key in self.item_checks:
            self.item_checks[key].blockSignals(True); self.item_checks[key].setChecked(False); self.item_checks[key].blockSignals(False)
        self._update_queue_summary()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_items()

    def apply_theme(self):
        c=palette(getattr(self.window(),"current_theme","default"))
        self.setStyleSheet(f"""
            QWidget#chronoClockPage {{ background: transparent; color: {c['text']}; }}
            QLabel#clockPageTitle {{ color:{c['text']}; font:700 23px 'Segoe UI'; }}
            QLabel#clockPageSubtitle,QLabel#clockMuted,QLabel#queueCount {{ color:{c['muted']}; font:12px 'Segoe UI'; }}
            QLabel#clockSectionTitle,QLabel#itemGroup {{ color:{c['text']}; font:700 12px 'Segoe UI'; }}
            QFrame#clockCard {{ background:{c['surface']}; border:1px solid {c['border_soft']}; border-radius:14px; }}
            QFrame#timerSetup {{ background:{c['surface_alt']}; border:1px solid {c['border_soft']}; border-radius:10px; }}
            QLabel#clockPreview {{ background:{c['surface_alt']}; color:{c['accent_hover']}; border:1px solid {c['border']}; border-radius:10px; font-family:Consolas,'Courier New',monospace; font-size:36px; font-weight:700; }}
            QRadioButton,QCheckBox#queueChoice {{ color:{c['text']}; spacing:9px; font:12px 'Segoe UI'; }}
            QCheckBox#queueChoice {{ background:{c['surface_alt']}; border:1px solid {c['border_soft']}; border-radius:9px; padding:9px 10px; }}
            QCheckBox#queueChoice:hover {{ border-color:{c['border']}; background:{c['surface']}; }}
            QCheckBox#queueChoice[queued="true"] {{ border-color:{c['accent']}; background:{c['surface']}; }}
            QListWidget#focusQueue {{ background:{c['surface_alt']}; color:{c['text']}; border:1px solid {c['border_soft']}; border-radius:9px; padding:4px; outline:none; }}
            QListWidget#focusQueue::item {{ border:none; border-bottom:1px solid {c['border_soft']}; padding:5px 8px; }}
            QListWidget#focusQueue::item:last {{ border-bottom:none; }}
            QSpinBox {{ color:{c['text']}; background:{c['input']}; border:1px solid {c['border_soft']}; border-radius:8px; padding:7px; min-width:62px; selection-background-color:{c['accent']}; selection-color:{c['text']}; }}
            QSpinBox:focus {{ border:1px solid {c['accent']}; }}
            QLabel#timerColon {{ color:{c['muted']}; font:700 15px 'Segoe UI'; }}
            QPushButton#timeStepButton {{ color:{c['text']}; background:{c['surface_alt']}; border:1px solid {c['border_soft']}; border-radius:7px; font:700 14px 'Segoe UI'; padding:0px; }}
            QPushButton#timeStepButton:hover {{ background:{c['surface']}; border-color:{c['accent']}; }}
            QPushButton#timeStepButton:pressed {{ background:{c['accent']}; color:{c['text']}; }}
            QPushButton#clockLaunch {{ background:{c['accent']}; color:{c['text']}; border:1px solid {c['accent_hover']}; border-radius:9px; padding:9px 15px; font:600 12px 'Segoe UI'; }}
            QScrollArea {{ background:transparent; border:none; }}
            QScrollArea > QWidget > QWidget {{ background:{c['surface']}; border:none; }}
            QWidget#clockItemsHost {{ background:{c['surface']}; border:none; }}
        """)
