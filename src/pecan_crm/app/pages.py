from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


@dataclass(frozen=True)
class PageDefinition:
    key: str
    title: str
    placeholder_text: str


PAGES: list[PageDefinition] = [
    PageDefinition("settings", "Settings", "Configure database, business profile, and tax."),
    PageDefinition("products", "Products", "Create and maintain product catalog."),
    PageDefinition("customers", "Customers", "Manage customer records and lookup."),
    PageDefinition("ring_up", "Ring-Up", "Build cart and prepare tender."),
    PageDefinition("sales_history", "Sales History", "Find prior sales and reprint receipts."),
]


class PlaceholderPage(QWidget):
    def __init__(self, title: str, placeholder: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        title_label = QLabel(f"<h2>{title}</h2>")
        body_label = QLabel(placeholder)
        body_label.setWordWrap(True)
        layout.addWidget(title_label)
        layout.addWidget(body_label)
        layout.addStretch(1)