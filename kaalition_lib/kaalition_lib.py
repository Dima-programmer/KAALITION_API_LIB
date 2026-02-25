"""
Kaalition.ru API Library
========================

Библиотека для работы с API сайта kaalition.ru.

Структура:
- KaalitionClient: Клиент для операций без авторизации (регистрация, логин, загрузка)
- Account: Унаследованный класс с данными аккаунта и методами с авторизацией
- User: Датакласс для найденных пользователей
- Message: Датакласс для сообщений с методами управления

Пример использования:

    from kaalition_lib import KaalitionClient

    # Регистрация нового аккаунта
    client = KaalitionClient()
    account = client.register()

    # Поиск пользователей
    users = account.search_users("никнейм")

    # Отправка сообщения пользователю
    if users:
        message = account.send_message(users[0], "Привет!")
        print(f"Отправлено: {message.text}")

    # Редактирование сообщения
    if message:
        message.edit_text("Исправленное привет!")

    # Установка реакции
    message.toggle_reaction("👍")

    # Удаление сообщения
    message.delete()

    # Получение истории чата
    messages = account.get_chat_history(users[0])
    for msg in messages:
        print(f"{msg.sender.nickname}: {msg.text}")
"""

import requests
import json
import os
import re
import time
import random
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple, Union
from dataclasses import dataclass, field
from faker import Faker

# ============================================================================
# КОНСТАНТЫ
# ============================================================================

DEFAULT_BASE_URL = "https://kaalition.ru"
DEFAULT_ACCOUNTS_FILE = "accounts.json"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
DEFAULT_DELAY = 2
DEFAULT_EMAIL_DOMAINS = ["gmail.com", "outlook.com", "ya.ru", "hotmail.com"]


# ============================================================================
# ИСКЛЮЧЕНИЯ
# ============================================================================

class KaalitionError(Exception):
    """Базовое исключение."""
    pass


class RegistrationError(KaalitionError):
    """Ошибка регистрации."""
    pass


class LoginError(KaalitionError):
    """Ошибка входа."""
    pass


class TokenError(KaalitionError):
    """Ошибка при работе с токеном."""
    pass


class ProfileUpdateError(KaalitionError):
    """Ошибка обновления профиля."""
    pass


class UserNotFoundError(KaalitionError):
    """Пользователь не найден."""
    pass


class MessageError(KaalitionError):
    """Базовое исключение для ошибок сообщений."""
    pass


class MessageNotFoundError(MessageError):
    """Сообщение не найдено."""
    pass


class MessageEditError(MessageError):
    """Ошибка редактирования сообщения."""
    pass


class MessageDeleteError(MessageError):
    """Ошибка удаления сообщения."""
    pass


class MessageReactionError(MessageError):
    """Ошибка установки реакции."""
    pass


class ChatHistoryError(MessageError):
    """Ошибка получения истории чата."""
    pass


# ============================================================================
# DATACLASSES
# ============================================================================

