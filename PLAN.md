# План разработки медицинского сайта

## 1. Схема БД (SQLite)

SQLite-файл: `backend/medsite.db`. Доступ только через SQLAlchemy 2.0 ORM. Время хранится в ISO 8601, серверная временная зона фиксируется в конфигурации. База содержит персональные данные; телефон запрещено выводить в логах без маскирования.

### `services`

| Колонка | Тип | Ограничения |
|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT |
| `name` | VARCHAR(120) | NOT NULL, UNIQUE |
| `description` | TEXT | NOT NULL, DEFAULT `''` |
| `price` | INTEGER | NOT NULL, CHECK `price >= 0`, цена в рублях |
| `duration_minutes` | INTEGER | NOT NULL, CHECK `duration_minutes > 0` |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT `1` |
| `created_at` | DATETIME | NOT NULL, DEFAULT current timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT current timestamp, обновляется приложением |

Связи: M:N с `doctors` через `doctor_services`, 1:N с `appointments`.

### `doctors`

| Колонка | Тип | Ограничения |
|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT |
| `full_name` | VARCHAR(160) | NOT NULL |
| `specialty` | VARCHAR(120) | NOT NULL |
| `bio` | TEXT | NOT NULL, DEFAULT `''` |
| `photo_url` | VARCHAR(500) | NULL |
| `experience_years` | INTEGER | NOT NULL, DEFAULT `0`, CHECK `experience_years >= 0` |
| `work_start` | TIME | NOT NULL, DEFAULT `09:00` |
| `work_end` | TIME | NOT NULL, DEFAULT `18:00`, CHECK на уровне приложения `work_end > work_start` |
| `slot_minutes` | INTEGER | NOT NULL, DEFAULT `30`, CHECK `slot_minutes > 0` |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT `1` |
| `created_at` | DATETIME | NOT NULL, DEFAULT current timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT current timestamp, обновляется приложением |

Связи: M:N с `services` через `doctor_services`, 1:N с `appointments`.

### `doctor_services`

| Колонка | Тип | Ограничения |
|---|---|---|
| `doctor_id` | INTEGER | PK, FK → `doctors.id`, ON DELETE CASCADE |
| `service_id` | INTEGER | PK, FK → `services.id`, ON DELETE CASCADE |

Таблица задаёт допустимые пары врач–услуга. Запись на услугу, не назначенную врачу, отклоняется.

### `faq`

| Колонка | Тип | Ограничения |
|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT |
| `question` | VARCHAR(500) | NOT NULL |
| `answer` | TEXT | NOT NULL |
| `sort_order` | INTEGER | NOT NULL, DEFAULT `0` |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT `1` |
| `created_at` | DATETIME | NOT NULL, DEFAULT current timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT current timestamp, обновляется приложением |

### `appointments`

| Колонка | Тип | Ограничения |
|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT |
| `doctor_id` | INTEGER | NOT NULL, FK → `doctors.id`, ON DELETE RESTRICT |
| `service_id` | INTEGER | NOT NULL, FK → `services.id`, ON DELETE RESTRICT |
| `slot_start` | DATETIME | NOT NULL, индекс |
| `client_name` | VARCHAR(120) | NOT NULL |
| `client_phone` | VARCHAR(32) | NOT NULL |
| `status` | VARCHAR(16) | NOT NULL, DEFAULT `new`, CHECK IN (`new`, `confirmed`, `cancelled`) |
| `utm_source` | VARCHAR(255) | NULL |
| `utm_medium` | VARCHAR(255) | NULL |
| `utm_campaign` | VARCHAR(255) | NULL |
| `utm_content` | VARCHAR(255) | NULL |
| `utm_term` | VARCHAR(255) | NULL |
| `source` | VARCHAR(255) | NULL |
| `client_id` | VARCHAR(255) | NULL |
| `lead_id` | VARCHAR(36) | NOT NULL, UNIQUE, UUID v4 генерируется сервером |
| `created_at` | DATETIME | NOT NULL, DEFAULT current timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT current timestamp, обновляется приложением |

