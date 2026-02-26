# kaalition_lib.py
"""
Kaalition.ru API Library
========================

Библиотека для работы с API сайта kaalition.ru.

Структура:
- KaalitionClient: Клиент для публичных данных
- Account: Класс для авторизованных операций
- User: Датакласс для пользователей
- Message: Датакласс для личных сообщений
- ChannelMessage: Датакласс для постов в каналах
- Channel: Датакласс для каналов
- Chat: Датакласс для списка чатов

Пример использования:

    from kaalition_lib import Account

    # Вход через email и пароль
    account = Account(email="email@mail.ru", password="password")

    # Или из токена
    account = Account(token="your_token")

    # === Работа с личными сообщениями ===
    # Поиск пользователей
    users = account.search_users("никнейм")

    if users:
        # Отправка сообщения
        message = account.send_message(users[0], "Привет!")

        # История чата
        messages = account.get_chat_history(users[0])

        # Список всех чатов
        chats = account.get_chats()

    # === Работа с каналами ===
    # Список каналов
    channels = account.get_channels()

    if channels:
        channel = channels[0]

        # Вступление
        account.join_channel(channel.id)

        # Сообщения в канале
        posts = account.get_channel_messages(channel.id)

        if posts:
            post = posts[0]

            # Ответ/пост
            new_post = account.send_channel_message(channel.id, "Мой ответ!")

            # Реакция
            post.toggle_reaction("🔥")

            # Закрепление
            post.pin()

        # Покинуть канал
        account.leave_channel(channel.id)
"""

import requests
import re
import random
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from faker import Faker

# ============================================================================
# КОНСТАНТЫ
# ============================================================================

DEFAULT_BASE_URL = "https://kaalition.ru"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
DEFAULT_EMAIL_DOMAINS = ["gmail.com", "outlook.com", "ya.ru", "hotmail.com"]
DEFAULT_SITE_KEY = "ZPCuKEjG9nT1o890yvmrJAkxvRWmLO0vXylIt92he6imCqAS"


# ============================================================================
# ИСКЛЮЧЕНИЯ
# ============================================================================

class KaalitionError(Exception):
    """Базовое исключение."""
    pass


class LoginError(KaalitionError):
    """Ошибка входа."""
    pass


class TokenError(KaalitionError):
    """Ошибка токена."""
    pass


class ProfileUpdateError(KaalitionError):
    """Ошибка обновления профиля."""
    pass


class UserNotFoundError(KaalitionError):
    """Пользователь не найден."""
    pass


class MessageError(KaalitionError):
    """Базовое исключение для сообщений."""
    pass


class MessageEditError(MessageError):
    """Ошибка редактирования сообщения."""
    pass


class MessageDeleteError(MessageError):
    """Ошибка удаления сообщения."""
    pass


class MessageReactionError(MessageError):
    """Ошибка реакции на сообщение."""
    pass


class ChatHistoryError(MessageError):
    """Ошибка получения истории чата."""
    pass


class ChannelError(KaalitionError):
    """Базовое исключение для каналов."""
    pass


class ChannelCreateError(ChannelError):
    """Ошибка создания канала."""
    pass


class ChannelUpdateError(ChannelError):
    """Ошибка обновления канала."""
    pass


class ChannelDeleteError(ChannelError):
    """Ошибка удаления канала."""
    pass


class ChannelMemberError(ChannelError):
    """Ошибка управления участниками."""
    pass


# ============================================================================
# DATACLASSES
# ============================================================================

@dataclass
class User:
    """Датакласс для пользователя."""
    id: int
    username: str
    nickname: str
    photo: str = ""
    avatar_emoji: Optional[str] = None
    is_verified: bool = False
    is_admin: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
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
        v = " ✅" if self.is_verified else ""
        a = " 👑" if self.is_admin else ""
        return f"User({self.id}, @{self.username}{v}{a})"

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class Reaction:
    """Датакласс для реакции на сообщение."""
    emoji: str
    count: int
    user_ids: List[int] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Reaction":
        return cls(
            emoji=data.get("emoji", ""),
            count=data.get("count", 0),
            user_ids=data.get("user_ids", [])
        )


@dataclass
class Message:
    """Датакласс для личного сообщения."""
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
    account: Optional["Account"] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any], sender: User, receiver: User,
                  account: Optional["Account"] = None) -> "Message":
        reactions = [Reaction.from_dict(r) for r in data.get("reactions", [])] if isinstance(data.get("reactions"),
                                                                                             list) else []
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
        return f"Message({self.id}, {self.sender.username} → {self.receiver.username})"

    def __repr__(self) -> str:
        return self.__str__()

    def is_edited(self) -> bool:
        return bool(self.edited_at)

    def has_reaction(self, emoji: str) -> bool:
        return any(r.emoji == emoji for r in self.reactions)

    def get_reaction_count(self, emoji: str) -> int:
        for r in self.reactions:
            if r.emoji == emoji:
                return r.count
        return 0

    # === Методы работы с сообщением ===

    def _ensure_account(self) -> bool:
        if not self.account:
            raise MessageError("Требуется Account")
        if not self.account.token:
            raise MessageError("Account не авторизован")
        return True

    def edit_text(self, new_text: str) -> Optional["Message"]:
        """Редактирует текст сообщения."""
        self._ensure_account()
        if self.sender.id != self.account.id:
            raise MessageEditError("Можно редактировать только свои сообщения")
        return self.account.edit_message_text(self, new_text)

    def delete(self) -> bool:
        """Удаляет сообщение."""
        self._ensure_account()
        return self.account.delete_message(self)

    def toggle_reaction(self, emoji: str) -> List[Reaction]:
        """Переключает реакцию на сообщении."""
        self._ensure_account()
        return self.account.toggle_message_reaction(self, emoji)