@dataclass
class User:
    """
    Датакласс для пользователя.

    Attributes:
        id: ID пользователя
        username: Имя пользователя
        nickname: Отображаемое имя
        photo: Путь к фото
        avatar_emoji: Эмодзи аватара
        is_verified: Верифицирован ли
        is_admin: Является ли админом
    """
    id: int
    username: str
    nickname: str
    photo: str = ""
    avatar_emoji: Optional[str] = None
    is_verified: bool = False
    is_admin: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Создаёт User из словаря."""
        return cls(
            id=data.get("id", 0),
            username=data.get("username", ""),
            nickname=data.get("nickname", ""),
            photo=data.get("photo", "") or "",
            avatar_emoji=data.get("avatar_emoji"),
            is_verified=data.get("is_verified", False),
            is_admin=data.get("is_admin", False)
        )

    def __str__(self) -> str:
        verified = " ✅" if self.is_verified else ""
        admin = " 👑" if self.is_admin else ""
        return f"User(id={self.id}, username='{self.username}', nickname='{self.nickname}'{verified}{admin})"

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class Reaction:
    """
    Датакласс для реакции на сообщение.

    Attributes:
        emoji: Эмодзи реакции
        count: Количество реакций
        user_ids: Список ID пользователей, поставивших реакцию
    """
    emoji: str
    count: int
    user_ids: List[int] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Reaction":
        """Создаёт Reaction из словаря."""
        return cls(
            emoji=data.get("emoji", ""),
            count=data.get("count", 0),
            user_ids=data.get("user_ids", [])
        )


# В классе Message добавляем поле account и методы:

@dataclass
class Message:
    id: int
    sender: User
    receiver: User
    text: str = ""
    image: Optional[str] = None
    is_read: bool = False
    read_at: Optional[str] = None
    edited_at: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    reactions: List[Reaction] = field(default_factory=list)
    account: Optional["Account"] = None  # Ссылка на аккаунт

    @classmethod
    def from_dict(cls, data: Dict[str, Any], sender: User, receiver: User,
                  account: Optional["Account"] = None) -> "Message":
        reactions_data = data.get("reactions", [])
        reactions = [Reaction.from_dict(r) for r in reactions_data] if isinstance(reactions_data, list) else []

        return cls(
            id=data.get("id", 0),
            sender=sender,
            receiver=receiver,
            text=data.get("message", ""),
            image=data.get("image"),
            is_read=data.get("is_read", False),
            read_at=data.get("read_at"),
            edited_at=data.get("edited_at"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            reactions=reactions,
            account=account
        )

    def __str__(self) -> str:
        return f"Message(id={self.id}, from={self.sender.username}, text='{self.text[:50]}...')"

    def __repr__(self) -> str:
        return self.__str__()

    def is_edited(self) -> bool:
        return self.edited_at is not None and self.edited_at != ""

    def has_reaction(self, emoji: str) -> bool:
        return any(r.emoji == emoji for r in self.reactions)

    def get_reaction_count(self, emoji: str) -> int:
        for reaction in self.reactions:
            if reaction.emoji == emoji:
                return reaction.count
        return 0

    # === Методы для работы с сообщением ===

    def _ensure_account(self) -> bool:
        """Проверяет наличие аккаунта."""
        if not self.account:
            raise MessageError("Для выполнения этой операции требуется Account")
        if not self.account.token:
            raise MessageError("Account не авторизован")
        return True

    def edit_text(self, new_text: str) -> Optional["Message"]:
        """
        Редактирует текст сообщения.

        Args:
            new_text: Новый текст сообщения

        Returns:
            Обновлённый Message или None при ошибке

        Raises:
            MessageError: Если нет связи с Account
        """
        self._ensure_account()

        if self.sender.id != self.account.id:
            raise MessageEditError("Вы можете редактировать только свои сообщения")

        return self.account.edit_message_text(self, new_text)

    def delete(self) -> bool:
        """
        Удаляет сообщение.

        Returns:
            True при успехе

        Raises:
            MessageError: Если нет связи с Account
        """
        self._ensure_account()

        # if self.sender.id != self.account.id:
        #     raise MessageDeleteError("Вы можете удалять только свои сообщения")

        return self.account.delete_message(self)

    def toggle_reaction(self, emoji: str) -> List[Reaction]:
        """
        Переключает реакцию на сообщении.

        Args:
            emoji: Эмодзи реакции

        Returns:
            Список реакций после изменения

        Raises:
            MessageError: Если нет связи с Account
        """
        self._ensure_account()
        return self.account.toggle_message_reaction(self, emoji)


@dataclass
class Project:
    """
    Датакласс для проекта.

    Attributes:
        id: ID проекта
        title: Название проекта
        description: Описание проекта
        image: Путь к изображению
        button_text: Текст кнопки
        link: Ссылка на проект
        order: Порядок сортировки
        is_active: Активен ли проект
        created_at: Дата создания
        updated_at: Дата обновления
    """
    id: int
    title: str
    description: str
    image: Optional[str] = None
    button_text: str = ""
    link: str = ""
    order: int = 0
    is_active: bool = True
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        """Создаёт Project из словаря."""
        return cls(
            id=data.get("id", 0),
            title=data.get("title", ""),
            description=data.get("description", ""),
            image=data.get("image"),
            button_text=data.get("button_text", ""),
            link=data.get("link", ""),
            order=data.get("order", 0),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", "")
        )

    def __str__(self) -> str:
        return f"Project(id={self.id}, title='{self.title}')"

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class Member:
    """
    Датакласс для участника (создателя сайта).

    Attributes:
        id: ID участника
        nickname: Никнейм участника
        photo: Путь к фото
        group: Группа/роль участника
        telegram: Ссылка на Telegram
        itd: Ссылка на ITD
        order: Порядок сортировки
        is_active: Активен ли участник
        created_at: Дата создания
        updated_at: Дата обновления
    """
    id: int
    nickname: str
    photo: Optional[str] = None
    group: str = ""
    telegram: str = ""
    itd: str = ""
    order: int = 0
    is_active: bool = True
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Member":
        """Создаёт Member из словаря."""
        return cls(
            id=data.get("id", 0),
            nickname=data.get("nickname", ""),
            photo=data.get("photo"),
            group=data.get("group", ""),
            telegram=data.get("telegram", ""),
            itd=data.get("itd", ""),
            order=data.get("order", 0),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", "")
        )

    def __str__(self) -> str:
        return f"Member(id={self.id}, nickname='{self.nickname}', group='{self.group}')"

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class News:
    """
    Датакласс для новости.

    Attributes:
        id: ID новости
        title: Заголовок новости
        subtitle: Подзаголовок
        image: Путь к изображению
        content: Содержание новости
        is_published: Опубликована ли
        views: Количество просмотров
        created_at: Дата создания
        updated_at: Дата обновления
    """
    id: int
    title: str
    content: str
    subtitle: Optional[str] = None
    image: Optional[str] = None
    is_published: bool = True
    views: int = 0
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "News":
        """Создаёт News из словаря."""
        return cls(
            id=data.get("id", 0),
            title=data.get("title", ""),
            content=data.get("content", ""),
            subtitle=data.get("subtitle"),
            image=data.get("image"),
            is_published=data.get("is_published", True),
            views=data.get("views", 0),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", "")
        )

    def __str__(self) -> str:
        return f"News(id={self.id}, title='{self.title}')"

    def __repr__(self) -> str:
        return self.__str__()


# ============================================================================
# УТИЛИТЫ (вне классов, для независимого использования)
# ============================================================================

def load_accounts(filepath: str = DEFAULT_ACCOUNTS_FILE, active_only: bool = True) -> List["Account"]:
    """
    Загружает аккаунты из JSON файла.

    Args:
        filepath: Путь к файлу
        active_only: Только активные

    Returns:
        Список объектов Account
    """
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        accounts = []
        for acc_data in data:
            # Создаём Account с упрощённой инициализацией
            account = Account(
                token=acc_data.get("token", ""),
                email=acc_data.get("email", ""),
                password=acc_data.get("password", ""),
                base_url=DEFAULT_BASE_URL,
                accounts_file=filepath
            )

            # Обновляем данные из сохранённых
            if not account.username and acc_data.get("username"):
                account.username = acc_data.get("username", "")
            if not account.nickname and acc_data.get("nickname"):
                account.nickname = acc_data.get("nickname", "")
            if not account.id and acc_data.get("user_id"):
                account.id = acc_data.get("user_id", 0)
            if acc_data.get("avatar"):
                account.avatar = acc_data.get("avatar", "")
            if acc_data.get("bio"):
                account.bio = acc_data.get("bio", "")
            if acc_data.get("avatar_emoji"):
                account.avatar_emoji = acc_data.get("avatar_emoji")
            if acc_data.get("profile_public"):
                account.profile_public = acc_data.get("profile_public", True)
            if acc_data.get("show_online"):
                account.show_online = acc_data.get("show_online", True)
            if acc_data.get("allow_messages"):
                account.allow_messages = acc_data.get("allow_messages", True)
            if acc_data.get("show_in_search"):
                account.show_in_search = acc_data.get("show_in_search", True)
            if acc_data.get("is_admin"):
                account.is_admin = acc_data.get("is_admin", False)
            if acc_data.get("is_verified"):
                account.is_verified = acc_data.get("is_verified", False)
            if acc_data.get("theme"):
                account.theme = acc_data.get("theme", "dark")
            if acc_data.get("created_at"):
                account.created_at = acc_data.get("created_at", "")
            if acc_data.get("updated_at"):
                account.updated_at = acc_data.get("updated_at")
            account.active = acc_data.get("active", True)

            accounts.append(account)

        if active_only:
            accounts = [acc for acc in accounts if acc.active]

        return accounts

    except (json.JSONDecodeError, IOError):
        return []


def save_accounts(accounts: List["Account"], filepath: str = DEFAULT_ACCOUNTS_FILE) -> bool:
    """
    Сохраняет список аккаунтов в JSON файл.

    Args:
        accounts: Список аккаунтов
        filepath: Путь к файлу

    Returns:
        True если успешно
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(
                [acc.to_dict() for acc in accounts],
                f,
                indent=4,
                ensure_ascii=False
            )
        return True
    except IOError:
        return False


