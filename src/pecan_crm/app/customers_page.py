from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QHBoxLayout,
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

from pecan_crm.db.repositories.customers import CustomerInput, CustomerRepository
from pecan_crm.db.runtime import build_session_factory_from_settings


class CustomersPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.selected_customer_id: int | None = None

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, phone, or email")
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
        self.table.setHorizontalHeaderLabels(["ID", "First", "Last", "Phone", "Email", "Active"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._load_selected)

        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.notes_input = QTextEdit()
        self.active_input = QCheckBox("Active")
        self.active_input.setChecked(True)

        form = QFormLayout()
        form.addRow("First Name", self.first_name_input)
        form.addRow("Last Name", self.last_name_input)
        form.addRow("Phone", self.phone_input)
        form.addRow("Email", self.email_input)
        form.addRow("Notes", self.notes_input)
        form.addRow("Status", self.active_input)

        new_btn = QPushButton("New")
        new_btn.clicked.connect(self._clear_form)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save)

        action_row = QHBoxLayout()
        action_row.addWidget(new_btn)
        action_row.addWidget(save_btn)
        action_row.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addLayout(search_row)
        layout.addWidget(self.table)
        layout.addLayout(form)
        layout.addLayout(action_row)

        self._refresh()

    def _repository(self) -> CustomerRepository | None:
        try:
            return CustomerRepository(build_session_factory_from_settings())
        except Exception as exc:
            QMessageBox.warning(self, "Customers", str(exc))
            return None

    def _refresh(self) -> None:
        repo = self._repository()
        if repo is None:
            return

        customers = repo.list_customers(
            include_inactive=self.include_inactive.isChecked(),
            search=self.search_input.text().strip(),
        )

        self.table.setRowCount(len(customers))
        for row, c in enumerate(customers):
            self.table.setItem(row, 0, QTableWidgetItem(str(c.customer_id)))
            self.table.setItem(row, 1, QTableWidgetItem(c.first_name or ""))
            self.table.setItem(row, 2, QTableWidgetItem(c.last_name or ""))
            self.table.setItem(row, 3, QTableWidgetItem(c.phone or ""))
            self.table.setItem(row, 4, QTableWidgetItem(c.email or ""))
            self.table.setItem(row, 5, QTableWidgetItem("Yes" if c.is_active else "No"))

    def _load_selected(self) -> None:
        selected = self.table.selectedItems()
        if not selected:
            return

        row = selected[0].row()
        self.selected_customer_id = int(self.table.item(row, 0).text())
        self.first_name_input.setText(self.table.item(row, 1).text())
        self.last_name_input.setText(self.table.item(row, 2).text())
        self.phone_input.setText(self.table.item(row, 3).text())
        self.email_input.setText(self.table.item(row, 4).text())
        self.active_input.setChecked(self.table.item(row, 5).text() == "Yes")

    def _save(self) -> None:
        repo = self._repository()
        if repo is None:
            return

        first = self.first_name_input.text().strip()
        last = self.last_name_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()

        duplicates = repo.find_likely_duplicates(
            phone=phone,
            email=email,
            first_name=first,
            last_name=last,
            exclude_customer_id=self.selected_customer_id,
        )
        if duplicates:
            answer = QMessageBox.warning(
                self,
                "Possible duplicate",
                f"Found {len(duplicates)} likely duplicate customer(s). Save anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

        payload = CustomerInput(
            first_name=first,
            last_name=last,
            phone=phone,
            email=email,
            notes=self.notes_input.toPlainText().strip(),
            is_active=self.active_input.isChecked(),
        )

        try:
            repo.save(payload, customer_id=self.selected_customer_id)
            QMessageBox.information(self, "Customers", "Saved.")
            self._refresh()
        except Exception as exc:
            QMessageBox.critical(self, "Customers", f"Save failed: {exc}")

    def _clear_form(self) -> None:
        self.selected_customer_id = None
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.notes_input.clear()
        self.active_input.setChecked(True)