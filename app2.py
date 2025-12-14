import logging
import os 
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import time

# --- 1. Настройка и Константы ---
# Получаем токен из переменной окружения Railway (BOT_TOKEN).
# Если переменная не найдена (например, при локальном запуске), 
# токен будет установлен как "ТОКЕН_НЕ_НАЙДЕН"
BOT_TOKEN = os.environ.get("BOT_TOKEN", "ТОКЕН_НЕ_НАЙДЕН") 

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__) 

# --- 2. Обработчик Сообщений ---
async def read_incoming_business_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    # Строгая проверка на Business Connection (работает только для вашего аккаунта)
    if not update.effective_message or not update.effective_message.business_connection_id:
        return

    # Получаем идентификаторы
    connection_id = update.effective_message.business_connection_id
    chat_id = update.effective_message.chat_id
    message_id = update.effective_message.message_id
    
    # --- ЛОГИКА ПРОЧТЕНИЯ ---
    logger.info(f"Получено Business-сообщение ID: {connection_id} от чата: {chat_id}. ID сообщения: {message_id}")

    try:
        # Чтение сообщения (ставить две синие галочки)
        await context.bot.read_business_message(
            business_connection_id=connection_id,
            chat_id=chat_id,
            message_id=message_id 
        )
        logger.info(f"✅ Успешно прочитано сообщение в чате {chat_id}.")

    except Exception as e:
        logger.error(f"❌ Ошибка при вызове readBusinessMessage: {e}")
        
# --- 3. Основная Функция Запуска ---
def main() -> None:
    # Проверка, что токен был получен (если токен "ТОКЕН_НЕ_НАЙДЕН", бот не запустится)
    if BOT_TOKEN == "ТОКЕН_НЕ_НАЙДЕН":
        logger.error("Ошибка: Токен BOT_TOKEN не был найден. Убедитесь, что вы задали переменную окружения на хостинге.")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    handler = MessageHandler(
        filters.ALL, 
        read_incoming_business_message
    )
    application.add_handler(handler)

    logger.info("Бот запущен и ожидает Business-сообщений (режим 24/7)...")
    application.run_polling(poll_interval=1)

if __name__ == '__main__':
    main()
