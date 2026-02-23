"""
Kaalition.ru API Library
========================

Библиотека для автоматизации работы с API сайта kaalition.ru.

Основные классы:
- KaalitionClient: Клиент для операций без авторизации
- Account: Аккаунт с авторизацией (наследует от KaalitionClient)
- User: Датакласс для найденных пользователей

Пример использования:
    from kaalition_lib import KaalitionClient

    client = KaalitionClient()
    account = client.register()
    account.send_message(user, "Привет!")
"""

from .kaalition_lib import (
    # Классы
    KaalitionClient,
    Account,
    User,

    # Исключения
    KaalitionError,
    RegistrationError,
    LoginError,
    TokenError,
    ProfileUpdateError,
    UserNotFoundError,
    MessageError,

    # Утилиты
    load_accounts,
    save_accounts,
    get_active_accounts,
    clean_accounts_file,
    parse_wait_time,

    # Константы
    DEFAULT_BASE_URL,
    DEFAULT_ACCOUNTS_FILE,
    DEFAULT_USER_AGENT,
    DEFAULT_DELAY,
    DEFAULT_EMAIL_DOMAINS,
)

__version__ = "b1.0.2"
__author__ = "Dmitry"

__all__ = [
    # Классы
    "KaalitionClient",
    "Account",
    "User",

    # Исключения
    "KaalitionError",
    "RegistrationError",
    "LoginError",
    "TokenError",
    "ProfileUpdateError",
    "UserNotFoundError",
    "MessageError",

    # Утилиты
    "load_accounts",
    "save_accounts",
    "get_active_accounts",
    "clean_accounts_file",
    "parse_wait_time",

    # Константы
    "DEFAULT_BASE_URL",
    "DEFAULT_ACCOUNTS_FILE",
    "DEFAULT_USER_AGENT",
    "DEFAULT_DELAY",
    "DEFAULT_EMAIL_DOMAINS",
]