# Kaalition API Library

Kaalition API Library — это Python библиотека с объектно-ориентированным интерфейсом для работы с API сайта kaalition.ru. Библиотека упрощает взаимодействие с API, беря на себя обработку HTTP-запросов, аутентификацию и управление ошибками.

## Установка

### Требования

- Python 3.8+
- requests
- faker

### pip (рекомендуется)

```bash
pip install kaalition-lib
```

### Из исходного кода

```bash
git clone https://github.com/Dima-programmer/KAALITION_API_LIB/kaalition-lib.git
cd kaalition-lib
pip install -e .
```

## Быстрый старт

```python
from kaalition_lib import KaalitionClient

# Создание клиента и регистрация аккаунта
client = KaalitionClient()
account = client.register()

print(f"Аккаунт создан: {account.username}")
print(f"ID пользователя: {account.id}")

# Поиск пользователей
users = account.search_users("никнейм")

if users:
    # Отправка сообщения (возвращает объект Message)
    message = account.send_message(users[0], "Привет!")
    print(f"Отправлено сообщение: {message.text}")
    print(f"ID сообщения: {message.id}")
    
    # Редактирование сообщения
    if message:
        updated = account.edit_message_text(message, "Исправленное привет!")
        print(f"Обновлено: {updated.text}")
        print(f"Отредактировано: {updated.is_edited()}")
    
    # Установка реакции
    if message:
        reactions = account.toggle_message_reaction(message, "👍")
        print(f"Количество реакций: {len(reactions)}")
    
    # Удаление сообщения
    if message:
        account.delete_message(message)
        print("Сообщение удалено")
    
    # Получение истории чата
    messages = account.get_chat_history(users[0])
    print(f"Сообщений в чате: {len(messages)}")
    
    for msg in messages:
        print(f"[{msg.created_at}] {msg.sender.nickname}: {msg.text}")
```

## Основные изменения в v2.0.0

### Новая система наследования

`Account` теперь наследуется сразу от `KaalitionClient` и `User`, что исключает дублирование полей и упрощает работу с данными пользователя. Все поля `User` доступны напрямую из `Account`:

```python
account = client.register()

# Поля User доступны напрямую
print(account.id)
print(account.username)
print(account.nickname)
print(account.is_verified)
print(account.is_admin)
```

### Упрощённая инициализация

Теперь для создания `Account` достаточно передать только:

```python
# Из токена
account = Account(token="your_token")

# Из email и пароля (автоматически выполнит вход)
account = Account(email="test@mail.ru", password="password")

# Все остальные поля заполняются автоматически при sync с сервером
```

### Новый класс Message

Полноценный класс для работы с сообщениями с методами управления:

```python
@dataclass
class Message:
    id: int                      # ID сообщения
    sender: User                 # Отправитель как объект User
    receiver: User               # Получатель как объект User
    text: str                    # Текст сообщения
    image: Optional[str]         # Путь к изображению
    is_read: bool                # Прочитано ли
    read_at: Optional[str]       # Дата прочтения
    edited_at: Optional[str]     # Дата редактирования
    created_at: str              # Дата создания
    updated_at: str              # Дата обновления
    reactions: List[Reaction]    # Список реакций
    
    # Методы
    def is_edited(self) -> bool           # Проверка на редактирование
    def has_reaction(emoji: str) -> bool   # Проверка наличия реакции
    def get_reaction_count(emoji: str) -> int  # Количество реакций
```

### Новые исключения

```python
from kaalition_lib import (
    KaalitionError,           # Базовое исключение
    RegistrationError,        # Ошибка регистрации
    LoginError,               # Ошибка входа
    TokenError,               # Ошибка токена
    ProfileUpdateError,       # Ошибка обновления профиля
    UserNotFoundError,        # Пользователь не найден
    MessageError,             # Базовое исключение для сообщений
    MessageNotFoundError,     # Сообщение не найдено
    MessageEditError,         # Ошибка редактирования
    MessageDeleteError,       # Ошибка удаления
    MessageReactionError,     # Ошибка реакции
    ChatHistoryError,         # Ошибка истории чата
)

try:
    account.edit_message_text(message, "Новый текст")
except MessageEditError as e:
    print(f"Ошибка редактирования: {e}")
```

