Вот подробное техническое задание для разработки frontend части проекта на Next.js 14 (TypeScript, Tailwind CSS, Zustand/React Query, shadcn/ui):

---

# Техническое задание: Frontend для Telegram AI Monitoring

## 1. Технологии и стек

- **Фреймворк:** Next.js 14 (App Router)
- **Язык:** TypeScript
- **UI:** Tailwind CSS, shadcn/ui (или кастомные компоненты)
- **Состояние:** Zustand или React Query
- **Аутентификация:** Telegram Login Widget + JWT (хранение токена в localStorage или Secure Cookies)
- **API:** Взаимодействие с backend через REST (Swagger: `/docs`)

---

## 2. Основные страницы и функционал

### 2.1. Авторизация
- `/login` — Telegram Login Widget.
- После успешного входа — получение и хранение JWT.
- Реализация AuthContext для доступа к данным пользователя и токену.

### 2.2. Дашборд
- `/dashboard` — графики и показатели по всем проектам.
- Использовать useStatsQuery для получения статистики (сообщения, лайки, статус).
- Визуализация: графики, таблицы (например, с помощью recharts или аналогов).

### 2.3. Проекты и подпроекты
- `/projects` — список проектов пользователя.
- `/projects/[id]/subprojects` — подпроекты внутри выбранного проекта.
- CRUD-операции: создание, редактирование, удаление.

### 2.4. Промпты
- `/subprojects/[id]/prompts` — редактор шаблонов промптов.
- Форма с предпросмотром результата (Jinja2-подобный синтаксис).
- Сохранение и версионирование промптов.

### 2.5. Каналы
- `/subprojects/[id]/channels` — список подключённых Telegram-каналов.
- Настройка фильтров (по ключевым словам, автоответам и т.д.).

### 2.6. Модерация
- `/moderation` — интерфейс модератора.
- Таблица: сообщение, AI-ответ, действия (отправить, отклонить, редактировать, лайк).
- Кнопки действий с вызовом соответствующих API.

### 2.7. Настройки
- `/settings/integrations` — добавление и управление интеграциями (MTProto, Bot API).
- `/settings/profile` — профиль пользователя (имя, email, язык, предпочтения).

---

## 3. Архитектура компонентов

- **AuthContext** — хранение и проверка JWT, данные пользователя.
- **use*Query** хуки — для загрузки данных (статистика, проекты, сообщения и т.д.).
- **UI-компоненты:** кнопки, формы, таблицы, модальные окна (shadcn/ui или кастом).
- **ErrorBoundary** — обработка ошибок API.
- **Лоадеры и скелетоны** — для UX при загрузке данных.

---

## 4. Требования к коду и UX

- Чистый, типизированный код (TypeScript).
- Адаптивная верстка (Tailwind).
- Современный UI/UX (минимум boilerplate, максимум удобства).
- Обработка ошибок и уведомления (toast/snackbar).
- Защита роутов (редирект на /login при отсутствии токена).
- Документация по запуску и настройке (README.md).

---

## 5. Примерная структура проекта

```
/app
  /login
  /dashboard
  /projects
  /projects/[id]/subprojects
  /subprojects/[id]/prompts
  /subprojects/[id]/channels
  /moderation
  /settings/integrations
  /settings/profile
/components
/hooks
/store (если Zustand)
/utils
```

---

## 6. Запуск и настройка

- Описать в README.md как запускать проект локально и в Docker.
- Пример .env.local для переменных окружения (API_URL и др.).

---

## 7. Тестирование

- Покрыть основные хуки и компоненты unit-тестами (Jest, React Testing Library).

---

## 8. Дополнительно

- Использовать OpenAPI-генерацию типов (по желанию).
- Поддержка темной темы (Tailwind).
- Возможность локализации (i18n).

---
Конечно! Вот подробная детализация каждого блока frontend-архитектуры для вашего проекта:

---

