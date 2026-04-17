/* Схема БД и начальные данные для первого запуска контейнера PostgreSQL */

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
    ('Входная дверь металлическая Порта C48 Антик медь', 'IN_PORTA_C48_AM', 42800.00, 4),
    ('Входная дверь Порта М К15 Муар белый', 'IN_PORTA_M_K15_W', 31200.00, 6),
    ('Входная дверь Торекс Дельта 100 медный антик', 'IN_TOREX_D100_MA', 38900.00, 3),
    ('Межкомнатное полотно экошпон Марсель дуб 700x2000', 'RM_MARSEILLE_DUB_70', 11800.00, 12),
    ('Межкомнатное полотно со стеклом Верона ясень 800x2000', 'RM_VERONA_ASH_GL80', 14500.00, 10),
    ('Межкомнатное полотно глухое Классика белая эмаль 600', 'RM_CLASSIC_WHITE_60', 8900.00, 18),
    ('Двустворчатая межкомнатная система Папа Карло орех', 'RM_PAPACARLO_WAL_DBL', 26400.00, 2),
    ('Коробка дверная МДФ телескопическая комплект', 'ACC_BOX_MDF_TEL', 4200.00, 35),
    ('Наличник МДФ 70 мм комплект на одну сторону', 'ACC_TRIM_MDF_70', 1850.00, 60),
    ('Добор МДФ 100 мм', 'ACC_EXT_MDF_100', 980.00, 45),
    ('Петля карточная универсальная 100x75 мм 2 шт', 'ACC_HINGE_CARD_100', 640.00, 120),
    ('Петля скрытая Simonswerk 3D 120 кг', 'ACC_HINGE_HID_SIM', 4200.00, 28),
    ('Ручка на розетке Bravo Z3 хром матовый', 'ACC_HANDLE_BR_Z3', 2150.00, 55),
    ('Ручка-скоба Archie S010 черный матовый', 'ACC_PULL_ARCH_S010', 1780.00, 48),
    ('Замок врезной Apecs 7000 с цилиндром', 'ACC_LOCK_APECS_7000', 3100.00, 40),
    ('Замок накладной для входной двери Border ЗН4', 'ACC_LOCK_OVR_BR_ZN4', 2650.00, 22),
    ('Цилиндровый механизм 70 мм перфорированный ключ', 'ACC_CYL_70_PERF', 890.00, 75),
    ('Доводчик дверной Dorma TS 92 EN2-4 серебро', 'ACC_CLOSER_TS92', 5600.00, 15),
    ('Уплотнитель коричневый самоклеящийся 6 м', 'ACC_SEAL_BR_6M', 420.00, 100),
    ('Глазок дверной угол обзора 180 градусов хром', 'ACC_PEEP_180_CR', 1150.00, 66),
    ('Порог алюминиевый 900 мм с уплотнителем', 'ACC_THRESH_AL_900', 1350.00, 38),
    ('Вентиляционная решетка в дверь 440x100 белая', 'ACC_VENT_440100_W', 780.00, 52),
    ('Комплект фурнитуры для межкомнатной двери базовый', 'ACC_KIT_RM_BASIC', 2900.00, 30),
    ('Ручка на планке 300 мм нержавеющая сталь', 'ACC_HANDLE_PL_300_SS', 2490.00, 25);
