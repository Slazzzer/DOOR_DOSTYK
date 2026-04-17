# Дверной Достык

Мини-прототип системы автоматизации склад-магазина дверных конструкций.

## Описание

Система решает две ключевые задачи:

- **Оформление заказа клиента** — менеджер выбирает товары из каталога, указывает количество, и система автоматически резервирует остатки на складе, рассчитывает итоговую сумму, отправляет данные в 1С:Бухгалтерия (mock) и уведомляет клиента по email (mock).
- **Приёмка товара** — кладовщик фиксирует поступление товара от поставщика, и система автоматически увеличивает остатки на складе.

## Стек технологий

| Слой | Технология |
|---|---|
| Frontend | Vue.js 3 + Vue Router + Axios |
| Backend | Python + FastAPI |
| База данных | PostgreSQL 16 |
| ORM | SQLAlchemy |
| Валидация | Pydantic v2 |
| Сборщик фронта | Vite |

## Структура проекта

В корне репозитория также лежит **`docker-compose.yml`** (PostgreSQL, бэкенд, фронт с nginx).

```
Door_dostyk/
├── docker/
│   └── init-db/                      # SQL для первого запуска контейнера БД
├── backend/
│   ├── Dockerfile
│   ├── .env                          # Строка подключения к БД (не коммитится)
│   ├── requirements.txt              # Python-зависимости
│   └── app/
│       ├── main.py                   # Точка входа FastAPI
│       ├── database.py               # Подключение к PostgreSQL
│       ├── api/
│       │   ├── products.py           # GET /api/products, GET /api/products/{id}
│       │   ├── orders.py             # POST /api/orders
│       │   └── shipments.py          # POST /api/shipments
│       ├── models/
│       │   ├── product.py            # Модель товара
│       │   ├── order.py              # Модели заказа и позиции заказа
│       │   └── shipment.py           # Модели приёмки и позиции приёмки
│       ├── schemas/
│       │   ├── order.py              # Pydantic-схемы заказа
│       │   └── shipment.py           # Pydantic-схемы приёмки
│       ├── services/
│       │   ├── order_service.py      # Бизнес-логика оформления заказа
│       │   └── shipment_service.py   # Бизнес-логика приёмки товара
│       └── mocks/
│           ├── accounting_mock.py    # Заглушка 1С:Бухгалтерия
│           └── email_mock.py         # Заглушка Email-сервиса
└── frontend/
    ├── Dockerfile
    ├── nginx-docker.conf             # Прокси /api → бэкенд внутри Compose
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.vue                   # Главный компонент с навигацией
        ├── main.js                   # Точка входа Vue + роутер
        ├── api/
        │   └── index.js              # HTTP-клиент (Axios)
        ├── views/
        │   ├── OrdersView.vue        # Страница оформления заказа
        │   └── ShipmentsView.vue     # Страница приёмки товара
        └── components/
            ├── OrderForm.vue         # Форма оформления заказа
            └── ShipmentForm.vue      # Форма приёмки товара
```

## База данных

5 таблиц с префиксным именованием полей:

| Таблица | Префикс | Описание |
|---|---|---|
| `products` | `prod_` | Товары (двери, фурнитура, комплектующие) |
| `orders` | `ord_` | Заказы клиентов (шапка) |
| `order_items` | `oi_` | Позиции заказа |
| `shipments` | `shp_` | Приёмки товара (шапка) |
| `shipment_items` | `si_` | Позиции приёмки |

## API-эндпоинты

| Метод | URL | Описание |
|---|---|---|
| `GET` | `/api/products/` | Список всех товаров |
| `GET` | `/api/products/{id}` | Товар по ID |
| `POST` | `/api/orders/` | Оформить заказ клиента |
| `POST` | `/api/shipments/` | Оформить приёмку товара |

## Mock-сервисы (заглушки)

| Внешняя система | Файл | Что делает |
|---|---|---|
| 1С:Бухгалтерия | `mocks/accounting_mock.py` | Имитирует отправку заказа — пишет лог в консоль uvicorn |
| Email-сервис | `mocks/email_mock.py` | Имитирует отправку письма — пишет лог в консоль uvicorn |

## Установка и запуск

### Предварительные требования

- Python 3.12+
- Node.js LTS (npm в комплекте)
- PostgreSQL 16
- Git

### 1. Клонировать репозиторий

```bash
git clone https://github.com/Slazzzer/DOOR_DOSTYK.git
cd DOOR_DOSTYK
```

### 2. Создать базу данных

Открыть pgAdmin 4, создать базу `dostyk`, затем в Query Tool выполнить SQL-скрипт создания 5 таблиц (products, orders, order_items, shipments, shipment_items), индексов и тестовых данных.

### 3. Настроить переменные окружения

Создать файл `Door_dostyk/backend/.env`:

```
DATABASE_URL=postgresql://postgres:ваш_пароль@localhost:5432/dostyk
```

### 4. Запустить бэкенд

```bash
cd Door_dostyk/backend
uvicorn app.main:app --reload
```

Бэкенд запустится на `http://localhost:8000`.
Swagger-документация доступна на `http://localhost:8000/docs`.

### 5. Запустить фронтенд

В отдельном терминале:

```bash
cd Door_dostyk/frontend
npm install
npm run dev
```

Фронтенд запустится на `http://localhost:5173`.

### 6. Запуск через Docker Compose

Нужны [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/macOS) или Docker Engine с плагином Compose.

Из **корня репозитория**, где лежит `docker-compose.yml`:

```bash
docker compose up --build
```

| Сервис | URL / доступ |
|--------|----------------|
| Веб-приложение (Vue через nginx) | [http://localhost:8080](http://localhost:8080) — запросы к `/api` проксируются в бэкенд |
| FastAPI / Swagger | [http://localhost:8000/docs](http://localhost:8000/docs) |
| PostgreSQL | хост `localhost`, порт `5432`, БД `dostyk`, пользователь `postgres`, пароль `postgres` |

При **первом** запуске контейнера БД выполняется `Door_dostyk/docker/init-db/01-schema.sql` (таблицы и несколько товаров). Чтобы полностью сбросить данные и пересоздать БД: `docker compose down -v`, затем снова `docker compose up --build`.

Остановка: `Ctrl+C` в терминале или `docker compose down`.

## Как пользоваться

1. Открыть приложение: при локальном запуске — `http://localhost:5173`, при Docker — `http://localhost:8080`
2. **Оформление заказа** — выбрать товары из выпадающего списка, указать количество, ввести ФИО и телефон клиента, нажать "Оформить заказ". Остатки на складе уменьшатся автоматически. В консоли бэкенда появятся логи моков (1С + Email).
3. **Приёмка товара** — указать поставщика, выбрать товары и количество, нажать "Принять товар". Остатки на складе увеличатся автоматически. В консоли бэкенда появится лог мока Email.
