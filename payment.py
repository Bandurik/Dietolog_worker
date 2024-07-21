import requests
import base64
import logging
import uuid
from config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY, TELEGRAM_TOKEN
from database import add_payment, get_pending_payments, update_payment_status, update_subscription
from telegram import Bot
import datetime

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_TOKEN)

def create_payment(amount, return_url, chat_id):
    auth_token = base64.b64encode(f"{YOOKASSA_SHOP_ID}:{YOOKASSA_SECRET_KEY}".encode()).decode()
    idempotence_key = str(uuid.uuid4())
    headers = {
        'Authorization': f'Basic {auth_token}',
        'Content-Type': 'application/json',
        'Idempotence-Key': idempotence_key
    }
    payload = {
        "amount": {"value": f"{amount:.2f}", "currency": "RUB"},
        "confirmation": {"type": "redirect", "return_url": return_url},
        "capture": True,
        "description": f"Подписка на диеты для заказа №{idempotence_key}",
        "metadata": {
            "chat_id": chat_id
        },
        "receipt": {
            "customer": {
                "full_name": "Иван Иванов",
                "email": "ivan@example.com"
            },
            "items": [
                {
                    "description": "Подписка на диеты",
                    "quantity": "1.00",
                    "amount": {
                        "value": f"{amount:.2f}",
                        "currency": "RUB"
                    },
                    "vat_code": 1
                }
            ]
        }
    }

    try:
        response = requests.post('https://api.yookassa.ru/v3/payments', headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()

        if 'confirmation' in response_data:
            payment_id = response_data['id']
            add_payment(payment_id, chat_id)
            logging.info(f"Payment link created, payment ID: {payment_id}")
            return response_data['confirmation']['confirmation_url']
        else:
            logging.error(f"Unexpected response data: {response_data}")
            return "Ошибка при создании ссылки на оплату. Пожалуйста, попробуйте позже."
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        if e.response is not None:
            logging.error(f"Response content: {e.response.content}")
        return "Ошибка при создании ссылки на оплату. Пожалуйста, попробуйте позже."

def check_payment_status(payment_id):
    auth_token = base64.b64encode(f"{YOOKASSA_SHOP_ID}:{YOOKASSA_SECRET_KEY}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(f'https://api.yookassa.ru/v3/payments/{payment_id}', headers=headers)
        response.raise_for_status()
        payment_data = response.json()

        if payment_data['status'] == 'succeeded':
            chat_id = payment_data['metadata']['chat_id']
            update_subscription(chat_id, datetime.datetime.now() + datetime.timedelta(days=30))
            update_payment_status(payment_id, 'succeeded')
            bot.send_message(chat_id=chat_id, text="Ваш платеж успешно обработан, и ваша подписка активирована!")
            logging.info(f"Payment {payment_id} succeeded for chat_id {chat_id}")
        else:
            logging.info(f"Payment {payment_id} status is {payment_data['status']}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        if e.response is not None:
            logging.error(f"Response content: {e.response.content}")

def get_all_payment_ids():
    pending_payments = get_pending_payments()
    return [payment.payment_id for payment in pending_payments]

