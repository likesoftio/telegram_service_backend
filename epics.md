Отлично, давай начнём с Эпика 1: Авторизация и пользователи, полностью подготовленного в формате для постановки задач в Cursor или любой другой task tracker (например, Jira, Linear, Notion).

⸻

🔐 EPIC 1: Авторизация и пользователи

🎯 Цель:

Организовать авторизацию пользователей через Telegram (WebLogin), хранение информации о пользователях и базовую защиту API через JWT.

⸻

✅ Результат эпика:
	•	Пользователь может авторизоваться через Telegram
	•	Получает JWT-токен
	•	Все запросы к API защищены токеном
	•	В БД создаётся сущность пользователя с telegram_id, username и др.

⸻

🧩 Подзадачи

⸻

1.1. База данных: таблица users

Тип: Tech
Описание: Создать таблицу users с полями:

users (
  id UUID PRIMARY KEY,
  telegram_id BIGINT UNIQUE NOT NULL,
  username TEXT,
  full_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMP DEFAULT now()
)


⸻

1.2. Эндпоинт авторизации POST /auth/telegram

Тип: API
Описание:
	•	Принимает данные из Telegram Login Widget
	•	Проверяет подпись (hash) через shared secret
	•	Находит или создаёт пользователя
	•	Возвращает JWT

Пример запроса:

{
  "telegram_id": 12345678,
  "username": "roma",
  "first_name": "Роман",
  "auth_date": 1710000000,
  "hash": "VALID_HASH"
}


⸻

1.3. Реализация JWT-аутентификации

Тип: Security / Middleware
Описание:
	•	Генерация JWT при входе (/auth/telegram)
	•	Middleware для проверки Authorization: Bearer <token>
	•	Токен содержит user_id, telegram_id

⸻

1.4. Эндпоинт GET /me

Тип: API
Описание:
Возвращает информацию о текущем пользователе по JWT.

{
  "id": "uuid",
  "telegram_id": 12345678,
  "username": "roma",
  "full_name": "Роман"
}


⸻

1.5. Валидация Telegram Login (безопасность)

Тип: Security
Описание:
	•	Проверить подпись Telegram (hash = SHA256(secret + sorted_fields))
	•	Использовать bot_token → derive secret key

⸻

1.6. Конфигурация окружения

Тип: DevOps
Описание:
	•	.env: переменная JWT_SECRET, TELEGRAM_BOT_TOKEN
	•	Добавить проверку наличия этих переменных при старте

⸻

1.7. Юнит-тесты и Postman-запросы

Тип: Testing
Описание:
	•	Тесты на авторизацию (валидная / невалидная подпись)
	•	Проверка запрета доступа без токена
	•	Добавить запросы в Postman коллекцию

⸻

📦 Структура модулей

/api/auth.py
/services/auth_service.py
/middleware/jwt_auth.py
/models/user.py


⸻


Отлично, продолжаем.

⸻

📁 EPIC 2: Проекты и подпроекты

🎯 Цель:

Позволить пользователям создавать проекты и подпроекты для структурирования работы, разделения Telegram-каналов, промптов и статистики.

⸻

✅ Результат эпика:
	•	У каждого пользователя может быть несколько проектов
	•	Внутри каждого проекта — подпроекты (например, по направлениям/кампаниям)
	•	Эти сущности будут основой для фильтрации сообщений, генерации ответов и построения аналитики

⸻

🧩 Подзадачи

⸻

2.1. Таблица projects

Тип: DB
Описание: Создать таблицу projects, содержащую:

projects (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT now()
)


⸻

2.2. Таблица subprojects

Тип: DB
Описание: Создать таблицу subprojects, связанную с проектом:

subprojects (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT now()
)


⸻

2.3. Эндпоинт POST /projects

Тип: API
Описание: Создание проекта:

{
  "name": "AI Responses",
  "description": "Ответы на сообщения из Telegram"
}


⸻

2.4. Эндпоинт GET /projects