def get_active_accounts(accounts: List["Account"]) -> List["Account"]:
    """
    Возвращает только активные аккаунты.
    """
    return [acc for acc in accounts if acc.active]


def clean_accounts_file(
        filepath: str = DEFAULT_ACCOUNTS_FILE,
        create_backup: bool = True
) -> Tuple[int, str]:
    """
    Удаляет неактивные аккаунты из файла.

    Args:
        filepath: Путь к файлу
        create_backup: Создавать ли бэкап

    Returns:
        Кортеж (удалено, путь_к_бэкапу)
    """
    accounts = load_accounts(filepath, active_only=False)

    if not accounts:
        return 0, ""

    active_accounts = get_active_accounts(accounts)
    deleted_count = len(accounts) - len(active_accounts)

    if deleted_count == 0:
        return 0, ""

    backup_path = ""

    if create_backup:
        backup_path = filepath.replace(".json", "_backup.json")
        save_accounts(accounts, backup_path)

    save_accounts(active_accounts, filepath)

    return deleted_count, backup_path


def parse_wait_time(response_text: str) -> Optional[int]:
    """
    Извлекает время ожидания из ответа сервера.
    """
    patterns = [
        r'подожди(?:те)?\s*(\d+)',
        r'wait\s*(\d+)',
        r'retry_after["\']?\s*:\s*(\d+)',
        r'timeout["\']?\s*:\s*(\d+)',
        r'(\d+)\s*секунд',
    ]

    for pattern in patterns:
        match = re.search(pattern, response_text, re.IGNORECASE)
        if match:
            return int(match.group(1))

    return None


# ============================================================================
# KAALITION CLIENT (операции без авторизации)
# ============================================================================

