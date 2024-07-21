from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from database import add_user, get_user, update_subscription, update_user_info, update_eating_schedule, delete_user, User
from payment import create_payment
from menu_data import menu_data  # Импортируем данные меню
import datetime
import pytz
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import DATABASE_URL

# Создаем новый engine и sessionmaker
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)



# States for the conversation handler
AGE, WEIGHT, HEIGHT, DIET_GOAL, EATING_SCHEDULE = range(5)

GENERAL_INFO = """ВАЖНО!!! Первый прием должен быть в 1 час пробуждения перерывы между едой не должны быть более 3 часов.
Также обязательно пить воду. На 1 кг веса- 30 мл воды. Например при весе 100кг*30мл=3л.
В воду можно добавить лимонный сок.

Для удобства предоставляем расписание приемов пищи:
Если Вы просыпаетесь в 5-00 то пробуждение в 8-00 тогда:
6-00 Перекус
8-00 Завтрак
11-00 Перекус
14-00 Обед
17-00 Перекус
19-30-20-00 Ужин

Если подъем в 7-00 то:
8-00 Завтрак
11-00 Перекус
14-00 Обед
17-00 Перекус
19-30-20-00 Ужин

Если подъем в 9-00 то:
10-00 Завтрак
13-00 Обед
16-00 Перекус
19-00 Ужин
ВАЖНО!!! Основные приемы пищи (завтрак, обед, ужин) не запиваем!!!
Чай или кофе можно употреблять с перекусами. Желательно, чтобы кофе был натуральным, возможно добавить молока, но не сахар. Сахарозаменитель также исключаем.
В день допустимо употребить 1-2 ч.л. сахара или меда.
"""

