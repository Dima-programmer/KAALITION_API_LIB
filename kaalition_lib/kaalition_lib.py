"""
Kaalition.ru API Library
========================

Библиотека для работы с API сайта kaalition.ru.

Структура:
- KaalitionClient: Клиент для операций без авторизации (регистрация, логин, загрузка)
- Account: Унаследованный класс с данными аккаунта и методами с авторизацией
- User: Датакласс для найденных пользователей

Пример использования:

    from kaalition_lib import KaalitionClient

    # Регистрация нового аккаунта
    client = KaalitionClient()
    account = client.register()

    # Поиск пользователей
    users = account.search_users("никнейм")

    # Отправка сообщения пользователю
    if users:
        account.send_message(users[0], "Привет!")

    # Создание тикета поддержки
    account.create_support_ticket("Вопрос", "Текст вопроса")
"""

import requests
import json
import os
import re
import time
import random
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
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
    """Ошибка отправки сообщения."""
    pass


# ============================================================================
# DATACLASSES
# ============================================================================

@dataclass
class User:
    """
    Датакласс для найденного пользователя.

    Attributes:
        id: ID пользователя
        username: Имя пользователя
        nickname: Отображаемое имя
        photo: Путь к фото
        avatar_emoji: Эмодзи аватара
        is_verified: Верифицирован ли
    """
    id: int
    username: str
    nickname: str
    photo: str = ""
    avatar_emoji: Optional[str] = None
    is_verified: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Создаёт User из словаря."""
        return cls(
            id=data.get("id", 0),
            username=data.get("username", ""),
            nickname=data.get("nickname", ""),
            photo=data.get("photo", "") or "",
            avatar_emoji=data.get("avatar_emoji"),
            is_verified=data.get("is_verified", False)
        )

    def __str__(self) -> str:
        verified = " ✅" if self.is_verified else ""
        return f"User(id={self.id}, username='{self.username}', nickname='{self.nickname}'{verified})"

    def __repr__(self) -> str:
        return self.__str__()


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
            client = KaalitionClient(accounts_file=filepath)
            account = Account(
                token=acc_data.get("token", ""),
                username=acc_data.get("username", ""),
                email=acc_data.get("email", ""),
                password=acc_data.get("password", ""),
                active=acc_data.get("active", True),
                nickname=acc_data.get("nickname", ""),
                user_id=acc_data.get("user_id"),
                avatar=acc_data.get("avatar"),
                bio=acc_data.get("bio"),
                avatar_emoji=acc_data.get("avatar_emoji"),
                profile_public=acc_data.get("profile_public", True),
                show_online=acc_data.get("show_online", True),
                allow_messages=acc_data.get("allow_messages", True),
                show_in_search=acc_data.get("show_in_search", True),
                is_admin=acc_data.get("is_admin", False),
                is_verified=acc_data.get("is_verified", False),
                theme=acc_data.get("theme", "dark"),
                base_url=client.base_url,
                accounts_file=client.accounts_file
            )
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

    # ... существующие методы register, login, create_from_token ...

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

            account = Account(
                token=token,
                username=username,
                email=email,
                password=password,
                active=True,
                nickname=nickname,
                base_url=self.base_url,
                accounts_file=self.accounts_file
            )

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

            user_data = resp_data.get("user", {})

            account = Account(
                token=token,
                username=user_data.get("username", ""),
                email=user_data.get("email", email),
                password=password,
                active=True,
                nickname=user_data.get("nickname", ""),
                user_id=user_data.get("id"),
                avatar=user_data.get("photo", ""),
                bio=user_data.get("bio", ""),
                avatar_emoji=user_data.get("avatar_emoji"),
                profile_public=user_data.get("profile_public", True),
                show_online=user_data.get("show_online", True),
                allow_messages=user_data.get("allow_messages", True),
                show_in_search=user_data.get("show_in_search", True),
                is_admin=user_data.get("is_admin", False),
                is_verified=user_data.get("is_verified", False),
                theme=user_data.get("theme", "dark"),
                base_url=self.base_url,
                accounts_file=self.accounts_file
            )

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

            account = Account(
                token=token,
                username=user_data.get("username", ""),
                email=user_data.get("email", ""),
                password="",
                active=True,
                nickname=user_data.get("nickname", ""),
                user_id=user_data.get("id"),
                avatar=user_data.get("photo", ""),
                bio=user_data.get("bio", ""),
                avatar_emoji=user_data.get("avatar_emoji"),
                profile_public=user_data.get("profile_public", True),
                show_online=user_data.get("show_online", True),
                allow_messages=user_data.get("allow_messages", True),
                show_in_search=user_data.get("show_in_search", True),
                is_admin=user_data.get("is_admin", False),
                is_verified=user_data.get("is_verified", False),
                theme=user_data.get("theme", "dark"),
                base_url=self.base_url,
                accounts_file=self.accounts_file
            )

            if save:
                account.save()

            return account

        except requests.exceptions.RequestException as e:
            raise TokenError(f"Ошибка сети: {e}")

    def load_accounts(self, active_only: bool = True) -> List["Account"]:
        return load_accounts(self.accounts_file, active_only)

    def clean_inactive(self, create_backup: bool = True) -> Tuple[int, str]:
        return clean_accounts_file(self.accounts_file, create_backup)

    def _get_error_message(self, response: requests.Response) -> str:
        try:
            resp_data = response.json()
            return resp_data.get("message", str(resp_data))
        except:
            return response.text[:200] if response.text else "Unknown error"


# ============================================================================
# ACCOUNT (операции с авторизацией)
# ============================================================================

class Account(KaalitionClient):
    """
    Аккаунт пользователя с авторизацией.

    Наследует от KaalitionClient, добавляет:
    - Хранение данных аккаунта (token, username, email, etc.)
    - Методы с авторизацией

    Создаётся через:
    - KaalitionClient.register() - регистрация
    - KaalitionClient.login() - вход
    - KaalitionClient.create_from_token() - из токена
    - load_accounts() - загрузка из файла
    """

    def __init__(
            self,
            token: str = "",
            username: str = "",
            email: str = "",
            password: str = "",
            active: bool = True,
            nickname: str = "",
            user_id: Optional[int] = None,
            avatar: str = "",
            bio: str = "",
            avatar_emoji: Optional[str] = None,
            profile_public: bool = True,
            show_online: bool = True,
            allow_messages: bool = True,
            show_in_search: bool = True,
            is_admin: bool = False,
            is_verified: bool = False,
            theme: str = "dark",
            base_url: str = DEFAULT_BASE_URL,
            accounts_file: str = DEFAULT_ACCOUNTS_FILE
    ):
        super().__init__(base_url=base_url, accounts_file=accounts_file)

        self.token = token
        self.username = username
        self.email = email
        self.password = password
        self.active = active
        self.nickname = nickname
        self.user_id = user_id
        self.avatar = avatar
        self.bio = bio
        self.avatar_emoji = avatar_emoji
        self.profile_public = profile_public
        self.show_online = show_online
        self.allow_messages = allow_messages
        self.show_in_search = show_in_search
        self.is_admin = is_admin
        self.is_verified = is_verified
        self.theme = theme
        self.created_at = datetime.now().isoformat()
        self.updated_at = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token": self.token,
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "active": self.active,
            "nickname": self.nickname,
            "user_id": self.user_id,
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

    def save(self) -> bool:
        accounts = load_accounts(self.accounts_file, active_only=False)
        for i, acc in enumerate(accounts):
            if acc.username == self.username:
                accounts[i] = self
                break
        else:
            accounts.append(self)
        return save_accounts(accounts, self.accounts_file)

    def mark_inactive(self) -> bool:
        self.active = False
        return self.save()

    def is_active(self) -> bool:
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

    def refresh(self) -> bool:
        if not self.token:
            return False
        try:
            response = self.session.get(
                self._me_url,
                headers=self._get_headers(self.token),
                timeout=10
            )
            if not response.ok:
                return False
            self._update_from_user_data(response.json())
            return True
        except requests.exceptions.RequestException:
            return False

    def _update_from_user_data(self, user_data: Dict[str, Any]):
        self.username = user_data.get("username", self.username)
        self.email = user_data.get("email", self.email)
        self.nickname = user_data.get("nickname", self.nickname)
        self.user_id = user_data.get("id", self.user_id)
        self.avatar = user_data.get("photo", self.avatar)
        self.bio = user_data.get("bio", self.bio)
        self.avatar_emoji = user_data.get("avatar_emoji", self.avatar_emoji)
        self.profile_public = user_data.get("profile_public", self.profile_public)
        self.show_online = user_data.get("show_online", self.show_online)
        self.allow_messages = user_data.get("allow_messages", self.allow_messages)
        self.show_in_search = user_data.get("show_in_search", self.show_in_search)
        self.is_admin = user_data.get("is_admin", self.is_admin)
        self.is_verified = user_data.get("is_verified", self.is_verified)
        self.theme = user_data.get("theme", self.theme)
        self.updated_at = user_data.get("updated_at", self.updated_at)

    def update_profile(
            self,
            nickname: Optional[str] = None,
            username: Optional[str] = None,
            bio: Optional[str] = None,
            avatar_emoji: Optional[str] = None,
            save_after: bool = True
    ) -> bool:
        if not self.token:
            return False
        data = {
            "nickname": nickname if nickname is not None else self.nickname,
            "username": username if username is not None else self.username,
            "bio": bio if bio is not None else (self.bio or ""),
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
            if nickname is not None:
                self.nickname = nickname
            if username is not None:
                self.username = username
            if bio is not None:
                self.bio = bio
            if avatar_emoji is not None:
                self.avatar_emoji = avatar_emoji
            self.updated_at = datetime.now().isoformat()
            if save_after:
                self.save()
            return True
        except requests.exceptions.RequestException:
            return False

    def search_users(self, query: str) -> List[User]:
        if not self.token:
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

    def send_message(
            self,
            user: User,
            message: str
    ) -> Tuple[bool, str]:
        if not self.token:
            return False, "no_token"
        payload = {
            "receiver_id": user.id,
            "message": message
        }
        try:
            response = self.session.post(
                self._send_message_url,
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

    def create_support_ticket(
            self,
            subject: str = "Обращение",
            message: Optional[str] = None
    ) -> Tuple[bool, Optional[int], str]:
        if not self.token:
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
        if not self.token:
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
# КОНЕЦ БИБЛИОТЕКИ
# ============================================================================
