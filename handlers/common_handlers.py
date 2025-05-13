import logging
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from config.settings import ADMIN_IDS
from config.keyboards import get_client_main_keyboard, get_operator_main_keyboard
from handlers.admin_handlers import staff_show_requests, staff_end_chat, staff_start
from handlers.client_handlers import client_end_chat, client_start
from models.state import active_chats

logger = logging.getLogger(__name__)


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Общий обработчик сообщений"""
    user = update.effective_user
    message_text = update.message.text

    # Логирование входящего сообщения
    logger.info(f"Получено сообщение от {user.id}: {message_text}")

    if message_text == "🔴 Завершить диалог":
        if user.id in ADMIN_IDS:
            await staff_end_chat(update, context)
        else:
            await client_end_chat(update, context)
        return

    if message_text == "📊 Активные запросы" and user.id in ADMIN_IDS:
        await staff_show_requests(update, context)
        return

    if user.id not in ADMIN_IDS:
        operator_id = active_chats.get(user.id)
        if not operator_id:
            await update.message.reply_text("⏳ Пожалуйста, дождитесь подключения оператора.")
            return

        try:
            await context.bot.send_message(
                chat_id=operator_id,
                text=f"👤 <b>Клиент {user.first_name}:</b>\n{message_text}",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Ошибка пересылки оператору {operator_id}: {str(e)}")
            await update.message.reply_text("⚠️ Не удалось отправить сообщение оператору. Попробуйте позже.")

    else:
        user_id = active_chats.get(user.id)
        if not user_id:
            return

        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"👨💼 <b>Оператор {user.first_name}:</b>\n{message_text}",
                parse_mode="HTML"
            )
            await update.message.reply_text("✓ Сообщение доставлено клиенту",
                                            reply_to_message_id=update.message.message_id)
        except Exception as e:
            logger.error(f"Ошибка отправки клиенту {user_id}: {str(e)}")
            await update.message.reply_text("❌ Не удалось отправить сообщение клиенту.",
                                            reply_markup=get_operator_main_keyboard())


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    if update.effective_user.id in ADMIN_IDS:
        await staff_start(update, context)
    else:
        await client_start(update, context)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logger.error(f"Ошибка при обработке обновления: {context.error}", exc_info=context.error)