@dataclass
class Chat:
    """Датакласс для списка чатов (диалогов)."""
    id: int = field(init=False)
    user: User  # API использует "user" а не "partner"
    last_message: Optional[Message] = None
    unread_count: int = 0

    def __post_init__(self):
        self.id = self.user.id

    @property
    def partner(self) -> User:
        """Алиас для user для совместимости."""
        return self.user

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Chat":
        user_data = data.get("user", {})
        user = User.from_dict(user_data) if user_data else User(id=0, username="", nickname="")

        last_msg_data = data.get("last_message")
        last_msg = None
        if last_msg_data:
            sender_data = last_msg_data.get("sender", {})
            receiver_data = last_msg_data.get("receiver", {})
            sender = User.from_dict(sender_data) if sender_data else User(id=0, username="", nickname="")
            receiver = User.from_dict(receiver_data) if receiver_data else User(id=0, username="", nickname="")
            last_msg = Message.from_dict(last_msg_data, sender=sender, receiver=receiver)

        return cls(
            user=user,
            last_message=last_msg,
            unread_count=data.get("unread_count", 0)
        )

    def __str__(self) -> str:
        return f"Chat({self.id}, {self.user.nickname or self.user.username})"

    def __repr__(self) -> str:
        return self.__str__()


# Обновлённый класс Channel

@dataclass
class Channel:
    """Датакласс для канала."""
    id: int
    name: str
    owner: User
    description: str = ""
    image: Optional[str] = None  # API использует "image" а не "photo"
    is_public: bool = True
    is_verified: bool = False
    members_count: int = 0
    is_member: bool = False  # Добавлено из API
    is_admin: bool = False  # Добавлено из API
    settings: Dict[str, Any] = field(default_factory=dict)
    subscriber_permissions: Dict[str, bool] = field(default_factory=dict)
    allowed_reactions: List[str] = field(default_factory=list)
    comments_channel_id: Optional[int] = None
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Channel":
        if not data:
            return None

        # Обработка owner
        owner_data = data.get("owner")
        if isinstance(owner_data, dict):
            owner = User.from_dict(owner_data)
        elif isinstance(owner_data, int):
            owner = User(id=owner_data, username="", nickname="")
        else:
            owner = User(id=0, username="", nickname="")

        # Настройки
        settings = data.get("settings", {})
        if not isinstance(settings, dict):
            settings = {}

        # Разрешённые реакции
        allowed_reactions = data.get("allowed_reactions", [])
        if not isinstance(allowed_reactions, list):
            allowed_reactions = []

        # Права подписчиков
        subscriber_permissions = data.get("subscriber_permissions", {})
        if not isinstance(subscriber_permissions, dict):
            subscriber_permissions = {}

        return cls(
            id=data.get("id", 0),
            name=data.get("name", "") or data.get("title", ""),
            owner=owner,
            description=data.get("description", "") or "",
            image=data.get("image") or data.get("photo"),
            is_public=data.get("is_public", True),
            is_verified=bool(data.get("is_verified")),
            members_count=data.get("members_count", 0),
            is_member=bool(data.get("is_member")),
            is_admin=bool(data.get("is_admin")),
            settings=settings,
            subscriber_permissions=subscriber_permissions,
            allowed_reactions=allowed_reactions,
            comments_channel_id=data.get("comments_channel_id"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", "")
        )

    def __str__(self) -> str:
        v = " ✅" if self.is_verified else ""
        m = " [вы]" if self.is_member else ""
        return f"Channel({self.id}, {self.name}{v}{m})"

    def __repr__(self) -> str:
        return self.__str__()


# Обновлённый класс ChannelMessage

@dataclass
class ChannelMessage:
    """Датакласс для поста/сообщения в канале."""
    id: int
    channel_id: int
    author: User  # API использует "user" а не "author"
    text: str = ""
    image: Optional[str] = None
    is_pinned: bool = False
    comments_count: int = 0
    reactions: List[Reaction] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    account: Optional["Account"] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any], channel_id: int = None,
                  account: Optional["Account"] = None) -> "ChannelMessage":
        # API может вернуть channel_id как строку!
        if channel_id is None:
            ch_id = int(data.get("channel_id", 0)) if data.get("channel_id") else 0
        else:
            ch_id = channel_id

        # Обработка author
        author_data = data.get("user") or data.get("author")
        if isinstance(author_data, dict):
            author = User.from_dict(author_data)
        elif isinstance(author_data, int):
            author = User(id=author_data, username="", nickname="")
        else:
            author = User(id=data.get("user_id", 0) or data.get("author_id", 0), username="", nickname="")

        # Реакции
        reactions = [Reaction.from_dict(r) for r in data.get("reactions", [])] if isinstance(data.get("reactions"),
                                                                                             list) else []

        return cls(
            id=data.get("id", 0),
            channel_id=ch_id,
            author=author,
            text=data.get("message", "") or data.get("text", ""),
            image=data.get("image"),
            is_pinned=bool(data.get("is_pinned")),
            comments_count=data.get("comments_count", 0),
            reactions=reactions,
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            account=account
        )

    def __str__(self) -> str:
        return f"ChannelMessage({self.id}, channel={self.channel_id}, author={self.author.username})"

    def __repr__(self) -> str:
        return self.__str__()

    def is_edited(self) -> bool:
        return bool(self.updated_at) and self.updated_at != self.created_at

    def has_reaction(self, emoji: str) -> bool:
        return any(r.emoji == emoji for r in self.reactions)

    def get_reaction_count(self, emoji: str) -> int:
        for r in self.reactions:
            if r.emoji == emoji:
                return r.count
        return 0

    # === Методы работы с постом ===

    def _ensure_account(self) -> bool:
        if not self.account:
            raise ChannelError("Требуется Account")
        if not self.account.token:
            raise ChannelError("Account не авторизован")
        return True

    def edit_text(self, new_text: str) -> Optional["ChannelMessage"]:
        """Редактирует текст поста."""
        self._ensure_account()
        return self.account.edit_channel_message(self.channel_id, self.id, new_text)

    def delete(self) -> bool:
        """Удаляет пост."""
        self._ensure_account()
        return self.account.delete_channel_message(self.channel_id, self.id)

    def toggle_reaction(self, emoji: str) -> List[Reaction]:
        """Переключает реакцию на посте."""
        self._ensure_account()
        return self.account.toggle_channel_message_reaction(self.channel_id, self.id, emoji)

    def pin(self) -> bool:
        """Закрепляет/открепляет пост."""
        self._ensure_account()
        result = self.account.pin_channel_message(self.channel_id, self.id)
        if result:
            self.is_pinned = not self.is_pinned
        return result

    def get_comments(self) -> List["ChannelMessage"]:
        """Получает комментарии к посту."""
        self._ensure_account()
        return self.account.get_channel_message_comments(self.channel_id, self.id)