Связи: N:1 с `doctors` и `services`, 1:1 с `leads` по `lead_id`. Частичный UNIQUE INDEX на (`doctor_id`, `slot_start`) при `status IN ('new', 'confirmed')` исключает двойную запись и освобождает отменённый слот. Внешние ключи SQLite включаются через `PRAGMA foreign_keys=ON`.

### `admin_users`

| Колонка | Тип | Ограничения |
|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT |
| `username` | VARCHAR(80) | NOT NULL, UNIQUE |
| `password_hash` | VARCHAR(255) | NOT NULL, bcrypt |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT `1` |
| `created_at` | DATETIME | NOT NULL, DEFAULT current timestamp |

Первый администратор создаётся при старте из переменных окружения `ADMIN_USERNAME` и `ADMIN_PASSWORD`, если таблица пуста. Пароль в открытом виде не хранится.

### `leads` (UTM/аналитика)

| Колонка | Тип | Ограничения |
|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT |
| `lead_id` | VARCHAR(36) | NOT NULL, UNIQUE, UUID v4 |
| `appointment_id` | INTEGER | NOT NULL, UNIQUE, FK → `appointments.id`, ON DELETE CASCADE |
| `client_id` | VARCHAR(255) | NULL, индекс |
| `source` | VARCHAR(255) | NULL |
| `utm_source` | VARCHAR(255) | NULL |
| `utm_medium` | VARCHAR(255) | NULL |
| `utm_campaign` | VARCHAR(255) | NULL |
| `utm_content` | VARCHAR(255) | NULL |
| `utm_term` | VARCHAR(255) | NULL |
| `created_at` | DATETIME | NOT NULL, DEFAULT current timestamp |

Создаётся в одной транзакции с `appointments`. Дублирование UTM в записи фиксирует снимок заявки, `leads` служит отдельным аналитическим контуром.

### `seo_settings`

| Колонка | Тип | Ограничения |
|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT |
| `page` | VARCHAR(64) | NOT NULL, UNIQUE |
| `title` | VARCHAR(255) | NOT NULL |
| `description` | VARCHAR(500) | NOT NULL |
| `updated_at` | DATETIME | NOT NULL, DEFAULT current timestamp, обновляется приложением |

Допустимые `page`: `index`, `services`, `doctors`, `faq`, `admin`. Таблица необходима для заявленных SEO-настроек.

## 2. API-контракт (финальный, неизменяемый)

Base URL: `/api`. Content type: `application/json`. Protected endpoints require `Authorization: Bearer <token>`. Dates use `YYYY-MM-DD`, time slots use timezone-naive local ISO 8601 `YYYY-MM-DDTHH:MM:SS`. Unknown request fields are rejected. Empty optional values are returned as `null`.

Every error has exactly this shape:

```json
{"error":{"code":"ERROR_CODE","message":"Human-readable message"}}
```

Common errors: `400 BAD_REQUEST`, `401 UNAUTHORIZED`, `404 NOT_FOUND`, `409 CONFLICT`, `422 VALIDATION_ERROR`, `500 INTERNAL_ERROR`. FastAPI validation errors must be converted to the common error shape.

### Shared response objects

`Service`:

```json
{"id":1,"name":"Consultation","description":"Initial visit","price":2500,"duration_minutes":30,"is_active":true,"created_at":"2026-09-10T10:00:00","updated_at":"2026-09-10T10:00:00"}
```

`Doctor`:

```json
{"id":1,"full_name":"Ivan Petrov","specialty":"Cardiologist","bio":"...","photo_url":null,"experience_years":12,"work_start":"09:00:00","work_end":"18:00:00","slot_minutes":30,"is_active":true,"service_ids":[1],"created_at":"2026-09-10T10:00:00","updated_at":"2026-09-10T10:00:00"}
```

`Faq`:

```json
{"id":1,"question":"How to prepare?","answer":"Bring previous reports.","sort_order":10,"is_active":true,"created_at":"2026-09-10T10:00:00","updated_at":"2026-09-10T10:00:00"}
```

`Appointment`:

```json
{"id":1,"doctor_id":1,"service_id":1,"slot_start":"2026-09-15T10:30:00","client_name":"Anna","client_phone":"+79990000000","status":"new","utm_source":"google","utm_medium":"cpc","utm_campaign":null,"utm_content":null,"utm_term":null,"source":"website","client_id":"cid-123","lead_id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-10T10:00:00","updated_at":"2026-09-10T10:00:00"}
```

### Health

- `GET /api/health`
- Auth: public.
- `200`: `{"status":"ok"}`.

### Services CRUD

- `GET /api/services`
- Auth: public. Query: `include_inactive` boolean, default `false`; `true` requires admin token.
- `200`: `{"items":[Service]}` ordered by `name`, `id`.
- Errors: `401` when requesting inactive records without a valid token.

- `GET /api/services/{id}`
- Auth: public for active records; admin token permits inactive records.
- `200`: `Service`.
- Errors: `404` if absent or inactive for a public request.

- `POST /api/services`
- Auth: admin.
- Body: `{"name":"Consultation","description":"Initial visit","price":2500,"duration_minutes":30,"is_active":true}`. Required: `name`, `price`, `duration_minutes`; remaining fields use DB defaults.
- `201`: `Service`.
- Errors: `401`, `409` duplicate name, `422` invalid fields.

- `PUT /api/services/{id}`
- Auth: admin.
- Body: same fields and required set as POST; full replacement.
- `200`: `Service`.
- Errors: `401`, `404`, `409` duplicate name, `422`.

- `DELETE /api/services/{id}`
- Auth: admin.
- `204`: empty body.
- Errors: `401`, `404`, `409` if referenced by an appointment.

### Doctors CRUD

- `GET /api/doctors`
- Auth: public. Query: `service_id` optional integer; `include_inactive` boolean, default `false`, and `true` requires admin token.
- `200`: `{"items":[Doctor]}` ordered by `full_name`, `id`.
- Errors: `401`, `422` invalid query.

- `GET /api/doctors/{id}`
- Auth: public for active records; admin token permits inactive records.
- `200`: `Doctor`.
- Errors: `404` if absent or inactive for a public request.

- `POST /api/doctors`
- Auth: admin.
- Body: `{"full_name":"Ivan Petrov","specialty":"Cardiologist","bio":"...","photo_url":null,"experience_years":12,"work_start":"09:00:00","work_end":"18:00:00","slot_minutes":30,"is_active":true,"service_ids":[1]}`. Required: `full_name`, `specialty`, `service_ids`; remaining fields use DB defaults.
- `201`: `Doctor`.
- Errors: `401`, `404` for unknown service ID, `422` invalid schedule/fields.

- `PUT /api/doctors/{id}`
- Auth: admin.
- Body: same fields and required set as POST; full replacement.
- `200`: `Doctor`.
- Errors: `401`, `404` doctor or service not found, `422`.

- `DELETE /api/doctors/{id}`
- Auth: admin.
- `204`: empty body.
- Errors: `401`, `404`, `409` if referenced by an appointment.

### FAQ CRUD

- `GET /api/faq`
- Auth: public. Query: `include_inactive` boolean, default `false`; `true` requires admin token.
- `200`: `{"items":[Faq]}` ordered by `sort_order`, `id`.
- Errors: `401`, `422` invalid query.

- `GET /api/faq/{id}`
- Auth: public for active records; admin token permits inactive records.
- `200`: `Faq`.
- Errors: `404` if absent or inactive for a public request.

- `POST /api/faq`
- Auth: admin.
- Body: `{"question":"How to prepare?","answer":"Bring previous reports.","sort_order":10,"is_active":true}`. Required: `question`, `answer`; remaining fields use DB defaults.
- `201`: `Faq`.
- Errors: `401`, `422`.

- `PUT /api/faq/{id}`
- Auth: admin.
- Body: same fields and required set as POST; full replacement.
- `200`: `Faq`.
- Errors: `401`, `404`, `422`.

- `DELETE /api/faq/{id}`
- Auth: admin.
- `204`: empty body.
- Errors: `401`, `404`.

### Doctor slots

