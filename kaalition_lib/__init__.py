# __init__.py

from .kaalition_lib import (
    # Классы
    KaalitionClient,
    Account,
    User,
    Message,
    Reaction,
    Project,
    Member,
    News,

    # Исключения
    KaalitionError,
    LoginError,
    TokenError,
    ProfileUpdateError,
    UserNotFoundError,
    MessageError,
    MessageEditError,
    MessageDeleteError,
    MessageReactionError,
    ChatHistoryError,

    # Утилиты
    parse_wait_time,

    # Константы
    DEFAULT_BASE_URL,
    DEFAULT_USER_AGENT,
    DEFAULT_EMAIL_DOMAINS,
)

__version__ = "3.0.0"
__author__ = "Dima-Programmer"

__all__ = [
    # Классы
    "KaalitionClient",
    "Account",
    "User",
    "Message",
    "Reaction",
    "Project",
    "Member",
    "News",

    # Исключения
    "KaalitionError",
    "LoginError",
    "TokenError",
    "ProfileUpdateError",
    "UserNotFoundError",
    "MessageError",
    "MessageEditError",
    "MessageDeleteError",
    "MessageReactionError",
    "ChatHistoryError",

    # Утилиты
    "parse_wait_time",

    # Константы
    "DEFAULT_BASE_URL",
    "DEFAULT_USER_AGENT",
    "DEFAULT_EMAIL_DOMAINS",
]