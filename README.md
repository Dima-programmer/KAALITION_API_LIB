# Python библиотека для автоматизации работы с API сайта kaalition.ru.

## Описание

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
```

## Быстрый старт

```python
from kaalition_lib import KaalitionClient

# Создание клиента и регистрация аккаунта
client = KaalitionClient()
account = client.register()

print(f"Аккаунт создан: {account.username}")

# Поиск пользователей
users = account.search_users("никнейм")

if users:
    # Отправка сообщения
    account.send_message(users[0], "Привет!")
```

## API Reference

### KaalitionClient

Базовый клиент для операций без авторизации.

```python
from kaalition_lib import KaalitionClient

client = KaalitionClient(
    base_url="https://kaalition.ru",
    accounts_file="accounts.json"
)
```

**Методы:**

| Метод | Описание |
|-------|----------|
| `register()` | Регистрация нового аккаунта |
| `login(email, password)` | Вход в аккаунт |
| `create_from_token(token)` | Создание аккаунта из токена |
| `load_accounts()` | Загрузка сохранённых аккаунтов |

### Account

Аккаунт с авторизацией.

```python
account = client.register()
```

**Методы:**

| Метод | Описание |
|-------|----------|
| `search_users(query)` | Поиск пользователей |
| `send_message(user, message)` | Отправка личного сообщения |
| `create_support_ticket(subject, message)` | Создание тикета поддержки |
| `send_to_support(message)` | Отправка в чат поддержки |
| `update_profile(...)` | Обновление профиля |
| `refresh()` | Синхронизация с сервером |
| `is_active()` | Проверка активности |
| `save()` | Сохранение аккаунта |

### User

```python
@dataclass
class User:
    id: int
    username: str
    nickname: str
    photo: str
    avatar_emoji: Optional[str]
    is_verified: bool
```

## Примеры

### Работа с коллекцией аккаунтов

```python
from kaalition_lib import load_accounts, clean_accounts_file

# Загрузка активных аккаунтов
accounts = load_accounts("accounts.json", active_only=True)

# Проверка активности
for acc in accounts:
    if acc.is_active():
        acc.update_profile(bio="Обновлено")
        acc.save()

# Очистка неактивных
clean_accounts_file("accounts.json")
```

### Массовая рассылка

```python
from kaalition_lib import KaalitionClient
import time

client = KaalitionClient()
account = client.login("email@mail.ru", "password")

users = account.search_users("аудитория")

for user in users:
    if account.is_active():
        account.send_message(user, "Ваше сообщение")
        time.sleep(1)
```

## Исключения

```python
from kaalition_lib import (
    KaalitionError,
    RegistrationError,
    LoginError,
    TokenError,
)

try:
    account = client.register()
except RegistrationError:
    print("Ошибка регистрации")
except LoginError:
    print("Ошибка входа")
except TokenError:
    print("Ошибка токена")
```

## Константы

```python
from kaalition_lib import (
    DEFAULT_BASE_URL,
    DEFAULT_ACCOUNTS_FILE,
    DEFAULT_USER_AGENT,
    DEFAULT_DELAY,
    DEFAULT_EMAIL_DOMAINS,
)
```

## Поддержка проекта

### Если библиотека оказалась полезной, вы можете:

- Поставить звезду на [GitHub](github.com/Dima-programmer/KAALITION_API_LIB):
- Сообщить об ошибке через Issues
- Предложить улучшения через Pull Requests

Ваша обратная связь помогает делать библиотеку лучше.

## Лицензия

MIT License. Подробности в файле LICENSE.

## Автор

[Dima-Programmer](github.com/Dima-programmer)