Тип: API
Описание: Получение всех проектов пользователя, к которому относится JWT.

⸻

2.5. Эндпоинт POST /subprojects

Тип: API
Описание: Создание подпроекта внутри проекта:

{
  "project_id": "uuid",
  "name": "Лидогенерация"
}


⸻

2.6. Эндпоинт GET /projects/{id}/subprojects

Тип: API
Описание: Получение всех подпроектов для проекта

⸻

2.7. Эндпоинт PATCH /projects/{id} и PATCH /subprojects/{id}

Тип: API
Описание: Изменение названия / описания

⸻

2.8. Эндпоинт DELETE /projects/{id} и DELETE /subprojects/{id}

Тип: API
Описание: Удаление проекта/подпроекта (каскадно удаляет привязанные сущности: промпты, каналы и т.д.)

⸻

2.9. Валидация прав доступа

Тип: Security
Описание: Все запросы должны проверять, что проект принадлежит текущему пользователю

⸻

2.10. Тесты и Postman

Тип: Testing
Описание:
	•	Тесты на CRUD-проектов и подпроектов
	•	Обработка ошибок: 403, 404
	•	Добавить в Postman коллекцию

⸻

📦 Структура модулей

/api/projects.py
/services/project_service.py
/models/project.py
/models/subproject.py

Отлично, переходим к следующему блоку.

⸻

🧠 EPIC 3: Промпты и настройки генерации (в т.ч. A/B версии)

🎯 Цель:

Реализовать систему шаблонов промптов, которые будут использоваться для генерации AI-ответов, с возможностью гибкой настройки параметров (модель, температура и т.д.) и поддержкой версионирования для A/B-тестирования качества.

⸻

✅ Результат эпика:
	•	У каждого подпроекта могут быть свои промпты
	•	Каждый промпт может иметь несколько версий настроек
	•	Активная версия используется в генерации
	•	Можно редактировать, отключать, сравнивать
	•	Все параметры генерации (модель, температура и т.п.) — в базе и управляются через API

⸻

🧩 Подзадачи

⸻

3.1. Таблица prompt_templates

Тип: DB
Описание: Хранит описание промптов, их тип и метаданные

