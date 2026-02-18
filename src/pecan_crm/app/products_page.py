from __future__ import annotations

from decimal import Decimal

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from pecan_crm.db.repositories.products import ProductInput, ProductRepository
from pecan_crm.db.runtime import build_session_factory_from_settings


class ProductsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.selected_product_id: int | None = None

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or SKU")
        self.include_inactive = QCheckBox("Include inactive")
        self.include_inactive.setChecked(True)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh)

        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Search:"))
        search_row.addWidget(self.search_input, stretch=1)
        search_row.addWidget(self.include_inactive)
        search_row.addWidget(refresh_btn)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "SKU", "Unit Type", "Price", "Active"])
        self.table.itemSelectionChanged.connect(self._load_selected)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.name_input = QLineEdit()
        self.sku_input = QLineEdit()
        self.unit_type_input = QComboBox()
        self.unit_type_input.addItems(["EACH", "WEIGHT"])
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.00, 9999999.99)
        self.price_input.setDecimals(2)
        self.price_input.setPrefix("$")
        self.active_input = QCheckBox("Active")
        self.active_input.setChecked(True)

        form = QFormLayout()
        form.addRow("Name", self.name_input)
        form.addRow("SKU", self.sku_input)
        form.addRow("Unit Type", self.unit_type_input)
        form.addRow("Price", self.price_input)
        form.addRow("Status", self.active_input)

        new_btn = QPushButton("New")
        new_btn.clicked.connect(self._clear_form)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save)
        archive_btn = QPushButton("Archive")
        archive_btn.clicked.connect(self._archive)

        action_row = QHBoxLayout()
        action_row.addWidget(new_btn)
        action_row.addWidget(save_btn)
        action_row.addWidget(archive_btn)
        action_row.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addLayout(search_row)
        layout.addWidget(self.table)
        layout.addLayout(form)
        layout.addLayout(action_row)

        self._refresh()

    def _repository(self) -> ProductRepository | None:
        try:
            return ProductRepository(build_session_factory_from_settings())
        except Exception as exc:
            QMessageBox.warning(self, "Products", str(exc))
            return None

    def _refresh(self) -> None:
        repo = self._repository()
        if repo is None:
            return

        products = repo.list_products(
            include_inactive=self.include_inactive.isChecked(),
            search=self.search_input.text().strip(),
        )

        self.table.setRowCount(len(products))
        for row, p in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(str(p.product_id)))
            self.table.setItem(row, 1, QTableWidgetItem(p.name))
            self.table.setItem(row, 2, QTableWidgetItem(p.sku or ""))
            self.table.setItem(row, 3, QTableWidgetItem(p.unit_type))
            self.table.setItem(row, 4, QTableWidgetItem(str(p.unit_price)))
            self.table.setItem(row, 5, QTableWidgetItem("Yes" if p.is_active else "No"))

    def _load_selected(self) -> None:
        selected = self.table.selectedItems()
        if not selected:
            return

        row = selected[0].row()
        self.selected_product_id = int(self.table.item(row, 0).text())
        self.name_input.setText(self.table.item(row, 1).text())
        self.sku_input.setText(self.table.item(row, 2).text())
        self.unit_type_input.setCurrentText(self.table.item(row, 3).text())
        self.price_input.setValue(float(self.table.item(row, 4).text()))
        self.active_input.setChecked(self.table.item(row, 5).text() == "Yes")

    def _save(self) -> None:
        repo = self._repository()
        if repo is None:
            return

        payload = ProductInput(
            name=self.name_input.text().strip(),
            sku=self.sku_input.text().strip(),
            unit_type=self.unit_type_input.currentText(),
            unit_price=Decimal(str(self.price_input.value())),
            is_active=self.active_input.isChecked(),
        )

        try:
            repo.save(payload, product_id=self.selected_product_id)
            QMessageBox.information(self, "Products", "Saved.")
            self._refresh()
        except Exception as exc:
            QMessageBox.critical(self, "Products", f"Save failed: {exc}")

    def _archive(self) -> None:
        if self.selected_product_id is None:
            QMessageBox.warning(self, "Products", "Select a product to archive.")
            return

        repo = self._repository()
        if repo is None:
            return

        try:
            repo.archive(self.selected_product_id)
            QMessageBox.information(self, "Products", "Archived.")
            self._refresh()
        except Exception as exc:
            QMessageBox.critical(self, "Products", f"Archive failed: {exc}")

    def _clear_form(self) -> None:
        self.selected_product_id = None
        self.name_input.clear()
        self.sku_input.clear()
        self.unit_type_input.setCurrentIndex(0)
        self.price_input.setValue(0.0)
        self.active_input.setChecked(True)