## 1. Авторизация (`/login`)

**Функционал:**
- Встраивание Telegram Login Widget (официальный скрипт Telegram).
- После успешного входа — отправка данных Telegram на backend (`/auth/telegram`), получение JWT.
- Хранение JWT в localStorage или Secure Cookies.
- Реализация AuthContext/Provider:
  - Проверка валидности токена.
  - Хранение данных пользователя (id, username, avatar).
  - Методы login/logout.
- Редирект на `/dashboard` после входа.
- Защита приватных роутов (если нет токена — редирект на `/login`).

**UI:**
- Кнопка Telegram Login.
- Лоадер/спиннер на время авторизации.
- Сообщения об ошибках (toast/snackbar).

---

## 2. Дашборд (`/dashboard`)

**Функционал:**
- Получение агрегированной статистики по всем проектам через API (`/api/stats/`).
- Визуализация:
  - Графики (например, количество сообщений по дням, лайки, статус сообщений).
  - Карточки с ключевыми метриками (всего сообщений, одобрено, отклонено, лайков).
- Фильтры по дате, проекту, подпроекту.
- Быстрые ссылки на проекты, модерацию.

**UI:**
- Графики (например, с помощью recharts, nivo, chart.js).
- Карточки-метрики.
- Дропдауны/календарь для фильтрации.
- Скелетоны/лоадеры на время загрузки.

---

## 3. Проекты и подпроекты (`/projects`, `/projects/[id]/subprojects`)

**Функционал:**
- Список всех проектов пользователя (GET `/api/projects/`).
- CRUD-проекты: создание, редактирование, удаление (POST, PATCH, DELETE).
- Вложенность: подпроекты внутри проекта (GET `/api/projects/{id}/subprojects/`).
- Навигация между проектами и подпроектами.
- Возможность перехода к настройкам, промптам, каналам подпроекта.

**UI:**
- Таблица или карточки проектов.
- Кнопка “Создать проект”, “Редактировать”, “Удалить”.
- Модальные окна для создания/редактирования.
- Бейджи/иконки статуса.

---

## 4. Промпты (`/subprojects/[id]/prompts`)

**Функционал:**
- Список и редактор шаблонов промптов (GET/POST/PATCH/DELETE `/api/prompt_templates/`).
- Версионирование промптов (GET `/api/prompt_settings_versions/`).
- Форма редактирования с предпросмотром (Jinja2-синтаксис).
- Активация версии промпта.
- Валидация шаблона (отправка на backend для проверки).

**UI:**
- Список версий промпта (с датой, статусом).
- Форма редактирования (textarea, предпросмотр).
- Кнопки “Сохранить”, “Активировать версию”, “Удалить”.
- Подсветка синтаксиса (по желанию).

---

## 5. Каналы (`/subprojects/[id]/channels`)

**Функционал:**
- Список подключённых Telegram-каналов (GET `/api/monitored_channels/`).
- Добавление нового канала (POST).
- Настройка фильтров (по ключевым словам, автоответам и т.д.).
- Включение/отключение мониторинга канала.
- Удаление канала.

**UI:**
- Таблица каналов (название, статус, фильтры).
- Кнопка “Добавить канал”.
- Модальное окно для настройки фильтров.
- Тогглы для включения/отключения.

---

## 6. Модерация (`/moderation`)

**Функционал:**
- Получение очереди сообщений на модерацию (GET `/api/messages/?status=pending`).
- Таблица: исходное сообщение, AI-ответ, статус, дата, канал.
- Действия:
  - “Отправить” (POST `/api/messages/{id}/approve`)
  - “Отклонить” (POST `/api/messages/{id}/decline`)
  - “Редактировать” (PATCH `/api/messages/{id}`)
  - “Лайк/дизлайк” (POST `/api/messages/{id}/like`)
- Фильтры по статусу, дате, каналу.
- Пагинация.

