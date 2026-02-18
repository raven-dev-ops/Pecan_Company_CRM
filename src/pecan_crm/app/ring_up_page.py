from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from PySide6.QtWidgets import (
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

from pecan_crm.config.store import ConfigStore
from pecan_crm.db.repositories.sales import CartLineInput, FinalizeSaleInput, SalesRepository
from pecan_crm.db.runtime import build_session_factory_from_settings
from pecan_crm.domain.pricing import SaleLine, calculate_totals, line_subtotal


@dataclass
class CartRow:
    product_id: int
    product_name: str
    unit_type: str
    unit_price: Decimal
    quantity: Decimal | None
    weight_lbs: Decimal | None


class RingUpPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.config_store = ConfigStore()
        self.cart: list[CartRow] = []

        self.product_search_input = QLineEdit()
        self.product_search_input.setPlaceholderText("Search products")
        refresh_products_btn = QPushButton("Refresh Products")
        refresh_products_btn.clicked.connect(self._refresh_products)

        product_search_row = QHBoxLayout()
        product_search_row.addWidget(QLabel("Products:"))
        product_search_row.addWidget(self.product_search_input, stretch=1)
        product_search_row.addWidget(refresh_products_btn)

        self.product_table = QTableWidget(0, 5)
        self.product_table.setHorizontalHeaderLabels(["ID", "Name", "SKU", "Unit Type", "Price"])
        self.product_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setDecimals(3)
        self.quantity_input.setRange(0.000, 999999.000)
        self.weight_input = QDoubleSpinBox()
        self.weight_input.setDecimals(3)
        self.weight_input.setRange(0.000, 999999.000)

        add_to_cart_btn = QPushButton("Add to Cart")
        add_to_cart_btn.clicked.connect(self._add_to_cart)

        add_row = QHBoxLayout()
        add_row.addWidget(QLabel("Qty"))
        add_row.addWidget(self.quantity_input)
        add_row.addWidget(QLabel("Weight (lb)"))
        add_row.addWidget(self.weight_input)
        add_row.addWidget(add_to_cart_btn)
        add_row.addStretch(1)

        self.cart_table = QTableWidget(0, 6)
        self.cart_table.setHorizontalHeaderLabels(
            ["Product", "Unit Type", "Qty", "Weight", "Unit Price", "Line Subtotal"]
        )
        self.cart_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        remove_line_btn = QPushButton("Remove Selected Line")
        remove_line_btn.clicked.connect(self._remove_selected_line)

        self.customer_search_input = QLineEdit()
        self.customer_search_input.setPlaceholderText("Search customer (optional)")
        customer_refresh_btn = QPushButton("Find")
        customer_refresh_btn.clicked.connect(self._refresh_customers)

        self.customer_combo = QComboBox()
        self.customer_combo.addItem("No customer", None)

        customer_row = QHBoxLayout()
        customer_row.addWidget(QLabel("Customer:"))
        customer_row.addWidget(self.customer_search_input, stretch=1)
        customer_row.addWidget(customer_refresh_btn)
        customer_row.addWidget(self.customer_combo, stretch=1)

        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems(["CASH", "CARD", "OTHER"])

        self.discount_type_combo = QComboBox()
        self.discount_type_combo.addItems(["NONE", "PERCENT", "FIXED"])
        self.discount_value_input = QDoubleSpinBox()
        self.discount_value_input.setDecimals(2)
        self.discount_value_input.setRange(0.00, 999999.99)

        form = QFormLayout()
        form.addRow("Payment Method", self.payment_method_combo)
        form.addRow("Discount Type", self.discount_type_combo)
        form.addRow("Discount Value", self.discount_value_input)

        self.subtotal_label = QLabel("$0.00")
        self.discount_label = QLabel("$0.00")
        self.tax_label = QLabel("$0.00")
        self.total_label = QLabel("$0.00")

        totals_form = QFormLayout()
        totals_form.addRow("Subtotal", self.subtotal_label)
        totals_form.addRow("Discount", self.discount_label)
        totals_form.addRow("Tax", self.tax_label)
        totals_form.addRow("Total", self.total_label)

        finalize_btn = QPushButton("Finalize Sale")
        finalize_btn.clicked.connect(self._finalize_sale)

        layout = QVBoxLayout(self)
        layout.addLayout(product_search_row)
        layout.addWidget(self.product_table)
        layout.addLayout(add_row)
        layout.addWidget(self.cart_table)
        layout.addWidget(remove_line_btn)
        layout.addLayout(customer_row)
        layout.addLayout(form)
        layout.addLayout(totals_form)
        layout.addWidget(finalize_btn)
        layout.addStretch(1)

        self.discount_type_combo.currentIndexChanged.connect(self._recalculate_totals)
        self.discount_value_input.valueChanged.connect(self._recalculate_totals)

        self._refresh_products()
        self._refresh_customers()

    def _repository(self) -> SalesRepository | None:
        try:
            return SalesRepository(build_session_factory_from_settings())
        except Exception as exc:
            QMessageBox.warning(self, "Ring-Up", str(exc))
            return None

    def _refresh_products(self) -> None:
        repo = self._repository()
        if repo is None:
            return
        products = repo.list_active_products(search=self.product_search_input.text().strip())

        self.product_table.setRowCount(len(products))
        for row, p in enumerate(products):
            self.product_table.setItem(row, 0, QTableWidgetItem(str(p.product_id)))
            self.product_table.setItem(row, 1, QTableWidgetItem(p.name))
            self.product_table.setItem(row, 2, QTableWidgetItem(p.sku or ""))
            self.product_table.setItem(row, 3, QTableWidgetItem(p.unit_type))
            self.product_table.setItem(row, 4, QTableWidgetItem(str(p.unit_price)))

    def _refresh_customers(self) -> None:
        repo = self._repository()
        if repo is None:
            return

        customers = repo.search_customers(self.customer_search_input.text().strip())
        self.customer_combo.clear()
        self.customer_combo.addItem("No customer", None)
        for c in customers:
            full_name = " ".join(part for part in [c.first_name or "", c.last_name or ""] if part).strip()
            label = full_name or c.phone or c.email or f"Customer {c.customer_id}"
            self.customer_combo.addItem(label, c.customer_id)

    def _add_to_cart(self) -> None:
        selected = self.product_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ring-Up", "Select a product first.")
            return

        row = selected[0].row()
        product_id = int(self.product_table.item(row, 0).text())
        product_name = self.product_table.item(row, 1).text()
        unit_type = self.product_table.item(row, 3).text()
        unit_price = Decimal(self.product_table.item(row, 4).text())

        quantity = Decimal(str(self.quantity_input.value())) if unit_type == "EACH" else None
        weight = Decimal(str(self.weight_input.value())) if unit_type == "WEIGHT" else None

        if unit_type == "EACH" and quantity <= 0:
            QMessageBox.warning(self, "Ring-Up", "Quantity must be greater than zero.")
            return
        if unit_type == "WEIGHT" and weight <= 0:
            QMessageBox.warning(self, "Ring-Up", "Weight must be greater than zero.")
            return

        self.cart.append(
            CartRow(
                product_id=product_id,
                product_name=product_name,
                unit_type=unit_type,
                unit_price=unit_price,
                quantity=quantity,
                weight_lbs=weight,
            )
        )
        self._refresh_cart_table()
        self._recalculate_totals()

    def _refresh_cart_table(self) -> None:
        self.cart_table.setRowCount(len(self.cart))
        for row, item in enumerate(self.cart):
            sale_line = SaleLine(
                unit_type=item.unit_type,
                unit_price=item.unit_price,
                quantity=item.quantity,
                weight_lbs=item.weight_lbs,
            )
            line_total = line_subtotal(sale_line)
            self.cart_table.setItem(row, 0, QTableWidgetItem(item.product_name))
            self.cart_table.setItem(row, 1, QTableWidgetItem(item.unit_type))
            self.cart_table.setItem(row, 2, QTableWidgetItem(str(item.quantity or "")))
            self.cart_table.setItem(row, 3, QTableWidgetItem(str(item.weight_lbs or "")))
            self.cart_table.setItem(row, 4, QTableWidgetItem(str(item.unit_price)))
            self.cart_table.setItem(row, 5, QTableWidgetItem(str(line_total)))

    def _remove_selected_line(self) -> None:
        selected = self.cart_table.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        self.cart.pop(row)
        self._refresh_cart_table()
        self._recalculate_totals()

    def _recalculate_totals(self) -> None:
        config = self.config_store.load()
        lines = [
            SaleLine(
                unit_type=item.unit_type,
                unit_price=item.unit_price,
                quantity=item.quantity,
                weight_lbs=item.weight_lbs,
            )
            for item in self.cart
        ]

        if not lines:
            self.subtotal_label.setText("$0.00")
            self.discount_label.setText("$0.00")
            self.tax_label.setText("$0.00")
            self.total_label.setText("$0.00")
            return

        totals = calculate_totals(
            lines,
            tax_enabled=config.tax.enabled,
            tax_rate_percent=Decimal(str(config.tax.rate_percent)),
            discount_type=self.discount_type_combo.currentText(),
            discount_value=Decimal(str(self.discount_value_input.value())),
        )

        self.subtotal_label.setText(f"${totals.subtotal:.2f}")
        self.discount_label.setText(f"${totals.discount_total:.2f}")
        self.tax_label.setText(f"${totals.tax_total:.2f}")
        self.total_label.setText(f"${totals.total:.2f}")

    def _finalize_sale(self) -> None:
        if not self.cart:
            QMessageBox.warning(self, "Ring-Up", "Cart is empty.")
            return

        repo = self._repository()
        if repo is None:
            return

        config = self.config_store.load()
        customer_id = self.customer_combo.currentData()

        payload = FinalizeSaleInput(
            cart_lines=[
                CartLineInput(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    weight_lbs=item.weight_lbs,
                )
                for item in self.cart
            ],
            payment_method=self.payment_method_combo.currentText(),
            customer_id=customer_id,
            discount_type=self.discount_type_combo.currentText(),
            discount_value=Decimal(str(self.discount_value_input.value())),
            tax_enabled=config.tax.enabled,
            tax_rate_percent=Decimal(str(config.tax.rate_percent)),
            receipt_folder=Path(config.receipt_folder),
            business_name=config.business.name,
            business_address=config.business.address,
            business_phone=config.business.phone,
        )

        try:
            result = repo.finalize_sale(payload)
            QMessageBox.information(
                self,
                "Sale Complete",
                f"Sale #{result.sale_id} saved. Receipt {result.receipt_number} generated at:\n{result.receipt_path}",
            )
            self.cart.clear()
            self._refresh_cart_table()
            self._recalculate_totals()
        except Exception as exc:
            QMessageBox.critical(self, "Finalize Sale", f"Failed to finalize sale: {exc}")