from datetime import datetime
import logging
from config.settings import ADMIN_IDS, OPERATOR_CHAT_ID
from models.state import active_requests, active_chats
from config.keyboards import get_client_main_keyboard, get_operator_main_keyboard

logger = logging.getLogger(__name__)


async def notify_operators(context, user):
    try:
        text = (
            f"🛎 <b>Новый запрос поддержки!</b>\n"
            f"👤 Клиент: {user.full_name}\n"
            f"🆔 ID: {user.id}\n"
            f"⏱ Время: {datetime.now().strftime('%H:%M %d.%m.%Y')}\n\n"
            f"Для подключения используйте кнопку <b>'📊 Активные запросы'</b>"
        )

        logger.info(f"Отправка уведомлений о новом запросе от {user.id}")

        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=text,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Ошибка отправки админу {admin_id}: {str(e)}")

        if OPERATOR_CHAT_ID:
            try:
                await context.bot.send_message(
                    chat_id=OPERATOR_CHAT_ID,
                    text=text,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Ошибка отправки в чат операторов: {str(e)}")

    except Exception as e:
        logger.error(f"Критическая ошибка в notify_operators: {str(e)}")


async def close_chat(context, user_id):
    operator_id = active_chats.get(user_id)

    if user_id in active_chats:
        del active_chats[user_id]
    if operator_id and operator_id in active_chats:
        del active_chats[operator_id]

    active_requests.pop(user_id, None)

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="🔴 Диалог завершён. Спасибо за обращение!",
            reply_markup=get_client_main_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка уведомления клиента {user_id}: {str(e)}")

    try:
        if operator_id:
            await context.bot.send_message(
                chat_id=operator_id,
                text="🔴 Чат с клиентом завершён",
                reply_markup=get_operator_main_keyboard()
            )
    except Exception as e:
        logger.error(f"Ошибка уведомления оператора {operator_id}: {str(e)}")

    logger.info(f"Чат завершен: оператор {operator_id} - клиент {user_id}")