**UI:**
- Таблица с действиями (кнопки, иконки).
- Модальное окно для редактирования.
- Toast-уведомления об успехе/ошибке.
- Скелетоны на время загрузки.

---

## 7. Настройки (`/settings/integrations`, `/settings/profile`)

**Интеграции:**
- Список интеграций (MTProto, Bot API).
- Добавление новой интеграции (форма: токен, api_id, api_hash).
- Проверка валидности интеграции (запрос к backend).
- Удаление интеграции.

**Профиль:**
- Просмотр и редактирование профиля (имя, email, язык, предпочтения).
- Смена пароля (если реализовано).
- Выход из аккаунта.

**UI:**
- Формы с валидацией.
- Кнопки “Добавить”, “Удалить”, “Сохранить”.
- Информативные сообщения об ошибках/успехе.

---

## 8. Общие компоненты и хуки

- **AuthContext** — глобальный провайдер авторизации, методы login/logout, хранение токена и данных пользователя.
- **use*Query** — хуки для загрузки данных (React Query/Zustand).
- **UI-компоненты:** кнопки, формы, таблицы, модальные окна (shadcn/ui или кастом).
- **ErrorBoundary** — обработка ошибок API.
- **Лоадеры и скелетоны** — для UX при загрузке данных.
- **Toast/Snackbar** — уведомления об ошибках и успехе.

Вот подробная бизнес-логика и REST API для каждого блока frontend:

---

## 1. Авторизация (`/login`)

**Бизнес-логика:**
- Пользователь кликает Telegram Login Widget.
- После успешного входа Telegram возвращает user info (id, username, hash).
- Frontend отправляет эти данные на backend:  
  **POST** `/api/auth/telegram`  
  ```json
  {
    "id": 123456,
    "username": "user",
    "first_name": "Ivan",
    "last_name": "Ivanov",
    "photo_url": "...",
    "auth_date": 1710000000,
    "hash": "..."
  }
  ```
- Backend возвращает JWT-токен и user info:
  ```json
  {
    "access_token": "jwt...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "username": "user",
      "full_name": "Ivan Ivanov"
    }
  }
  ```
- Токен сохраняется в localStorage/cookie.
- AuthContext хранит токен и user info, предоставляет методы login/logout.
- Все приватные роуты защищены (редирект на `/login` при отсутствии токена).

---

## 2. Дашборд (`/dashboard`)

**Бизнес-логика:**
- После авторизации загружается агрегированная статистика по всем проектам.
- Пользователь может фильтровать по дате, проекту, подпроекту.
- Данные отображаются в виде графиков и карточек.

**REST API:**
- **GET** `/api/stats/summary`  
  Ответ:
  ```json
  {
    "total_messages": 1234,
    "approved": 1000,
    "declined": 200,
    "likes": 500,
    "by_day": [
      {"date": "2024-06-01", "messages": 100, "likes": 40},
      ...
    ]
  }
  ```
- **GET** `/api/stats/project/{project_id}` — статистика по проекту
- **GET** `/api/stats/subproject/{subproject_id}` — по подпроекту

---

## 3. Проекты и подпроекты (`/projects`, `/projects/[id]/subprojects`)

**Бизнес-логика:**
- Пользователь видит список своих проектов.
- Может создавать, редактировать, удалять проекты.
- Внутри проекта — список подпроектов, те же CRUD-операции.

**REST API:**
- **GET** `/api/projects/` — список проектов
- **POST** `/api/projects/` — создать проект  
  ```json
  { "name": "My Project", "description": "..." }
  ```
- **PATCH** `/api/projects/{id}` — редактировать
- **DELETE** `/api/projects/{id}` — удалить

- **GET** `/api/projects/{id}/subprojects/` — подпроекты
- **POST** `/api/subprojects/` — создать подпроект  
  ```json
  { "project_id": 1, "name": "Subproject", "description": "..." }
  ```