## API Reference

### KaalitionClient

Базовый клиент для операций без авторизации.

```python
from kaalition_lib import KaalitionClient

client = KaalitionClient(
    base_url="https://kaalition.ru",  # Базовый URL (по умолчанию)
    accounts_file="accounts.json",    # Файл для сохранения аккаунтов
    user_agent="..."                  # User-Agent (по умолчанию)
)
```

**Методы:**

| Метод | Описание | Возвращает |
|-------|----------|------------|
| `register()` | Регистрация нового аккаунта | `Account` |
| `login(email, password)` | Вход в аккаунт | `Account` |
| `create_from_token(token)` | Создание аккаунта из токена | `Account` |
| `load_accounts(active_only=True)` | Загрузка сохранённых аккаунтов | `List[Account]` |
| `clean_inactive(create_backup=True)` | Удаление неактивных аккаунтов | `Tuple[int, str]` |
| `get_projects()` | Получение списка проектов | `List[Project]` |
| `get_members()` | Получение списка участников | `List[Member]` |
| `get_news()` | Получение списка новостей | `List[News]` |

### Account

Аккаунт с авторизацией. Наследуется от `KaalitionClient` и `User`.

```python
# Создание через регистрацию
account = client.register()

# Создание через вход
account = client.login("email@mail.ru", "password")

# Создание из токена
account = client.create_from_token("your_token")

# Поля User доступны напрямую
print(account.id)           # ID пользователя
print(account.username)     # Имя пользователя
print(account.nickname)     # Отображаемое имя
print(account.email)        # Email
print(account.avatar)       # Путь к аватару
print(account.bio)          # Биография
print(account.is_verified)  # Верифицирован ли
print(account.is_admin)     # Является ли админом
```

**Методы профиля:**

| Метод | Описание | Возвращает |
|-------|----------|------------|
| `refresh()` | Синхронизация с сервером | `bool` |
| `is_active()` | Проверка активности | `bool` |
| `save()` | Сохранение аккаунта | `bool` |
| `mark_inactive()` | Пометить как неактивный | `bool` |
| `update_profile(...)` | Обновление профиля | `bool` |

**Методы поиска:**

| Метод | Описание | Возвращает |
|-------|----------|------------|
| `search_users(query)` | Поиск пользователей | `List[User]` |

**Методы сообщений:**

| Метод | Описание | Возвращает |
|-------|----------|------------|
| `send_message(user, text)` | Отправка сообщения | `Optional[Message]` |
| `get_chat_history(user)` | История чата | `List[Message]` |
| `edit_message_text(message, new_text)` | Редактирование | `Optional[Message]` |
| `delete_message(message)` | Удаление | `bool` |
| `toggle_message_reaction(message, emoji)` | Реакция | `List[Reaction]` |

**Методы поддержки:**

| Метод | Описание | Возвращает |
|-------|----------|------------|
| `create_support_ticket(subject, message)` | Создание тикета | `Tuple[bool, Optional[int], str]` |
| `send_to_support(message, subject)` | Отправка в поддержку | `Tuple[bool, str]` |

### User

```python
@dataclass
class User:
    id: int                      # ID пользователя
    username: str                # Имя пользователя
    nickname: str                # Отображаемое имя
    photo: str = ""              # Путь к фото
    avatar_emoji: Optional[str] = None  # Эмодзи аватара
    is_verified: bool = False    # Верифицирован ли
    is_admin: bool = False       # Является ли админом
    
    @classmethod
    def from_dict(data: Dict) -> User  # Создание из словаря
```

### Message