- `GET /api/doctors/{id}/slots?date=2026-09-15`
- Auth: public.
- `200`: `{"doctor_id":1,"date":"2026-09-15","slots":["2026-09-15T09:00:00","2026-09-15T09:30:00"]}`.
- Rules: generate slots from `work_start` inclusive to `work_end` exclusive in `slot_minutes` steps; omit past slots and slots occupied by `new` or `confirmed` appointments. A slot is valid only if it and the selected service duration fit before `work_end`; because no service is supplied here, the doctor's `slot_minutes` defines the returned interval and appointment creation performs the final duration check.
- Errors: `404` doctor absent/inactive, `422` missing/invalid date.

### Public appointment creation

- `POST /api/appointments`
- Auth: public.
- Body:

```json
{"doctor_id":1,"service_id":1,"slot_start":"2026-09-15T10:30:00","client_name":"Anna","client_phone":"+79990000000","utm_source":"google","utm_medium":"cpc","utm_campaign":null,"utm_content":null,"utm_term":null,"source":"website","client_id":"cid-123"}
```

- Required: `doctor_id`, `service_id`, `slot_start`, `client_name`, `client_phone`. UTM fields, `source`, and `client_id` are optional. `status` and `lead_id` cannot be supplied by clients.
- `201`: `Appointment`; status is `new`, `lead_id` is a server-generated UUID v4.
- Rules: doctor and service must be active and linked; slot must be future, align with the doctor's slot grid, fit the selected service duration into working hours, and not overlap any `new`/`confirmed` appointment for that doctor. Appointment and lead are inserted atomically. Normalize the phone for validation/storage and mask it in all logs.
- Errors: `404` doctor/service absent or inactive, `409 SLOT_UNAVAILABLE` overlap or concurrent booking, `422` invalid fields, doctor-service mismatch, or invalid slot.

### Admin appointments

- `GET /api/admin/appointments?status=new`
- Auth: admin. Optional query `status`: `new`, `confirmed`, or `cancelled`; omitted means all.
- `200`: `{"items":[Appointment]}` ordered by `slot_start` ascending, then `id`.
- Errors: `401`, `422` invalid status.

- `PATCH /api/admin/appointments/{id}`
- Auth: admin.
- Body: `{"status":"confirmed"}`; no other fields accepted.
- `200`: `Appointment`.
- Errors: `401`, `404`, `409` if restoring a cancelled appointment would conflict with an occupied slot, `422` invalid status/body.

### Admin authentication

- `POST /api/admin/login`
- Auth: public.
- Body: `{"username":"admin","password":"secret"}`.
- `200`: `{"token":"opaque-random-token","token_type":"bearer","expires_in":28800}`.
- Token validity: 8 hours. Store only a SHA-256 token digest server-side or use an HMAC-signed token containing admin ID and expiry; never log token or password.
- Errors: `401 INVALID_CREDENTIALS` for any invalid username/password/inactive-user case, `422` malformed body.

### SEO settings

- `GET /api/admin/seo/{page}`
- Auth: admin.
- `200`: `{"page":"index","title":"Clinic","description":"Medical clinic"}`.
- Errors: `401`, `404` setting absent, `422` unsupported page.

- `PUT /api/admin/seo/{page}`
- Auth: admin.
- Body: `{"title":"Clinic","description":"Medical clinic"}`; full upsert for the specified page.
- `200`: `{"page":"index","title":"Clinic","description":"Medical clinic"}`.
- Errors: `401`, `422` unsupported page or invalid fields.

Этот контракт является единственным источником правды для backend- и frontend-команд. Изменения путей, полей, статусов, форматов ответов и ошибок допускаются только через согласованное изменение `PLAN.md` до начала параллельной реализации.

## 3. Структура файлов