- **PATCH/DELETE** `/api/subprojects/{id}`

---

## 4. Промпты (`/subprojects/[id]/prompts`)

**Бизнес-логика:**
- Для каждого подпроекта можно создавать и редактировать шаблоны промптов.
- Поддержка версионирования: можно активировать нужную версию.
- Предпросмотр результата шаблона (рендеринг с тестовыми данными).

**REST API:**
- **GET** `/api/prompt_templates/?subproject_id=1` — список шаблонов
- **POST** `/api/prompt_templates/` — создать шаблон  
  ```json
  { "subproject_id": 1, "name": "Greeting", "template": "Hello, {{ user_name }}!" }
  ```
- **PATCH/DELETE** `/api/prompt_templates/{id}`

- **GET** `/api/prompt_settings_versions/?prompt_template_id=1` — версии шаблона
- **POST** `/api/prompt_settings_versions/activate/{id}` — активировать версию

---

## 5. Каналы (`/subprojects/[id]/channels`)

**Бизнес-логика:**
- Пользователь видит список каналов, подключённых к подпроекту.
- Может добавить новый канал, настроить фильтры (по ключевым словам и т.д.), включить/отключить мониторинг.

**REST API:**
- **GET** `/api/monitored_channels/?subproject_id=1`
- **POST** `/api/monitored_channels/`  
  ```json
  { "subproject_id": 1, "channel_id": 123456, "title": "My Channel", "filters": { "keywords": ["ai", "news"] } }
  ```
- **PATCH/DELETE** `/api/monitored_channels/{id}`

---

## 6. Модерация (`/moderation`)

**Бизнес-логика:**
- Модератор видит очередь сообщений на рассмотрение.
- Может одобрить, отклонить, отредактировать AI-ответ, поставить лайк.
- После действия сообщение исчезает из очереди.

**REST API:**
- **GET** `/api/messages/?status=pending` — сообщения на модерацию
- **POST** `/api/messages/{id}/approve` — одобрить
- **POST** `/api/messages/{id}/decline` — отклонить
- **PATCH** `/api/messages/{id}` — редактировать  
  ```json
  { "ai_response": "Новый ответ" }
  ```
- **POST** `/api/messages/{id}/like` — лайк/дизлайк

---

## 7. Настройки (`/settings/integrations`, `/settings/profile`)

**Интеграции:**
- Список интеграций (боты, MTProto).
- Добавление новой интеграции (проверка валидности токена).

**REST API:**
- **GET** `/api/telegram_integrations/`
- **POST** `/api/telegram_integrations/`  
  ```json
  { "type": "bot", "token": "123:ABC" }
  ```
- **DELETE** `/api/telegram_integrations/{id}`

**Профиль:**
- Просмотр/редактирование профиля пользователя.

**REST API:**
- **GET** `/api/users/me`
- **PATCH** `/api/users/me`  
  ```json
  { "full_name": "New Name", "language": "ru" }
  ```

---

## 8. Общие компоненты и хуки

- **AuthContext** — хранит токен, user info, методы login/logout, refresh.
- **use*Query** — хуки для загрузки данных (React Query/Zustand).
- **ErrorBoundary** — обработка ошибок API.
- **Toast/Snackbar** — уведомления об ошибках/успехе.

---
Вот примеры REST-запросов и ответов для основных блоков frontend.  
Все запросы требуют JWT-токен в заголовке:  
`Authorization: Bearer <token>`

---

## 1. Авторизация

