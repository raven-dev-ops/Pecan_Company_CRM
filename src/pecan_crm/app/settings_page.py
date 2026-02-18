from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pecan_crm.config.models import AppConfig, BusinessProfileConfig, DatabaseConfig, TaxConfig
from pecan_crm.config.secret_store import SecretStore
from pecan_crm.config.store import ConfigStore
from pecan_crm.db.health import test_connection


class SettingsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.config_store = ConfigStore()
        self.secret_store = SecretStore()

        self.server_input = QLineEdit()
        self.database_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.business_name_input = QLineEdit()
        self.business_address_input = QLineEdit()
        self.business_phone_input = QLineEdit()

        self.tax_enabled_checkbox = QCheckBox("Enable tax")
        self.tax_rate_input = QDoubleSpinBox()
        self.tax_rate_input.setRange(0.0, 100.0)
        self.tax_rate_input.setDecimals(4)
        self.tax_rate_input.setSingleStep(0.01)
        self.tax_rate_input.setSuffix(" %")

        self.receipt_folder_input = QLineEdit()
        browse_receipt_btn = QPushButton("Browse")
        browse_receipt_btn.clicked.connect(self._choose_receipt_folder)

        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self._save)

        test_btn = QPushButton("Test Connection")
        test_btn.clicked.connect(self._test_connection)

        form = QFormLayout()
        form.addRow("Azure SQL Server", self.server_input)
        form.addRow("Azure SQL Database", self.database_input)
        form.addRow("Azure SQL Username", self.username_input)
        form.addRow("Azure SQL Password", self.password_input)
        form.addRow("Business Name", self.business_name_input)
        form.addRow("Business Address", self.business_address_input)
        form.addRow("Business Phone", self.business_phone_input)
        form.addRow("Tax Enabled", self.tax_enabled_checkbox)
        form.addRow("Tax Rate", self.tax_rate_input)

        receipt_row = QHBoxLayout()
        receipt_row.addWidget(self.receipt_folder_input, stretch=1)
        receipt_row.addWidget(browse_receipt_btn)
        receipt_row_widget = QWidget()
        receipt_row_widget.setLayout(receipt_row)
        form.addRow("Receipt Folder", receipt_row_widget)

        action_row = QHBoxLayout()
        action_row.addWidget(save_btn)
        action_row.addWidget(test_btn)
        action_row.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(action_row)
        layout.addStretch(1)

        self._load()

    def _load(self) -> None:
        config = self.config_store.load()
        self.server_input.setText(config.database.server)
        self.database_input.setText(config.database.database)
        self.username_input.setText(config.database.username)
        self.password_input.setText(self.secret_store.get_db_password())

        self.business_name_input.setText(config.business.name)
        self.business_address_input.setText(config.business.address)
        self.business_phone_input.setText(config.business.phone)

        self.tax_enabled_checkbox.setChecked(config.tax.enabled)
        self.tax_rate_input.setValue(config.tax.rate_percent)
        self.receipt_folder_input.setText(config.receipt_folder)

    def _build_config(self) -> AppConfig:
        return AppConfig(
            database=DatabaseConfig(
                server=self.server_input.text().strip(),
                database=self.database_input.text().strip(),
                username=self.username_input.text().strip(),
            ),
            business=BusinessProfileConfig(
                name=self.business_name_input.text().strip(),
                address=self.business_address_input.text().strip(),
                phone=self.business_phone_input.text().strip(),
            ),
            tax=TaxConfig(
                enabled=self.tax_enabled_checkbox.isChecked(),
                rate_percent=float(self.tax_rate_input.value()),
            ),
            receipt_folder=self.receipt_folder_input.text().strip(),
        )

    def _save(self) -> None:
        config = self._build_config()
        self.config_store.save(config)
        self.secret_store.set_db_password(self.password_input.text())

        receipt_dir = Path(config.receipt_folder)
        receipt_dir.mkdir(parents=True, exist_ok=True)

        QMessageBox.information(self, "Saved", "Settings saved successfully.")

    def _test_connection(self) -> None:
        try:
            test_connection(
                server=self.server_input.text().strip(),
                database=self.database_input.text().strip(),
                username=self.username_input.text().strip(),
                password=self.password_input.text(),
                attempts=3,
            )
            QMessageBox.information(self, "Connection", "Connection successful.")
        except Exception as exc:
            QMessageBox.critical(self, "Connection", f"Connection failed: {exc}")

    def _choose_receipt_folder(self) -> None:
        current = self.receipt_folder_input.text().strip() or str(Path.home())
        selected = QFileDialog.getExistingDirectory(self, "Select receipt folder", current)
        if selected:
            self.receipt_folder_input.setText(selected)