```text
.
├── BRIEF.md
├── PLAN.md
├── README.md
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── auth.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── health.py
│   │       ├── services.py
│   │       ├── doctors.py
│   │       ├── faq.py
│   │       ├── appointments.py
│   │       └── admin.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_health.py
│   │   ├── test_crud.py
│   │   ├── test_auth.py
│   │   └── test_appointments.py
│   ├── requirements.txt
│   └── medsite.db
└── frontend/
    ├── index.html
    ├── services.html
    ├── doctors.html
    ├── faq.html
    ├── admin.html
    ├── css/
    │   └── style.css
    └── js/
        ├── config.js
        ├── api.js
        ├── app.js
        ├── appointment.js
        └── admin.js
```

`backend/medsite.db` создаётся при запуске и не коммитится. `frontend/js/config.js` содержит единственную константу API URL и подключается до `api.js`. Корневой `README.md` описывает установку, переменные окружения, запуск backend/frontend, тесты и структуру проекта.

## 4. Декомпозиция на две параллельные задачи

### TASK_BACKEND

Область владения строго `backend/`; контракт не менять.

1. Создать зависимости для Python 3.12: FastAPI, Uvicorn, SQLAlchemy 2.0, Pydantic, bcrypt/passlib-совместимую библиотеку, pytest и HTTP test client; версии зафиксировать в `requirements.txt`.
2. Настроить SQLite engine/session, `PRAGMA foreign_keys=ON`, тестовую подмену БД и `create_all` при старте. Описать ORM-модели, связи, каскады, CHECK/UNIQUE/partial indexes.
3. Описать строгие Pydantic-схемы контракта: ограничения строк, неотрицательная цена/стаж, телефон, UUID, дата/время, enum статусов, запрет лишних полей.
4. Реализовать bcrypt-хеширование, инициализацию первого администратора, 8-часовой bearer token и общую dependency проверки токена. Не логировать пароль/токен.
5. Реализовать роутеры health, services, doctors, FAQ, slots, appointments, admin appointments, login и SEO; преобразовывать все ошибки, включая validation и integrity errors, в единый формат.
6. Для записи использовать одну транзакцию, повторную проверку доступности и DB unique constraint. Проверять сетку врача, длительность услуги, M:N-связь и пересечения интервалов. Отменённые записи не блокируют слот.
7. Настроить CORS на явный список origins из `CORS_ORIGINS`, включая локальный frontend; разрешить нужные методы и `Authorization`, не использовать wildcard вместе с credentials.
8. Настроить логирование с фильтром маскирования телефонов; отметить в README, что `medsite.db` содержит ПД и должна быть исключена из VCS/публичных артефактов.
9. Написать минимум 8 pytest-сценариев: health; полный CRUD услуг; CRUD врачей и связь с услугой; CRUD FAQ; успешный/неуспешный login; создание записи и lead/UTM; расчёт и исключение занятых слотов; смена статуса; `401` на защищённом endpoint без токена; конфликт параллельной/повторной записи. Использовать отдельную временную SQLite БД.

Результат: backend запускается командой `uvicorn app.main:app --reload` из `backend/`, все endpoints соответствуют разделу 2, `pytest` проходит.

### TASK_FRONTEND

Область владения строго `frontend/`; контракт не менять, backend-файлы и корень не редактировать.

1. Создать пять страниц: `index.html` (главная, контакты, форма записи), `services.html`, `doctors.html`, `faq.html`, `admin.html`. Использовать общую навигацию, семантическую разметку и доступные labels/focus states.
2. Сделать адаптивную медицинскую визуальную систему без фреймворков: бело-голубая палитра, читаемая типографика, карточки услуг/врачей, состояния загрузки/ошибки/пустого списка, мобильная компоновка.
3. В `js/config.js` хранить API base URL. В `js/api.js` централизовать все вызовы контракта: health, CRUD services/doctors/FAQ, slots, create appointment, login, list/update appointments, get/put SEO; единообразно разбирать ошибки.
4. В `js/app.js` загрузить публичные данные API и отрисовать услуги, врачей, FAQ и общие элементы без вставки непроверенного HTML.
5. В `js/appointment.js` реализовать форму: услуги и врачи только из API, фильтрация врачей по услуге, запрос слотов после выбора врача/даты, валидация имени/телефона, блокировка повторной отправки, экран успеха с `lead_id`.
6. При загрузке разобрать `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term` и source из URL. Прочитать `clientID` из cookie, а при отсутствии сгенерировать UUID и записать cookie с `SameSite=Lax`; передать аналитику только в POST appointment.
7. В `js/admin.js` реализовать login, хранение token в `sessionStorage`, bearer-заголовок, logout/очистку при `401`, CRUD услуг/врачей/FAQ, список заявок с фильтром и сменой статуса, чтение/изменение SEO.
8. Проверить страницы через статический сервер на desktop/mobile: навигацию, пустые данные, ошибки API/CORS, формы, клавиатурный доступ и полный сценарий «создать запись → увидеть в админке → сменить статус».

