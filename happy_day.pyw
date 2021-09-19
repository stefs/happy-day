#!/usr/bin/env python

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
    value: timedelta
    total: timedelta

    def __post_init__(self) -> None:
        self.value = max(min(self.value, self.total), timedelta())

    @property
    def remaining(self) -> timedelta:
        return self.total - self.value


class HappyDay(QMainWindow):
    PHASES = [
        Phase(name='Wake', start=time(hour=7, minute=30)),
        Phase(name='Sleep', start=time(hour=23, minute=30))]

    def __init__(self) -> None:
        super().__init__()
        # widgets and layout
        layout = QGridLayout()
        self.progress_bars = []
        for index, phase in enumerate(self.PHASES):
            layout.addWidget(QLabel(phase.name), index, 0)
            layout.addWidget(QLabel(f'{phase.start:%H:%M}'), index, 1)
            progress_bar = QProgressBar()
            layout.addWidget(progress_bar, index, 2)
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
        day = now.date() if now.time() > self.PHASES[0].start else now.date() - timedelta(days=1)
        # calculate start times
        start_times = [datetime.combine(day, phase.start) for phase in self.PHASES]
        start_times.append(datetime.combine(day + timedelta(days=1), self.PHASES[0].start))
        self.progress_values = [
            Progress(
                value=now - start_times[index],
                total=start_times[index + 1] - start_times[index])
            for index in range(len(self.progress_bars))]
        # set progress bars values
        for progress_bar, progress in zip(self.progress_bars, self.progress_values):
            progress_bar.setMaximum(int(progress.total.total_seconds()))
            progress_bar.setValue(max(int(progress.value.total_seconds()), 1))
            progress_bar.setFormat(f'{progress.remaining.total_seconds() / 3600:.1f} h')
        # set progress bar widths
        self.update_progress_width(self.width(), self.width())


if __name__ == '__main__':
    main()
