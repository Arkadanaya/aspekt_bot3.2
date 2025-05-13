import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    filters
)
from config.settings import BOT_TOKEN, LOG_FILE, LOG_LEVEL
from models.state import WAITING_FOR_OPERATOR
from handlers.client_handlers import (
    client_request_operator,
    client_cancel_request,
    client_end_chat, show_properties, show_contacts, about_company
)
from handlers.admin_handlers import (
    staff_start,
    staff_show_requests,
    staff_connect_to_user,
    staff_end_chat
)
from handlers.common_handlers import (
    message_handler,
    start,
    error_handler
)

async def post_init(application: Application):
    await application.bot.set_my_commands([
        ("start", "Запустить бота"),
    ])
    application.bot_data['logger'] = logging.getLogger(__name__)
    logging.info("Бот инициализирован")

def setup_handlers(application):
    # Основные команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", staff_start))

    # Обработчики кнопок клиента
    application.add_handler(MessageHandler(
        filters.Regex('^📞 Связаться с оператором$'),
        client_request_operator
    ))
    application.add_handler(MessageHandler(
        filters.Regex('^🏘️ Наши объекты$'),
        show_properties
    ))
    application.add_handler(MessageHandler(
        filters.Regex('^📍 Контакты$'),
        show_contacts
    ))
    application.add_handler(MessageHandler(
        filters.Regex('^ℹ️ О компании$'),
        about_company
    ))
    application.add_handler(MessageHandler(
        filters.Regex('^❌ Отменить запрос$'),
        client_cancel_request
    ))

    # Обработчики callback-кнопок
    application.add_handler(CallbackQueryHandler(
        staff_connect_to_user,
        pattern=r"^connect_"
    ))

    # Обработчик диалога с оператором
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(
            filters.Regex('^📞 Связаться с оператором$'),
            client_request_operator
        )],
        states={
            WAITING_FOR_OPERATOR: [
                MessageHandler(
                    filters.Regex('^❌ Отменить запрос$'),
                    client_cancel_request
                ),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    message_handler
                )
            ]
        },
        fallbacks=[CommandHandler("cancel", client_cancel_request)],
        allow_reentry=True
    )
    application.add_handler(conv_handler)

    # Общий обработчик сообщений
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        message_handler
    ))

    # Обработчик ошибок
    application.add_error_handler(error_handler)

def main() -> None:
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=LOG_LEVEL,
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.WARNING)

    application = Application.builder() \
        .token(BOT_TOKEN) \
        .post_init(post_init) \
        .build()

    setup_handlers(application)
    application.run_polling()

if __name__ == '__main__':
    main()