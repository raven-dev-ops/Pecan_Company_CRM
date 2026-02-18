from __future__ import annotations

import os
import subprocess
from pathlib import Path

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from pecan_crm.config.store import ConfigStore
from pecan_crm.db.repositories.sales import SalesRepository
from pecan_crm.db.runtime import build_session_factory_from_settings


class SalesHistoryPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.config_store = ConfigStore()

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())

        self.payment_filter = QComboBox()
        self.payment_filter.addItems(["ANY", "CASH", "CARD", "OTHER"])

        self.receipt_filter = QLineEdit()
        self.receipt_filter.setPlaceholderText("Receipt contains")

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("From"))
        filter_row.addWidget(self.date_from)
        filter_row.addWidget(QLabel("To"))
        filter_row.addWidget(self.date_to)
        filter_row.addWidget(QLabel("Payment"))
        filter_row.addWidget(self.payment_filter)
        filter_row.addWidget(QLabel("Receipt"))
        filter_row.addWidget(self.receipt_filter)
        filter_row.addWidget(refresh_btn)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            ["Sale ID", "Receipt", "Date/Time", "Payment", "Status", "Total", "Customer"]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._load_detail)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)

        regenerate_btn = QPushButton("Open/Regen Receipt")
        regenerate_btn.clicked.connect(self._open_or_regen_receipt)
        print_btn = QPushButton("Print Receipt")
        print_btn.clicked.connect(self._print_receipt)
        void_btn = QPushButton("Void Sale")
        void_btn.clicked.connect(self._void_sale)
        export_btn = QPushButton("Export CSV")
        export_btn.clicked.connect(self._export_csv)

        action_row = QHBoxLayout()
        action_row.addWidget(regenerate_btn)
        action_row.addWidget(print_btn)
        action_row.addWidget(void_btn)
        action_row.addWidget(export_btn)
        action_row.addStretch(1)

        self.summary_date = QDateEdit()
        self.summary_date.setCalendarPopup(True)
        self.summary_date.setDate(QDate.currentDate())
        summary_btn = QPushButton("Daily Summary")
        summary_btn.clicked.connect(self._daily_summary)
        self.summary_output = QLabel("-")

        summary_row = QHBoxLayout()
        summary_row.addWidget(QLabel("Date"))
        summary_row.addWidget(self.summary_date)
        summary_row.addWidget(summary_btn)
        summary_row.addWidget(self.summary_output, stretch=1)

        layout = QVBoxLayout(self)
        layout.addLayout(filter_row)
        layout.addWidget(self.table)
        layout.addWidget(QLabel("Sale Detail"))
        layout.addWidget(self.detail_text)
        layout.addLayout(action_row)
        layout.addLayout(summary_row)

        self._refresh()

    def _repository(self) -> SalesRepository | None:
        try:
            return SalesRepository(build_session_factory_from_settings())
        except Exception as exc:
            QMessageBox.warning(self, "Sales History", str(exc))
            return None

    def _refresh(self) -> None:
        repo = self._repository()
        if repo is None:
            return

        items = repo.list_sales(
            date_from=self.date_from.date().toPython(),
            date_to=self.date_to.date().toPython(),
            payment_method=self.payment_filter.currentText(),
            receipt_number_contains=self.receipt_filter.text().strip(),
        )

        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.table.setItem(row, 0, QTableWidgetItem(str(item.sale_id)))
            self.table.setItem(row, 1, QTableWidgetItem(item.receipt_number))
            self.table.setItem(row, 2, QTableWidgetItem(item.sold_at_utc.strftime("%Y-%m-%d %H:%M:%S")))
            self.table.setItem(row, 3, QTableWidgetItem(item.payment_method))
            self.table.setItem(row, 4, QTableWidgetItem(item.status))
            self.table.setItem(row, 5, QTableWidgetItem(f"${item.total:.2f}"))
            self.table.setItem(row, 6, QTableWidgetItem(item.customer_name))

    def _selected_sale_id(self) -> int | None:
        selected = self.table.selectedItems()
        if not selected:
            return None
        return int(self.table.item(selected[0].row(), 0).text())

    def _load_detail(self) -> None:
        sale_id = self._selected_sale_id()
        if sale_id is None:
            self.detail_text.clear()
            return

        repo = self._repository()
        if repo is None:
            return

        try:
            sale, items, customer = repo.get_sale_detail(sale_id)
        except Exception as exc:
            QMessageBox.critical(self, "Sales History", f"Failed to load detail: {exc}")
            return

        lines = [
            f"Sale ID: {sale.sale_id}",
            f"Receipt: {sale.receipt_number}",
            f"Status: {sale.status}",
            f"Payment: {sale.payment_method}",
            f"Customer ID: {sale.customer_id or '-'}",
            f"Subtotal: ${sale.subtotal:.2f}",
            f"Discount: ${sale.discount_total:.2f}",
            f"Tax: ${sale.tax_total:.2f}",
            f"Total: ${sale.total:.2f}",
            "Items:",
        ]
        for item in items:
            measure = f"qty={item.quantity}" if item.unit_type == "EACH" else f"wt={item.weight_lbs}"
            lines.append(
                f"- {item.product_name_snapshot} | {measure} | ${item.unit_price:.2f} | ${item.line_subtotal:.2f}"
            )

        if sale.status == "VOIDED" and sale.void_reason:
            lines.append(f"Void reason: {sale.void_reason}")

        self.detail_text.setPlainText("\n".join(lines))

    def _open_or_regen_receipt(self) -> None:
        sale_id = self._selected_sale_id()
        if sale_id is None:
            QMessageBox.warning(self, "Sales History", "Select a sale first.")
            return

        repo = self._repository()
        if repo is None:
            return

        config = self.config_store.load()

        try:
            sale, _, _ = repo.get_sale_detail(sale_id)
            receipt_path = Path(config.receipt_folder) / f"receipt_{sale.receipt_number}.pdf"
            if not receipt_path.exists():
                receipt_path = repo.regenerate_receipt(
                    sale_id=sale_id,
                    receipt_folder=Path(config.receipt_folder),
                    business_name=config.business.name,
                    business_address=config.business.address,
                    business_phone=config.business.phone,
                )
            self._open_file(receipt_path)
        except Exception as exc:
            QMessageBox.critical(self, "Sales History", f"Receipt open/regenerate failed: {exc}")

    def _print_receipt(self) -> None:
        sale_id = self._selected_sale_id()
        if sale_id is None:
            QMessageBox.warning(self, "Sales History", "Select a sale first.")
            return

        repo = self._repository()
        if repo is None:
            return

        config = self.config_store.load()

        try:
            sale, _, _ = repo.get_sale_detail(sale_id)
            receipt_path = Path(config.receipt_folder) / f"receipt_{sale.receipt_number}.pdf"
            if not receipt_path.exists():
                receipt_path = repo.regenerate_receipt(
                    sale_id=sale_id,
                    receipt_folder=Path(config.receipt_folder),
                    business_name=config.business.name,
                    business_address=config.business.address,
                    business_phone=config.business.phone,
                )

            if hasattr(os, "startfile"):
                os.startfile(str(receipt_path), "print")  # type: ignore[attr-defined]
            else:
                raise RuntimeError("Print action is only supported on Windows")

            QMessageBox.information(self, "Sales History", "Print command sent.")
        except Exception as exc:
            QMessageBox.critical(self, "Sales History", f"Print failed: {exc}")

    def _void_sale(self) -> None:
        sale_id = self._selected_sale_id()
        if sale_id is None:
            QMessageBox.warning(self, "Sales History", "Select a sale first.")
            return

        reason, ok = QInputDialog.getText(self, "Void Sale", "Reason for void:")
        if not ok:
            return

        repo = self._repository()
        if repo is None:
            return

        try:
            repo.void_sale(sale_id=sale_id, reason=reason)
            QMessageBox.information(self, "Sales History", "Sale voided.")
            self._refresh()
        except Exception as exc:
            QMessageBox.critical(self, "Sales History", f"Void failed: {exc}")

    def _export_csv(self) -> None:
        repo = self._repository()
        if repo is None:
            return

        directory = QFileDialog.getExistingDirectory(self, "Choose export folder")
        if not directory:
            return

        try:
            files = repo.export_csv(Path(directory))
            QMessageBox.information(
                self,
                "Sales History",
                "Export complete:\n" + "\n".join(f"{k}: {v}" for k, v in files.items()),
            )
        except Exception as exc:
            QMessageBox.critical(self, "Sales History", f"Export failed: {exc}")

    def _daily_summary(self) -> None:
        repo = self._repository()
        if repo is None:
            return

        try:
            summary = repo.daily_summary(for_date=self.summary_date.date().toPython())
            self.summary_output.setText(
                f"Gross ${summary.gross:.2f} | Tax ${summary.tax_total:.2f} | Discounts ${summary.discounts:.2f} | Net ${summary.net:.2f} | Txns {summary.transaction_count}"
            )
        except Exception as exc:
            QMessageBox.critical(self, "Sales History", f"Summary failed: {exc}")

    @staticmethod
    def _open_file(path: Path) -> None:
        if hasattr(os, "startfile"):
            os.startfile(str(path))  # type: ignore[attr-defined]
            return

        if os.name == "posix":
            subprocess.run(["xdg-open", str(path)], check=True)
            return

        raise RuntimeError("Unsupported platform for opening files")
