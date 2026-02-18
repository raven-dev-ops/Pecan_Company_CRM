-- Canonical schema for Pecan Company CRM (Azure SQL)

CREATE TABLE customers (
    customer_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    first_name NVARCHAR(100) NULL,
    last_name NVARCHAR(100) NULL,
    phone NVARCHAR(30) NULL,
    email NVARCHAR(254) NULL,
    notes NVARCHAR(500) NULL,
    is_active BIT NOT NULL CONSTRAINT DF_customers_is_active DEFAULT (1),
    created_at_utc DATETIME2 NOT NULL CONSTRAINT DF_customers_created_at DEFAULT (SYSUTCDATETIME()),
    updated_at_utc DATETIME2 NOT NULL CONSTRAINT DF_customers_updated_at DEFAULT (SYSUTCDATETIME())
);

CREATE TABLE products (
    product_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    sku NVARCHAR(50) NULL,
    name NVARCHAR(200) NOT NULL,
    unit_type NVARCHAR(10) NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    is_active BIT NOT NULL CONSTRAINT DF_products_is_active DEFAULT (1),
    created_at_utc DATETIME2 NOT NULL CONSTRAINT DF_products_created_at DEFAULT (SYSUTCDATETIME()),
    updated_at_utc DATETIME2 NOT NULL CONSTRAINT DF_products_updated_at DEFAULT (SYSUTCDATETIME()),
    CONSTRAINT CK_products_unit_type CHECK (unit_type IN ('EACH', 'WEIGHT')),
    CONSTRAINT CK_products_unit_price_nonnegative CHECK (unit_price >= 0)
);

CREATE TABLE sales (
    sale_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    receipt_number NVARCHAR(20) NOT NULL,
    finalize_idempotency_key NVARCHAR(64) NULL,
    customer_id BIGINT NULL,
    payment_method NVARCHAR(20) NOT NULL,
    status NVARCHAR(20) NOT NULL CONSTRAINT DF_sales_status DEFAULT ('FINALIZED'),
    subtotal DECIMAL(12,2) NOT NULL,
    discount_total DECIMAL(12,2) NOT NULL CONSTRAINT DF_sales_discount_total DEFAULT (0),
    tax_total DECIMAL(12,2) NOT NULL CONSTRAINT DF_sales_tax_total DEFAULT (0),
    total DECIMAL(12,2) NOT NULL,
    void_reason NVARCHAR(300) NULL,
    sold_at_utc DATETIME2 NOT NULL CONSTRAINT DF_sales_sold_at DEFAULT (SYSUTCDATETIME()),
    created_at_utc DATETIME2 NOT NULL CONSTRAINT DF_sales_created_at DEFAULT (SYSUTCDATETIME()),
    updated_at_utc DATETIME2 NOT NULL CONSTRAINT DF_sales_updated_at DEFAULT (SYSUTCDATETIME()),
    CONSTRAINT UQ_sales_receipt_number UNIQUE (receipt_number),
    CONSTRAINT UQ_sales_finalize_idempotency_key UNIQUE (finalize_idempotency_key),
    CONSTRAINT FK_sales_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT CK_sales_payment_method CHECK (payment_method IN ('CASH', 'CARD', 'OTHER')),
    CONSTRAINT CK_sales_status CHECK (status IN ('FINALIZED', 'VOIDED')),
    CONSTRAINT CK_sales_money_nonnegative CHECK (subtotal >= 0 AND discount_total >= 0 AND tax_total >= 0 AND total >= 0)
);

CREATE TABLE sale_items (
    sale_item_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    sale_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    product_name_snapshot NVARCHAR(200) NOT NULL,
    unit_type NVARCHAR(10) NOT NULL,
    quantity DECIMAL(10,3) NULL,
    weight_lbs DECIMAL(10,3) NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    line_subtotal DECIMAL(12,2) NOT NULL,
    created_at_utc DATETIME2 NOT NULL CONSTRAINT DF_sale_items_created_at DEFAULT (SYSUTCDATETIME()),
    CONSTRAINT FK_sale_items_sale FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
    CONSTRAINT FK_sale_items_product FOREIGN KEY (product_id) REFERENCES products(product_id),
    CONSTRAINT CK_sale_items_unit_type CHECK (unit_type IN ('EACH', 'WEIGHT')),
    CONSTRAINT CK_sale_items_values_nonnegative CHECK (
        (quantity IS NULL OR quantity >= 0) AND
        (weight_lbs IS NULL OR weight_lbs >= 0) AND
        unit_price >= 0 AND
        line_subtotal >= 0
    ),
    CONSTRAINT CK_sale_items_measure_pair CHECK (
        (unit_type = 'EACH' AND quantity IS NOT NULL AND weight_lbs IS NULL) OR
        (unit_type = 'WEIGHT' AND weight_lbs IS NOT NULL AND quantity IS NULL)
    )
);

CREATE TABLE app_settings (
    setting_key NVARCHAR(100) NOT NULL PRIMARY KEY,
    setting_value NVARCHAR(MAX) NOT NULL,
    updated_at_utc DATETIME2 NOT NULL CONSTRAINT DF_app_settings_updated_at DEFAULT (SYSUTCDATETIME())
);

CREATE INDEX IX_sales_sold_at_utc ON sales(sold_at_utc);
CREATE INDEX IX_sales_customer_id ON sales(customer_id);
CREATE INDEX IX_sale_items_sale_id ON sale_items(sale_id);
CREATE INDEX IX_products_name ON products(name);
CREATE INDEX IX_customers_phone ON customers(phone);
CREATE INDEX IX_customers_email ON customers(email);