class KaalitionClient:
    """
    Клиент для работы с API kaalition.ru.

    Используется для операций без авторизации:
    - Регистрация новых аккаунтов
    - Вход в существующие аккаунты
    - Получение публичных данных (проекты, участники, новости)
    """

    def __init__(
            self,
            base_url: str = DEFAULT_BASE_URL,
            accounts_file: str = DEFAULT_ACCOUNTS_FILE,
            user_agent: str = DEFAULT_USER_AGENT
    ):
        self.base_url = base_url.rstrip("/")
        self.accounts_file = accounts_file

        self.faker_ru = Faker("ru_RU")
        self.faker_en = Faker()

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept": "application/json",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "X-Requested-With": "XMLHttpRequest",
        })

        # URLs
        self._register_url = f"{self.base_url}/api/auth/register"
        self._login_url = f"{self.base_url}/api/auth/login"
        self._me_url = f"{self.base_url}/api/auth/me"
        self._profile_url = f"{self.base_url}/api/user/profile"
        self._support_url = f"{self.base_url}/api/support"
        self._support_chat_url = f"{self.base_url}/api/support/chat"
        self._search_users_url = f"{self.base_url}/api/messages/search/users"
        self._send_message_url = f"{self.base_url}/api/messages/send"

        # Новые URL (без авторизации)
        self._projects_url = f"{self.base_url}/api/projects"
        self._members_url = f"{self.base_url}/api/members"
        self._news_url = f"{self.base_url}/api/news"

        # URLs для работы с сообщениями
        self._chat_history_url = f"{self.base_url}/api/messages"
        self._message_edit_url = f"{self.base_url}/api/messages"
        self._message_delete_url = f"{self.base_url}/api/messages"
        self._message_react_url = f"{self.base_url}/api/messages"

    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _generate_password(self) -> str:
        return self.faker_en.password(
            length=12,
            special_chars=True,
            digits=True,
            upper_case=True
        )

    def _get_error_message(self, response: requests.Response) -> str:
        """Извлекает сообщение об ошибке из ответа."""
        try:
            resp_data = response.json()
            return resp_data.get("message", str(resp_data))
        except:
            return response.text[:200] if response.text else "Unknown error"

    def get_projects(self) -> List[Project]:
        """
        Получает список всех проектов.

        Отправляет GET на /api/projects

        Returns:
            Список проектов (Project dataclass)

        Example:
            client = KaalitionClient()
            projects = client.get_projects()
            for project in projects:
                print(f"{project.title}: {project.link}")
        """
        try:
            response = self.session.get(
                self._projects_url,
                headers=self._get_headers(),
                timeout=10
            )

            if not response.ok:
                return []

            projects_data = response.json()

            if isinstance(projects_data, list):
                return [Project.from_dict(data) for data in projects_data]

            return []

        except requests.exceptions.RequestException:
            return []

    def get_members(self) -> List[Member]:
        """
        Получает список всех участников (создателей сайта).

        Отправляет GET на /api/members

        Returns:
            Список участников (Member dataclass)

        Example:
            client = KaalitionClient()
            members = client.get_members()
            for member in members:
                print(f"{member.nickname} ({member.group})")
        """
        try:
            response = self.session.get(
                self._members_url,
                headers=self._get_headers(),
                timeout=10
            )

            if not response.ok:
                return []

            members_data = response.json()

            if isinstance(members_data, list):
                return [Member.from_dict(data) for data in members_data]

            return []

        except requests.exceptions.RequestException:
            return []

    def get_news(self) -> List[News]:
        """
        Получает список всех новостей сайта.

        Отправляет GET на /api/news

        Returns:
            Список новостей (News dataclass)

        Example:
            client = KaalitionClient()
            news = client.get_news()
            for item in news:
                print(f"{item.title}: {item.content[:100]}...")
        """
        try:
            response = self.session.get(
                self._news_url,
                headers=self._get_headers(),
                timeout=10
            )

            if not response.ok:
                return []

            news_data = response.json()

            if isinstance(news_data, list):
                return [News.from_dict(data) for data in news_data]

            return []

        except requests.exceptions.RequestException:
            return []

    def register(
            self,
            username: Optional[str] = None,
            email: Optional[str] = None,
            password: Optional[str] = None,
            email_domains: Optional[List[str]] = None,
            save: bool = True
    ) -> "Account":
        """
        Регистрирует новый аккаунт.

        Args:
            username: Имя пользователя (опционально, генерируется автоматически)
            email: Email (опционально, генерируется автоматически)
            password: Пароль (опционально, генерируется автоматически)
            email_domains: Список доменов для генерации email
            save: Сохранять ли аккаунт в файл

        Returns:
            Объект Account с авторизацией

        Raises:
            RegistrationError: При ошибке регистрации
        """
        if username is None:
            username = self.faker_en.user_name()

        if email is None:
            if email_domains is None:
                email_domains = DEFAULT_EMAIL_DOMAINS
            local_part = self.faker_en.email().split('@')[0]
            email = f"{local_part}@{random.choice(email_domains)}"

        if password is None:
            password = self._generate_password()

        # РУССКИЙ НИКнейм вместо английского
        nickname = self.faker_ru.name()

        payload = {
            "username": username,
            "nickname": nickname,
            "email": email,
            "password": password,
            "password_confirmation": password
        }

        try:
            response = self.session.post(
                self._register_url,
                json=payload,
                headers=self._get_headers(),
                timeout=10
            )

            if not response.ok:
                error_msg = self._get_error_message(response)
                raise RegistrationError(f"Код {response.status_code}: {error_msg}")

            resp_data = response.json()
            token = resp_data.get("token") or resp_data.get("access_token")

            if not token:
                raise RegistrationError(f"Токен не получен: {resp_data}")

            # Создаём Account с автоматическим заполнением данных через refresh
            account = Account(
                token=token,
                password=password,
                base_url=self.base_url,
                accounts_file=self.accounts_file
            )

            # Синхронизируем данные с сервером
            account.refresh()

            if save:
                account.save()

            return account

        except requests.exceptions.RequestException as e:
            raise RegistrationError(f"Ошибка сети: {e}")

    def login(
            self,
            email: str,
            password: str,
            save: bool = True
    ) -> "Account":
        """
        Вход в существующий аккаунт.

        Args:
            email: Email пользователя
            password: Пароль пользователя
            save: Сохранять ли аккаунт в файл

        Returns:
            Объект Account с авторизацией

        Raises:
            LoginError: При ошибке входа
        """
        payload = {
            "email": email,
            "password": password
        }

        try:
            response = self.session.post(
                self._login_url,
                json=payload,
                headers=self._get_headers(),
                timeout=10
            )

            if not response.ok:
                error_msg = self._get_error_message(response)
                raise LoginError(f"Код {response.status_code}: {error_msg}")

            resp_data = response.json()

            token = resp_data.get("token") or resp_data.get("access_token")
            if not token:
                raise LoginError(f"Токен не получен: {resp_data}")

            # Создаём Account с автоматическим заполнением данных
            account = Account(
                token=token,
                email=email,
                password=password,
                base_url=self.base_url,
                accounts_file=self.accounts_file
            )

            # Синхронизируем данные с сервером
            account.refresh()

            if save:
                account.save()

            return account

        except requests.exceptions.RequestException as e:
            raise LoginError(f"Ошибка сети: {e}")

    def create_from_token(
            self,
            token: str,
            save: bool = True
    ) -> "Account":
        """
        Создаёт Account из существующего токена.

        Args:
            token: Bearer токен
            save: Сохранять ли аккаунт в файл

        Returns:
            Объект Account с авторизацией

        Raises:
            TokenError: При ошибке валидации токена
        """
        try:
            response = self.session.get(
                self._me_url,
                headers=self._get_headers(token),
                timeout=10
            )

            if not response.ok:
                error_msg = self._get_error_message(response)
                raise TokenError(f"Код {response.status_code}: {error_msg}")

            user_data = response.json()

            if "id" not in user_data:
                raise TokenError(f"ID пользователя не получен: {user_data}")

            # Создаём Account с автоматическим заполнением данных
            account = Account(
                token=token,
                base_url=self.base_url,
                accounts_file=self.accounts_file
            )

            # Синхронизируем данные с сервером
            account.refresh()

            if save:
                account.save()

            return account

        except requests.exceptions.RequestException as e:
            raise TokenError(f"Ошибка сети: {e}")

    def load_accounts(self, active_only: bool = True) -> List["Account"]:
        """
        Загружает сохранённые аккаунты из файла.

        Args:
            active_only: Только активные аккаунты

        Returns:
            Список объектов Account
        """
        return load_accounts(self.accounts_file, active_only)

    def clean_inactive(self, create_backup: bool = True) -> Tuple[int, str]:
        """
        Удаляет неактивные аккаунты из файла.

        Args:
            create_backup: Создавать ли бэкап

        Returns:
            Кортеж (количество удалённых, путь к бэкапу)
        """
        return clean_accounts_file(self.accounts_file, create_backup)


