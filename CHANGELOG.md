# Changelog

## [3.0.0] - 2026

### ⚠️ Breaking Changes

#### Удалено

- Функция `load_accounts()` — загрузка аккаунтов из файла
- Функция `save_accounts()` — сохранение аккаунтов в файл
- Функция `get_active_accounts()` — фильтрация активных аккаунтов
- Функция `clean_accounts_file()` — очистка неактивных аккаунтов
- Константа `DEFAULT_ACCOUNTS_FILE` — путь к файлу аккаунтов
- Поддержка коллекции аккаунтов
- Метод `register()` — регистрация недоступна
- Метод `create_support_ticket()` — поддержка недоступна
- Метод `send_to_support()` — поддержка недоступна
- Методы `login()` и `create_from_token()` из `KaalitionClient`

#### Изменено

- `Account` теперь инициализируется напрямую без `KaalitionClient`
- Новая структура инициализации: `Account(email, password)` или `Account(token)`

### Причина изменений

Новая политика сайта kaalition.ru ограничила доступ к API регистрации и поддержки.

### Добавлено

#### Новый класс Message

Полноценный класс для работы с сообщениями:

```python
@dataclass
class Message:
    id: int                      # ID сообщения
    sender: User                 # Отправитель
    receiver: User               # Получатель
    text: str                    # Текст
    image: Optional[str]         # Изображение
    is_read: bool                # Прочитано
    read_at: Optional[str]       # Дата прочтения
    edited_at: Optional[str]     # Дата редактирования
    created_at: str              # Дата создания
    updated_at: str              # Дата обновления
    reactions: List[Reaction]    # Реакции
    account: Optional[Account]   # Связанный аккаунт
```

#### Методы Message

| Метод | Описание |
|-------|----------|
| `edit_text(new_text)` | Редактирование сообщения |
| `delete()` | Удаление сообщения |
| `toggle_reaction(emoji)` | Переключение реакции |
| `is_edited()` | Проверка на редактирование |
| `has_reaction(emoji)` | Проверка наличия реакции |
| `get_reaction_count(emoji)` | Количество реакций |

#### Новые исключения

```python
MessageError           # Базовое для сообщений
MessageEditError       # Ошибка редактирования
MessageDeleteError     # Ошибка удаления
MessageReactionError   # Ошибка реакции
ChatHistoryError       # Ошибка истории чата
```

### Улучшено

- Оптимизирована структура кода
- Исправлены проблемы с зависанием при ошибках 401
- Упрощённая инициализация `Account`
- Привязка `Account` к `Message` для методов

### Миграция с v2.x

```python
# v2.x — старый код
from kaalition_lib import KaalitionClient

client = KaalitionClient()
account = client.login("email@mail.ru", "password")

# v3.0.0 — новый код
from kaalition_lib import Account

account = Account(email="email@mail.ru", password="password")
# или
account = Account(token="your_token")
```

---

## [2.0.0] - 2026

### Изменено

- `Account` теперь наследуется от `KaalitionClient` и `User`
- Упрощённая инициализация с автоматическим заполнением данных
- `send_message()` возвращает объект `Message`

### Добавлено

- Класс `Message` с информацией об отправителе и получателе
- Класс `Reaction` для работы с реакциями
- Метод `get_chat_history()` — история чата
- Метод `edit_message_text()` — редактирование сообщений
- Метод `delete_message()` — удаление сообщений
- Метод `toggle_message_reaction()` — управление реакциями
- Новые исключения для сообщений

---

## [1.1.0] - 2026

### Добавлено

- Метод `get_projects()` — список проектов
- Метод `get_members()` — список участников
- Метод `get_news()` — список новостей

### Изменено

- Улучшена генерация паролей

---

## [1.0.0] - 2026

### Добавлено

- Базовый клиент `KaalitionClient`
- Регистрация и вход в аккаунт
- Поиск пользователей
- Отправка сообщений
- Поддержка тикетов
- Сохранение/загрузка аккаунтов
- Классы данных: `User`

---

[3.0.0]: https://github.com/Dima-programmer/KAALITION_API_LIB/compare/v2.0.0...v3.0.0
[2.0.0]: https://github.com/Dima-programmer/KAALITION_API_LIB/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/Dima-programmer/KAALITION_API_LIB/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Dima-programmer/KAALITION_API_LIB/releases/tag/v1.0.0