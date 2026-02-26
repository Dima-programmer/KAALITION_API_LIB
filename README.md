# Kaalition API Library

Python библиотека для работы с API сайта kaalition.ru.

## Документация

Полная документация доступна в [docs/README.md](https://github.com/Dima-programmer/KAALITION_API_LIB/tree/master/docs/README.md).

---

## Возможности

- Авторизация по email/password или токену
- Личные сообщения (отправка, редактирование, удаление, реакции)
- Список чатов и история переписки
- Каналы (создание, редактирование, удаление)
- Посты в каналах и комментарии
- Реакции, закрепление постов
- Управление участниками каналов
- Профиль (смена никнейма, пароля, темы, приватности)
- Управление сессиями
- Публичные данные (проекты, участники, новости)

---

## Установка

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

### Авторизация

```python
from kaalition_lib import Account

# Через email и пароль
account = Account(email="mail@test.com", password="pass")

# Или через токен
account = Account(token="eyJ0eXAiOiJKV1Qi...")
```

### Сообщения

```python
# Отправка сообщения (по ID)
account.send_message(receiver_id=42, text="Привет!")

# История чата
messages = account.get_chat_history(user_id=42)

# Список всех чатов
chats = account.get_chats()
```

### Работа с каналами

```python
# Список каналов
channels = account.get_channels()

# Создание канала
channel = account.create_channel("Мой канал", "Описание", is_public=True)

# Вступление
account.join_channel(channel.id)

# Отправка поста
post = account.send_channel_message(channel.id, "Первый пост!")

# Реакция и закрепление
post.toggle_reaction("🔥")
post.pin()

# Покинуть канал
account.leave_channel(channel.id)
```

---

## Требования

- Python 3.8+
- requests

---

## Документация

Полная документация: [docs/README.md](https://github.com/Dima-programmer/KAALITION_API_LIB/tree/master/docs/README.md)

---

## Версия

**3.1.0** — [FULL CHANGELOG](https://github.com/Dima-programmer/KAALITION_API_LIB/tree/master/CHANGELOG.md)

### Changelog

- **3.1.0** — Каналы, чаты, управление профилем и сессиями
- **3.0.0** — Новая структура API
- **2.0.0** — Сообщения и реакции
- **1.0.0** — Базовый функционал

---

## Лицензия

[LICENSE](https://github.com/Dima-programmer/KAALITION_API_LIB/tree/master/LICENSE)

---

## Автор

[Dima-Programmer](https://github.com/Dima-programmer)