## [3.1.0] - 2026

### Added

- **X-Site-Key header** - Added `X-Site-Key` header to all API requests
- **New class: Chat** - Working with dialogs list
- **New class: Channel** - Working with channels
- **New class: ChannelMessage** - Posts and comments in channels
- **New class: ChannelMember** - Channel members
- **New exception: ChannelError** - Base exception for channels
- **New exception: ChannelCreateError** - Channel creation error
- **New exception: ChannelUpdateError** - Channel update error
- **New exception: ChannelDeleteError** - Channel deletion error
- **New exception: ChannelMemberError** - Channel member management error
- **Constant: DEFAULT_SITE_KEY** - Default site key for API

#### Account methods - Profile

- `update_password()` - Change password
- `update_theme()` - Change theme (dark/light)
- `update_privacy()` - Privacy settings
- `get_sessions()` - Get active sessions list
- `delete_session()` - Delete specific session
- `delete_all_sessions()` - Delete all sessions except current
- `logout()` - Logout from account

#### Account methods - Channels

- `get_channels()` - Get channels list (with auto pagination)
- `get_channel()` - Get channel info
- `create_channel()` - Create channel
- `update_channel()` - Update channel
- `delete_channel()` - Delete channel
- `join_channel()` - Join channel
- `leave_channel()` - Leave channel

#### Account methods - Channel messages

- `get_channel_messages()` - Get channel posts
- `send_channel_message()` - Send post to channel
- `edit_channel_message()` - Edit channel post
- `delete_channel_message()` - Delete channel post
- `pin_channel_message()` - Pin/unpin post
- `toggle_channel_message_reaction()` - Reaction on post
- `get_channel_message_comments()` - Get post comments
- `get_channel_reactions()` - Get all channel reactions

#### Account methods - Channel members

- `get_channel_members()` - Get members list
- `update_channel_member_role()` - Change member role
- `kick_channel_member()` - Kick member

### Changed

- `send_message()` now accepts `receiver_id: int` instead of `User` object
- `get_chat_history()` now accepts `user_id: int` instead of `User` object
- `Channel` - removed `owner_id`, now only `owner: User` with `.id` field
- `Chat.id` automatically set to `partner.id`
- `ChannelMessage` - API returns `user` instead of `author`
- `get_channels()` - Added auto pagination (loads all pages until `has_more` is false)
- `get_channels()` - Now accepts optional `page` parameter

### Fixed

- `Chat.from_dict()` - Fixed parsing from API response
- `Channel.from_dict()` - Fixed parsing from API response (image, is_verified, etc.)
- `ChannelMessage.from_dict()` - Fixed parsing (channel_id can be string)
- `logout()` - Always returns True now

---

## [3.0.0] - 2026

### ⚠️ Breaking Changes

- Removed `load_accounts()` function
- Removed `save_accounts()` function
- Removed `get_active_accounts()` function
- Removed `clean_accounts_file()` function
- Removed `DEFAULT_ACCOUNTS_FILE` constant
- Removed account collection support
- Removed `register()` method
- Removed `create_support_ticket()` method
- Removed `send_to_support()` method
- Removed `login()` and `create_from_token()` from `KaalitionClient`

### Changed

- `Account` now initializes directly without `KaalitionClient`
- New initialization structure: `Account(email, password)` or `Account(token)`

### Added

- **New class: Message** - Full-featured class for messages
- **New class: Reaction** - Working with reactions
- New exceptions: `MessageError`, `MessageEditError`, `MessageDeleteError`, `MessageReactionError`, `ChatHistoryError`
- `Account.refresh()` - Sync with server
- `Account.is_active()` - Check session activity
- `Account.update_profile()` - Update profile
- `Account.search_users()` - Search users
- `Account.send_message()` - Send message
- `Account.get_chat_history()` - Chat history
- `Account.edit_message_text()` - Edit message
- `Account.delete_message()` - Delete message
- `Account.toggle_message_reaction()` - Message reaction

### Improved

- Optimized code structure
- Fixed issues with hanging on 401 errors
- Simplified `Account` initialization
- Bound `Account` to `Message` for methods

---

## [2.0.0] - 2026

### Changed

- `Account` now inherits from `KaalitionClient` and `User`
- Simplified initialization with automatic data filling
- `send_message()` returns `Message` object

### Added

- Class `Message` with sender and receiver info
- Class `Reaction` for working with reactions
- Method `get_chat_history()` - Chat history
- Method `edit_message_text()` - Edit messages
- Method `delete_message()` - Delete messages
- Method `toggle_message_reaction()` - Manage reactions
- New exceptions for messages

---

## [1.1.0] - 2026

### Added

- Method `get_projects()` - Projects list
- Method `get_members()` - Members list
- Method `get_news()` - News list

### Changed

- Improved password generation

---

## [1.0.0] - 2026

### Added

- Basic client `KaalitionClient`
- Registration and login
- User search
- Message sending
- Support tickets
- Save/load accounts
- Data classes: `User`

---

[3.1.0]: https://github.com/Dima-programmer/KAALITION_API_LIB/compare/v3.0.0...v3.1.0
[3.0.0]: https://github.com/Dima-programmer/KAALITION_API_LIB/compare/v2.0.0...v3.0.0
[2.0.0]: https://github.com/Dima-programmer/KAALITION_API_LIB/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/Dima-programmer/KAALITION_API_LIB/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Dima-programmer/KAALITION_API_LIB/releases/tag/v1.0.0