```python
@dataclass
class Message:
    id: int                      # ID сообщения
    sender: User                 # Отправитель
    receiver: User               # Получатель
    text: str = ""               # Текст сообщения
    image: Optional[str] = None  # Путь к изображению
    is_read: bool = False        # Прочитано ли
    read_at: Optional[str] = None  # Дата прочтения
    edited_at: Optional[str] = None  # Дата редактирования
    created_at: str = ""         # Дата создания
    updated_at: str = ""         # Дата обновления
    reactions: List[Reaction] = field(default_factory=list)  # Реакции
    
    @classmethod
    def from_dict(data: Dict, sender: User, receiver: User) -> Message
    
    def is_edited(self) -> bool              # Было ли отредактировано
    def has_reaction(emoji: str) -> bool     # Есть ли реакция
    def get_reaction_count(emoji: str) -> int  # Количество реакций
```

### Reaction

```python
@dataclass
class Reaction:
    emoji: str              # Эмодзи реакции
    count: int              # Количество
    user_ids: List[int]     # Список ID пользователей
    
    @classmethod
    def from_dict(data: Dict) -> Reaction
```

### Project

```python
@dataclass
class Project:
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
```

### Member

```python
@dataclass
class Member:
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
```

### News

```python
@dataclass
class News:
    id: int
    title: str
    content: str
    subtitle: Optional[str] = None
    image: Optional[str] = None
    is_published: bool = True
    views: int = 0
    created_at: str = ""
    updated_at: str = ""
```

## Примеры

### Работа с коллекцией аккаунтов

```python
from kaalition_lib import load_accounts, clean_accounts_file

# Загрузка активных аккаунтов
accounts = load_accounts("accounts.json", active_only=True)
print(f"Загружено аккаунтов: {len(accounts)}")

# Проверка активности и обновление
for acc in accounts:
    if acc.is_active():
        acc.update_profile(bio="Обновлено через API")
        acc.save()
        print(f"Обновлён: {acc.username}")

# Очистка неактивных аккаунтов
deleted, backup = clean_accounts_file("accounts.json")
print(f"Удалено: {deleted}, бэкап: {backup}")
```

### Массовая рассылка сообщений

```python
from kaalition_lib import KaalitionClient
import time

client = KaalitionClient()
account = client.login("email@mail.ru", "password")

# Поиск целевой аудитории
users = account.search_users("подписчик")

for user in users:
    if account.is_active():
        message = account.send_message(user, "Ваше сообщение")
        if message:
            print(f"Отправлено {user.nickname}: {message.id}")
        time.sleep(1)  # Задержка между сообщениями
```

### Работа с проектами, участниками и новостями

```python
from kaalition_lib import KaalitionClient

client = KaalitionClient()

# Проекты
projects = client.get_projects()
for project in projects:
    print(f"{project.title}: {project.link}")

# Участники
members = client.get_members()
for member in members:
    print(f"{member.nickname} ({member.group})")

# Новости
news = client.get_news()
for item in news:
    print(f"{item.title}: {item.content[:100]}...")
```

### Полная работа с сообщениями

```python
from kaalition_lib import KaalitionClient

client = KaalitionClient()
account = client.login("email@mail.ru", "password")

# Поиск пользователя
users = account.search_users("ник")
if not users:
    print("Пользователь не найден")
    exit()

user = users[0]
print(f"Чат с: {user.nickname}")

# Получение истории чата
messages = account.get_chat_history(user)
print(f"Сообщений в чате: {len(messages)}")

for msg in messages:
    # Определяем, отправитель или получатель
    direction = "→" if msg.sender.id == account.id else "←"
    edited = " (ред.)" if msg.is_edited() else ""
    print(f"{direction} {msg.sender.nickname}: {msg.text}{edited}")

# Отправка нового сообщения
new_message = account.send_message(user, "Привет из API!")
if new_message:
    print(f"Отправлено: {new_message.id}")

# Редактирование последнего сообщения
if messages:
    last_msg = messages[-1]
    if last_msg.sender.id == account.id:
        updated = account.edit_message_text(last_msg, "Исправленный текст")
        if updated:
            print(f"Отредактировано: {updated.text}")

# Установка реакции
if messages:
    reactions = account.toggle_message_reaction(messages[0], "❤️")
    print(f"Реакций на сообщении: {len(reactions)}")

# Удаление сообщения (своего)
if messages:
    if messages[-1].sender.id == account.id:
        account.delete_message(messages[-1])
        print("Удалено")
```

