# Changelog

## 2.0.0

### Изменено

#### Новая система наследования

`Account` теперь наследуется сразу от `KaalitionClient` и `User`, что исключает дублирование полей и упрощает работу с данными пользователя.

**До:**
```python
# Поля User и Account были раздельными
print(account.username)
print(account.nickname)
```

**После:**
```python
# Account включает все поля User
print(account.id)           # ID пользователя
print(account.username)     # Имя пользователя
print(account.nickname)     # Отображаемое имя
print(account.is_verified)  # Верификация
print(account.is_admin)     # Админ
```

#### Упрощённая инициализация

Теперь для создания `Account` достаточно передать только `token` или `email` + `password`. Все остальные поля заполняются автоматически при синхронизации с сервером.

**До:**
```python
account = client.register(
    username="test_user",
    email="test@mail.ru",
    password="password123",
    nickname="Test User"
)
```

**После:**
```python
# Из токена
account = Account(token="your_token")

# Из email и пароля (автоматически выполнит вход)
account = Account(email="test@mail.ru", password="password")

# Все остальные поля заполняются автоматически
```

### Добавлено

#### Новый класс Message

Полноценный класс для работы с сообщениями, включающий информацию об отправителе и получателе как объектах `User`.

```python
@dataclass
class Message:
    id: int                      # ID сообщения
    sender: User                 # Отправитель (объект User)
    receiver: User               # Получатель (объект User)
    text: str                    # Текст сообщения
    image: Optional[str]         # Путь к изображению
    is_read: bool                # Прочитано ли
    read_at: Optional[str]       # Дата прочтения
    edited_at: Optional[str]     # Дата редактирования
    created_at: str              # Дата создания
    updated_at: str              # Дата обновления
    reactions: List[Reaction]    # Список реакций
```

**Методы:**

- `is_edited()` — проверяет, было ли сообщение отредактировано
- `has_reaction(emoji)` — проверяет наличие определённой реакции
- `get_reaction_count(emoji)` — возвращает количество определённых реакций

#### Новый класс Reaction

```python
@dataclass
class Reaction:
    emoji: str              # Эмодзи реакции
    count: int              # Количество
    user_ids: List[int]     # Список ID пользователей
```

#### Новые методы в Account

| Метод | Описание | Возвращает |
|-------|----------|------------|
| `get_chat_history(user)` | Получение истории чата с пользователем | `List[Message]` |
| `edit_message_text(message, new_text)` | Редактирование текста сообщения | `Optional[Message]` |
| `delete_message(message)` | Удаление сообщения | `bool` |
| `toggle_message_reaction(message, emoji)` | Переключение реакции на сообщении | `List[Reaction]` |

#### Изменение метода send_message

Метод `send_message()` теперь возвращает объект `Message` вместо кортежа.

**До:**
```python
success, status = account.send_message(user, "Привет!")
if success:
    print("Отправлено")
```

**После:**
```python
message = account.send_message(user, "Привет!")
if message:
    print(f"Отправлено: {message.id}")
    print(f"Текст: {message.text}")
    print(f"Отправитель: {message.sender.nickname}")
```

#### Новые исключения

Добавлены специализированные исключения для работы с сообщениями:

```python
from kaalition_lib import (
    MessageError,           # Базовое исключение для сообщений
    MessageNotFoundError,   # Сообщение не найдено
    MessageEditError,       # Ошибка редактирования сообщения
    MessageDeleteError,     # Ошибка удаления сообщения
    MessageReactionError,   # Ошибка установки реакции
    ChatHistoryError,       # Ошибка получения истории чата
)
```

### Улучшения

- Оптимизирована структура классов
- Улучшена обработка ошибок с использованием специализированных исключений
- Добавлены методы для проверки состояния сообщений
- Улучшена синхронизация данных с сервером при инициализации

---

## [1.1.0] - 2025

### Добавлено

- Метод `get_projects()` — получение списка проектов
- Метод `get_members()` — получение списка участников (создателей сайта)
- Метод `get_news()` — получение списка новостей

### Изменено

- Улучшена генерация паролей с использованием библиотеки Faker
- Оптимизирована обработка HTTP-запросов

### Исправлено

- Мелкие ошибки и баги

---

## [1.0.0] - 2025

### Добавлено

- Базовый клиент `KaalitionClient` для операций без авторизации
- Регистрация новых аккаунтов через `register()`
- Вход в существующие аккаунты через `login()`
- Создание аккаунта из токена через `create_from_token()`
- Поиск пользователей через `search_users()`
- Отправка личных сообщений через `send_message()`
- Создание тикетов поддержки через `create_support_ticket()`
- Отправка сообщений в поддержку через `send_to_support()`
- Обновление профиля через `update_profile()`
- Сохранение и загрузка аккаунтов из JSON файла
- Утилиты для управления коллекцией аккаунтов

### Классы данных

- `User` — данные о пользователе
- `Project` — данные о проекте
- `Member` — данные об участнике
- `News` — данные о новости

### Исключения

- `KaalitionError` — базовое исключение
- `RegistrationError` — ошибка регистрации
- `LoginError` — ошибка входа
- `TokenError` — ошибка токена
- `ProfileUpdateError` — ошибка обновления профиля
- `UserNotFoundError` — пользователь не найден
- `MessageError` — ошибка отправки сообщения

---

## [Unreleased]

### Планируется

- [ ] Работа с групповыми чатами
- [ ] Поддержка WebSocket для real-time уведомлений
- [ ] Асинхронная версия библиотеки

---

[2.0.0]: https://github.com/Dima-programmer/KAALITION_API_LIB/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/Dima-programmer/KAALITION_API_LIB/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Dima-programmer/KAALITION_API_LIB/releases/tag/v1.0.0