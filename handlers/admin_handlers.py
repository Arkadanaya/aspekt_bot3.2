from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from utils.decorators import for_staff_only
from utils.helpers import close_chat
from config.keyboards import get_operator_main_keyboard, get_chat_keyboard
from models.state import active_requests, active_chats


@for_staff_only
async def staff_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "⚙️ Панель оператора поддержки",
        reply_markup=get_operator_main_keyboard()
    )


@for_staff_only
async def staff_show_requests(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not active_requests:
        await update.message.reply_text("✅ Нет активных запросов на поддержку.",
                                        reply_markup=get_operator_main_keyboard())
        return

    buttons = []
    for user_id, request in active_requests.items():
        user = request['user']
        time_ago = (datetime.now() - request['timestamp']).seconds // 60
        buttons.append([
            InlineKeyboardButton(
                text=f"👤 {user.first_name} ({time_ago} мин назад)",
                callback_data=f"connect_{user_id}"
            )
        ])

    await update.message.reply_text(
        "🛎 Активные запросы на поддержку:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@for_staff_only
async def staff_connect_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = int(query.data.split('_')[1])
    operator = update.effective_user

    if user_id not in active_requests:
        await query.message.reply_text("❌ Этот запрос уже обработан")
        return

    user = active_requests[user_id]['user']
    del active_requests[user_id]

    active_chats[operator.id] = user_id
    active_chats[user_id] = operator.id

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ Оператор {operator.first_name} подключился к чату!\n\nЗадайте ваш вопрос...",
            reply_markup=get_chat_keyboard()
        )

        try:
            await query.message.delete()
        except Exception:
            pass

        await context.bot.send_message(
            chat_id=operator.id,
            text=f"Вы подключены к клиенту {user.first_name} (ID: {user_id})\n\n"
                 "Теперь все ваши сообщения будут пересылаться клиенту.",
            reply_markup=get_operator_main_keyboard()
        )
    except Exception:
        await query.message.reply_text(
            "⚠️ Не удалось отправить уведомление клиенту, но чат создан",
            reply_markup=get_operator_main_keyboard()
        )


@for_staff_only
async def staff_end_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    operator_id = update.effective_user.id
    user_id = active_chats.get(operator_id)

    if not user_id:
        await update.message.reply_text("ℹ️ Нет активного диалога.", reply_markup=get_operator_main_keyboard())
        return

    await close_chat(context, user_id)