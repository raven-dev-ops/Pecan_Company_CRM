from __future__ import annotations

import logging

from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from pecan_crm.app.pages import PAGES, PlaceholderPage
from pecan_crm.app.settings_page import SettingsPage
from pecan_crm import __version__


LOGGER = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"Pecan Company CRM v{__version__}")
        self.resize(1200, 750)

        root = QWidget()
        layout = QHBoxLayout(root)

        self.nav = QListWidget()
        self.nav.setFixedWidth(240)
        self.stack = QStackedWidget()

        self._page_keys: list[str] = []
        self._build_pages()

        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.currentRowChanged.connect(self._log_page_change)

        layout.addWidget(self.nav)
        layout.addWidget(self.stack, stretch=1)

        self.setCentralWidget(root)
        self.statusBar().showMessage(f"Ready | Version {__version__}")

        if self.nav.count() > 0:
            self.nav.setCurrentRow(0)

    def _build_pages(self) -> None:
        self._add_page("settings", "Settings", SettingsPage())

        for page in PAGES:
            if page.key == "settings":
                continue
            widget = PlaceholderPage(page.title, page.placeholder_text)
            self._add_page(page.key, page.title, widget)

    def _add_page(self, key: str, title: str, widget: QWidget) -> None:
        self._page_keys.append(key)
        self.nav.addItem(QListWidgetItem(title))
        self.stack.addWidget(widget)

    def _log_page_change(self, index: int) -> None:
        if 0 <= index < len(self._page_keys):
            LOGGER.info("Navigated to page: %s", self._page_keys[index])
