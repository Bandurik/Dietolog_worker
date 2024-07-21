from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler
from handlers import start, menu, subscribe, payment_success, register, age, weight, height, diet_goal, cancel, main_menu, check_subscription, delete_profile, general_info, choose_eating_schedule, update_schedule, conv_handler, choose_timezone, set_timezone
from reminders import start_scheduler
import datetime
import threading

def main():
    updater = Updater("6891513570:AAGdb1fhPcg87GPpg7m-dAG8VTEWOlFfL3A", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(menu, pattern='^menu$'))
    dp.add_handler(CallbackQueryHandler(subscribe, pattern='^subscribe$'))
    dp.add_handler(CallbackQueryHandler(payment_success, pattern='^payment_success$'))
    dp.add_handler(CallbackQueryHandler(start, pattern='^start$'))
    dp.add_handler(CallbackQueryHandler(check_subscription, pattern='^check_subscription$'))
    dp.add_handler(CallbackQueryHandler(delete_profile, pattern='^delete_profile$'))
    dp.add_handler(CallbackQueryHandler(general_info, pattern='^general_info$'))
    dp.add_handler(CallbackQueryHandler(choose_eating_schedule, pattern='^choose_eating_schedule$'))
    dp.add_handler(CallbackQueryHandler(update_schedule, pattern='^schedule_'))
    dp.add_handler(CallbackQueryHandler(choose_timezone, pattern='^choose_timezone$'))
    dp.add_handler(CallbackQueryHandler(set_timezone, pattern='^set_timezone:.+'))
    dp.add_handler(CallbackQueryHandler(main_menu, pattern='^start$'))
    dp.add_handler(conv_handler)

    dp.add_handler(conv_handler)

    # Запуск планировщика напоминаний в отдельном потоке
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()

    try:
        updater.start_polling()
        updater.idle()
    except KeyboardInterrupt:
        updater.stop()
        print("Bot stopped by user")

if __name__ == '__main__':
    main()
