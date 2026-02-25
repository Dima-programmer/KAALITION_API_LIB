# kaalition_lib.py
"""
Kaalition.ru API Library
========================

Библиотека для работы с API сайта kaalition.ru.

Структура:
- KaalitionClient: Клиент для публичных данных
- Account: Класс для авторизованных операций
- User: Датакласс для пользователей
- Message: Датакласс для сообщений
- Reaction: Датакласс для реакций

Пример использования:

    from kaalition_lib import Account

    # Вход через email и пароль
    account = Account(email="email@mail.ru", password="password")

    # Или из токена
    account = Account(token="your_token")

    # Поиск пользователей
    users = account.search_users("никнейм")

    # Отправка сообщения
    if users:
        message = account.send_message(users[0], "Привет!")
        print(f"ID: {message.id}")

        # Редактирование
        message.edit_text("Новый текст")

        # Реакция
        message.toggle_reaction("👍")

        # Удаление
        message.delete()

    # История чата
    messages = account.get_chat_history(users[0])
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
    """Датакласс для сообщения."""
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
    def from_dict(cls, data: Dict[str, Any], sender: User, receiver: User, account: Optional["Account"] = None) -> "Message":
        reactions = [Reaction.from_dict(r) for r in data.get("reactions", [])] if isinstance(data.get("reactions"), list) else []
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
        # if self.sender.id != self.account.id:
        #     raise MessageDeleteError("Можно удалять только свои сообщения")
        return self.account.delete_message(self)

    def toggle_reaction(self, emoji: str) -> List[Reaction]:
        """Переключает реакцию на сообщении."""
        self._ensure_account()
        return self.account.toggle_message_reaction(self, emoji)


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
            user_agent: str = DEFAULT_USER_AGENT
    ):
        self.base_url = base_url.rstrip("/")

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept": "application/json",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "X-Requested-With": "XMLHttpRequest",
        })

        self._projects_url = f"{self.base_url}/api/projects"
        self._members_url = f"{self.base_url}/api/members"
        self._news_url = f"{self.base_url}/api/news"

    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {"Origin": self.base_url, "Referer": f"{self.base_url}/"}
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
            base_url: str = DEFAULT_BASE_URL
    ):
        KaalitionClient.__init__(self, base_url=base_url)

        # URLs
        self._login_url = f"{self.base_url}/api/auth/login"
        self._me_url = f"{self.base_url}/api/auth/me"
        self._profile_url = f"{self.base_url}/api/user/profile"
        self._search_users_url = f"{self.base_url}/api/messages/search/users"
        self._send_message_url = f"{self.base_url}/api/messages/send"
        self._chat_history_url = f"{self.base_url}/api/messages"

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
        self.updated_at = None

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
            response = self.session.post(self._profile_url, data=data, headers=self._get_headers(self.token), timeout=10)
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

    # === Сообщения ===

    def send_message(self, user: User, text: str) -> Optional[Message]:
        """Отправка сообщения."""
        if not self.token:
            return None

        payload = {"receiver_id": user.id, "message": text}

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
                id=user.id,
                username=user.username,
                nickname=user.nickname,
                photo=user.photo,
                avatar_emoji=user.avatar_emoji,
                is_verified=user.is_verified,
                is_admin=user.is_admin
            )
            return Message.from_dict(resp_data, sender=sender, receiver=receiver, account=self)

        except requests.exceptions.RequestException:
            return None

    def get_chat_history(self, user: User) -> List[Message]:
        """Получение истории чата."""
        if not self.token:
            raise ChatHistoryError("Не авторизован")

        try:
            response = self.session.get(
                f"{self._chat_history_url}/{user.id}",
                headers=self._get_headers(self.token),
                timeout=10
            )
            if not response.ok:
                raise ChatHistoryError(f"Ошибка: {response.status_code}")

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

    def __repr__(self) -> str:
        return f"Account({self.username}, active={self.active})"


# ============================================================================
# КОНЕЦ
# ============================================================================