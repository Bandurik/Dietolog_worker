import logging
from telegram.ext import Updater
from handlers import setup_handlers

# Токен бота
TOKEN = '6891513570:AAGdb1fhPcg87GPpg7m-dAG8VTEWOlFfL3A'

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Инициализация бота
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    # Настройка обработчиков
    setup_handlers(dp)

    logger.info("Бот запущен и готов к приему сообщений.")
    
    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
