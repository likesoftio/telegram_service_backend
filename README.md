# Telegram AI Monitoring Backend

## Описание

Масштабируемая backend-платформа для мониторинга Telegram-каналов, генерации AI-ответов (OpenAI), модерации, лайков и аналитики. Поддержка проектов, подпроектов, индивидуальных промптов, A/B тестов, Telegram-интеграций (бот/MTProto), очередей (Celery), статистики (PostgreSQL).

---

## Архитектура (эпики)
- Авторизация через Telegram (web)
- Проекты и подпроекты
- Промпты и версионирование
- Интеграции Telegram (бот/номер)
- Мониторинг каналов
- Сообщения и AI-ответы (OpenAI)
- Модерация, лайки
- Ежедневная статистика, A/B анализ
- Воркеры (Celery + Redis)
- Хранение MTProto-сессий

---

## Быстрый старт (Docker Compose)

1. Клонируйте репозиторий и создайте `.env` на основе `.env.example`:
   ```bash
   cp .env.example .env
   # Заполните переменные (Postgres, Redis, OpenAI, Telegram)
   ```
2. Соберите и запустите сервисы:
   ```bash
   docker-compose up --build -d
   ```
3. Проверьте, что все сервисы стартовали:
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```
4. Документация API: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Переменные окружения (.env)

```env
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=telegram_service
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# FastAPI
SECRET_KEY=supersecretkey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# OpenAI
OPENAI_API_KEY=sk-...

# Telegram MTProto
TELEGRAM_API_ID=123456
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_SESSION=mtproto_session
```

---

## Тесты

1. Установите зависимости:
   ```bash
   pip install pytest httpx pytest-asyncio
   ```
2. Запустите тесты:
   ```bash
   pytest app/tests/
   ```
   или через Docker:
   ```bash
   docker-compose exec api pytest app/tests/
   ```

---

## Swagger/OpenAPI
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- OpenAPI JSON: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## DevOps и воркеры
- Все сервисы (api, db, redis, worker, beat) описаны в docker-compose.yml
- Воркеры Celery: автоматический запуск задач (сканирование каналов, генерация AI-ответов, агрегация статистики)
- Логирование: loguru (воркеры), uvicorn (api)
- MTProto-сессии: хранятся в session_file (см. telegram_integrations)

---

## Контакты и поддержка
- Вопросы и баги — через Issues или Pull Requests
- Для production: настройте HTTPS, CORS, мониторинг, секреты 