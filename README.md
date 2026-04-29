## test-task (Django + Stripe Checkout)

Это Django-проект с интеграцией Stripe Checkout. Пользователь сначала открывает страницу товара/платежа, затем фронтенд вызывает бэкенд для создания Stripe Checkout session и редиректа на страницу оплаты.

Проект использует SQLite БД: `db.sqlite3` (лежит в корне репозитория).

## Приложения

### `core`
Корневой Django-проект: настройки (`core/settings.py`) и роутинг (`core/urls.py`).

### `api`
Содержит ручки и вьюшки для платежного флоу:
- генерация Stripe Checkout session для заказа;
- рендер страницы оплаты (`payment.html`);
- страницы статуса (`success.html`, `cancel.html`).

### `payments`
Содержит доменные модели, которые использует `api` при создании Stripe line items:
- `Item` (товар),
- `Order` (заказ),
- `OrderItem` (связка заказ-товар),
- `Discount` (скидка) и соответствующее `stripe_coupon_id`,
- `Tax` (налог) и соответствующее `stripe_tax_id`.

Сейчас у `payments` нет собственных HTTP-ручек: роутинг `payments/` пустой.

## Переменные окружения (env)

В `core/settings.py` используются:
- `STRIPE_PUBLIC_KEY` — публичный ключ Stripe (встраивается в страницу оплаты),
- `STRIPE_SECRET_KEY` — секретный ключ Stripe (используется на сервере для создания Checkout session, coupon и tax).

Создайте файл `.env` в корне проекта, например:

```env
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

Если ключи не заданы или Stripe API недоступен, обработчик в `api/views.py` перехватывает исключения и возвращает `"test_id"`, после чего фронтенд редиректит на `/success/`.

## Сборка и запуск через Docker

### 1) Сборка образа

Выполните из корня проекта (там, где лежит `Dockerfile`):

```powershell
docker build -t test-task .
```

### 2) (Рекомендуется) Применить миграции

```powershell
docker run --rm -it --env-file .env `
  -v "${PWD}/db.sqlite3:/app/db.sqlite3" `
  test-task python manage.py migrate
```

Для доступа в Django Admin дополнительно можно создать суперпользователя:

```powershell
docker run --rm -it --env-file .env `
  -v "${PWD}/db.sqlite3:/app/db.sqlite3" `
  test-task python manage.py createsuperuser
```

### 3) Запуск сервера

Сервер слушает порт `8000` внутри контейнера.

Чтобы сохранить `db.sqlite3`, смонтируйте файл из хоста в контейнер:

```powershell
docker run --rm -it `
  -p 8000:8000 `
  --env-file .env `
  -v "${PWD}/db.sqlite3:/app/db.sqlite3" `
  test-task
```

После запуска откройте:
- `http://localhost:8000/admin/`
- `http://localhost:8000/api/item/<item_id>/` (после того как заведёте `Item` в админке)
- `http://localhost:8000/success/` и `http://localhost:8000/cancel/` (страницы статусов)

## HTTP ручки (эндпоинты)

Базовый URL: `http://localhost:8000`

### Django Admin
- `GET/POST /admin/`

### API / платежный флоу
- `GET /api/item/<item_id>/`
  - Рендерит страницу оплаты `payment.html`
  - Встраивает `STRIPE_PUBLIC_KEY`
  - Подставляет `ITEM_ID` для фронтенда (`static/js/payment.js`)

- `GET /api/buy/<order_id>/`
  - Создаёт Stripe Checkout session для заказа `Order`
  - Возвращает JSON: `{"id": "<stripe_session_id>"}`
  - Учитывает опциональные `discount` и `tax` у заказа

Фронтенд вызывает `/api/buy/...` и делает редирект через Stripe JS (`stripe.redirectToCheckout`).

### Статусы платежа
- `GET /success/`
  - Рендерит `success.html`
- `GET /cancel/`
  - Рендерит `cancel.html`

### Важно про согласованность `item_id` и `order_id`

`payment.js` сейчас вызывает:
- `/api/buy/${ITEM_ID}/`

а бэкенд ожидает:
- `GET /api/buy/<order_id>/`

То есть для корректной работы демо нужно, чтобы `order_id` совпадал с тем `item_id`, который подставляется на страницу товара (или нужно поправить связку в коде).

## Страницы и шаблоны

Шаблоны находятся в `templates/`:
- `payment.html` — страница товара/кнопка Buy + подключение `static/js/payment.js`
- `success.html` — страница успешной оплаты
- `cancel.html` — страница отмены/ошибки

JS находится в `static/js/payment.js`:
- запрашивает `/api/buy/<...>/`
- делает редирект на Stripe Checkout