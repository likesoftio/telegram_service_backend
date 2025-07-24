#!/usr/bin/env python3
"""
Скрипт для генерации ключа шифрования
Запусти: python generate_encryption_key.py
"""

from src.core.encryption import EncryptionService

def main():
    # Создаем новый сервис шифрования
    encryption_service = EncryptionService()
    
    # Получаем ключ в base64 формате
    key_base64 = encryption_service.get_key_base64()
    
    print("=" * 50)
    print("КЛЮЧ ШИФРОВАНИЯ")
    print("=" * 50)
    print(f"ENCRYPTION_KEY={key_base64}")
    print("=" * 50)
    print("\nДобавь эту строку в твой .env файл!")
    print("ВНИМАНИЕ: Сохрани этот ключ в безопасном месте!")
    print("Без него ты не сможешь расшифровать данные!")

if __name__ == "__main__":
    main() 