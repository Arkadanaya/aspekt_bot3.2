from functools import wraps
from config.settings import ADMIN_IDS

def for_clients_only(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        if update.effective_user.id in ADMIN_IDS:
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

def for_staff_only(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("🚫 Эта функция только для сотрудников")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped