# Kaalition API Library — Полная документация

Python библиотека для работы с API сайта [kaalition.ru](https://kaalition.ru).

---

## 📑 Навигация

- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
- [Константы](#константы)
- [Исключения](#исключения)
- [Классы](#классы)
    - [Account](#account)
    - [User](#user)
    - [Message](#message)
    - [Chat](#chat)
    - [Channel](#channel)
    - [ChannelMessage](#channelmessage)
    - [ChannelMember](#channelmember)
    - [Reaction](#reaction)
    - [KaalitionClient](#kaalitionclient)
    - [Project](#project)
    - [Member](#member)
    - [News](#news)
- [Примеры](#примеры-использования)
    - [Личные сообщения](#личные-сообщения)
    - [Каналы](#каналы)
    - [Профиль](#профиль)
    - [Публичные данные](#публичные-данные)
- [Частые вопросы](#частые-вопросы)

---

## Установка

### Требования

- Python 3.8+
- requests

### pip

```bash
pip install kaalition-lib
```

### Из исходников

```bash
git clone https://github.com/Dima-programmer/KAALITION_API_LIB.git
cd KAALITION_API_LIB
pip install -e .
```

---

## Быстрый старт

```python
from kaalition_lib import Account

# Авторизация через email и пароль
account = Account(email="mail@test.com", password="pass")

# Или через токен
account = Account(token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...")

print(f"Привет, {account.nickname}!")
print(f"ID: {account.id}, Токен: {account.token[:20]}...")
```

---

## Константы

```python
from kaalition_lib import (
    DEFAULT_BASE_URL,  # "https://kaalition.ru"
    DEFAULT_USER_AGENT,  # User-Agent браузера по умолчанию
    DEFAULT_EMAIL_DOMAINS,  # Список email доменов ["gmail.com", "outlook.com", ...]
    DEFAULT_SITE_KEY,  # "ZPCuKEjG9nT1o890yvmrJAkxvRWmLO0vXylIt92he6imCqAS"
)
```

---

## Исключения

Все исключения наследуются от базового класса `KaalitionError`.

```python
from kaalition_lib import KaalitionError

try:
    account = Account(email="wrong@mail.com", password="wrong")
except KaalitionError as e:
    print(f"Ошибка: {e}")
```

### Иерархия исключений

```
KaalitionError
├── LoginError              # Ошибка входа в аккаунт
├── TokenError              # Ошибка токена авторизации
├── ProfileUpdateError      # Ошибка обновления профиля
├── UserNotFoundError       # Пользователь не найден
├── MessageError            # Базовое исключение для сообщений
│   ├── MessageEditError    # Ошибка редактирования сообщения
│   ├── MessageDeleteError  # Ошибка удаления сообщения
│   ├── MessageReactionError # Ошибка установки реакции
│   └── ChatHistoryError    # Ошибка получения истории чата
└── ChannelError            # Базовое исключение для каналов
    ├── ChannelCreateError  # Ошибка создания канала
    ├── ChannelUpdateError  # Ошибка обновления канала
    ├── ChannelDeleteError  # Ошибка удаления канала
    └── ChannelMemberError  # Ошибка управления участниками
```

---

## Классы

### Account

Основной класс для авторизованных операций с API. Наследуется от `KaalitionClient`.

#### Создание

```python
# Через email и пароль
account = Account(email="mail@test.com", password="pass")

# Через токен
account = Account(token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...")

# С кастомным URL (для тестирования)
account = Account(
    email="mail@test.com",
    password="pass",
    base_url="https://test.kaalition.ru"
)
```

#### Атрибуты

| Атрибут            | Тип          | Описание                           |
|--------------------|--------------|------------------------------------|
| `id`               | `int`        | ID пользователя                    |
| `username`         | `str`        | Имя пользователя (уникальное)      |
| `nickname`         | `str`        | Отображаемое имя                   |
| `email`            | `str`        | Email адрес                        |
| `photo` / `avatar` | `str`        | Ссылка на фото профиля             |
| `avatar_emoji`     | `str \ None` | Эмодзи-аватар                      |
| `bio`              | `str`        | О себе                             |
| `is_verified`      | `bool`       | Верифицирован ли пользователь      |
| `is_admin`         | `bool`       | Является ли администратором        |
| `theme`            | `str`        | Тема оформления (`dark`/`light`)   |
| `profile_public`   | `bool`       | Профиль публичен?                  |
| `show_online`      | `bool`       | Показывать онлайн-статус?          |
| `allow_messages`   | `bool`       | Разрешены входящие сообщения?      |
| `show_in_search`   | `bool`       | Показывать в поиске пользователей? |
| `token`            | `str`        | JWT токен авторизации              |
| `active`           | `bool`       | Активна ли сессия                  |

#### Методы

##### Авторизация и профиль

| Метод                                                                         | Возвращает | Описание                        |
|-------------------------------------------------------------------------------|------------|---------------------------------|
| `refresh()`                                                                   | `bool`     | Синхронизация данных с сервером |
| `is_active()`                                                                 | `bool`     | Проверка активности сессии      |
| `update_profile(nickname, username, bio, avatar_emoji)`                       | `bool`     | Обновление профиля              |
| `update_password(current, new, confirmation)`                                 | `bool`     | Смена пароля                    |
| `update_theme(theme)`                                                         | `bool`     | Смена темы (`dark`/`light`)     |
| `update_privacy(profile_public, show_online, allow_messages, show_in_search)` | `bool`     | Настройки приватности           |

##### Сессии

| Метод                        | Возвращает   | Описание                           |
|------------------------------|--------------|------------------------------------|
| `get_sessions()`             | `List[Dict]` | Список активных сессий             |
| `delete_session(session_id)` | `bool`       | Удалить конкретную сессию          |
| `delete_all_sessions()`      | `bool`       | Удалить все сессии (кроме текущей) |
| `logout()`                   | `bool`       | Выйти из аккаунта                  |

##### Поиск пользователей

| Метод                 | Возвращает   | Описание                          |
|-----------------------|--------------|-----------------------------------|
| `search_users(query)` | `List[User]` | Поиск пользователей по нику/имени |

##### Личные сообщения

| Метод                                     | Возвращает          | Описание                     |
|-------------------------------------------|---------------------|------------------------------|
| `send_message(receiver_id, text)`         | `Optional[Message]` | Отправить сообщение          |
| `get_chat_history(user_id)`               | `List[Message]`     | История чата с пользователем |
| `get_chats()`                             | `List[Chat]`        | Список всех чатов            |
| `edit_message_text(message, new_text)`    | `Optional[Message]` | Редактировать сообщение      |
| `delete_message(message)`                 | `bool`              | Удалить сообщение            |
| `toggle_message_reaction(message, emoji)` | `List[Reaction]`    | Добавить/убрать реакцию      |

##### Каналы

| Метод                                                    | Возвращает          | Описание            |
|----------------------------------------------------------|---------------------|---------------------|
| `get_channels(page=None)`                                | `List[Channel]`     | Список каналов      |
| `get_channel(channel_id)`                                | `Optional[Channel]` | Информация о канале |
| `create_channel(name, description, is_public, settings)` | `Optional[Channel]` | Создать канал       |
| `update_channel(channel_id, ...)`                        | `bool`              | Обновить канал      |
| `delete_channel(channel_id)`                             | `bool`              | Удалить канал       |
| `join_channel(channel_id)`                               | `bool`              | Вступить в канал    |
| `leave_channel(channel_id)`                              | `bool`              | Покинуть канал      |

##### Посты в каналах

| Метод                                                            | Возвращает                 | Описание                 |
|------------------------------------------------------------------|----------------------------|--------------------------|
| `get_channel_messages(channel_id)`                               | `List[ChannelMessage]`     | Посты канала             |
| `send_channel_message(channel_id, text)`                         | `Optional[ChannelMessage]` | Отправить пост           |
| `edit_channel_message(channel_id, message_id, text)`             | `Optional[ChannelMessage]` | Редактировать пост       |
| `delete_channel_message(channel_id, message_id)`                 | `bool`                     | Удалить пост             |
| `pin_channel_message(channel_id, message_id)`                    | `bool`                     | Закрепить/открепить пост |
| `toggle_channel_message_reaction(channel_id, message_id, emoji)` | `List[Reaction]`           | Реакция на пост          |
| `get_channel_message_comments(channel_id, message_id)`           | `List[ChannelMessage]`     | Комментарии              |
| `get_channel_reactions(channel_id)`                              | `Dict`                     | Все реакции канала       |

##### Участники канала

| Метод                                                   | Возвращает            | Описание          |
|---------------------------------------------------------|-----------------------|-------------------|
| `get_channel_members(channel_id)`                       | `List[ChannelMember]` | Список участников |
| `update_channel_member_role(channel_id, user_id, role)` | `bool`                | Изменить роль     |
| `kick_channel_member(channel_id, user_id)`              | `bool`                | Удалить участника |

---

### User

Датакласс пользователя.

```python
@dataclass
class User:
    id: int  # ID пользователя
    username: str  # Имя пользователя
    nickname: str  # Отображаемое имя
    photo: str = ""  # Ссылка на фото
    avatar_emoji: Optional[str] = None  # Эмодзи-аватар
    is_verified: bool = False  # Верифицирован?
    is_admin: bool = False  # Админ?
```

#### Методы

```python
# Создать из словаря API
user = User.from_dict(data: Dict[str, Any]) -> User

# Строковое представление
str(user)  # "User(1, @username ✅ 👑)"
repr(user)  # "User(1, @username ✅ 👑)"
```

---

### Message

Датакласс личного сообщения.

```python
@dataclass
class Message:
    id: int  # ID сообщения
    sender: User  # Отправитель
    receiver: User  # Получатель
    text: str = ""  # Текст сообщения
    image: Optional[str] = None  # Изображение
    is_read: bool = False  # Прочитано?
    read_at: Optional[str] = None  # Дата прочтения
    edited_at: Optional[str] = None  # Дата редактирования
    created_at: str = ""  # Дата создания
    updated_at: str = ""  # Дата обновления
    reactions: List[Reaction] = field(default_factory=list)  # Реакции
    account: Optional[Account] = None  # Связанный аккаунт
```

#### Методы

| Метод                       | Возвращает          | Описание                 |
|-----------------------------|---------------------|--------------------------|
| `edit_text(new_text)`       | `Optional[Message]` | Редактировать текст      |
| `delete()`                  | `bool`              | Удалить сообщение        |
| `toggle_reaction(emoji)`    | `List[Reaction]`    | Добавить/убрать реакцию  |
| `is_edited()`               | `bool`              | Было ли отредактировано? |
| `has_reaction(emoji)`       | `bool`              | Есть ли реакция?         |
| `get_reaction_count(emoji)` | `int`               | Количество реакций       |

#### Пример

```python
msg = account.send_message(user_id, "Привет!")

# Редактирование
msg.edit_text("Новый текст")

# Реакция
msg.toggle_reaction("👍")

# Удаление
msg.delete()
```

---

### Chat

Датакласс диалога (чата).

```python
@dataclass
class Chat:
    id: int  # ID = partner.id
    user: User  # Собеседник (API использует "user")
    last_message: Optional[Message] = None  # Последнее сообщение
    unread_count: int = 0  # Непрочитанных сообщений
```

#### Свойства

```python
chat.partner  # Алиас для user (для совместимости)
```

#### Пример

```python
for chat in account.get_chats():
    print(f"Чат #{chat.id} с {chat.user.nickname}")
    print(f"Непрочитанных: {chat.unread_count}")
    if chat.last_message:
        print(f"Последнее: {chat.last_message.text}")
```

---

### Channel

Датакласс канала.

```python
@dataclass
class Channel:
    id: int  # ID канала
    name: str  # Название
    owner: User  # Владелец
    description: str = ""  # Описание
    image: Optional[str] = None  # Обложка
    is_public: bool = True  # Публичный?
    is_verified: bool = False  # Верифицирован?
    members_count: int = 0  # Количество участников
    is_member: bool = False  # Я участник?
    is_admin: bool = False  # Я админ?
    settings: Dict[str, Any] = field(default_factory=dict)  # Настройки
    subscriber_permissions: Dict[str, bool] = field(default_factory=dict)  # Права
    allowed_reactions: List[str] = field(default_factory=list)  # Разрешённые реакции
    comments_channel_id: Optional[int] = None  # Канал для комментариев
    created_at: str = ""  # Дата создания
    updated_at: str = ""  # Дата обновления
```

#### Пример

```python
for ch in account.get_channels():
    print(f"#{ch.id} {ch.name}")
    print(f"  Участников: {ch.members_count}")
    print(f"  Владелец: {ch.owner.nickname}")
    print(f"  Я участник: {ch.is_member}")
```

---

### ChannelMessage

Датакласс поста или комментария в канале.

```python
@dataclass
class ChannelMessage:
    id: int  # ID поста
    channel_id: int  # ID канала
    author: User  # Автор
    text: str = ""  # Текст
    image: Optional[str] = None  # Изображение
    is_pinned: bool = False  # Закреплён?
    comments_count: int = 0  # Комментариев
    reactions: List[Reaction] = field(default_factory=list)  # Реакции
    created_at: str = ""  # Дата создания
    updated_at: str = ""  # Дата обновления
    account: Optional[Account] = None  # Связанный аккаунт
```

#### Методы

| Метод                       | Возвращает                 | Описание                |
|-----------------------------|----------------------------|-------------------------|
| `edit_text(new_text)`       | `Optional[ChannelMessage]` | Редактировать текст     |
| `delete()`                  | `bool`                     | Удалить пост            |
| `toggle_reaction(emoji)`    | `List[Reaction]`           | Добавить/убрать реакцию |
| `pin()`                     | `bool`                     | Закрепить/открепить     |
| `get_comments()`            | `List[ChannelMessage]`     | Получить комментарии    |
| `is_edited()`               | `bool`                     | Был ли отредактирован?  |
| `has_reaction(emoji)`       | `bool`                     | Есть ли реакция?        |
| `get_reaction_count(emoji)` | `int`                      | Количество реакций      |

#### Пример

```python
post = account.send_channel_message(ch_id, "Мой пост!")

# Реакция
post.toggle_reaction("🔥")

# Закрепление
post.pin()

# Комментарии
comments = post.get_comments()

# Удаление
post.delete()
```

---

### ChannelMember

Датакласс участника канала.

```python
@dataclass
class ChannelMember:
    user: User  # Пользователь
    role: str = "member"  # Роль: owner, admin, member
    joined_at: str = ""  # Дата вступления
```

#### Пример

```python
for member in account.get_channel_members(ch_id):
    print(f"{member.user.nickname} — {member.role}")
```

---

### Reaction

Датакласс реакции на сообщение.

```python
@dataclass
class Reaction:
    emoji: str  # Эмодзи реакции
    count: int  # Количество
    user_ids: List[int] = field(default_factory=list)  # Кто поставил
```

#### Пример

```python
for reaction in message.reactions:
    print(f"{reaction.emoji} — {reaction.count}")
    print(f"Поставили: {reaction.user_ids}")
```

---

### KaalitionClient

Клиент для работы с публичными данными (без авторизации).

```python
client = KaalitionClient()
```

#### Создание

```python
from kaalition_lib import KaalitionClient

# Стандартный
client = KaalitionClient()

# С кастомным URL
client = KaalitionClient(base_url="https://test.kaalition.ru")
```

#### Методы

| Метод            | Возвращает      | Описание          |
|------------------|-----------------|-------------------|
| `get_projects()` | `List[Project]` | Список проектов   |
| `get_members()`  | `List[Member]`  | Список участников |
| `get_news()`     | `List[News]`    | Список новостей   |

---

### Project

Датакласс проекта.

```python
@dataclass
class Project:
    id: int  # ID проекта
    title: str  # Название
    description: str  # Описание
    image: Optional[str] = None  # Обложка
    button_text: str = ""  # Текст кнопки
    link: str = ""  # Ссылка
    order: int = 0  # Порядок
    is_active: bool = True  # Активен?
    created_at: str = ""  # Дата создания
    updated_at: str = ""  # Дата обновления
```

---

### Member

Датакласс участника (организации/команды).

```python
@dataclass
class Member:
    id: int  # ID
    nickname: str  # Никнейм
    photo: Optional[str] = None  # Фото
    group: str = ""  # Группа
    telegram: str = ""  # Telegram
    itd: str = ""  # ИТД
    order: int = 0  # Порядок
    is_active: bool = True  # Активен?
    created_at: str = ""  # Дата создания
    updated_at: str = ""  # Дата обновления
```

---

### News

Датакласс новости.

```python
@dataclass
class News:
    id: int  # ID новости
    title: str  # Заголовок
    content: str  # Содержание
    subtitle: Optional[str] = None  # Подзаголовок
    image: Optional[str] = None  # Изображение
    is_published: bool = True  # Опубликовано?
    views: int = 0  # Просмотры
    created_at: str = ""  # Дата создания
    updated_at: str = ""  # Дата обновления
```

---

## Примеры использования

### Личные сообщения

```python
from kaalition_lib import Account

account = Account(email="mail@test.com", password="pass")

# Поиск пользователей
users = account.search_users("никнейм")
if not users:
    print("Пользователь не найден")
    exit()

user_id = users[0].id

# Отправка сообщения
msg = account.send_message(user_id, "Привет!")
if msg:
    print(f"Отправлено! ID: {msg.id}")
else:
    print("Ошибка отправки")

# История чата
history = account.get_chat_history(user_id)
print(f"Сообщений в чате: {len(history)}")

for m in history:
    direction = "→" if m.sender.id == account.id else "←"
    edited = " (ред.)" if m.is_edited() else ""
    print(f"{direction} {m.sender.nickname}: {m.text}{edited}")

# Работа с сообщением
if msg:
    msg.edit_text("Отредактированный текст")
    msg.toggle_reaction("👍")
    msg.delete()

# Все чаты
print("\nСписок чатов:")
for chat in account.get_chats():
    print(f"#{chat.id} {chat.user.nickname}: {chat.unread_count} непрочитанных")
```

### Каналы

```python
from kaalition_lib import Account

account = Account(email="mail@test.com", password="pass")

# Список каналов
channels = account.get_channels()
print(f"Всего каналов: {len(channels)}")

for ch in channels:
    member_status = " [участник]" if ch.is_member else ""
    verified = " ✅" if ch.is_verified else ""
    print(f"#{ch.id} {ch.name}{verified}{member_status}")
    print(f"   Участников: {ch.members_count}, Владелец: {ch.owner.nickname}")

# Создание канала
channel = account.create_channel(
    name="Новый канал",
    description="Описание канала",
    is_public=True
)

if channel:
    ch_id = channel.id
    print(f"\nКанал создан! ID: {ch_id}")

    # Вступление
    account.join_channel(ch_id)
    print("Вступили в канал")

    # Отправка поста
    post = account.send_channel_message(ch_id, "Первый пост!")
    if post:
        print(f"Пост создан! ID: {post.id}")

        # Реакция
        post.toggle_reaction("🔥")

        # Закрепление
        post.pin()

        # Комментарии
        comments = post.get_comments()

        # Редактирование
        post.edit_text("Отредактированный пост")

        # Удаление
        post.delete()

    # Участники канала
    members = account.get_channel_members(ch_id)
    for member in members:
        print(f"  {member.user.nickname}: {member.role}")

    # Изменение роли участника (если вы админ)
    if channel.is_admin:
        account.update_channel_member_role(ch_id, user_id, "admin")

    # Покидание канала
    account.leave_channel(ch_id)
    print("Покинули канал")

    # Удаление канала (если вы владелец)
    if channel.owner.id == account.id:
        account.delete_channel(ch_id)
        print("Канал удалён")
else:
    print("Не удалось создать канал")
```

### Профиль

```python
from kaalition_lib import Account

account = Account(email="mail@test.com", password="pass")

# Просмотр профиля
print(f"Никнейм: {account.nickname}")
print(f"Email: {account.email}")
print(f"Тема: {account.theme}")
print(f"Профиль публичный: {account.profile_public}")

# Обновление профиля
account.update_profile(
    nickname="Новый ник",
    bio="Обо мне",
    avatar_emoji="😎"
)

# Смена темы
account.update_theme("light")  # или "dark"

# Настройки приватности
account.update_privacy(
    profile_public=True,
    show_online=False,
    allow_messages=True,
    show_in_search=True
)

# Смена пароля
account.update_password(
    current_password="СтарыйПароль123",
    new_password="НовыйПароль456",
    new_password_confirmation="НовыйПароль456"
)

# Управление сессиями
sessions = account.get_sessions()
print(f"Активных сессий: {len(sessions)}")

for s in sessions:
    current = " (текущая)" if s.get("is_current") else ""
    print(f"  {s.get('device')} — {s.get('ip_address')}{current}")

# Удаление всех сессий кроме текущей
account.delete_all_sessions()

# Выход из аккаунта
account.logout()
```

### Публичные данные

```python
from kaalition_lib import KaalitionClient

client = KaalitionClient()

# Проекты
print("=== Проекты ===")
for p in client.get_projects():
    print(f"{p.title}: {p.link}")

# Участники
print("\n=== Участники ===")
for m in client.get_members():
    print(f"{m.nickname} ({m.group})")

# Новости
print("\n=== Новости ===")
for n in client.get_news():
    print(f"{n.title}")
    print(f"  {n.content[:100]}...")
```

---

## Частые вопросы

### Как получить токен?

```python
account = Account(email="mail@test.com", password="pass")
token = account.token  # Сохраните этот токен
```

### Как использовать сохранённый токен?

```python
account = Account(token="сохранённый_токен")
```

### Как работать с несколькими аккаунтами?

```python
tokens = {
    "acc1": "token1",
    "acc2": "token2"
}

accounts = {name: Account(token=tok) for name, tok in tokens.items()}
```

### Как отправить сообщение с изображением?

```python
# В текущей версии отправка с изображением требует дополнительной реализации
# Используйте базовый метод send_message с text
account.send_message(user_id, "Текст сообщения")
```

### Как получить все посты канала?

```python
# get_channels загружает все страницы автоматически
channels = account.get_channels()

# get_channel_messages возвращает все посты одной страницы
posts = account.get_channel_messages(channel_id)
```

### Как проверить права на канал?

```python
ch = account.get_channel(channel_id)

if ch.owner.id == account.id:
    print("Вы владелец")
elif ch.is_admin:
    print("Вы админ")
elif ch.is_member:
    print("Вы участник")
else:
    print("Вы не состоите в канале")
```

---

## Версии

| Версия | Описание                                      |
|--------|-----------------------------------------------|
| 3.1.0  | Добавлена работа с каналами, чатами, профилем |
| 3.0.0  | Переход на новую структуру                    |
| 2.0.0  | Добавлены сообщения                           |
| 1.0.0  | Базовый функционал                            |

---

## Лицензия

[MIT](https://github.com/Dima-programmer/KAALITION_API_LIB/blob/master/LICENSE)

## Автор

**Dima-Programmer**

- GitHub: [@Dima-programmer](https://github.com/Dima-programmer)

```

Теперь структура документации:

```

kaalition-lib/
├── docs/
│ └── README.md # Полная документация (ссылка сюда из основного README)
├── kaalition_lib/
│ ├── __init__.py
│ └── kaalition_lib.py
├── README.md # Краткое описание + ссылка на docs/README.md
├── setup.py
└── ...

```

В основном `README.md` добавь ссылку:

```markdown
## Документация

Полная документация доступна в [docs/README.md](docs/README.md)
```

#### Методы

| Метод            | Возвращает      | Описание          |
|------------------|-----------------|-------------------|
| `get_projects()` | `List[Project]` | Список проектов   |
| `get_members()`  | `List[Member]`  | Список участников |
| `get_news()`     | `List[News]`    | Список новостей   |

#### Пример

```python
client = KaalitionClient()

# Проекты
for project in client.get_projects():
    print(f"{project.title}: {project.link}")

# Участники
for member in client.get_members():
    print(f"{member.nickname} — {member.group}")

# Новости
for news in client.get_news():
    print(f"{news.title}: {news.content[:100]}...")
```

---

### Project

Датакласс проекта.

```python
@dataclass
class Project:
    id: int  # ID проекта
    title: str  # Название
    description: str = ""  # Описание
    image: Optional[str] = None  # Обложка
    button_text: str = ""  # Текст кнопки
    link: str = ""  # Ссылка
    order: int = 0  # Порядок
    is_active: bool = True  # Активен?
    created_at: str = ""  # Дата создания
    updated_at: str = ""  # Дата обновления
```

---

### Member

Датакласс участника (организации/команды).

```python
@dataclass
class Member:
    id: int  # ID
    nickname: str  # Никнейм
    photo: Optional[str] = None  # Фото
    group: str = ""  # Группа
    telegram: str = ""  # Telegram
    itd: str = ""  # ИТД
    order: int = 0  # Порядок
    is_active: bool = True  # Активен?
    created_at: str = ""  # Дата создания
    updated_at: str = ""  # Дата обновления
```

---

### News

Датакласс новости.

```python
@dataclass
class News:
    id: int  # ID новости
    title: str  # Заголовок
    content: str = ""  # Содержание
    subtitle: Optional[str] = None  # Подзаголовок
    image: Optional[str] = None  # Обложка
    is_published: bool = True  # Опубликована?
    views: int = 0  # Просмотры
    created_at: str = ""  # Дата создания
    updated_at: str = ""  # Дата обновления
```

---

## Примеры использования

### Личные сообщения

```python
from kaalition_lib import Account

account = Account(email="mail@test.com", password="pass")

# Поиск пользователя
users = account.search_users("никнейм")
if not users:
    print("Пользователь не найден")
    exit()

user_id = users[0].id

# Отправка сообщения
msg = account.send_message(user_id, "Привет!")
if msg:
    print(f"Отправлено! ID: {msg.id}")

# История чата
history = account.get_chat_history(user_id)
print(f"Всего сообщений: {len(history)}")

for m in history:
    direction = "→" if m.sender.id == account.id else "←"
    edited = " (ред.)" if m.is_edited() else ""
    print(f"{direction} {m.sender.nickname}: {m.text}{edited}")

# Работа с сообщением
msg.edit_text("Новый текст")
msg.toggle_reaction("👍")
msg.delete()

# Список всех чатов
for chat in account.get_chats():
    print(f"Чат #{chat.id} с {chat.user.nickname}")
    print(f"Непрочитанных: {chat.unread_count}")
```

### Каналы

```python
from kaalition_lib import Account

account = Account(email="mail@test.com", password="pass")

# Список каналов
print("Мои каналы:")
for ch in account.get_channels():
    member_status = " [участник]" if ch.is_member else ""
    verified = " ✅" if ch.is_verified else ""
    print(f"#{ch.id} {ch.name}{verified}{member_status}")
    print(f"   Участников: {ch.members_count}")
    print(f"   Владелец: {ch.owner.nickname}")

# Создание канала
channel = account.create_channel(
    name="Мой канал",
    description="Описание канала",
    is_public=True
)

if channel:
    ch_id = channel.id
    print(f"Создан канал: {channel.name} (ID: {ch_id})")

    # Вступление
    account.join_channel(ch_id)
    print("Вступили в канал")

    # Посты
    post = account.send_channel_message(ch_id, "Первый пост!")
    if post:
        print(f"Пост создан: #{post.id}")

        # Реакция
        post.toggle_reaction("🔥")

        # Закрепление
        if post.pin():
            print("Пост закреплён")

        # Комментарии
        comments = post.get_comments()
        print(f"Комментариев: {len(comments)}")

        # Редактирование
        post.edit_text("Отредактированный текст")

        # Удаление
        post.delete()
        print("Пост удалён")

    # Участники канала
    print("Участники канала:")
    for member in account.get_channel_members(ch_id):
        print(f"  {member.user.nickname}: {member.role}")

    # Выход из канала
    account.leave_channel(ch_id)
    print("Покинули канал")

    # Удаление (если владелец)
    account.delete_channel(ch_id)
    print("Канал удалён")
```

### Профиль

```python
from kaalition_lib import Account

account = Account(email="mail@test.com", password="pass")

# Просмотр профиля
print(f"Никнейм: {account.nickname}")
print(f"Email: {account.email}")
print(f"О себе: {account.bio}")
print(f"Тема: {account.theme}")
print(f"Верифицирован: {account.is_verified}")
print(f"Админ: {account.is_admin}")

# Обновление профиля
account.update_profile(
    nickname="Новый ник",
    bio="Обновлённое описание"
)

# Смена темы
account.update_theme("light")

# Настройки приватности
account.update_privacy(
    profile_public=True,
    show_online=False,
    allow_messages=True,
    show_in_search=True
)

# Смена пароля
account.update_password(
    current_password="СтарыйПароль123",
    new_password="НовыйПароль456",
    new_password_confirmation="НовыйПароль456"
)

# Управление сессиями
print("\nАктивные сессии:")
for session in account.get_sessions():
    device = session.get("device", "Unknown")
    ip = session.get("ip_address", "Unknown")
    is_current = session.get("is_current", False)
    current = " (текущая)" if is_current else ""
    print(f"  {device} — {ip}{current}")

# Удаление всех сессий кроме текущей
account.delete_all_sessions()

# Выход
account.logout()
print("Вышли из аккаунта")
```

### Публичные данные

```python
from kaalition_lib import KaalitionClient

client = KaalitionClient()

# Проекты
print("Проекты:")
for p in client.get_projects():
    print(f"  {p.title}: {p.link}")
    if p.image:
        print(f"    Обложка: {p.image}")

# Участники
print("\nУчастники:")
for m in client.get_members():
    print(f"  {m.nickname} ({m.group})")
    if m.telegram:
        print(f"    Telegram: {m.telegram}")

# Новости
print("\nНовости:")
for n in client.get_news():
    print(f"  {n.title}")
    print(f"    Просмотров: {n.views}")
    print(f"    {n.content[:100]}...")
```

---

## Частые вопросы

### Как получить токен?

```python
account = Account(email="mail@test.com", password="pass")
token = account.token
print(f"Ваш токен: {token}")
```

### Как использовать токен позже?

```python
account = Account(token="eyJ0eXAiOiJKV1Qi...")
```

### Как работать с несколькими аккаунтами?

```python
accounts = {
    "acc1": Account(email="mail1@test.com", password="pass1"),
    "acc2": Account(email="mail2@test.com", password="pass2"),
}

for name, acc in accounts.items():
    print(f"{name}: {acc.nickname}")
```

### Как отправить сообщение с изображением?

```python
# Отправка с изображением (через файл)
with open("image.jpg", "rb") as f:
    account.session.post(
        account._send_message_url,
        data={"receiver_id": user_id, "message": "Подпись"},
        files={"image": f},
        headers=account._get_headers(account.token)
    )
```

### Как проверить права админа/владельца?

```python
channel = account.get_channel(ch_id)

if channel.owner.id == account.id:
    print("Вы владелец канала")
elif channel.is_admin:
    print("Вы админ канала")
elif channel.is_member:
    print("Вы участник канала")
else:
    print("Вы не состоите в канале")
```

### Как работает пагинация в каналах?

```python
# Автоматически загружает все страницы
all_channels = account.get_channels()

# Конкретная страница
first_page = account.get_channels(page=1)
second_page = account.get_channels(page=2)
```

### Как обрабатывать ошибки?

```python
from kaalition_lib import (
    KaalitionError,
    LoginError,
    ChannelError,
    MessageError
)

try:
    account = Account(email="wrong", password="wrong")
except LoginError as e:
    print(f"Ошибка входа: {e}")
except TokenError as e:
    print(f"Ошибка токена: {e}")
except KaalitionError as e:
    print(f"Ошибка API: {e}")
```

---

## Версии

| Версия | Дата | Изменения                                     |
|--------|------|-----------------------------------------------|
| 3.1.0  | 2026 | Добавлена работа с каналами, чатами, профилем |
| 3.0.0  | 2026 | Переход на новую структуру Account            |
| 2.0.0  | 2026 | Добавлены Message, Reaction                   |
| 1.0.0  | 2026 | Первая версия                                 |

---

## Лицензия

[MIT](https://github.com/Dima-programmer/KAALITION_API_LIB/blob/master/LICENSE)

## Автор

**Dima-Programmer**

- GitHub: [@Dima-programmer](https://github.com/Dima-programmer)
