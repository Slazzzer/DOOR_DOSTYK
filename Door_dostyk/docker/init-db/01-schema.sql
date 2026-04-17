-- Схема и тестовые данные для первого запуска контейнера PostgreSQL

CREATE TABLE products (
    prod_id SERIAL PRIMARY KEY,
    prod_name VARCHAR(200) NOT NULL,
    prod_sku VARCHAR(50) NOT NULL UNIQUE,
    prod_price NUMERIC(10, 2) NOT NULL DEFAULT 0,
    prod_quantity INTEGER NOT NULL DEFAULT 0,
    prod_created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE orders (
    ord_id SERIAL PRIMARY KEY,
    ord_client_name VARCHAR(150) NOT NULL,
    ord_client_phone VARCHAR(20),
    ord_status VARCHAR(30) NOT NULL DEFAULT 'new',
    ord_total_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    ord_created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE order_items (
    oi_id SERIAL PRIMARY KEY,
    oi_order_id INTEGER NOT NULL REFERENCES orders (ord_id) ON DELETE CASCADE,
    oi_product_id INTEGER NOT NULL REFERENCES products (prod_id),
    oi_quantity INTEGER NOT NULL,
    oi_price NUMERIC(10, 2) NOT NULL
);

CREATE TABLE shipments (
    shp_id SERIAL PRIMARY KEY,
    shp_supplier_name VARCHAR(150) NOT NULL,
    shp_status VARCHAR(30) NOT NULL DEFAULT 'received',
    shp_created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE shipment_items (
    si_id SERIAL PRIMARY KEY,
    si_shipment_id INTEGER NOT NULL REFERENCES shipments (shp_id) ON DELETE CASCADE,
    si_product_id INTEGER NOT NULL REFERENCES products (prod_id),
    si_quantity INTEGER NOT NULL
);

INSERT INTO products (prod_name, prod_sku, prod_price, prod_quantity)
VALUES
    ('Входная дверь Стандарт', 'DOOR-IN-01', 18500.00, 10),
    ('Межкомнатная дверь Альфа', 'DOOR-RM-02', 9200.00, 15),
    ('Фурнитура набор', 'ACC-KIT-01', 3500.00, 40);
