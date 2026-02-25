# Kaalition API Library

Python библиотека для работы с API сайта kaalition.ru.

## Описание

Библиотека упрощает взаимодействие с API:
- HTTP-запросы
- Аутентификация
- Работа с сообщениями и пользователями

## Установка

### Требования

- Python 3.8+
- requests
- faker

### pip

```bash
pip install kaalition-lib
```

### Из исходного кода

```bash
git clone https://github.com/Dima-programmer/KAALITION_API_LIB.git
cd KAALITION_API_LIB/kaalition-lib
pip install -e .
```

## ⚠️ Важные изменения в 3.0.0

Версия **3.0.0** содержит критические изменения:

### Удалено

- Функции сохранения/загрузки аккаунтов
- Поддержка коллекции аккаунтов
- Методы регистрации и поддержки

### Новая инициализация

Теперь `Account` инициализируется напрямую:

```python
# Вместо client.login()
account = Account(email="email@mail.ru", password="password")

# Вместо client.create_from_token()
account = Account(token="your_token")
```

## Быстрый старт

```python
from kaalition_lib import Account

# Вход через email и пароль
account = Account(email="email@mail.ru", password="password")

# Или из токена
account = Account(token="your_token")

print(f"Вошли как: {account.username}")
print(f"ID: {account.id}")

# Поиск пользователей
users = account.search_users("никнейм")

if users:
    user = users[0]
    
    # Отправка сообщения
    message = account.send_message(user, "Привет!")
    print(f"Отправлено: {message.id}")
    
    # Методы Message
    message.edit_text("Новый текст")
    message.toggle_reaction("👍")
    message.delete()
    
    # История чата
    messages = account.get_chat_history(user)
    for msg in messages:
        print(f"{msg.sender.nickname}: {msg.text}")
```

## API Reference

### Account

Класс для авторизованных операций.

```python
account = Account(email="email@mail.ru", password="password")

# Поля
print(account.id)           # ID пользователя
print(account.username)     # Имя пользователя
print(account.nickname)     # Отображаемое имя
print(account.email)        # Email
print(account.avatar)       # Аватар
print(account.is_verified)  # Верификация
print(account.is_admin)     # Админ
```

**Методы:**

| Метод | Описание |
|-------|----------|
| `refresh()` | Синхронизация с сервером |
| `is_active()` | Проверка активности |
| `update_profile(...)` | Обновление профиля |
| `search_users(query)` | Поиск пользователей |
| `send_message(user, text)` | Отправка сообщения |
| `get_chat_history(user)` | История чата |
| `edit_message_text(msg, text)` | Редактирование сообщения |
| `delete_message(msg)` | Удаление сообщения |
| `toggle_message_reaction(msg, emoji)` | Реакция на сообщение |

### KaalitionClient

Клиент для публичных данных (без авторизации).

```python
from kaalition_lib import KaalitionClient

client = KaalitionClient()
```

**Методы:**

| Метод | Описание |
|-------|----------|
| `get_projects()` | Список проектов |
| `get_members()` | Список участников |
| `get_news()` | Список новостей |

### User

```python
@dataclass
class User:
    id: int
    username: str
    nickname: str
    photo: str = ""
    avatar_emoji: Optional[str] = None
    is_verified: bool = False
    is_admin: bool = False
```

### Message

```python
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
    account: Optional[Account] = None
```

**Методы:**

```python
message.edit_text("Новый текст")      # Редактировать
message.toggle_reaction("👍")          # Добавить/убрать реакцию
message.delete()                       # Удалить
message.is_edited()                    # Было ли отредактировано
message.has_reaction("👍")             # Есть ли реакция
message.get_reaction_count("👍")       # Количество реакций
```

### Reaction

```python
@dataclass
class Reaction:
    emoji: str
    count: int
    user_ids: List[int]
```

### Project, Member, News

```python
@dataclass
class Project:
    id: int
    title: str
    description: str
    image: Optional[str] = None
    button_text: str = ""
    link: str = ""

@dataclass
class Member:
    id: int
    nickname: str
    photo: Optional[str] = None
    group: str = ""
    telegram: str = ""

@dataclass
class News:
    id: int
    title: str
    content: str
    subtitle: Optional[str] = None
    image: Optional[str] = None
    views: int = 0
```

## Примеры

### Работа с сообщениями

```python
from kaalition_lib import Account

account = Account(email="email@mail.ru", password="password")

# Поиск
users = account.search_users("друг")
if not users:
    print("Не найден")
    exit()

user = users[0]

# Отправка
message = account.send_message(user, "Привет!")
if message:
    print(f"Отправлено: {message.id}")

# Редактирование
message.edit_text("Исправленное привет!")

# Реакция
message.toggle_reaction("❤️")

# Удаление
message.delete()
```

### История чата

```python
from kaalition_lib import Account

account = Account(email="email@mail.ru", password="password")

users = account.search_users("собеседник")
if users:
    messages = account.get_chat_history(users[0])
    
    for msg in messages:
        direction = "→" if msg.sender.id == account.id else "←"
        edited = " (ред.)" if msg.is_edited() else ""
        print(f"{direction} {msg.sender.nickname}: {msg.text}{edited}")
```

### Публичные данные

```python
from kaalition_lib import KaalitionClient

client = KaalitionClient()

for p in client.get_projects():
    print(f"{p.title}: {p.link}")

for m in client.get_members():
    print(f"{m.nickname} ({m.group})")

for n in client.get_news():
    print(f"{n.title}: {n.content[:100]}...")
```

### Работа с токеном

```python
from kaalition_lib import Account

# Сохраните токен после входа
account = Account(email="email@mail.ru", password="password")
token = account.token

# Позже используйте токен
account2 = Account(token=token)
```

## Исключения

```python
from kaalition_lib import (
    KaalitionError,
    LoginError,
    TokenError,
    MessageEditError,
    MessageDeleteError,
    ChatHistoryError,
)

try:
    account = Account(email="email@mail.ru", password="wrong")
except LoginError as e:
    print(f"Ошибка входа: {e}")

try:
    message.edit_text("Новый текст")
except MessageEditError as e:
    print(f"Ошибка: {e}")
```

## Константы

```python
from kaalition_lib import (
    DEFAULT_BASE_URL,      # "https://kaalition.ru"
    DEFAULT_USER_AGENT,    # User-Agent
    DEFAULT_EMAIL_DOMAINS, # Домены для email
)
```

## Частые вопросы

### Как получить токен?

```python
account = Account(email="email@mail.ru", password="password")
token = account.token  # Сохраните
```

### Как работать с несколькими аккаунтами?

```python
tokens = {"acc1": "token1", "acc2": "token2"}

accounts = {name: Account(token=tok) for name, tok in tokens.items()}
```

## Структура проекта

```
kaalition-lib/
├── kaalition_lib/
│   ├── __init__.py
│   └── kaalition_lib.py
├── setup.py
├── requirements.txt
├── README.md
└── CHANGELOG.md
```

## Лицензия

[MIT](https://github.com/Dima-programmer/KAALITION_API_LIB/blob/master/LICENSE)

## Автор

**Dima-Programmer**

- GitHub: [@Dima-programmer](https://github.com/Dima-programmer)

## Версия

3.0.0