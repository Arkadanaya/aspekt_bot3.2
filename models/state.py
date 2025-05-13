from datetime import datetime
from typing import Dict, Any
from telegram import User

# Глобальные переменные состояния
active_requests: Dict[int, Dict[str, Any]] = {}
active_chats: Dict[int, int] = {}

# Состояния ConversationHandler
WAITING_FOR_OPERATOR, CHATTING_WITH_OPERATOR = range(2)