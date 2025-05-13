from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from models.state import WAITING_FOR_OPERATOR
from utils.decorators import for_clients_only
from utils.helpers import notify_operators, close_chat
from config.keyboards import (
    get_client_main_keyboard,
    get_client_waiting_keyboard,
    get_chat_keyboard
)
from models.state import active_requests, active_chats


@for_clients_only
async def client_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        text=f"Добро пожаловать в риелторскую компанию «АСПЕКТ»!\n\n{user.first_name}, мы рады приветствовать вас! Чем можем помочь?",
        reply_markup=get_client_main_keyboard()
    )


@for_clients_only
async def client_request_operator(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    active_requests[user.id] = {'user': user, 'timestamp': datetime.now()}

    await notify_operators(context, user)

    await update.message.reply_text(
        "⏳ Запрос отправлен оператору. Ожидайте подключения специалиста...",
        reply_markup=get_client_waiting_keyboard()
    )
    return WAITING_FOR_OPERATOR


@for_clients_only
async def client_cancel_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    active_requests.pop(user.id, None)

    await update.message.reply_text(
        "Запрос на поддержку отменён.",
        reply_markup=get_client_main_keyboard()
    )
    return ConversationHandler.END


@for_clients_only
async def client_end_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id

    if user_id not in active_chats:
        await update.message.reply_text("ℹ️ У вас нет активного чата.", reply_markup=get_client_main_keyboard())
        return ConversationHandler.END

    await close_chat(context, user_id)
    return ConversationHandler.END

@for_clients_only
async def show_properties(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text="🏘️ Наши объекты недвижимости:\n\n"
             "1. ЖК 'Солнечный' - от 5 млн руб.\n"
             "2. ЖК 'Лесной' - от 6.5 млн руб.\n"
             "3. ЖК 'Центральный' - от 8 млн руб.\n\n"
             "Подробнее: https://aspectrealtor24.ru/",
        reply_markup=get_client_main_keyboard()
    )


@for_clients_only
async def show_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показываем контактную информацию с кликабельным номером"""
    contacts_text = (
        "📍 <b>Наши контакты:</b>\n\n"
        "📞 Телефон: <a href='tel:+79135398081'>+7(913)539-80-81</a>\n\n"
        "🏠 Адрес: <a href='https://yandex.ru/maps/?text=г. Красноярск, ул.Урицкого 117'>г. Красноярск, ул.Урицкого 117, офис 5-03, пом.9, комн.4</a>\n\n"
        "✉️ Email: <a href='XXXXX@example.com'>inXXXXX@example.com</a>\n\n"
        "⏰ Режим работы: Пн-Пт: 10:00-18:00"
    )

    await update.message.reply_text(
        text=contacts_text,
        parse_mode="HTML",
        reply_markup=get_client_main_keyboard(),
        disable_web_page_preview=True
    )

@for_clients_only
async def about_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = (
        "ℹ️ <b>О компании</b>\n\n"
        "<b>Опыт и надёжность</b>\n"
        "Мы работаем на рынке недвижимости с 2010 года, что свидетельствует о стабильности и накопленном опыте. "
        "За более чем 10 лет работы компания успела изучить рынок, сформировать профессиональные подходы и заслужить доверие клиентов.\n\n"
        "<b>Экспертные консультации</b>\n"
        "Специализация на предоставлении консультационных услуг при купле-продаже недвижимости говорит о глубоком понимании рынка, "
        "юридических аспектов и нюансов сделок. Это позволяет нашим клиентам избежать ошибок и получить максимально выгодные условия.\n\n"
        "<b>Индивидуальный подход</b>\n"
        "Работа за вознаграждение подразумевает гибкость в сотрудничестве. Мы учитываем потребности каждого клиента, "
        "предлагая персонализированные решения и адаптируясь под конкретные запросы.\n\n"
        "<b>Репутация и отзывы</b>\n"
        "За долгие годы работы у компании сформировалась база довольных клиентов и положительных отзывов. "
        "Это подтверждает профессионализм наших сотрудников и способность решать задачи любой сложности в сфере недвижимости.\n\n"
        "<a href='https://aspectrealtor24.ru/'>Подробнее на нашем сайте</a>"
    )

    await update.message.reply_text(
        text=about_text,
        parse_mode="HTML",
        reply_markup=get_client_main_keyboard()
    )