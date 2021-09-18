from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from datetime import time, datetime, timedelta
from typing import Optional

from PySide6.QtCore import QTimer
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QMainWindow, QApplication, QGridLayout, QLabel, QProgressBar, QWidget


def main() -> None:
    # noinspection SpellCheckingInspection
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    # run application
    app = QApplication([])
    widget = HappyDay()
    widget.show()
    sys.exit(app.exec())


@dataclass
class Phase(object):
    name: str
    start: time


@dataclass
class Progress(object):
    value: float
    total: float


class HappyDay(QMainWindow):
    PHASES = [
        Phase(name='Wake', start=time(hour=7)),
        Phase(name='Sleep', start=time(hour=23))]

    def __init__(self) -> None:
        super().__init__()
        # widgets and layout
        layout = QGridLayout()
        self.progress_bars = []
        for index, phase in enumerate(self.PHASES):
            layout.addWidget(QLabel(phase.name), index, 0)
            progress_bar = QProgressBar()
            layout.addWidget(progress_bar, index, 1)
            self.progress_bars.append(progress_bar)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        # attributes
        self.progress_values: Optional[list[Progress]] = None
        self.progress_width_offset: Optional[int] = None
        # start status update
        QTimer.singleShot(100, self.update_status)
        self.timer = QTimer()
        self.timer.setInterval(10000)
        self.timer.timeout.connect(self.update_status)
        self.timer.start()

    def resizeEvent(
            self,
            event: QResizeEvent
    ) -> None:
        self.update_progress_width(event.oldSize().width(), event.size().width())
        super().resizeEvent(event)

    def update_progress_width(
            self,
            width_old: int,
            width_new: int
    ) -> None:
        if self.progress_values is None:
            return
        if self.progress_width_offset is None:
            self.progress_width_offset = width_old - self.progress_bars[0].width()
        width_max = width_new - self.progress_width_offset
        total_max = max(progress_value.total for progress_value in self.progress_values)
        for progress_bar, progress in zip(self.progress_bars, self.progress_values):
            progress_bar.setMaximumWidth(progress.total / total_max * width_max)

    def update_status(self) -> None:
        now = datetime.now()
        # calculate start times
        start_times = [datetime.combine(now.date(), phase.start) for phase in self.PHASES]
        start_times.append(datetime.combine(now.date() + timedelta(days=1), self.PHASES[0].start))
        self.progress_values = [
            Progress(
                value=(now - start_times[index]).total_seconds(),
                total=(start_times[index + 1] - start_times[index]).total_seconds())
            for index in range(len(self.progress_bars))]
        # set progress bars values
        for progress_bar, progress in zip(self.progress_bars, self.progress_values):
            progress_bar.setMaximum(progress.total)
            progress_bar.setValue(progress.value)
        # set progress bar widths
        self.update_progress_width(self.width(), self.width())


if __name__ == '__main__':
    main()
