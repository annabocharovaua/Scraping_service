from telebot import types
from datetime import datetime
from dateutil.relativedelta import relativedelta

class PaymentManager:

    def __init__(self, bot, payments_token, db_manager):
        self.bot = bot
        self.payments_token = payments_token
        self.db_manager = db_manager

    def pre_checkout_query(self, pre_checkout_query):
        try:
            self.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
        except Exception as e:
            print(f"Error handling pre_checkout_query: {e}")

    def successful_payment(self, message):
        payment_info = message.successful_payment
        payment_details = (f"Chat id: {message.chat.id}\n"
                           f"Currency: {payment_info.currency}\n"
                           f"Total amount: {payment_info.total_amount / 100:.2f} {payment_info.currency}\n"
                           f"Invoice payload: {payment_info.invoice_payload}")
        print("SUCCESSFUL PAYMENT:", payment_details)
        self.bot.send_message(message.chat.id,
                              f"Платіж на суму {payment_info.total_amount / 100:.2f} {payment_info.currency} пройшов успішно.")

        if payment_info.invoice_payload == "🔴 Економ":
            self.pay1_payment_end(message.chat.id)
        elif payment_info.invoice_payload == "🟠 Стандарт":
            self.pay2_payment_end(message.chat.id)
        elif payment_info.invoice_payload == "🟢 Бізнес":
            self.pay3_payment_end(message.chat.id)

    def pay1_command(self, message):
        prices = [types.LabeledPrice(label="🔴 Економ", amount=4000)]
        self.bot.send_invoice(
            chat_id=message.chat.id,
            title="🔴 Економ",
            description="""Створюйте до двох(2) пошукових запитів вакансій на місяць. \nТариф активується автоматично одразу після оплати та триває протягом одного календарного місяця. \nОплачуючи Ви погоджуєтесь з Умовами Користування.""",
            provider_token=self.payments_token,
            currency='UAH',
            photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg",
            # Фото можна змінити
            photo_width=416,
            photo_height=234,
            photo_size=416,
            is_flexible=False,
            prices=prices,
            max_tip_amount=20000,
            suggested_tip_amounts=[1000, 5000, 10000],
            start_parameter='time-machine-subs',
            invoice_payload='🔴 Економ'
        )

    def pay2_command(self, message):
        prices = [types.LabeledPrice(label="🟠 Стандарт", amount=8000)]
        self.bot.send_invoice(
            chat_id=message.chat.id,
            title="🟠 Стандарт",
            description="""Створюйте до чотирьох(4) пошукових запитів вакансій на місяць. \nТариф активується автоматично одразу після оплати та триває протягом одного календарного місяця. \nОплачуючи Ви погоджуєтесь з Умовами Користування.""",
            provider_token=self.payments_token,
            currency='UAH',
            photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg",
            # Фото можна змінити
            photo_width=416,
            photo_height=234,
            photo_size=416,
            is_flexible=False,
            prices=prices,
            max_tip_amount=20000,
            suggested_tip_amounts=[1000, 5000, 10000],
            start_parameter='time-machine-subs',
            invoice_payload='🟠 Стандарт'
        )

    def pay3_command(self, message):
        prices = [types.LabeledPrice(label="🟢 Бізнес", amount=20000)]
        self.bot.send_invoice(
            chat_id=message.chat.id,
            title="🟢 Бізнес",
            description="""Створюйте до десяти(10) пошукових запитів вакансій на місяць. \nТариф активується автоматично одразу після оплати та триває протягом одного календарного місяця. \nОплачуючи Ви погоджуєтесь з Умовами Користування.""",
            provider_token=self.payments_token,
            currency='UAH',
            photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg",
            # Фото можна змінити
            photo_width=416,
            photo_height=234,
            photo_size=416,
            is_flexible=False,
            prices=prices,
            max_tip_amount=20000,
            suggested_tip_amounts=[1000, 5000, 10000],
            start_parameter='time-machine-subs',
            invoice_payload='🟢 Бізнес'
        )

    def pay1_payment_end(self, chat_id):
        end_date_subscription = self.get_end_subscription_date()
        self.db_manager.execute_query(
            "UPDATE users SET paid_subscription = 1, max_num_of_request = 2, end_date_subscription = %s WHERE chat_id = %s",
            (end_date_subscription, chat_id))
        self.bot.send_message(chat_id, "Ваш поточний тариф змінено на Економ.")

    def pay2_payment_end(self, chat_id):
        end_date_subscription = self.get_end_subscription_date()
        self.db_manager.execute_query(
            "UPDATE users SET paid_subscription = 2, max_num_of_request = 4, end_date_subscription = %s WHERE chat_id = %s",
            (end_date_subscription, chat_id))
        self.bot.send_message(chat_id, "Ваш поточний тариф змінено на Стандарт.")

    def pay3_payment_end(self, chat_id):
        end_date_subscription = self.get_end_subscription_date()
        self.db_manager.execute_query(
            "UPDATE users SET paid_subscription = 3, max_num_of_request = 10, end_date_subscription = %s WHERE chat_id = %s",
            (end_date_subscription, chat_id))
        self.bot.send_message(chat_id, "Ваш поточний тариф змінено на Бізнес.")

    def get_end_subscription_date(self):
        current_date = datetime.now().date()
        return current_date + relativedelta(months=1)