# ============================================================================
# ACCOUNT (операции с авторизацией)
# ============================================================================

class Account(KaalitionClient, User):
    """
    Аккаунт пользователя с авторизацией.

    Наследуется от KaalitionClient и User для избежания дублирования полей.
    Предоставляет полный доступ к API с авторизацией.

    Создаётся через:
    - KaalitionClient.register() - регистрация
    - KaalitionClient.login() - вход
    - KaalitionClient.create_from_token() - из токена
    - load_accounts() - загрузка из файла

    Attributes:
        token: Bearer токен авторизации
        password: Пароль (для сохранения)
        active: Активен ли аккаунт
        created_at: Дата создания записи
        updated_at: Дата последнего обновления
    """

    def __init__(
            self,
            token: str = "",
            email: str = "",
            password: str = "",
            base_url: str = DEFAULT_BASE_URL,
            accounts_file: str = DEFAULT_ACCOUNTS_FILE
    ):
        # Инициализация родительских классов
        KaalitionClient.__init__(self, base_url=base_url, accounts_file=accounts_file)

        # Инициализация всех полей User вручную
        self.id: int = 0
        self.username: str = ""
        self.nickname: str = ""
        self.photo: str = ""
        self.avatar_emoji: Optional[str] = None
        self.is_verified: bool = False
        self.is_admin: bool = False

        # Дополнительные поля профиля
        self.email: str = email
        self.bio: str = ""
        self.avatar: str = ""
        self.profile_public: bool = True
        self.show_online: bool = True
        self.allow_messages: bool = True
        self.show_in_search: bool = True
        self.theme: str = "dark"

        # Основные поля авторизации
        self.token = token
        self.password = password
        self.active = True
        self.created_at = datetime.now().isoformat()
        self.updated_at = None

        # Если передан email, сохраняем для возможности повторного входа
        self._login_email = email

        # Если есть токен, синхронизируем данные с сервером
        if self.token:
            self.refresh()
            self.refresh()

    def _ensure_authenticated(self) -> bool:
        """
        Проверяет наличие токена и авторизации.

        Returns:
            True если авторизован
        """
        if not self.token:
            return False
        return self.active

    def _get_current_user_sender(self) -> User:
        """
        Возвращает объект User для текущего аккаунта (для создания Message).

        Returns:
            Объект User с данными текущего аккаунта
        """
        return User(
            id=self.id,
            username=self.username,
            nickname=self.nickname,
            photo=self.avatar or "",
            avatar_emoji=self.avatar_emoji,
            is_verified=self.is_verified,
            is_admin=self.is_admin
        )

    def refresh(self) -> bool:
        """
        Синхронизирует данные аккаунта с сервером.

        Returns:
            True при успехе
        """
        if not self.token:
            return False

        try:
            response = self.session.get(
                self._me_url,
                headers=self._get_headers(self.token),
                timeout=10
            )

            if not response.ok:
                if response.status_code == 401:
                    self.active = False
                    self.save()
                return False

            user_data = response.json()
            self._update_from_user_data(user_data)
            return True

        except requests.exceptions.RequestException:
            return False

    def _update_from_user_data(self, user_data: Dict[str, Any]):
        """
        Обновляет данные аккаунта из ответа сервера.

        Args:
            user_data: Данные пользователя от сервера
        """
        # Обновляем поля из User (родительский класс)
        self.id = user_data.get("id", self.id)
        self.username = user_data.get("username", self.username)
        self.nickname = user_data.get("nickname", self.nickname)
        self.avatar = user_data.get("photo", self.avatar or "")
        self.avatar_emoji = user_data.get("avatar_emoji", self.avatar_emoji)
        self.is_verified = user_data.get("is_verified", self.is_verified)
        self.is_admin = user_data.get("is_admin", self.is_admin)

        # Обновляем дополнительные поля
        self.email = user_data.get("email", getattr(self, 'email', ""))
        self.bio = user_data.get("bio", getattr(self, 'bio', ""))
        self.profile_public = user_data.get("profile_public", getattr(self, 'profile_public', True))
        self.show_online = user_data.get("show_online", getattr(self, 'show_online', True))
        self.allow_messages = user_data.get("allow_messages", getattr(self, 'allow_messages', True))
        self.show_in_search = user_data.get("show_in_search", getattr(self, 'show_in_search', True))
        self.theme = user_data.get("theme", getattr(self, 'theme', "dark"))
        self.updated_at = user_data.get("updated_at", self.updated_at)

    def save(self) -> bool:
        """
        Сохраняет аккаунт в файл.

        Returns:
            True при успехе
        """
        accounts = load_accounts(self.accounts_file, active_only=False)

        # Проверяем, существует ли уже этот аккаунт
        for i, acc in enumerate(accounts):
            if acc.username == self.username or (self.email and acc.email == self.email):
                accounts[i] = self
                break
        else:
            accounts.append(self)

        return save_accounts(accounts, self.accounts_file)

    def mark_inactive(self) -> bool:
        """
        Помечает аккаунт как неактивный.

        Returns:
            True при успехе
        """
        self.active = False
        return self.save()

    def is_active(self) -> bool:
        """
        Проверяет активность аккаунта.

        Returns:
            True если активен
        """
        if not self.token:
            self.active = False
            return False

        try:
            response = self.session.get(
                self._me_url,
                headers=self._get_headers(self.token),
                timeout=10
            )

            if response.status_code == 401:
                self.active = False
                self.save()
                return False

            self.active = True
            return True

        except requests.exceptions.RequestException:
            return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token": self.token,
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "active": self.active,
            "nickname": self.nickname,
            "user_id": self.id,
            "avatar": self.avatar,
            "bio": self.bio,
            "avatar_emoji": self.avatar_emoji,
            "profile_public": self.profile_public,
            "show_online": self.show_online,
            "allow_messages": self.allow_messages,
            "show_in_search": self.show_in_search,
            "is_admin": self.is_admin,
            "is_verified": self.is_verified,
            "theme": self.theme,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    # =========================================================================
    # МЕТОДЫ ПРОФИЛЯ
    # =========================================================================

    def update_profile(
            self,
            nickname: Optional[str] = None,
            username: Optional[str] = None,
            bio: Optional[str] = None,
            avatar_emoji: Optional[str] = None,
            save_after: bool = True
    ) -> bool:
        """
        Обновляет профиль пользователя.

        Args:
            nickname: Новый отображаемый никнейм
            username: Новое имя пользователя
            bio: Новая биография
            avatar_emoji: Новый эмодзи аватара
            save_after: Сохранить после обновления

        Returns:
            True при успехе
        """
        if not self._ensure_authenticated():
            return False

        data = {
            "nickname": nickname if nickname is not None else self.nickname,
            "username": username if username is not None else self.username,
            "bio": bio if bio is not None else (getattr(self, 'bio', "") or ""),
            "avatar_emoji": avatar_emoji if avatar_emoji is not None else (self.avatar_emoji or ""),
            "_method": "PUT"
        }

        try:
            response = self.session.post(
                self._profile_url,
                data=data,
                headers=self._get_headers(self.token),
                timeout=10
            )

            if not response.ok:
                return False

            resp_data = response.json()
            if "user" in resp_data:
                self._update_from_user_data(resp_data["user"])
            else:
                self._update_from_user_data(resp_data)

            self.updated_at = datetime.now().isoformat()

            if save_after:
                self.save()

            return True

        except requests.exceptions.RequestException:
            return False

    # =========================================================================
    # МЕТОДЫ ПОИСКА ПОЛЬЗОВАТЕЛЕЙ
    # =========================================================================

    def search_users(self, query: str) -> List[User]:
        """
        Ищет пользователей по запросу.

        Args:
            query: Поисковый запрос

        Returns:
            Список найденных пользователей
        """
        if not self._ensure_authenticated():
            return []

        try:
            url = f"{self._search_users_url}?query={query}"
            response = self.session.get(
                url,
                headers=self._get_headers(self.token),
                timeout=10
            )

            if not response.ok:
                return []

            users_data = response.json()

            if isinstance(users_data, list):
                return [User.from_dict(user_data) for user_data in users_data]

            return []

        except requests.exceptions.RequestException:
            return []

    # =========================================================================
    # МЕТОДЫ СООБЩЕНИЙ
    # =========================================================================

    # В методе send_message класса Account обновляем создание Message:

    def send_message(self, user: User, text: str) -> Optional[Message]:
        if not self._ensure_authenticated():
            return None

        payload = {
            "receiver_id": user.id,
            "message": text
        }

        try:
            response = self.session.post(
                self._send_message_url,
                json=payload,
                headers=self._get_headers(self.token),
                timeout=10
            )

            if not response.ok:
                if response.status_code == 401:
                    self.mark_inactive()
                return None

            resp_data = response.json()

            sender = self._get_current_user_sender()
            receiver = User(
                id=user.id,
                username=user.username,
                nickname=user.nickname,
                photo=user.photo,
                avatar_emoji=user.avatar_emoji,
                is_verified=user.is_verified,
                is_admin=user.is_admin
            )

            # Передаём self (account) в Message
            message = Message.from_dict(resp_data, sender=sender, receiver=receiver, account=self)

            return message

        except requests.exceptions.RequestException:
            return None

    # В методе get_chat_history класса Account обновляем создание Message:

    def get_chat_history(self, user: User) -> List[Message]:
        if not self._ensure_authenticated():
            raise ChatHistoryError("Не авторизован")

        try:
            url = f"{self._chat_history_url}/{user.id}"
            response = self.session.get(
                url,
                headers=self._get_headers(self.token),
                timeout=10
            )

            if not response.ok:
                if response.status_code == 401:
                    self.mark_inactive()
                    raise ChatHistoryError("Сессия истекла")
                raise ChatHistoryError(f"Ошибка сервера: {response.status_code}")

            messages_data = response.json()

            if not isinstance(messages_data, list):
                return []

            current_user = self._get_current_user_sender()
            target_user = User(
                id=user.id,
                username=user.username,
                nickname=user.nickname,
                photo=user.photo,
                avatar_emoji=user.avatar_emoji,
                is_verified=user.is_verified,
                is_admin=user.is_admin
            )

            messages = []
            for msg_data in messages_data:
                sender_data = msg_data.get("sender", {})
                sender_id = msg_data.get("sender_id")

                if sender_data:
                    sender = User.from_dict(sender_data)
                else:
                    sender = User(id=sender_id, username="", nickname="")

                if msg_data.get("receiver_id") == self.id:
                    receiver = current_user
                else:
                    receiver = target_user

                # Передаём self (account) в Message
                message = Message.from_dict(msg_data, sender=sender, receiver=receiver, account=self)
                messages.append(message)

            messages.sort(key=lambda m: m.created_at)
            return messages

        except requests.exceptions.RequestException as e:
            raise ChatHistoryError(f"Ошибка сети: {e}")

    def edit_message_text(
            self,
            message: Message,
            new_text: str
    ) -> Optional[Message]:
        """
        Редактирует текст сообщения.

        Args:
            message: Сообщение для редактирования
            new_text: Новый текст сообщения

        Returns:
            Обновлённый Message при успехе, None при ошибке

        Raises:
            MessageEditError: При ошибке редактирования
        """
        if not self._ensure_authenticated():
            raise MessageEditError("Не авторизован")

        # Проверяем, что пользователь является отправителем
        if message.sender.id != self.id:
            raise MessageEditError("Вы можете редактировать только свои сообщения")

        try:
            url = f"{self._message_edit_url}/{message.id}/edit"
            payload = {"message": new_text}

            response = self.session.put(
                url,
                json=payload,
                headers=self._get_headers(self.token),
                timeout=10
            )

            if not response.ok:
                if response.status_code == 401:
                    self.mark_inactive()
                    raise MessageEditError("Сессия истекла")
                raise MessageEditError(f"Ошибка сервера: {response.status_code}")

            resp_data = response.json()

            # Обновляем сообщение
            message.text = resp_data.get("message", new_text)
            message.edited_at = resp_data.get("edited_at", datetime.now().isoformat())
            message.updated_at = resp_data.get("updated_at", message.updated_at)

            # Обновляем реакции, если они есть
            reactions_data = resp_data.get("reactions", [])
            if isinstance(reactions_data, list):
                message.reactions = [Reaction.from_dict(r) for r in reactions_data]

            return message

        except requests.exceptions.RequestException as e:
            raise MessageEditError(f"Ошибка сети: {e}")

    def delete_message(self, message: Message) -> bool:
        """
        Удаляет сообщение.

        Args:
            message: Сообщение для удаления

        Returns:
            True при успехе

        Raises:
            MessageDeleteError: При ошибке удаления
        """
        if not self._ensure_authenticated():
            raise MessageDeleteError("Не авторизован")

        # Проверяем, что пользователь является отправителем
        # if message.sender.id != self.id:
        #     raise MessageDeleteError("Вы можете удалять только свои сообщения")

        try:
            url = f"{self._message_delete_url}/{message.id}"

            response = self.session.delete(
                url,
                headers=self._get_headers(self.token),
                timeout=10
            )

            if not response.ok:
                if response.status_code == 401:
                    self.mark_inactive()
                    raise MessageDeleteError("Сессия истекла")
                raise MessageDeleteError(f"Ошибка сервера: {response.status_code}")

            return True

        except requests.exceptions.RequestException as e:
            raise MessageDeleteError(f"Ошибка сети: {e}")

    def toggle_message_reaction(
            self,
            message: Message,
            emoji: str
    ) -> List[Reaction]:
        """
        Переключает реакцию на сообщении.

        Args:
            message: Сообщение для реакции
            emoji: Эмодзи реакции

        Returns:
            Список реакций после изменения

        Raises:
            MessageReactionError: При ошибке установки реакции
        """
        if not self._ensure_authenticated():
            raise MessageReactionError("Не авторизован")

        try:
            url = f"{self._message_react_url}/{message.id}/react"
            payload = {"emoji": emoji}

            response = self.session.post(
                url,
                json=payload,
                headers=self._get_headers(self.token),
                timeout=10
            )

            if not response.ok:
                if response.status_code == 401:
                    self.mark_inactive()
                    raise MessageReactionError("Сессия истекла")
                raise MessageReactionError(f"Ошибка сервера: {response.status_code}")

            resp_data = response.json()

            # Обновляем реакции в сообщении
            reactions_data = resp_data.get("reactions", [])
            if isinstance(reactions_data, list):
                message.reactions = [Reaction.from_dict(r) for r in reactions_data]

            return message.reactions

        except requests.exceptions.RequestException as e:
            raise MessageReactionError(f"Ошибка сети: {e}")

        # =========================================================================
        # МЕТОДЫ ПОДДЕРЖКИ
        # =========================================================================

    def create_support_ticket(
            self,
            subject: str = "Обращение",
            message: Optional[str] = None
    ) -> Tuple[bool, Optional[int], str]:
        """
        Создаёт тикет поддержки.

        Args:
            subject: Тема обращения
            message: Текст обращения (опционально, сгенерируется автоматически)

        Returns:
            Кортеж (успех, ID тикета, статус)
        """
        if not self._ensure_authenticated():
            return False, None, "no_token"

        if message is None:
            message = self.faker_ru.text(max_nb_chars=200)

        payload = {
            "subject": subject,
            "message": message
        }

        try:
            response = self.session.post(
                self._support_url,
                json=payload,
                headers=self._get_headers(self.token),
                timeout=10
            )

            if response.ok:
                return True, None, "success"
            elif response.status_code == 401:
                self.mark_inactive()
                return False, None, "unauthorized"
            else:
                wait_time = parse_wait_time(response.text)
                return False, wait_time, f"error_{response.status_code}"

        except requests.exceptions.RequestException:
            return False, None, "exception"

    def send_to_support(
            self,
            message: str,
            subject: str = "Обращение"
    ) -> Tuple[bool, str]:
        """
        Отправляет сообщение в поддержку.

        Сначала проверяет существующий чат поддержки.
        Если тикет существует — продолжает его.
        Если нет — создаёт новый.

        Args:
            message: Текст сообщения
            subject: Тема для нового тикета

        Returns:
            Кортеж (успех, статус)
        """
        if not self._ensure_authenticated():
            return False, "no_token"

        try:
            # Проверяем существующий чат
            response = self.session.get(
                self._support_chat_url,
                headers=self._get_headers(self.token),
                timeout=10
            )

            if response.status_code == 401:
                self.mark_inactive()
                return False, "unauthorized"

            if response.ok:
                chat_data = response.json()
                ticket_id = chat_data.get("ticket")

                if ticket_id:
                    # Продолжаем существующий тикет
                    return self._send_to_existing_ticket(ticket_id, message)
                else:
                    # Создаём новый тикет
                    return self._create_new_ticket(subject, message)

            return False, f"error_{response.status_code}"

        except requests.exceptions.RequestException:
            return False, "exception"

    def _send_to_existing_ticket(
            self,
            ticket_id: int,
            message: str
    ) -> Tuple[bool, str]:
        """
        Отправляет сообщение в существующий тикет.

        Args:
            ticket_id: ID тикета
            message: Текст сообщения

        Returns:
            Кортеж (успех, статус)
        """
        try:
            url = f"{self._support_url}/{ticket_id}/message"
            payload = {"message": message}

            response = self.session.post(
                url,
                json=payload,
                headers=self._get_headers(self.token),
                timeout=10
            )

            if response.ok:
                return True, "success"
            elif response.status_code == 401:
                self.mark_inactive()
                return False, "unauthorized"
            else:
                return False, f"error_{response.status_code}"

        except requests.exceptions.RequestException:
            return False, "exception"

    def _create_new_ticket(
            self,
            subject: str,
            message: str
    ) -> Tuple[bool, str]:
        """
        Создаёт новый тикет поддержки.

        Args:
            subject: Тема тикета
            message: Текст сообщения

        Returns:
            Кортеж (успех, статус)
        """
        try:
            payload = {
                "subject": subject,
                "message": message
            }

            response = self.session.post(
                self._support_url,
                json=payload,
                headers=self._get_headers(self.token),
                timeout=10
            )

            if response.ok:
                return True, "created"
            elif response.status_code == 401:
                self.mark_inactive()
                return False, "unauthorized"
            else:
                return False, f"error_{response.status_code}"

        except requests.exceptions.RequestException:
            return False, "exception"

    def __repr__(self) -> str:
        status = "active" if self.active else "inactive"
        return f"Account(username='{self.username}', status={status})"

    # ============================================================================
    # МЕТОДЫ КЛАССА MESSAGE (для удобного управления сообщениями)
    # ============================================================================

    def _get_account_for_message(message: "Message") -> Optional["Account"]:
        """
        Вспомогательная функция для получения Account из Message.
        Требуется для методов edit_text, delete, toggle_reaction.

        Args:
            message: Сообщение

        Returns:
            Объект Account или None
        """
        # Пытаемся найти аккаунт в глобальном контексте
        # Это упрощённая реализация, в реальном использовании
        # рекомендуется вызывать методы через Account
        return None

    # ============================================================================
    # КОНЕЦ БИБЛИОТЕКИ
    # ============================================================================