Результат: frontend работает как статические HTML/CSS/JS без сборщика, URL API меняется в одном файле, ни один вызов не отклоняется от раздела 2.

## 5. Порядок сборки и риски

1. Зафиксировать `PLAN.md`; после старта параллельных задач контракт не менять.
2. Backend сначала поднимает database/models/schemas и health, затем auth и CRUD, после этого слоты/appointments и SEO, в конце CORS, обработчики ошибок и тесты.
3. Frontend параллельно создаёт каркас страниц, CSS и API client по контракту, затем публичные списки/форму, после этого admin и SEO.
4. Интеграцию начать после зелёных backend-тестов: запустить backend и статический frontend на разных origins, создать услугу и врача через admin/API, записаться через публичную форму, проверить заявку и сменить статус.
5. В конце выполнить чистую установку зависимостей, `pytest`, smoke-проверку `/api/health`, адаптивности и README-инструкций.

Ключевые риски и меры:

- **Пересечения записей:** два одновременных запроса могут увидеть один слот свободным. Защита: транзакционная проверка, проверка интервалов и частичный unique index; `IntegrityError` преобразуется в `409 SLOT_UNAVAILABLE`.
- **Длительность услуги:** услуга может занимать несколько базовых слотов. Создание заявки проверяет весь интервал `[slot_start, slot_start + duration)` и границу рабочего дня, а slots возвращает базовую сетку.
- **Отмена и повторное подтверждение:** отмена освобождает время; возврат в `new`/`confirmed` повторно проверяет конфликт и при необходимости отвечает `409`.
- **CORS:** статический frontend работает с другого origin. Origins задаются явно, проверяются preflight-запросы и заголовок `Authorization`.
- **Авторизация:** кража токена даёт доступ к ПД. Короткий TTL 8 часов, `sessionStorage`, отсутствие токенов в URL/логах, единый `401`, bcrypt для пароля.
- **Персональные данные:** телефон и заявки не должны попасть в логи, git или публичный demo dump. Используются маскирование, `.gitignore`, минимальные ответы и предупреждение в README.
- **Расхождение команд:** backend/frontend не придумывают поля и пути. Любое несоответствие сверяется только с разделом 2.
- **SQLite и миграции:** `create_all` подходит для прототипа, но не обновляет существующую схему. До релиза схема фиксируется; при изменении тестовая/локальная БД пересоздаётся, для развития проекта потребуется Alembic.

Критерии приёмки:

- `pip install -r backend/requirements.txt` успешно выполняется на Python 3.12.
- Из `backend/` запускается `uvicorn app.main:app --reload`; `GET /api/health` возвращает `200` и `{"status":"ok"}`.
- CRUD услуг, врачей и FAQ работает; запись требует токен, публичное чтение доступно без него.
- Через API/admin создаются связанные услуга и врач; публичная форма получает их и доступные слоты.
- Форма создаёт appointment и lead с UTM/clientID/серверным UUID; заявка видна в admin, её статус меняется.
- Двойное бронирование исключено, отменённый слот освобождается, ошибки имеют единый формат.
- SEO title/description читаются и изменяются в admin.
- Телефоны маскируются в логах, пароль хешируется, CORS разрешает настроенный frontend.
- Все backend-тесты, включая минимум требуемых сценариев, проходят; пять страниц корректно работают на desktop и mobile.
- Корневой `README.md` содержит точные команды установки, запуска frontend/backend и тестов, описание структуры и предупреждение о ПД.
