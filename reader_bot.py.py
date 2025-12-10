import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import time

# --- 1. Настройка и Константы ---
# ВАШ ТОКЕН
BOT_TOKEN = "8520712073:AAEjMrFGG0mYlDWTQEnviES-Fkxa9eklfPs" 

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__) 

# --- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ АНТИ-СПАМА ---
# Хранение истории сообщений для каждого чата
SPAM_TRACKER = {} 
SPAM_LIMIT = 3   # Максимальное количество сообщений (напр., 3)
TIME_WINDOW = 5  # Окно времени в секундах (напр., 5 секунд)

# --- 2. Обработчик Сообщений ---
async def read_incoming_business_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    global SPAM_TRACKER

    # Строгая проверка на Business Connection (работает только для вашего аккаунта)
    if not update.effective_message or not update.effective_message.business_connection_id:
        return

    # Получаем идентификаторы
    connection_id = update.effective_message.business_connection_id
    chat_id = update.effective_message.chat_id
    message_id = update.effective_message.message_id
    current_time = time.time()
    
    # --- ЛОГИКА АНТИ-СПАМА ---
    
    if chat_id not in SPAM_TRACKER:
        SPAM_TRACKER[chat_id] = []
    
    # Очистка старых меток времени и добавление новой
    SPAM_TRACKER[chat_id] = [t for t in SPAM_TRACKER[chat_id] if current_time - t <= TIME_WINDOW]
    SPAM_TRACKER[chat_id].append(current_time)
    
    # Проверка: если сообщений больше лимита
    if len(SPAM_TRACKER[chat_id]) > SPAM_LIMIT:
        logger.warning(f"Спам обнаружен в чате {chat_id}. Бот отвечает и пропускает прочтение.")
        
        try:
            # Отправка предупреждения
            await context.bot.send_message(
                chat_id=chat_id, 
                text="Не спамьте, пожалуйста!",
                business_connection_id=connection_id
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке анти-спам сообщения: {e}")
            
        SPAM_TRACKER[chat_id] = [] # Сброс, чтобы не спамить ответом
        return # Важно: выходим, НЕ ЧИТАЯ сообщение

    # --- ЛОГИКА ПРОЧТЕНИЯ (Если не спам) ---
    logger.info(f"Получено Business-сообщение ID: {connection_id} от чата: {chat_id}. ID сообщения: {message_id}")

    try:
        # Чтение сообщения (ставить две синие галочки)
        await context.bot.read_business_message(
            business_connection_id=connection_id,
            chat_id=chat_id,
            message_id=message_id 
        )
        logger.info(f"✅ Успешно прочитано сообщение в чате {chat_id}.")
        
        # Бот продолжает работать и ждать следующего сообщения.

    except Exception as e:
        logger.error(f"❌ Ошибка при вызове readBusinessMessage: {e}")
        
# --- 3. Основная Функция Запуска ---
def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    handler = MessageHandler(
        filters.ALL, 
        read_incoming_business_message
    )
    application.add_handler(handler)

    logger.info("Бот запущен и ожидает Business-сообщений (режим 24/7)...")
    # run_polling будет работать бесконечно, пока не будет остановлен вручную
    application.run_polling(poll_interval=1)

if __name__ == '__main__':
    main()