### Обработка ошибок

```python
from kaalition_lib import (
    KaalitionClient,
    KaalitionError,
    RegistrationError,
    LoginError,
    MessageEditError,
    MessageDeleteError,
    ChatHistoryError,
)

client = KaalitionClient()

try:
    # Регистрация
    account = client.register()
    print(f"Создан: {account.username}")
    
except RegistrationError as e:
    print(f"Ошибка регистрации: {e}")

try:
    # Вход
    account = client.login("email@mail.ru", "password")
    print(f"Вход выполнен: {account.username}")
    
except LoginError as e:
    print(f"Ошибка входа: {e}")

try:
    # Редактирование сообщения
    account.edit_message_text(message, "Новый текст")
    
except MessageEditError as e:
    print(f"Не удалось редактировать: {e}")

try:
    # Удаление сообщения
    account.delete_message(message)
    
except MessageDeleteError as e:
    print(f"Не удалось удалить: {e}")

try:
    # История чата
    messages = account.get_chat_history(user)
    
except ChatHistoryError as e:
    print(f"Ошибка получения истории: {e}")
```

## Константы

```python
from kaalition_lib import (
    DEFAULT_BASE_URL,        # "https://kaalition.ru"
    DEFAULT_ACCOUNTS_FILE,   # "accounts.json"
    DEFAULT_USER_AGENT,      # User-Agent браузера
    DEFAULT_DELAY,           # 2 секунды
    DEFAULT_EMAIL_DOMAINS,   # Список доменов для генерации email
)
```

## Утилиты

```python
from kaalition_lib import (
    load_accounts,           # Загрузка аккаунтов из файла
    save_accounts,           # Сохранение аккаунтов в файл
    get_active_accounts,     # Фильтрация активных аккаунтов
    clean_accounts_file,     # Очистка неактивных аккаунтов
    parse_wait_time,         # Парсинг времени ожидания из ответа
)
```

### load_accounts

```python
accounts = load_accounts(
    filepath="accounts.json",    # Путь к файлу
    active_only=True             # Только активные
)
```

### save_accounts

```python
success = save_accounts(
    accounts=[account1, account2],
    filepath="accounts.json"
)
```

### clean_accounts_file

```python
deleted, backup = clean_accounts_file(
    filepath="accounts.json",
    create_backup=True
)
print(f"Удалено: {deleted}, бэкап: {backup}")
```

### parse_wait_time

```python
wait_time = parse_wait_time(response_text)
if wait_time:
    print(f"Подождите {wait_time} секунд")
```

## Структура проекта

```
kaalition-lib/
├── kaalition_lib/
│   ├── __init__.py          # Экспорт публичных API
│   ├── kaalition_lib.py     # Основной код библиотеки
│   └── README.md            # Документация
├── setup.py                 # Конфигурация пакета
├── requirements.txt         # Зависимости
└── README.md                # Этот файл
```

## Обновление с v1.x до v2.0.0

### Старый код (v1.x)

```python
from kaalition_lib import KaalitionClient, Account, User

client = KaalitionClient()

# Регистрация с явным указанием всех полей
account = client.register(
    username="test_user",
    email="test@mail.ru",
    password="password123"
)

# Поля Account и User были раздельными
print(account.username)
print(account.nickname)
```

### Новый код (v2.0.0)

