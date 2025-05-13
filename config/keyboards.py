from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_client_main_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📞 Связаться с оператором")],
        [KeyboardButton("🏘️ Наши объекты")],
        [KeyboardButton("📍 Контакты"), KeyboardButton("ℹ️ О компании")]
    ], resize_keyboard=True)

def get_client_waiting_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("❌ Отменить запрос")]
    ], resize_keyboard=True)

def get_chat_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🔴 Завершить диалог")]
    ], resize_keyboard=True)

def get_operator_main_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📊 Активные запросы")],
        [KeyboardButton("🔴 Завершить диалог")]
    ], resize_keyboard=True)