from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from datetime import time, datetime, timedelta

from PySide6.QtCore import QTimer
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


class HappyDay(QMainWindow):
    PHASES = [
        Phase('Wake', time(hour=7)),
        Phase('Sleep', time(hour=23))]

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
        # start status update
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_status)
        self.timer.start()

    def update_status(self) -> None:
        now = datetime.now()
        start_times = [
            datetime.combine(now.date(), phase.start)
            for phase in self.PHASES]
        start_times.append(datetime.combine(now.date() + timedelta(days=1), self.PHASES[0].start))
        for index, progress_bar in enumerate(self.progress_bars):
            start_time = start_times[index]
            start_time_next = start_times[index + 1]
            progress_bar.setMaximum((start_time_next - start_time).total_seconds())
            progress_bar.setValue((now - start_time).total_seconds())


if __name__ == '__main__':
    main()