@dataclass
class ChannelMember:
    """Датакласс для участника канала."""
    user: User
    role: str = "member"  # owner, admin, member
    joined_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChannelMember":
        user_data = data.get("user", {})
        user = User.from_dict(user_data) if user_data else User(
            id=data.get("id", 0),
            username=data.get("username", ""),
            nickname=data.get("nickname", "")
        )
        return cls(
            user=user,
            role=data.get("role", "member"),
            joined_at=data.get("joined_at", "")
        )


@dataclass
class Project:
    """Датакласс для проекта."""
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


@dataclass
class Member:
    """Датакласс для участника."""
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


@dataclass
class News:
    """Датакласс для новости."""
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


# ============================================================================
# УТИЛИТЫ
# ============================================================================

def parse_wait_time(response_text: str) -> Optional[int]:
    """Извлекает время ожидания из ответа сервера."""
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
# KAALITION CLIENT
# ============================================================================

class KaalitionClient:
    """Клиент для работы с публичными данными API kaalition.ru."""

    def __init__(
            self,
            base_url: str = DEFAULT_BASE_URL,
            user_agent: str = DEFAULT_USER_AGENT,
            site_key: str = DEFAULT_SITE_KEY
    ):
        self.base_url = base_url.rstrip("/")
        self.site_key = site_key

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept": "application/json",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "X-Requested-With": "XMLHttpRequest",
            "X-Site-Key": site_key,
        })

        self._projects_url = f"{self.base_url}/api/projects"
        self._members_url = f"{self.base_url}/api/members"
        self._news_url = f"{self.base_url}/api/news"

    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/",
            "X-Site-Key": self.site_key
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _get_error_message(self, response: requests.Response) -> str:
        try:
            return response.json().get("message", str(response.json()))
        except:
            return response.text[:200] if response.text else "Unknown error"

    def get_projects(self) -> List[Project]:
        """Получает список проектов."""
        try:
            response = self.session.get(self._projects_url, headers=self._get_headers(), timeout=10)
            if response.ok:
                return [Project.from_dict(p) for p in response.json()] if isinstance(response.json(), list) else []
        except requests.exceptions.RequestException:
            pass
        return []

    def get_members(self) -> List[Member]:
        """Получает список участников."""
        try:
            response = self.session.get(self._members_url, headers=self._get_headers(), timeout=10)
            if response.ok:
                return [Member.from_dict(m) for m in response.json()] if isinstance(response.json(), list) else []
        except requests.exceptions.RequestException:
            pass
        return []

    def get_news(self) -> List[News]:
        """Получает список новостей."""
        try:
            response = self.session.get(self._news_url, headers=self._get_headers(), timeout=10)
            if response.ok:
                return [News.from_dict(n) for n in response.json()] if isinstance(response.json(), list) else []
        except requests.exceptions.RequestException:
            pass
        return []