```python
from kaalition_lib import KaalitionClient, Account, User

client = KaalitionClient()

# Регистрация с автоматической генерацией данных
account = client.register()

# Account теперь включает все поля User
print(account.id)           # ID пользователя
print(account.username)     # Имя пользователя
print(account.nickname)     # Отображаемое имя
print(account.is_verified)  # Верификация
print(account.is_admin)     # Админ

# send_message теперь возвращает Message
message = account.send_message(user, "Привет!")
print(message.text)         # Текст сообщения
print(message.sender)       # Отправитель (User)
print(message.receiver)     # Получатель (User)
```

### Изменения в методах сообщений

| v1.x | v2.0.0 |
|------|--------|
| `send_message(user, text)` → `Tuple[bool, str]` | `send_message(user, text)` → `Optional[Message]` |
| Нет | `get_chat_history(user)` → `List[Message]` |
| Нет | `edit_message_text(message, text)` → `Optional[Message]` |
| Нет | `delete_message(message)` → `bool` |
| Нет | `toggle_message_reaction(message, emoji)` → `List[Reaction]` |

## Частые вопросы

### Как получить токен?

Токен можно получить через регистрацию или вход:

```python
client = KaalitionClient()
account = client.register()  # Токен в account.token
print(account.token)
```

### Как сохранить и загрузить аккаунты?

```python
# Автосохранение (включено по умолчанию)
account = client.register()  # Сохраняется автоматически

# Ручное сохранение
account.save()

# Загрузка
accounts = client.load_accounts()
```

### Как работать с историей чата?

```python
# Получение истории
messages = account.get_chat_history(user)

# Сортировка (старые сообщения сверху)
messages.sort(key=lambda m: m.created_at)

# Фильтрация только своих сообщений
my_messages = [m for m in messages if m.sender.id == account.id]

# Фильтрация по наличию реакций
messages_with_reactions = [m for m in messages if m.reactions]
```

### Как обрабатывать ошибки?

```python
from kaalition_lib import (
    MessageEditError,
    MessageDeleteError,
    MessageReactionError,
)

try:
    account.edit_message_text(message, "Новый текст")
except MessageEditError:
    print("Не удалось редактировать")

try:
    account.delete_message(message)
except MessageDeleteError:
    print("Не удалось удалить")

try:
    account.toggle_message_reaction(message, "👍")
except MessageReactionError:
    print("Не удалось добавить реакцию")
```

## Лицензия

[MIT License](https://github.com/Dima-programmer/KAALITION_API_LIB/blob/master/LICENSE)

## Автор

**Dima-Programmer**

- GitHub: [@Dima-programmer](https://github.com/Dima-programmer)

## Поддержка проекта

Если библиотека оказалась полезной, вы можете:

- Поставить звезду на GitHub
- Сообщить об ошибке через Issues
- Предложить улучшения через Pull Requests

Ваша обратная связь помогает делать библиотеку лучше.

## Журнал изменений

### v2.0.0 (2026)

**Новые функции:**
- `Account` теперь наследуется от `KaalitionClient` и `User`
- Упрощённая инициализация с автоматическим заполнением данных
- Новый класс `Message` с полной информацией об отправителе и получателе
- Новый класс `Reaction` для работы с реакциями
- Метод `get_chat_history()` для получения истории чата
- Метод `edit_message_text()` для редактирования сообщений
- Метод `delete_message()` для удаления сообщений
- Метод `toggle_message_reaction()` для управления реакциями
- `send_message()` теперь возвращает объект `Message`

**Новые исключения:**
- `MessageError`
- `MessageNotFoundError`
- `MessageEditError`
- `MessageDeleteError`
- `MessageReactionError`
- `ChatHistoryError`

**Улучшения:**
- Оптимизирована структура классов
- Улучшена обработка ошибок
- Добавлены методы для проверки состояния сообщений

### v1.1.0 (2025)

- Добавлены методы `get_projects()`, `get_members()`, `get_news()`
- Улучшена генерация паролей
- Исправлены мелкие ошибки

### v1.0.0 (2025)

- Первая версия библиотеки
- Базовые функции: регистрация, вход, поиск пользователей
- Отправка сообщений
- Поддержка тикетов
- Сохранение аккаунтов в файл