prompt_templates (
  id UUID PRIMARY KEY,
  subproject_id UUID REFERENCES subprojects(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  active_version INT,
  created_at TIMESTAMP DEFAULT now()
)


⸻

3.2. Таблица prompt_settings_versions

Тип: DB
Описание: Отдельная версия настроек генерации:

prompt_settings_versions (
  id UUID PRIMARY KEY,
  prompt_template_id UUID REFERENCES prompt_templates(id) ON DELETE CASCADE,
  version INT NOT NULL,
  is_active BOOLEAN DEFAULT FALSE,

  system_prompt TEXT DEFAULT 'Ты помощник, отвечающий экспертно и понятно',
  temperature FLOAT DEFAULT 0.7,
  top_p FLOAT DEFAULT 1.0,
  frequency_penalty FLOAT DEFAULT 0.0,
  presence_penalty FLOAT DEFAULT 0.0,
  max_tokens INT DEFAULT 600,
  model TEXT NOT NULL DEFAULT 'gpt-4',

  created_at TIMESTAMP,
  updated_at TIMESTAMP
)


⸻

3.3. Эндпоинт POST /prompts

Тип: API
Описание: Создание нового шаблона промпта

{
  "subproject_id": "uuid",
  "name": "Ответ на заказ",
  "description": "Генерирует ответ для канала заказов"
}


⸻

3.4. Эндпоинт GET /subprojects/{id}/prompts

Тип: API
Описание: Получить список промптов подпроекта

⸻

3.5. POST /prompts/{id}/settings

Тип: API
Описание: Создание новой версии параметров генерации

{
  "version": 2,
  "model": "gpt-3.5-turbo",
  "system_prompt": "Ты эксперт по продвижению",
  "temperature": 0.4,
  "top_p": 1,
  "max_tokens": 800
}


⸻

3.6. POST /prompts/{id}/settings/{version}/activate

Тип: API
Описание: Установить конкретную версию как активную

⸻

3.7. GET /prompts/{id}/settings

Тип: API
Описание: Получить список всех версий настроек и флаг is_active

⸻

3.8. Использование настроек в generate_ai_response_worker

Тип: Logic / Integration
Описание:
	•	Подгрузить активную версию настроек для matched_prompt_id
	•	Использовать её при вызове OpenAI

⸻

3.9. Связь с сообщениями

Тип: Extension
Описание:
	•	Каждое сгенерированное сообщение хранит prompt_template_id и prompt_version
	•	Это позволит строить аналитику по версиям

⸻

3.10. Тесты и Postman

Тип: Testing
Описание:
	•	CRUD для промптов
	•	Создание/активация версии
	•	Использование версии в генерации
	•	Добавить в Postman коллекцию

⸻

📦 Структура модулей

/api/prompts.py
/services/prompt_service.py
/models/prompt_template.py
/models/prompt_settings_versions.py


⸻

Отлично, переходим к следующему блоку.

⸻

📡 EPIC 4: Telegram-интеграции (бот и номер телефона)

🎯 Цель:

Позволить пользователю подключить Telegram аккаунт через Bot API или по номеру телефона (MTProto), чтобы считывать сообщения из каналов и отправлять AI-ответы от имени бота или пользователя.

⸻

✅ Результат эпика:
	•	Пользователь может добавить одну или несколько Telegram-интеграций
	•	Два типа интеграции: bot и phone
	•	Для bot используется Bot API токен
	•	Для phone — авторизация через номер + api_id, api_hash (Telethon)
	•	Интеграция привязывается к пользователю и используется для мониторинга каналов

⸻

🧩 Подзадачи

⸻

4.1. Таблица telegram_integrations

Тип: DB
Описание:

telegram_integrations (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  type TEXT CHECK (type IN ('bot', 'phone')),
  api_id INT,
  api_hash TEXT,
  bot_token TEXT,
  phone_number TEXT,
  session_path TEXT,
  status TEXT DEFAULT 'active',
  created_at TIMESTAMP DEFAULT now()
)


⸻

4.2. POST /telegram/integrations — добавить интеграцию

Тип: API
Описание:
	•	Если type: bot — проверка токена (через Bot API getMe)
	•	Если type: phone — сохранить api_id, api_hash, инициировать сессию через Telethon

{
  "type": "bot",
  "bot_token": "123456:ABC-DEF"
}

{
  "type": "phone",
  "phone_number": "+79990001122",
  "api_id": 123456,
  "api_hash": "abcdef123456"
}


⸻

4.3. Инициализация сессии (для типа phone)

Тип: Integration
Описание:
	•	Использовать Telethon (TelegramClient) для подключения по номеру
	•	Сохранить .session файл
	•	Обрабатывать коды подтверждения (через Telegram код)
	•	Позже можно добавить POST /telegram/integrations/{id}/verify для ввода кода

⸻

4.4. GET /telegram/integrations — список

Тип: API
Описание: Возвращает список всех интеграций текущего пользователя

⸻

4.5. DELETE /telegram/integrations/{id} — удалить интеграцию

Тип: API
Описание: Удаляет интеграцию, отвязывает каналы

⸻

4.6. Валидация доступа

Тип: Security
Описание:
	•	Интеграция может использоваться только её владельцем
	•	Проверка на активность (можно добавить status: error, если токен протух)

⸻

4.7. Хранение сессий MTProto (безопасно)

Тип: DevOps
Описание:
	•	Путь до .session файлов хранится в session_path
	•	Сам файл сохраняется в папке, доступной только API

⸻

4.8. Логгирование и метрики подключения

Тип: Observability
Описание:
	•	Лог успешных и неуспешных подключений
	•	Тайм-ауты, ошибки токенов

⸻

4.9. Тесты и Postman

Тип: Testing
Описание:
	•	Проверка добавления бота
	•	Проверка инициализации с номером
	•	Ошибки: дубликаты, неверные токены, 403

⸻

📦 Структура модулей

/api/telegram.py
/services/telegram_integration_service.py
/integrations/telegram_bot.py
/integrations/telegram_phone.py
/models/telegram_integration.py


⸻

Отлично, продолжаем.

⸻

📺 EPIC 5: Мониторинг Telegram-каналов

🎯 Цель:

Позволить пользователю настроить отслеживание сообщений из выбранных Telegram-каналов через подключённые интеграции (бот или MTProto), с возможностью фильтрации сообщений по ключевым словам, регулярным выражениям и категориям.

⸻

✅ Результат эпика:
	•	Пользователь может указать, какие каналы он хочет отслеживать в каждом подпроекте
	•	У каждого канала можно задать фильтры (ключевые слова, regexp)
	•	Каждое новое сообщение из канала обрабатывается и отправляется в pipeline генерации
	•	Сохраняется информация о последней проверке

⸻

🧩 Подзадачи

⸻

5.1. Таблица monitored_channels

Тип: DB
Описание:

monitored_channels (
  id UUID PRIMARY KEY,
  subproject_id UUID REFERENCES subprojects(id) ON DELETE CASCADE,
  integration_id UUID REFERENCES telegram_integrations(id) ON DELETE CASCADE,

  channel_id TEXT NOT NULL,              -- Telegram ID
  channel_name TEXT,                     -- @handle (если есть)
  filters JSONB,                         -- {"keywords": [...], "regex": [...]}
  is_active BOOLEAN DEFAULT true,
  last_checked_at TIMESTAMP
)


⸻

5.2. POST /channels — добавить мониторинг

Тип: API
Описание: Привязка канала к подпроекту через указанную интеграцию

{
  "subproject_id": "uuid",
  "integration_id": "uuid",
  "channel_id": "-1001234567890",
  "channel_name": "@sales_news",
  "filters": {
    "keywords": ["скидка", "подарок"],
    "regex": ["вебинар\\s\\d{1,2}\\.\\d{1,2}"]
  }
}


⸻

5.3. GET /subprojects/{id}/channels

Тип: API
Описание: Получение всех каналов, привязанных к подпроекту

⸻

5.4. PATCH /channels/{id} и DELETE /channels/{id}

Тип: API
Описание:
	•	Редактирование фильтров и активности
	•	Удаление мониторинга

⸻

5.5. Валидация доступа

Тип: Security
Описание:
	•	Только владелец подпроекта может настраивать каналы
	•	Интеграция должна принадлежать текущему пользователю

⸻

5.6. Worker: channel_scanner_worker

Тип: Background Task
Описание:
	•	Проходит по monitored_channels с is_active = true
	•	Использует Bot API или MTProto-сессию (по integration_id)
	•	Получает новые сообщения (с учётом last_checked_at)
	•	Применяет фильтры:
	•	ключевые слова (in text)
	•	регулярные выражения (re.search)
	•	Если матч найден → создаёт message со статусом NEW

⸻

5.7. Обновление last_checked_at

Тип: Logic
Описание: После прохода по каналу обновляется last_checked_at в базе

⸻

5.8. Логгирование и пропуск дубликатов

Тип: Observability
Описание:
	•	Не обрабатывать уже прочитанные сообщения (по telegram_message_id)
	•	Вести логи: сколько сообщений проверено, сколько добавлено

⸻

5.9. Тесты и Postman

Тип: Testing
Описание:
	•	Добавление каналов
	•	Обработка сообщений
	•	Валидация фильтров
	•	Имитация новых сообщений в юнит-тестах

⸻

📦 Структура модулей

/api/channels.py
/services/channel_monitor_service.py
/tasks/channel_scanner_worker.py
/models/monitored_channel.py


⸻

Отлично, переходим к ключевому компоненту — генерации AI-ответов.

⸻

🧠 EPIC 6: Генерация AI-ответов (OpenAI worker)

🎯 Цель:

Автоматически генерировать ответы на отобранные сообщения из Telegram-каналов с помощью OpenAI, используя выбранный промпт-шаблон и активную версию его настроек.

⸻

✅ Результат эпика:
	•	Новое сообщение, прошедшее фильтры, отправляется в очередь на генерацию
	•	Используется активный промпт и его настройки (температура, модель, system prompt и т.д.)
	•	Ответ сохраняется в базу данных, сообщение получает статус PENDING

⸻

🧩 Подзадачи

⸻

6.1. Таблица messages

Тип: DB
Описание:

messages (
  id UUID PRIMARY KEY,
  channel_id UUID REFERENCES monitored_channels(id),
  telegram_message_id BIGINT,
  text TEXT NOT NULL,
  matched_prompt_id UUID REFERENCES prompt_templates(id),
  prompt_version INT,
  suggested_reply TEXT,
  model TEXT,
  token_usage INT,
  status TEXT CHECK (status IN ('NEW', 'PENDING', 'APPROVED', 'DECLINED', 'SENT', 'NOT_SENT')),
  created_at TIMESTAMP DEFAULT now(),
  moderated_at TIMESTAMP,
  liked_by_user BOOLEAN
)


⸻

6.2. Ворк generate_ai_response_worker

Тип: Background / Celery / BullMQ
Описание:
	•	Принимает message_id
	•	Загружает сообщение, промпт, активные настройки
	•	Формирует текст запроса через Jinja2 шаблонизатор
	•	Вызывает OpenAI Chat API (gpt-4, gpt-3.5-turbo)
	•	Сохраняет suggested_reply, token_usage, model, status = PENDING

⸻

6.3. Использование версии настроек

Тип: Logic
Описание:
	•	Получить prompt_settings_versions где is_active = true
	•	Применить:
	•	system_prompt
	•	temperature, top_p, max_tokens
	•	model

⸻

6.4. Генерация prompt через шаблон

Тип: Logic
Описание:
	•	Использовать Jinja2:

Template(prompt.template_text).render(message_text=message.text)


⸻

6.5. Вызов OpenAI API

Тип: Integration
Описание:

openai.ChatCompletion.create(
  model=settings.model,
  messages=[
    {"role": "system", "content": settings.system_prompt},
    {"role": "user", "content": rendered_prompt}
  ],
  temperature=settings.temperature,
  top_p=settings.top_p,
  max_tokens=settings.max_tokens
)


⸻

6.6. Обработка ошибок и retry

Тип: Robustness
Описание:
	•	Если OpenAI API вернул ошибку — retry через delay
	•	При превышении лимита токенов или rate limit → лог и ошибка

⸻

6.7. Учет времени и токенов

Тип: Observability
Описание:
	•	Сохранять token_usage и latency в messages
	•	Использовать это в статистике по промптам

⸻

6.8. Тесты

Тип: Testing
Описание:
	•	Моки OpenAI API
	•	Подстановка шаблона
	•	Проверка сохранения ответа и статуса
	•	Ошибки модели

⸻

📦 Структура модулей

/tasks/generate_ai_response_worker.py
/services/ai_response_service.py
/templates/jinja_prompt_renderer.py
/models/message.py


⸻

Отлично, переходим к следующему ключевому блоку — модерации AI-ответов.

⸻

✅ EPIC 7: Модерация сообщений и действия пользователя

🎯 Цель:

Предоставить интерфейс и API для модерации сгенерированных AI-ответов: пользователь может принять, отклонить, отредактировать или отправить ответ вручную, после чего статус сообщения обновляется и, при необходимости, происходит отправка в Telegram.

⸻

✅ Результат эпика:
	•	Пользователь видит список сообщений со статусом PENDING
	•	Может подтвердить ответ (APPROVED → SENT)
	•	Может отклонить (DECLINED)
	•	Может вручную редактировать предложенный ответ
	•	Отправка в Telegram через соответствующую интеграцию

⸻

🧩 Подзадачи

⸻

7.1. Эндпоинт GET /messages?status=PENDING

Тип: API
Описание:
	•	Возвращает список всех сообщений, ожидающих модерации
	•	Поддерживает фильтрацию по проекту, дате, каналу

⸻

7.2. POST /messages/{id}/approve

Тип: API
Описание:
	•	Устанавливает статус APPROVED
	•	Переходит к отправке сообщения через Telegram

⸻

7.3. POST /messages/{id}/decline

Тип: API
Описание:
	•	Устанавливает статус DECLINED
	•	Сообщение архивируется и не отправляется

⸻

7.4. PATCH /messages/{id} — редактировать ответ

Тип: API
Описание:
	•	Пользователь редактирует предложенный AI-ответ
	•	Новое значение сохраняется в suggested_reply

{
  "suggested_reply": "Спасибо за ваш вопрос. Мы скоро с вами свяжемся!"
}


⸻

7.5. Отправка сообщения в Telegram

Тип: Integration
Описание:
	•	Если интеграция bot — использовать Telegram Bot API sendMessage
	•	Если интеграция phone — использовать Telethon send_message
	•	После успешной отправки:
	•	status = SENT
	•	moderated_at = now()
	•	сохраняется moderator_id

⸻

7.6. Обновление таблицы messages

Тип: DB Logic
Описание:
	•	Устанавливаются:
	•	status
	•	moderated_at
	•	moderator_id
	•	Используются для расчёта статистики

⸻

7.7. Статусы: финальный список

Статус	Описание
NEW	Сообщение найдено, не обработано
PENDING	Есть AI-ответ, ожидает модерации
APPROVED	Принят, готов к отправке
DECLINED	Отклонён
SENT	Отправлен в Telegram
NOT_SENT	Ошибка при отправке или отмена


⸻

7.8. Логирование действий

Тип: Audit
Описание:
	•	Вести лог модерации (moderator_id, действие, дата)
	•	Можно позже использовать для ревью качества

⸻

7.9. Тесты и Postman

Тип: Testing
Описание:
	•	Проверка перехода по статусам
	•	Отправка сообщений
	•	Ошибки Telegram API
	•	Невозможность редактировать после SENT

⸻

📦 Структура модулей

/api/messages.py
/services/moderation_service.py
/tasks/message_sender_worker.py
/integrations/send_via_bot.py
/integrations/send_via_phone.py
/models/message.py


⸻

Отлично, переходим к следующему компоненту — лайки и обратная связь.

⸻

❤️ EPIC 8: Лайки и обратная связь от пользователя

🎯 Цель:

Собрать обратную связь от пользователя на предложенные AI-ответы для оценки их качества, последующей аналитики и возможного обучения модели. Это также важный сигнал для сравнения эффективности промптов и их версий.

⸻

✅ Результат эпика:
	•	Пользователь может лайкнуть понравившийся ответ
	•	Эта информация сохраняется в messages.liked_by_user
	•	Статистика лайков используется в метриках (like_rate, сравнение версий и пр.)
	•	Позже можно будет расширить до «лайк/дизлайк» или оставить комментарий

⸻

🧩 Подзадачи

⸻

8.1. Расширение таблицы messages

Тип: DB
Описание: Добавить колонку:

liked_by_user BOOLEAN DEFAULT false


⸻

8.2. Эндпоинт POST /messages/{id}/like

Тип: API
Описание:
	•	Устанавливает liked_by_user = true
	•	Только для сообщений со статусом SENT
	•	Повторный лайк не допускается (или игнорируется)

⸻

8.3. GET /messages?liked=true (фильтр по лайкам)

Тип: API
Описание: Возможность отобразить только лайкнутые сообщения

⸻

8.4. Расширение в UI: лайк после отправки

Тип: Extension (для фронта)
Описание:
	•	После отправки сообщения появляется кнопка «лайк»
	•	Или выводится прямо в таблице

⸻

8.5. Использование лайков в аналитике

Тип: Integration
Описание:
	•	В message_stats_daily добавляется поле liked_messages
	•	Используется для расчёта:
	•	Like Rate = liked_messages / messages_sent

⸻

8.6. Поддержка лайков в A/B-аналитике

Тип: Analytics
Описание:
	•	Позволяет сравнивать версии промптов по лайкам
	•	Примеры:
	•	“Версия 1 — 21% лайков”
	•	“Версия 2 — 46% лайков → победитель”

⸻

8.7. Тесты и Postman

Тип: Testing
Описание:
	•	API: лайк → 200 OK, лайк уже есть → 204 No Content
	•	Защита от лайка до отправки (status != SENT)
	•	Проверка подсчёта в статистике

⸻

📦 Структура модулей

/api/messages.py
/services/like_service.py
/models/message.py
/stats/aggregation.py


⸻

Отлично, переходим к блоку аналитики и статистики, построенному на PostgreSQL.

⸻

📊 EPIC 9: Статистика и трекинг (PostgreSQL)

🎯 Цель:

Реализовать сбор, хранение и доступ к аналитике использования системы: по качеству промптов, активности модераторов, A/B-тестам и динамике отправок. Используется PostgreSQL для агрегации и хранения статистики.

⸻

✅ Результат эпика:
	•	Собирается ежедневная агрегированная статистика
	•	Метрики: total / sent / approved / declined / liked, время модерации, usage
	•	Разбивка по проекту, промпту, версии и модератору
	•	API для получения аналитики и сравнения версий промптов

⸻

🧩 Подзадачи

⸻

9.1. Таблица message_stats_daily

Тип: DB
Описание:

message_stats_daily (
  id UUID PRIMARY KEY,
  date DATE NOT NULL,

  project_id UUID REFERENCES projects(id),
  subproject_id UUID REFERENCES subprojects(id),
  prompt_template_id UUID REFERENCES prompt_templates(id),
  prompt_version INT,
  moderator_id UUID REFERENCES users(id),
  model TEXT,

  messages_total INT,
  messages_sent INT,
  messages_approved INT,
  messages_declined INT,
  liked_messages INT,

  avg_moderation_time FLOAT,
  avg_tokens_used INT,

  created_at TIMESTAMP DEFAULT now()
)


⸻

9.2. SQL-агрегация за день

Тип: Cron Job / Celery Beat
Описание: Считать агрегаты за yesterday по сообщениям

INSERT INTO message_stats_daily (...)
SELECT
  CURRENT_DATE - 1 AS date,
  p.project_id,
  p.subproject_id,
  p.id,
  p.active_version,
  m.moderator_id,
  m.model,

  COUNT(*) AS messages_total,
  COUNT(*) FILTER (WHERE m.status = 'SENT') AS messages_sent,
  COUNT(*) FILTER (WHERE m.status = 'APPROVED') AS messages_approved,
  COUNT(*) FILTER (WHERE m.status = 'DECLINED') AS messages_declined,
  COUNT(*) FILTER (WHERE m.liked_by_user = true) AS liked_messages,
  AVG(EXTRACT(EPOCH FROM m.moderated_at - m.created_at)) AS avg_moderation_time,
  AVG(m.token_usage) AS avg_tokens_used
FROM messages m
JOIN prompt_templates p ON p.id = m.matched_prompt_id
WHERE m.created_at::date = CURRENT_DATE - 1
GROUP BY p.project_id, p.subproject_id, p.id, p.active_version, m.moderator_id, m.model;


⸻

9.3. API GET /stats/prompt/{id}?version=2&period=7d

Тип: API
Описание:
	•	Вернёт агрегаты по промпту и версии
	•	Метрики: approve rate, like rate, avg moderation time

⸻

9.4. API GET /stats/prompts/compare?prompt_id=...

Тип: API
Описание:
	•	Сравнение версий одного промпта по всем метрикам
	•	Результат: массив с version, ctr, like_rate, avg_time

⸻

9.5. API GET /stats/project/{id}

Тип: API
Описание:
	•	График активности за последние 7 / 30 дней
	•	Суммарные показатели: сколько отправлено, лайкнуто, отклонено

⸻

9.6. Метрики и определения

Метрика	Расчёт
CTR	messages_sent / messages_total
Approve rate	messages_approved / messages_total
Like rate	liked_messages / messages_sent
Avg moderation	avg_moderation_time (в секундах)
Token usage	avg_tokens_used


⸻

9.7. Индексы и оптимизация PostgreSQL

Тип: DB
Описание:
	•	Индексы на date, prompt_template_id, project_id
	•	Возможно: materialized views (в будущем)

⸻

9.8. Обновление при лайках и модерации

Тип: Sync logic
Описание:
	•	При лайке → инкремент в liked_messages в следующую агрегацию
	•	Валидация на неполные данные (например, ещё не модерировано)

⸻

9.9. Тесты и контроль агрегаций

Тип: Testing
Описание:
	•	Cron агрегирует корректно
	•	Запросы по API возвращают точные данные
	•	Ошибки обрабатываются (0 / 0 → 0)

⸻

📦 Структура модулей

/api/stats.py
/services/stats_service.py
/tasks/update_daily_stats.py
/models/message_stats_daily.py


⸻

Отлично, переходим к следующему компоненту: A/B-анализ версий промптов.

⸻

🧪 EPIC 10: A/B-анализ версий промптов

🎯 Цель:

Дать возможность сравнивать между собой разные версии одного промпт-шаблона по основным метрикам (CTR, лайки, время модерации), чтобы принимать решение — какая версия работает лучше, и активировать её.

⸻

✅ Результат эпика:
	•	В системе можно видеть сравнение версий одного промпта
	•	Метрики по каждому варианту автоматически считаются из статистики
	•	Возможность активировать победившую версию
	•	Основа для итеративного улучшения AI-ответов

⸻

🧩 Подзадачи

⸻

10.1. Привязка сообщений к версии промпта

Тип: Logic
Описание:
	•	В messages уже должно быть поле prompt_version
	•	При генерации AI-ответа подставляется active_version из prompt_template

⸻

10.2. Расширение агрегации статистики по prompt_version

Тип: DB
Описание:
	•	В message_stats_daily добавить группировку и расчёт по версии
	•	Это уже реализовано в EPIC 9, здесь только верификация

⸻

10.3. Эндпоинт GET /stats/prompts/compare?prompt_id=...

Тип: API
Описание:
Возвращает массив вида:

[
  {
    "version": 1,
    "ctr": 0.48,
    "like_rate": 0.33,
    "avg_moderation_time": 9.2
  },
  {
    "version": 2,
    "ctr": 0.67,
    "like_rate": 0.41,
    "avg_moderation_time": 8.4
  }
]


⸻

10.4. Вывод аналитики в дашборде / UI

Тип: Frontend extension
Описание:
	•	Сравнение: версия 1 vs версия 2
	•	Кнопка: “Сделать версию активной”

⸻

10.5. Эндпоинт POST /prompts/{id}/settings/{version}/activate

Тип: API
Описание:
	•	Снимает is_active у всех других версий
	•	Устанавливает is_active = true для указанной

⸻

10.6. Безопасность переключения версии

Тип: Validation
Описание:
	•	Только владелец промпта может менять активную версию
	•	Валидация: версия принадлежит текущему промпту

⸻

10.7. Автоматизация (будущее)

Тип: Extension (фаза 2)
Описание:
	•	Можно будет задать правило: «если CTR > 60% и like_rate > 40% — активировать автоматически»

⸻

10.8. Тесты

Тип: Testing
Описание:
	•	Сравнение метрик по версиям
	•	Корректная активация версии
	•	Поведение воркера при смене версии

⸻

📦 Структура модулей

/api/prompts.py
/services/ab_analysis_service.py
/models/prompt_settings_versions.py
/models/message_stats_daily.py



