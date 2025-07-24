import json
from typing import List
from openai import OpenAI
from loguru import logger
from jinja2 import Template, TemplateError


def format_messages(messages) -> str:
    """Форматирует сообщения для промпта"""
    formatted = []
    for msg in messages:
        formatted.append(f"ID: {msg.id}, Текст: {msg.text or 'Нет текста'}")
    return "\n".join(formatted)


def create_filter_prompt(channel_filter: str, messages) -> str:
    return f"""
Ты - система фильтрации сообщений Telegram.

КРИТЕРИЙ ФИЛЬТРАЦИИ: {channel_filter}

СООБЩЕНИЯ ДЛЯ ПРОВЕРКИ:
{format_messages(messages)}

ИНСТРУКЦИИ:
1. Проанализируй каждое сообщение по критерию
2. Верни ТОЛЬКО JSON с ID подходящих сообщений:
{{"suitable_ids": [список ID подходящих сообщений]}}

ВАЖНО: Верни только JSON, без дополнительного текста.
"""


def filter_messages_with_ai(channel_filter: str, messages, openai_client: OpenAI) -> List[int]:
    """Фильтрует сообщения с помощью ИИ"""
    try:
        # Создаем промпт
        prompt = create_filter_prompt(channel_filter, messages)
        
        # Отправляем в OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        # Парсим результат
        result = json.loads(response.choices[0].message.content)
        return result.get("suitable_ids", [])
        
    except Exception as e:
        logger.error(f"Ошибка фильтрации ИИ: {e}")
        return []  # В случае ошибки возвращаем пустой список


def render_prompt_template(template_text: str, context: dict) -> str:
    """Рендерит промпт шаблон с Jinja2"""
    try:
        template = Template(template_text)
        return template.render(**context)
    except TemplateError as e:
        logger.error(f"Jinja2 template error: {e}")
        raise e


def create_ai_response_prompt(user_prompt: str, message_text: str) -> str:
    """Создает промпт для генерации ИИ ответа"""
    return f"""
Ты - помощник для ответа на сообщения из Telegram каналов.

ЗАДАЧА ПОЛЬЗОВАТЕЛЯ: {user_prompt}

СООБЩЕНИЕ ДЛЯ АНАЛИЗА:
{message_text}

ИНСТРУКЦИИ:
1. Проанализируй сообщение согласно задаче пользователя
2. Дай четкий и полезный ответ
3. Если задача неясна, уточни что именно нужно сделать

ВАЖНО: Отвечай только на задачу пользователя, не добавляй лишнего текста.
"""


def generate_ai_response(user_prompt: str, message_text: str, openai_client: OpenAI, model_params: dict = None) -> tuple[str, int, str]:
    """Генерирует ИИ ответ на сообщение"""
    try:
        # Создаем промпт
        prompt = create_ai_response_prompt(user_prompt, message_text)
        
        # Параметры по умолчанию
        default_params = {
            "model": "gpt-3.5-turbo",
            "max_tokens": 256,
            "temperature": 0.7
        }
        
        # Обновляем параметры пользователя
        if model_params:
            default_params.update(model_params)
        
        # Отправляем в OpenAI
        response = openai_client.chat.completions.create(
            model=default_params["model"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=default_params["max_tokens"],
            temperature=default_params["temperature"],
        )
        
        # Получаем ответ и информацию о токенах
        ai_response = response.choices[0].message.content
        token_usage = response.usage.total_tokens
        model_name = response.model
        
        return ai_response, token_usage, model_name
        
    except Exception as e:
        logger.error(f"Ошибка генерации ИИ ответа: {e}")
        raise e