# ============================================================================
# ACCOUNT
# ============================================================================

class Account(KaalitionClient):
    """Класс для авторизованных операций с API kaalition.ru."""

    def __init__(
            self,
            token: str = "",
            email: str = "",
            password: str = "",
            base_url: str = DEFAULT_BASE_URL,
            site_key: str = DEFAULT_SITE_KEY
    ):
        KaalitionClient.__init__(self, base_url=base_url, site_key=site_key)

        # URLs
        self._login_url = f"{self.base_url}/api/auth/login"
        self._me_url = f"{self.base_url}/api/auth/me"
        self._profile_url = f"{self.base_url}/api/user/profile"
        self._password_url = f"{self.base_url}/api/user/password"
        self._theme_url = f"{self.base_url}/api/user/theme"
        self._privacy_url = f"{self.base_url}/api/user/privacy"
        self._sessions_url = f"{self.base_url}/api/auth/sessions"

        # Messages URLs
        self._chats_url = f"{self.base_url}/api/messages/chats"
        self._search_users_url = f"{self.base_url}/api/messages/search/users"
        self._send_message_url = f"{self.base_url}/api/messages/send"
        self._chat_history_url = f"{self.base_url}/api/messages"

        # Channels URLs
        self._channels_url = f"{self.base_url}/api/channels"

        # Поля User
        self.id: int = 0
        self.username: str = ""
        self.nickname: str = ""
        self.photo: str = ""
        self.avatar_emoji: Optional[str] = None
        self.is_verified: bool = False
        self.is_admin: bool = False

        # Поля профиля
        self.email: str = email
        self.bio: str = ""
        self.avatar: str = ""
        self.profile_public: bool = True
        self.show_online: bool = True
        self.allow_messages: bool = True
        self.show_in_search: bool = True
        self.theme: str = "dark"

        # Поля авторизации
        self.token = token
        self.password = password
        self.active = True
        self.created_at = datetime.now().isoformat()
        self.updated_at: Optional[str] = None

        # Авторизация
        if email and password:
            self._do_login(email, password)
        elif token:
            self._do_create_from_token(token)

    def _do_login(self, email: str, password: str) -> bool:
        """Выполняет вход."""
        payload = {"email": email, "password": password}

        try:
            response = self.session.post(self._login_url, json=payload, headers=self._get_headers(), timeout=10)
            if not response.ok:
                raise LoginError(f"Код {response.status_code}: {self._get_error_message(response)}")

            resp_data = response.json()
            token = resp_data.get("token") or resp_data.get("access_token")
            if not token:
                raise LoginError("Токен не получен")

            self.token = token
            self.password = password
            self.active = True

            user_data = resp_data.get("user", {})
            if user_data:
                self._update_from_user_data(user_data)
            else:
                self._fetch_user_data()

            return True

        except requests.exceptions.RequestException as e:
            raise LoginError(f"Ошибка сети: {e}")

    def _do_create_from_token(self, token: str) -> bool:
        """Создаёт из токена."""
        try:
            response = self.session.get(self._me_url, headers=self._get_headers(token), timeout=10)
            if not response.ok:
                raise TokenError(f"Код {response.status_code}: {self._get_error_message(response)}")

            user_data = response.json()
            if "id" not in user_data:
                raise TokenError("ID пользователя не получен")

            self.token = token
            self.active = True
            self._update_from_user_data(user_data)

            return True

        except requests.exceptions.RequestException as e:
            raise TokenError(f"Ошибка сети: {e}")

    def _fetch_user_data(self) -> bool:
        """Получает данные пользователя."""
        try:
            response = self.session.get(self._me_url, headers=self._get_headers(self.token), timeout=10)
            if response.ok:
                user_data = response.json()
                if "id" in user_data:
                    self._update_from_user_data(user_data)
                    self.active = True
                    return True
            self.active = False
            return False
        except requests.exceptions.RequestException:
            self.active = False
            return False

    def _update_from_user_data(self, user_data: Dict[str, Any]):
        """Обновляет данные из ответа сервера."""
        self.id = user_data.get("id", self.id)
        self.username = user_data.get("username", self.username)
        self.nickname = user_data.get("nickname", self.nickname)
        self.photo = user_data.get("photo", self.photo) or ""
        self.avatar = self.photo
        self.avatar_emoji = user_data.get("avatar_emoji", self.avatar_emoji)
        self.is_verified = user_data.get("is_verified", self.is_verified)
        self.is_admin = user_data.get("is_admin", self.is_admin)
        self.email = user_data.get("email", self.email)
        self.bio = user_data.get("bio", self.bio) or ""
        self.profile_public = user_data.get("profile_public", self.profile_public)
        self.show_online = user_data.get("show_online", self.show_online)
        self.allow_messages = user_data.get("allow_messages", self.allow_messages)
        self.show_in_search = user_data.get("show_in_search", self.show_in_search)
        self.theme = user_data.get("theme", self.theme)
        self.updated_at = user_data.get("updated_at", self.updated_at)

    def refresh(self) -> bool:
        """Синхронизация с сервером."""
        if not self.token:
            return False
        return self._fetch_user_data()

    def is_active(self) -> bool:
        """Проверка активности."""
        if not self.token:
            self.active = False
            return False
        return self.active

    def _get_current_user_sender(self) -> User:
        """Возвращает текущего пользователя как User."""
        return User(
            id=self.id,
            username=self.username,
            nickname=self.nickname,
            photo=self.photo,
            avatar_emoji=self.avatar_emoji,
            is_verified=self.is_verified,
            is_admin=self.is_admin
        )

        # === Профиль ===

    def update_profile(
            self,
            nickname: Optional[str] = None,
            username: Optional[str] = None,
            bio: Optional[str] = None,
            avatar_emoji: Optional[str] = None
    ) -> bool:
        """Обновление профиля."""
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
            response = self.session.post(self._profile_url, data=data, headers=self._get_headers(self.token),
                                         timeout=10)
            if response.ok:
                resp_data = response.json()
                if "user" in resp_data:
                    self._update_from_user_data(resp_data["user"])
                else:
                    self._update_from_user_data(resp_data)
                return True
            return False
        except requests.exceptions.RequestException:
            return False

    def update_password(
            self,
            current_password: str,
            new_password: str,
            new_password_confirmation: str
    ) -> bool:
        """Изменение пароля."""
        if not self.token:
            return False

        data = {
            "current_password": current_password,
            "new_password": new_password,
            "new_password_confirmation": new_password_confirmation,
            "_method": "PUT"
        }

        try:
            response = self.session.post(self._password_url, data=data, headers=self._get_headers(self.token),
                                         timeout=10)
            return response.ok
        except requests.exceptions.RequestException:
            return False

    def update_theme(self, theme: str) -> bool:
        """Изменение темы (dark/amoled/forest/navy)."""
        if not self.token:
            return False

        try:
            response = self.session.put(
                self._theme_url,
                json={"theme": theme},
                headers=self._get_headers(self.token),
                timeout=10
            )
            if response.ok:
                self.theme = theme
                return True
            return False
        except requests.exceptions.RequestException:
            return False

    def update_privacy(
            self,
            profile_public: Optional[bool] = None,
            show_online: Optional[bool] = None,
            allow_messages: Optional[bool] = None,
            show_in_search: Optional[bool] = None
    ) -> bool:
        """Изменение настроек приватности."""
        if not self.token:
            return False

        data = {}
        if profile_public is not None:
            data["profile_public"] = profile_public
        if show_online is not None:
            data["show_online"] = show_online
        if allow_messages is not None:
            data["allow_messages"] = allow_messages
        if show_in_search is not None:
            data["show_in_search"] = show_in_search

        if not data:
            return False

        try:
            response = self.session.put(self._privacy_url, json=data, headers=self._get_headers(self.token), timeout=10)
            if response.ok:
                resp_data = response.json()
                self.profile_public = resp_data.get("profile_public", self.profile_public)
                self.show_online = resp_data.get("show_online", self.show_online)
                self.allow_messages = resp_data.get("allow_messages", self.allow_messages)
                self.show_in_search = resp_data.get("show_in_search", self.show_in_search)
                return True
            return False
        except requests.exceptions.RequestException:
            return False

        # === Сессии ===

    def get_sessions(self) -> List[Dict[str, Any]]:
        """Получение списка активных сессий."""
        if not self.token:
            return []

        try:
            response = self.session.get(self._sessions_url, headers=self._get_headers(self.token), timeout=10)
            if response.ok:
                return response.json()
        except requests.exceptions.RequestException:
            pass
        return []

    def delete_session(self, session_id: int) -> bool:
        """Удаление конкретной сессии."""
        if not self.token:
            return False

        try:
            response = self.session.delete(
                f"{self._sessions_url}/{session_id}",
                headers=self._get_headers(self.token),
                timeout=10
            )
            return response.ok
        except requests.exceptions.RequestException:
            return False

    def delete_all_sessions(self) -> bool:
        """Удаление всех сессий кроме текущей."""
        if not self.token:
            return False

        try:
            response = self.session.delete(
                self._sessions_url,
                headers=self._get_headers(self.token),
                timeout=10
            )
            return response.ok
        except requests.exceptions.RequestException:
            return False

    def logout(self) -> bool:
        """Выход из аккаунта."""
        if not self.token:
            return False

        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/logout",
                headers=self._get_headers(self.token),
                timeout=10
            )
            # Даже если ответ не OK, считаем что logout выполнен
            self.token = ""
            self.active = False
            return True  # Меняем на True чтобы всегда выполнялось
        except requests.exceptions.RequestException:
            self.token = ""
            self.active = False
            return True

    # === Поиск ===

    def search_users(self, query: str) -> List[User]:
        """Поиск пользователей."""
        if not self.token:
            return []

        try:
            response = self.session.get(
                f"{self._search_users_url}?query={query}",
                headers=self._get_headers(self.token),
                timeout=10
            )
            if response.ok:
                users_data = response.json()
                return [User.from_dict(u) for u in users_data] if isinstance(users_data, list) else []
        except requests.exceptions.RequestException:
            pass
        return []

        # === Личные сообщения ===

    def send_message(self, receiver_id: int, text: str) -> Optional[Message]:
        """Отправка сообщения. receiver_id - ID получателя."""
        if not self.token:
            return None

        payload = {"receiver_id": receiver_id, "message": text}

        try:
            response = self.session.post(
                self._send_message_url,
                json=payload,
                headers=self._get_headers(self.token),
                timeout=10
            )
            if not response.ok:
                return None

            resp_data = response.json()
            sender = self._get_current_user_sender()
            receiver = User(
                id=receiver_id,
                username="",
                nickname=""
            )
            return Message.from_dict(resp_data, sender=sender, receiver=receiver, account=self)

        except requests.exceptions.RequestException:
            return None

    def get_chat_history(self, user_id: int) -> List[Message]:
        """Получение истории чата. user_id - ID собеседника."""
        if not self.token:
            raise ChatHistoryError("Не авторизован")

        try:
            response = self.session.get(
                f"{self._chat_history_url}/{user_id}",
                headers=self._get_headers(self.token),
                timeout=10
            )
            if not response.ok:
                raise ChatHistoryError(f"Ошибка: {response.status_code}")

            messages_data = response.json()
            if not isinstance(messages_data, list):
                return []

            current_user = self._get_current_user_sender()
            target_user = User(id=user_id, username="", nickname="")

            messages = []
            for msg_data in messages_data:
                sender_data = msg_data.get("sender", {})
                sender = User.from_dict(sender_data) if sender_data else User(
                    id=msg_data.get("sender_id", 0),
                    username="",
                    nickname=""
                )
                receiver = current_user if msg_data.get("receiver_id") == self.id else target_user
                message = Message.from_dict(msg_data, sender=sender, receiver=receiver, account=self)
                messages.append(message)

            messages.sort(key=lambda m: m.created_at)
            return messages

        except requests.exceptions.RequestException as e:
            raise ChatHistoryError(f"Ошибка сети: {e}")

    def get_chats(self) -> List[Chat]:
        """Получение списка всех чатов."""
        if not self.token:
            return []

        try:
            response = self.session.get(
                self._chats_url,
                headers=self._get_headers(self.token),
                timeout=10
            )
            if response.ok:
                chats_data = response.json()
                return [Chat.from_dict(c) for c in chats_data] if isinstance(chats_data, list) else []
        except requests.exceptions.RequestException:
            pass
        return []

    def edit_message_text(self, message: Message, new_text: str) -> Optional[Message]:
        """Редактирование сообщения."""
        if not self.token:
            return None

        try:
            response = self.session.put(
                f"{self._chat_history_url}/{message.id}/edit",
                json={"message": new_text},
                headers=self._get_headers(self.token),
                timeout=10
            )
            if not response.ok:
                return None

            resp_data = response.json()
            message.text = resp_data.get("message", new_text)
            message.edited_at = resp_data.get("edited_at", message.edited_at)
            message.updated_at = resp_data.get("updated_at", message.updated_at)

            reactions_data = resp_data.get("reactions", [])
            if isinstance(reactions_data, list):
                message.reactions = [Reaction.from_dict(r) for r in reactions_data]

            return message

        except requests.exceptions.RequestException:
            return None

    def delete_message(self, message: Message) -> bool:
        """Удаление сообщения."""
        if not self.token:
            return False

        try:
            response = self.session.delete(
                f"{self._chat_history_url}/{message.id}",
                headers=self._get_headers(self.token),
                timeout=10
            )
            return response.ok

        except requests.exceptions.RequestException:
            return False

    def toggle_message_reaction(self, message: Message, emoji: str) -> List[Reaction]:
        """Установка реакции."""
        if not self.token:
            return []

        try:
            response = self.session.post(
                f"{self._chat_history_url}/{message.id}/react",
                json={"emoji": emoji},
                headers=self._get_headers(self.token),
                timeout=10
            )
            if response.ok:
                reactions_data = response.json().get("reactions", [])
                if isinstance(reactions_data, list):
                    message.reactions = [Reaction.from_dict(r) for r in reactions_data]
            return message.reactions

        except requests.exceptions.RequestException:
            return []

        # === Каналы ===

    def get_channels(self, page: Optional[int] = None) -> List[Channel]:
        """Получение списка каналов.

        Args:
            page: Номер страницы. Если None - загружает все страницы.
        """
        if not self.token:
            return []

        all_channels = []
        current_page = page if page is not None else 1

        while True:
            try:
                url = f"{self._channels_url}?page={current_page}"
                response = self.session.get(
                    url,
                    headers=self._get_headers(self.token),
                    timeout=10
                )
                if not response.ok:
                    break

                resp_data = response.json()

                # Извлекаем массив каналов
                if isinstance(resp_data, dict):
                    channels_data = resp_data.get("data", [])
                    has_more = resp_data.get("has_more", False)
                    total = resp_data.get("total", 0)
                else:
                    channels_data = resp_data if isinstance(resp_data, list) else []
                    has_more = False
                    total = len(channels_data)

                if not isinstance(channels_data, list):
                    break

                # Добавляем каналы текущей страницы
                for c in channels_data:
                    channel = Channel.from_dict(c)
                    if channel:
                        all_channels.append(channel)

                # Если page указан явно - выходим после первой страницы
                if page is not None:
                    break

                # Если нет больше страниц - выходим
                if not has_more:
                    break

                # Переходим к следующей странице
                current_page += 1

            except requests.exceptions.RequestException:
                break

        return all_channels

    def get_channel(self, channel_id: int) -> Optional[Channel]:
        """Получение информации о канале."""
        if not self.token:
            return None

        try:
            response = self.session.get(
                f"{self._channels_url}/{channel_id}",
                headers=self._get_headers(self.token),
                timeout=10
            )
            if response.ok:
                return Channel.from_dict(response.json())
        except requests.exceptions.RequestException:
            pass
        return None

    # Замените метод create_channel на этот:

    def create_channel(
            self,
            name: str,
            description: str = "",
            is_public: bool = True,
            settings: Optional[Dict[str, Any]] = None
    ) -> Optional[Channel]:
        """Создание канала."""
        if not self.token:
            return None

        data = {
            "name": name,
            "description": description,
            "is_public": is_public
        }
        if settings:
            data["settings"] = settings

        try:
            response = self.session.post(
                self._channels_url,
                json=data,
                headers=self._get_headers(self.token),
                timeout=10
            )

            # Для отладки
            if not response.ok:
                print(f"  [DEBUG] Ошибка создания канала: {response.status_code}")
                print(f"  [DEBUG] Ответ: {response.text[:200]}")
                return None

            return Channel.from_dict(response.json())
        except requests.exceptions.RequestException as e:
            print(f"  [DEBUG] Исключение: {e}")
            return None
        except Exception as e:
            print(f"  [DEBUG] Неожиданная ошибка: {e}")
            return None

    def update_channel(
            self,
            channel_id: int,
            name: Optional[str] = None,
            description: Optional[str] = None,
            is_public: Optional[bool] = None,
            settings: Optional[Dict[str, Any]] = None,
            subscriber_permissions: Optional[Dict[str, bool]] = None,
            allowed_reactions: Optional[List[str]] = None,
            comments_channel_id: Optional[int] = None
    ) -> bool:
        """Обновление канала (только владелец/админ)."""
        if not self.token:
            return False

        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if is_public is not None:
            data["is_public"] = is_public
        if settings is not None:
            data["settings"] = settings
        if subscriber_permissions is not None:
            data["subscriber_permissions"] = subscriber_permissions
        if allowed_reactions is not None:
            data["allowed_reactions"] = allowed_reactions
        if comments_channel_id is not None:
            data["comments_channel_id"] = comments_channel_id

        if not data:
            return False

        try:
            response = self.session.put(
                f"{self._channels_url}/{channel_id}",
                json=data,
                headers=self._get_headers(self.token),
                timeout=10
            )
            return response.ok
        except requests.exceptions.RequestException:
            return False

    def delete_channel(self, channel_id: int) -> bool:
        """Удаление канала (только владелец)."""
        if not self.token:
            return False

        try:
            response = self.session.delete(
                f"{self._channels_url}/{channel_id}",
                headers=self._get_headers(self.token),
                timeout=10
            )
            return response.ok
        except requests.exceptions.RequestException:
            return False

    def join_channel(self, channel_id: int) -> bool:
        """Вступление в канал."""
        if not self.token:
            return False

        try:
            response = self.session.post(
                f"{self._channels_url}/{channel_id}/join",
                headers=self._get_headers(self.token),
                timeout=10
            )
            return response.ok
        except requests.exceptions.RequestException:
            return False

    def leave_channel(self, channel_id: int) -> bool:
        """Покидание канала."""
        if not self.token:
            return False

        try:
            response = self.session.post(
                f"{self._channels_url}/{channel_id}/leave",
                headers=self._get_headers(self.token),
                timeout=10
            )
            return response.ok
        except requests.exceptions.RequestException:
            return False

        # === Сообщения каналов ===

    def get_channel_messages(self, channel_id: int) -> List[ChannelMessage]:
        """Получение сообщений канала."""
        if not self.token:
            return []

        try:
            response = self.session.get(
                f"{self._channels_url}/{channel_id}/messages",
                headers=self._get_headers(self.token),
                timeout=10
            )
            if response.ok:
                messages_data = response.json()
                return [ChannelMessage.from_dict(m, channel_id, self) for m in messages_data] if isinstance(
                    messages_data, list) else []
        except requests.exceptions.RequestException:
            pass
        return []

    def send_channel_message(self, channel_id: int, text: str) -> Optional[ChannelMessage]:
        """Отправка сообщения в канал."""
        if not self.token:
            return None

        try:
            response = self.session.post(
                f"{self._channels_url}/{channel_id}/messages",
                json={"message": text},
                headers=self._get_headers(self.token),
                timeout=10
            )
            if response.ok:
                return ChannelMessage.from_dict(response.json(), channel_id, self)
        except requests.exceptions.RequestException:
            pass
        return None

    def edit_channel_message(self, channel_id: int, message_id: int, new_text: str) -> Optional[ChannelMessage]:
        """Редактирование сообщения в канале."""
        if not self.token:
            return None

        try:
            response = self.session.put(
                f"{self._channels_url}/{channel_id}/messages/{message_id}",
                json={"message": new_text},
                headers=self._get_headers(self.token),
                timeout=10
            )
            if response.ok:
                return ChannelMessage.from_dict(response.json(), channel_id, self)
        except requests.exceptions.RequestException:
            pass
        return None

    def delete_channel_message(self, channel_id: int, message_id: int) -> bool:
        """Удаление сообщения в канале."""
        if not self.token:
            return False

        try:
            response = self.session.delete(
                f"{self._channels_url}/{channel_id}/messages/{message_id}",
                headers=self._get_headers(self.token),
                timeout=10
            )
            return response.ok
        except requests.exceptions.RequestException:
            return False

    def pin_channel_message(self, channel_id: int, message_id: int) -> bool:
        """Закрепление/открепление сообщения в канале."""
        if not self.token:
            return False

        try:
            response = self.session.post(
                f"{self._channels_url}/{channel_id}/messages/{message_id}/pin",
                headers=self._get_headers(self.token),
                timeout=10
            )
            return response.ok
        except requests.exceptions.RequestException:
            return False

    def toggle_channel_message_reaction(self, channel_id: int, message_id: int, emoji: str) -> List[Reaction]:
        """Установка реакции на сообщение в канале."""
        if not self.token:
            return []

        try:
            response = self.session.post(
                f"{self._channels_url}/{channel_id}/messages/{message_id}/react",
                json={"emoji": emoji},
                headers=self._get_headers(self.token),
                timeout=10
            )
            if response.ok:
                reactions_data = response.json().get("reactions", [])
                if isinstance(reactions_data, list):
                    return [Reaction.from_dict(r) for r in reactions_data]
        except requests.exceptions.RequestException:
            pass
        return []

    def get_channel_message_comments(self, channel_id: int, message_id: int) -> List[ChannelMessage]:
        """Получение комментариев к посту в канале."""
        if not self.token:
            return []

        try:
            response = self.session.get(
                f"{self._channels_url}/{channel_id}/messages/{message_id}/comments",
                headers=self._get_headers(self.token),
                timeout=10
            )
            if response.ok:
                comments_data = response.json()
                return [ChannelMessage.from_dict(c, channel_id, self) for c in comments_data] if isinstance(
                    comments_data, list) else []
        except requests.exceptions.RequestException:
            pass
        return []

    def get_channel_reactions(self, channel_id: int) -> Dict[str, Any]:
        """Получение всех реакций канала."""
        if not self.token:
            return {}

        try:
            response = self.session.get(
                f"{self._channels_url}/{channel_id}/reactions",
                headers=self._get_headers(self.token),
                timeout=10
            )
            if response.ok:
                return response.json()
        except requests.exceptions.RequestException:
            pass
        return {}

        # === Участники канала ===

    def get_channel_members(self, channel_id: int) -> List[ChannelMember]:
        """Получение списка участников канала."""
        if not self.token:
            return []

        try:
            response = self.session.get(
                f"{self._channels_url}/{channel_id}/members",
                headers=self._get_headers(self.token),
                timeout=10
            )
            if response.ok:
                members_data = response.json()
                return [ChannelMember.from_dict(m) for m in members_data] if isinstance(members_data, list) else []
        except requests.exceptions.RequestException:
            pass
        return []

    def update_channel_member_role(self, channel_id: int, user_id: int, role: str) -> bool:
        """Изменение роли участника канала (admin/member)."""
        if not self.token:
            return False

        try:
            response = self.session.put(
                f"{self._channels_url}/{channel_id}/members/{user_id}/role",
                json={"role": role},
                headers=self._get_headers(self.token),
                timeout=10
            )
            return response.ok
        except requests.exceptions.RequestException:
            return False

    def kick_channel_member(self, channel_id: int, user_id: int) -> bool:
        """Удаление участника из канала."""
        if not self.token:
            return False

        try:
            response = self.session.delete(
                f"{self._channels_url}/{channel_id}/members/{user_id}",
                headers=self._get_headers(self.token),
                timeout=10
            )
            return response.ok
        except requests.exceptions.RequestException:
            return False

    def __repr__(self) -> str:
        return f"Account({self.username}, active={self.active})"

    # ============================================================================
    # КОНЕЦ
    # ============================================================================