def start(update: Update, context: CallbackContext):
    if update.message:
        chat_id = update.message.chat_id
        add_user(chat_id)
        keyboard = [
            [InlineKeyboardButton("Просмотреть меню", callback_data='menu')],
            [InlineKeyboardButton("Подписаться", callback_data='subscribe')],
            [InlineKeyboardButton("Регистрация", callback_data='register')],
            [InlineKeyboardButton("Проверить подписку", callback_data='check_subscription')],
            [InlineKeyboardButton("Удалить профиль", callback_data='delete_profile')],
            [InlineKeyboardButton("Общая информация", callback_data='general_info')],
            [InlineKeyboardButton("Выбрать режим питания", callback_data='choose_eating_schedule')],
            [InlineKeyboardButton("Выбрать часовой пояс", callback_data='choose_timezone')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Добро пожаловать! Выберите действие:", reply_markup=reply_markup)
    elif update.callback_query:
        query = update.callback_query
        query.answer()
        chat_id = query.message.chat_id
        add_user(chat_id)
        keyboard = [
            [InlineKeyboardButton("Просмотреть меню", callback_data='menu')],
            [InlineKeyboardButton("Подписаться", callback_data='subscribe')],
            [InlineKeyboardButton("Регистрация", callback_data='register')],
            [InlineKeyboardButton("Проверить подписку", callback_data='check_subscription')],
            [InlineKeyboardButton("Удалить профиль", callback_data='delete_profile')],
            [InlineKeyboardButton("Общая информация", callback_data='general_info')],
            [InlineKeyboardButton("Выбрать режим питания", callback_data='choose_eating_schedule')],
            [InlineKeyboardButton("Выбрать часовой пояс", callback_data='choose_timezone')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text("Добро пожаловать! Выберите действие:", reply_markup=reply_markup)

def choose_timezone(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    timezones = [
        ['Europe/Moscow', 'Europe/Kaliningrad', 'Asia/Yekaterinburg'],
        ['Asia/Omsk', 'Asia/Krasnoyarsk', 'Asia/Irkutsk'],
        ['Asia/Yakutsk', 'Asia/Vladivostok', 'Asia/Magadan'],
        ['Asia/Kamchatka']
    ]

    buttons = []
    for row in timezones:
        buttons.append([InlineKeyboardButton(tz, callback_data=f'set_timezone:{tz}') for tz in row])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    query.edit_message_text(text="Выберите ваш часовой пояс:", reply_markup=reply_markup)

def set_timezone(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    chat_id = query.message.chat_id
    _, timezone = query.data.split(':')
    
    session = Session()
    user = session.query(User).filter_by(chat_id=chat_id).first()
    if user:
        user.timezone = timezone
        session.commit()
    session.close()
    
    query.edit_message_text(text=f"Ваш часовой пояс установлен на: {timezone}")

def update_user_timezone(chat_id, timezone):
    session = Session()
    user = session.query(User).filter_by(chat_id=chat_id).first()
    if user:
        user.timezone = timezone
        session.commit()
    session.close()

def menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    chat_id = query.message.chat_id
    user = get_user(chat_id)

    if user and user.subscribed and user.subscription_end > datetime.datetime.now():
        current_week = f"Неделя {user.current_week or 1}"
        menu_for_week = menu_data.get(current_week, "Меню не найдено.")
        
        if menu_for_week == "Меню не найдено.":
            query.edit_message_text(text="Меню не найдено.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='start')]]))
        else:
            menu_text = "\n".join(menu_for_week)
            query.edit_message_text(text=f"Меню на {current_week}:\n\n{menu_text}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='start')]]))
    else:
        query.edit_message_text(text="У вас нет активной подписки. Пожалуйста, подпишитесь для просмотра меню.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='start')]]))

def subscribe(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    chat_id = query.message.chat_id
    payment_url = create_payment(5.00, "https://www.example.com/return_url", chat_id)
    
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(text=f"Перейдите по ссылке для оплаты: {payment_url}", reply_markup=reply_markup)

def payment_success(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    chat_id = query.message.chat_id
    update_subscription(chat_id, datetime.datetime.now() + datetime.timedelta(days=30))
    
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(text="Подписка успешно оформлена!", reply_markup=reply_markup)

def register(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    chat_id = query.message.chat_id
    add_user(chat_id)
    
    context.user_data['chat_id'] = chat_id
    
    query.edit_message_text(text="Введите ваш возраст:")
    return AGE

def age(update: Update, context: CallbackContext):
    context.user_data['age'] = int(update.message.text)
    update.message.reply_text("Введите ваш вес (в кг):")
    return WEIGHT

def weight(update: Update, context: CallbackContext):
    context.user_data['weight'] = float(update.message.text)
    update.message.reply_text("Введите ваш рост (в см):")
    return HEIGHT

def height(update: Update, context: CallbackContext):
    context.user_data['height'] = float(update.message.text)
    update.message.reply_text("Введите вашу цель диеты (например, похудение, набор массы и т.д.):")
    return DIET_GOAL

def diet_goal(update: Update, context: CallbackContext):
    diet_goal = update.message.text
    chat_id = context.user_data['chat_id']
    age = context.user_data['age']
    weight = context.user_data['weight']
    height = context.user_data['height']
    
    update_user_info(chat_id, age, weight, height, diet_goal)
    update.message.reply_text("Регистрация завершена. Спасибо!")
    
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Регистрация отменена.")
    return ConversationHandler.END

def main_menu(update: Update, context: CallbackContext):
    start(update, context)
    return ConversationHandler.END

def check_subscription(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    chat_id = query

def check_subscription(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    chat_id = query.message.chat_id
    user = get_user(chat_id)

    if user and user.subscribed and user.subscription_end > datetime.datetime.now():
        query.edit_message_text(text="У вас есть активная подписка.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='start')]]))
    else:
        query.edit_message_text(text="У вас нет активной подписки.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='start')]]))

def delete_profile(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    chat_id = query.message.chat_id
    delete_user(chat_id)
    
    query.edit_message_text(text="Ваш профиль был удален.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='start')]]))

def general_info(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    query.edit_message_text(text=GENERAL_INFO, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='start')]]))

def choose_eating_schedule(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    chat_id = query.message.chat_id
    add_user(chat_id)
    
    keyboard = [
        [InlineKeyboardButton("Режим 1: Пробуждение в 5-00", callback_data='schedule_5')],
        [InlineKeyboardButton("Режим 2: Пробуждение в 7-00", callback_data='schedule_7')],
        [InlineKeyboardButton("Режим 3: Пробуждение в 9-00", callback_data='schedule_9')],
        [InlineKeyboardButton("Назад", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(text="Выберите режим питания:", reply_markup=reply_markup)

def update_schedule(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    chat_id = query.message.chat_id
    schedule_type = query.data.split('_')[-1]
    
    schedules = {
        '5': "Пробуждение в 5-00: 6-00 Перекус, 8-00 Завтрак, 11-00 Перекус, 14-00 Обед, 17-00 Перекус, 19-30-20-00 Ужин",
        '7': "Пробуждение в 7-00: 8-00 Завтрак, 11-00 Перекус, 14-00 Обед, 17-00 Перекус, 19-30-20-00 Ужин",
        '9': "Пробуждение в 9-00: 10-00 Завтрак, 13-00 Обед, 16-00 Перекус, 19-00 Ужин"
    }

    selected_schedule = schedules.get(schedule_type, "Режим не найден.")
    update_eating_schedule(chat_id, selected_schedule)
    
    query.edit_message_text(text=f"Вы выбрали следующий режим питания:\n\n{selected_schedule}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='start')]]))

# Define the conversation handler
conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(register, pattern='^register$')],
    states={
        AGE: [MessageHandler(Filters.text & ~Filters.command, age)],
        WEIGHT: [MessageHandler(Filters.text & ~Filters.command, weight)],
        HEIGHT: [MessageHandler(Filters.text & ~Filters.command, height)],
        DIET_GOAL: [MessageHandler(Filters.text & ~Filters.command, diet_goal)],
    },
    fallbacks=[CommandHandler('cancel', cancel), CallbackQueryHandler(main_menu, pattern='^start$')]
)

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
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
    dp.add_handler(CallbackQueryHandler(choose_timezone, pattern='^choose_timezone$')),
    dp.add_handler(CallbackQueryHandler(set_timezone, pattern='^set_timezone:.+')),
    dp.add_handler(CallbackQueryHandler(main_menu, pattern='^start$'))
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
