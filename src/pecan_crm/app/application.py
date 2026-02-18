from __future__ import annotations

import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from pecan_crm.app.logging_utils import configure_logging
from pecan_crm.app.main_window import MainWindow


APP_NAME = "PecanCRM"


def run() -> int:
    log_path = configure_logging(APP_NAME)
    logging.getLogger(__name__).info("Starting app; log file: %s", log_path)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    window = MainWindow()
    window.show()

    return app.exec()