**POST /api/auth/telegram**  
_Отправка данных Telegram после логина:_
```json
{
  "id": 123456,
  "username": "user",
  "first_name": "Ivan",
  "last_name": "Ivanov",
  "photo_url": "https://t.me/i/userpic/320/abc.jpg",
  "auth_date": 1710000000,
  "hash": "..."
}
```
**Ответ:**
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "user",
    "full_name": "Ivan Ivanov"
  }
}
```

---

## 2. Дашборд

**GET /api/stats/summary**
**Ответ:**
```json
{
  "total_messages": 1234,
  "approved": 1000,
  "declined": 200,
  "likes": 500,
  "by_day": [
    {"date": "2024-06-01", "messages": 100, "likes": 40},
    {"date": "2024-06-02", "messages": 120, "likes": 50}
  ]
}
```

---

## 3. Проекты и подпроекты

**GET /api/projects/**
**Ответ:**
```json
[
  {
    "id": 1,
    "name": "AI News",
    "description": "Новости искусственного интеллекта"
  },
  {
    "id": 2,
    "name": "Crypto Monitor",
    "description": "Криптовалютные каналы"
  }
]
```

**POST /api/projects/**
```json
{
  "name": "New Project",
  "description": "Описание"
}
```
**Ответ:**
```json
{
  "id": 3,
  "name": "New Project",
  "description": "Описание"
}
```

**GET /api/projects/1/subprojects/**
**Ответ:**
```json
[
  {
    "id": 10,
    "project_id": 1,
    "name": "Новости",
    "description": "Все новости"
  }
]
```

---

## 4. Промпты

**GET /api/prompt_templates/?subproject_id=10**
**Ответ:**
```json
[
  {
    "id": 100,
    "subproject_id": 10,
    "name": "Greeting",
    "template": "Привет, {{ user_name }}!"
  }
]
```

**POST /api/prompt_templates/**
```json
{
  "subproject_id": 10,
  "name": "Welcome",
  "template": "Добро пожаловать, {{ user_name }}!"
}
```
**Ответ:**
```json
{
  "id": 101,
  "subproject_id": 10,
  "name": "Welcome",
  "template": "Добро пожаловать, {{ user_name }}!"
}
```

**GET /api/prompt_settings_versions/?prompt_template_id=100**
**Ответ:**
```json
[
  {
    "id": 1,
    "prompt_template_id": 100,
    "version": 1,
    "is_active": true,
    "created_at": "2024-06-01T12:00:00"
  }
]
```

---

## 5. Каналы

**GET /api/monitored_channels/?subproject_id=10**
**Ответ:**
```json
[
  {
    "id": 200,
    "subproject_id": 10,
    "channel_id": 123456,
    "title": "AI News Channel",
    "filters": {"keywords": ["ai", "news"]},
    "is_active": true
  }
]
```

**POST /api/monitored_channels/**
```json
{
  "subproject_id": 10,
  "channel_id": 654321,
  "title": "Crypto News",
  "filters": {"keywords": ["crypto", "btc"]}
}
```
**Ответ:**
```json
{
  "id": 201,
  "subproject_id": 10,
  "channel_id": 654321,
  "title": "Crypto News",
  "filters": {"keywords": ["crypto", "btc"]},
  "is_active": true
}
```

---

## 6. Модерация

**GET /api/messages/?status=pending**
**Ответ:**
```json
[
  {
    "id": 300,
    "channel_id": 123456,
    "text": "Как работает AI?",
    "ai_response": "AI работает на основе нейросетей.",
    "status": "pending",
    "created_at": "2024-06-02T10:00:00"
  }
]
```

**POST /api/messages/300/approve**
**Ответ:**
```json
{
  "id": 300,
  "status": "approved"
}
```

**POST /api/messages/300/decline**
**Ответ:**
```json
{
  "id": 300,
  "status": "declined"
}
```

**PATCH /api/messages/300**
```json
{
  "ai_response": "Обновленный AI-ответ"
}
```
**Ответ:**
```json
{
  "id": 300,
  "ai_response": "Обновленный AI-ответ"
}
```

**POST /api/messages/300/like**
**Ответ:**
```json
{
  "id": 300,
  "liked": true
}
```

---

## 7. Настройки

**GET /api/telegram_integrations/**
**Ответ:**
```json
[
  {
    "id": 1,
    "type": "bot",
    "token": "123:ABC",
    "is_valid": true
  }
]
```

**POST /api/telegram_integrations/**
```json
{
  "type": "mtproto",
  "api_id": 12345,
  "api_hash": "abcdef"
}
```
**Ответ:**
```json
{
  "id": 2,
  "type": "mtproto",
  "api_id": 12345,
  "api_hash": "abcdef",
  "is_valid": true
}
```

**GET /api/users/me**
**Ответ:**
```json
{
  "id": 1,
  "username": "user",
  "full_name": "Ivan Ivanov",
  "email": "user@email.com",
  "language": "ru"
}
```

**PATCH /api/users/me**
```json
{
  "full_name": "Ivan Petrov",
  "language": "en"
}
```
**Ответ:**
```json
{
  "id": 1,
  "full_name": "Ivan Petrov",
  "language": "en"
}
```

---
Да, для frontend-разработки обязательно нужны примеры запросов и ответов для каждого ключевого REST API. Это позволяет:

- Быстро интегрировать хуки (React Query, Zustand) с backend.
- Понимать структуру данных для UI-компонентов.
- Упростить мокирование данных и тестирование.
- Снизить количество ошибок при интеграции.

---

### Пример:  
**Авторизация (Telegram Login)**
- **POST** `/auth/telegram`
- **Request:**
  ```json
  {
    "id": 123456,
    "username": "user",
    "first_name": "Ivan",
    "last_name": "Ivanov",
    "auth_date": 1710000000,
    "hash": "..."
  }
  ```
- **Response:**
  ```json
  {
    "access_token": "jwt_token_here",
    "refresh_token": "jwt_refresh_token",
    "token_type": "bearer"
  }
  ```

---

**Дашборд (статистика)**
- **GET** `/stats/project/1`
- **Response:**
  ```json
  [
    {
      "date": "2024-06-01",
      "messages": 100,
      "approved": 80,
      "declined": 10,
      "likes": 40
    },
    ...
  ]
  ```

---

**Модерация**
- **GET** `/messages?status=pending`
- **Response:**
  ```json
  [
    {
      "id": 300,
      "channel_id": 123456,
      "text": "Как работает AI?",
      "ai_response": "AI работает на основе нейросетей.",
      "status": "pending",
      "created_at": "2024-06-02T10:00:00"
    }
  ]
  ```
- **POST** `/messages/300/approve`
- **Response:**
  ```json
  {
    "id": 300,
    "status": "approved"
  }
  ```

---

**Проекты**
- **GET** `/projects`
- **Response:**
  ```json
  [
    {
      "id": 1,
      "name": "AI News",
      "description": "Новости искусственного интеллекта"
    }
  ]
  ```

---

**Промпты**
- **GET** `/prompts?subproject_id=10`
- **Response:**
  ```json
  [
    {
      "id": 100,
      "subproject_id": 10,
      "name": "Greeting",
      "template": "Привет, {{ user_name }}!"
    }
  ]
  ```

---

**Каналы**
- **GET** `/channels?subproject_id=10`
- **Response:**
  ```json
  [
    {
      "id": 200,
      "subproject_id": 10,
      "channel_id": 123456,
      "title": "AI News Channel",
      "filters": {"keywords": ["ai", "news"]},
      "is_active": true
    }
  ]
  ```

---

**Интеграции**
- **GET** `/telegram/integrations`
- **Response:**
  ```json
  [
    {
      "id": 1,
      "type": "bot",
      "token": "123:ABC",
      "is_valid": true
    }
  ]
  ```

---

**Профиль**
- **GET** `/me`
- **Response:**
  ```json
  {
    "id": 1,
    "telegram_id": "123456",
    "username": "user",
    "first_name": "Ivan",
    "last_name": "Ivanov",
    "is_active": true,
    "created_at": "2024-06-01T12:00:00"
  }
  ```

---

