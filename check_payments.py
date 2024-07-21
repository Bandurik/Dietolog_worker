import time
from payment import check_payment_status, get_all_payment_ids

def main():
    while True:
        payment_ids = get_all_payment_ids()
        for payment_id in payment_ids:
            check_payment_status(payment_id)
        time.sleep(300)  # Wait for 5 minutes before the next check

if __name__ == '__main__':
    main()
