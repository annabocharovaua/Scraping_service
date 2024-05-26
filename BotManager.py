import threading
from datetime import datetime
from dateutil.relativedelta import relativedelta
import telebot
from telebot import types
from JobSearch import JobSearch
from Request import Request
from Stage import STAGE
from UniqueVacancy import UniqueVacancy
from Vacancy import format_unique_vacancy, send_job_offer_instructions
from config import categories, programming_languages, technical_specialties, nontechnical_specialties, positions, \
    cities, headers

def get_end_subscription_date():
    current_date = datetime.now().date()
    return current_date + relativedelta(months=1)

class BotManager:
    def __init__(self, token, payments_token, db_manager, user_manager, admin_manager):
        self.bot = telebot.TeleBot(token)
        self.payments_token = payments_token
        self.db_manager = db_manager
        self.db_manager.execute_query("UPDATE users SET stage = 0")
        self.user_manager = user_manager
        self.admin_manager = admin_manager
        self.job_search = JobSearch(headers, db_manager, self.bot)
        self.users_vacancies = {}
        self.users_requests = {}
        self.setup_handlers()

    def run(self):
        self.bot.polling(none_stop=True, interval=0)

    def setup_handlers(self):
        self.bot.message_handler(commands=['start'])(self.start)
        self.bot.message_handler(commands=['pay1'])(self.pay1_command)
        self.bot.message_handler(commands=['pay2'])(self.pay2_command)
        self.bot.message_handler(commands=['pay3'])(self.pay3_command)
        self.bot.message_handler(content_types=['text'])(self.handle_text)
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('delete_request_'))(self.delete_request)
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('delete_new_unique_vacancy_'))(self.delete_new_unique_vacancy)
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('approve_new_unique_vacancy_'))(self.approve_new_unique_vacancy)
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('delete_unique_vacancy_'))(self.delete_unique_vacancy)
        self.bot.pre_checkout_query_handler(func=lambda query: True)(self.pre_checkout_query)
        self.bot.message_handler(content_types=['successful_payment'])(self.successful_payment)

    def show_main_menu(self, user_id):
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

        item1 = types.KeyboardButton("📝 Створити запит")
        item2 = types.KeyboardButton("📋 Мої запити")
        item3 = types.KeyboardButton("💳 Тарифи та Оплата")
        item4 = types.KeyboardButton("ℹ️ Про бот")
        item5 = types.KeyboardButton("💼 Запропонувати вакансію")
        item6 = types.KeyboardButton("📞 Служба підтримки")

        markup.add(item1, item2, item3, item4, item5, item6)

        self.bot.send_message(user_id, "Оберіть наступну дію:", reply_markup=markup)

    def show_create_UV_required_fields_menu(self, user_id):
        mandatory_markup = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=True)

        item1 = telebot.types.KeyboardButton("Додати назву вакансії")
        item2 = telebot.types.KeyboardButton("Додати категорію")
        item3 = telebot.types.KeyboardButton("Додати контакт для зв'язку")
        item4 = telebot.types.KeyboardButton("⬅️")
        item5 = telebot.types.KeyboardButton("➡️")

        mandatory_markup.add(item1,item2, item3)
        mandatory_markup.add(item4, item5)

        # Надсилання повідомлення з клавіатурою
        self.bot.send_message(user_id, "Оберіть обов'язкове поле для заповнення:", reply_markup=mandatory_markup)

    def show_create_UV_optional_fields_menu(self, user_id):
        mandatory_markup = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=True)

        item1 = telebot.types.KeyboardButton("Додати назву компанії")
        item2 = telebot.types.KeyboardButton("Додати позицію")
        item3 = telebot.types.KeyboardButton("Додати опис вакансії")
        item4 = telebot.types.KeyboardButton("Додати заробітню плату")
        item5 = telebot.types.KeyboardButton("Додати місто роботи")
        item6 = telebot.types.KeyboardButton("Додати досвід роботи")
        item7 = telebot.types.KeyboardButton("Повернутись назад")
        item8 = telebot.types.KeyboardButton("✅Готово")

        mandatory_markup.add(item1, item2, item3, item4, item5, item6, item7, item8)

        self.bot.send_message(user_id, "Оберіть необов'язкове поле для заповнення:",  reply_markup=mandatory_markup)

    def generate_keyboard(self, options, button_size):
       keyboard_rows = []
       for i in range(0, len(options), button_size):
            keyboard_rows.append(options[i:i + button_size])
       markup = types.ReplyKeyboardMarkup(row_width=button_size, resize_keyboard=True)
       for row in keyboard_rows:
            markup.row(*[types.KeyboardButton(option) for option in row])

       return markup

    def start(self, message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        welcome_message = """
        👋 <b>Привіт!</b> Вас вітає бот з пошуку роботи!

        Наш бот надає можливості скрапінгу вакансій з сайтів <b>Work.ua</b>, <b>Robota.ua</b>, <b>Djinni.co</b>, <b>Dou.ua</b> та <b>Jooble.ua</b>.
       
        🔹 <b>Безкоштовний запит</b>: 1 запит доступний безкоштовно. Для додаткових запитів натисніть <b>Тарифи та оплата</b>.

        🔹 <b>Запропонувати вакансію</b>: Шановні роботодавці, ви можете запропонувати унікальну вакансію, яка буде виділятися серед інших. Для цього натисніть кнопку <b>Запропонувати вакансію</b>.

        🔹 <b>Мої запити</b>: Переглядайте і керуйте своїми запитами, натиснувши <b>Мої запити</b>.

        Наш сервіс оновлює дані кожні 10 хвилин, тому ви завжди бачите найсвіжіші вакансії.

        Бажаємо успіху у пошуку роботи!🥰
        """

        self.bot.send_message(message.from_user.id, welcome_message, reply_markup=markup, parse_mode="HTML")
        self.show_main_menu(message.from_user.id)
        self.user_manager.set_stage(message.from_user.id, STAGE.START.value)


    def show_create_request_menu(self, user_id):
        self.bot.send_message(user_id, "Оберіть параметр для пошуку:", reply_markup=self.generate_keyboard(["📂 Категорія", "🏙 Місто", "💼 Позиція", "⏳ Досвід роботи", "💰 Зарплата", "🔍 Почати пошук!"], 2))

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
        self.bot.send_message(message.chat.id, f"Платіж на суму {payment_info.total_amount / 100:.2f} {payment_info.currency} пройшов успішно.")

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
            photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg", # Фото можна змінити
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
            photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg", # Фото можна змінити
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
            photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg", # Фото можна змінити
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
        end_date_subscription = get_end_subscription_date()
        self.db_manager.execute_query("UPDATE users SET paid_subscription = 1, max_num_of_request = 2, end_date_subscription = %s WHERE chat_id = %s", (end_date_subscription, chat_id))
        self.bot.send_message(chat_id, "Ваш поточний тариф змінено на Економ.")

    def pay2_payment_end(self, chat_id):
        end_date_subscription = get_end_subscription_date()
        self.db_manager.execute_query("UPDATE users SET paid_subscription = 2, max_num_of_request = 4, end_date_subscription = %s WHERE chat_id = %s", (end_date_subscription, chat_id))
        self.bot.send_message(chat_id, "Ваш поточний тариф змінено на Стандарт.")

    def pay3_payment_end(self, chat_id):
        end_date_subscription = get_end_subscription_date()
        self.db_manager.execute_query("UPDATE users SET paid_subscription = 3, max_num_of_request = 10, end_date_subscription = %s WHERE chat_id = %s", (end_date_subscription, chat_id))
        self.bot.send_message(chat_id, "Ваш поточний тариф змінено на Бізнес.")

    def show_user_requests(self, chat_id):
        query = "SELECT * FROM requests WHERE chat_id = %s"
        params = (chat_id,)
        user_requests = self.db_manager.execute_query(query, params)

        if user_requests:
            for i, req in enumerate(user_requests, start=1):
                request_text = f"""
    <b>🔍 Номер запиту:</b> {i} \n
"""

                if req[2]:
                    request_text += f"<b>📂 Категорія:</b> {req[2]}\n"
                if req[3]:
                    request_text += f"<b>💼 Позиція:</b> {req[3]}\n"
                if req[4]:
                    request_text += f"<b>🏙 Місто:</b> {req[4]}\n"
                if req[5] != 0:
                    request_text += f"<b>💰 Мінімальна заробітна плата:</b> {req[5]}\n"
                if req[6] != -2:
                    if req[6] == -1:
                        request_text += "<b>🕒 Досвід роботи:</b> Студент\n"
                    else:
                        request_text += f"<b>🕒 Досвід роботи:</b> {req[6]} років\n"

                # Додавання пояснення
                request_text += "\n<i>Якщо ви бажаєте видалити свій запит, натисніть кнопку нижче.</i>\n"

                # Створюємо InlineKeyboardButton для кожного запиту з кнопкою "Видалити"
                button = types.InlineKeyboardButton(text="❌ Видалити", callback_data=f"delete_request_{req[0]}")
                markup = types.InlineKeyboardMarkup().add(button)
                self.bot.send_message(chat_id, request_text, reply_markup=markup, parse_mode="HTML")
        else:
             no_requests_text = """
                <b>Ви ще не створили жодного запиту.</b> \n \nДля того, щоб створити запит, натисніть кнопку <b>Створити запит</b> в меню."""
             self.bot.send_message(chat_id, no_requests_text, parse_mode="HTML")

    def delete_request(self, call):
        request_id = int(call.data.split('_')[-1])
        self.db_manager.execute_query("UPDATE users SET num_of_used_request = num_of_used_request - 1 WHERE chat_id = %s", (call.from_user.id,))
        self.db_manager.execute_query("DELETE FROM requests WHERE request_id = %s", (request_id,))
        self.bot.answer_callback_query(call.id, "Запит видалено успішно.")
        self.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    def delete_unique_vacancy(self, call):
        unique_vacancy_id = int(call.data.split('_')[-1])
        delete_result = self.db_manager.execute_query("DELETE FROM unique_vacancies WHERE vacancy_id = %s", (unique_vacancy_id,))
        self.bot.answer_callback_query(call.id, "Вакансія видалена успішно.")
        self.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    def send_new_vacancy_to_admin(self, chat_id):
        button_delete = types.InlineKeyboardButton(text="❌", callback_data=f"delete_new_unique_vacancy_{chat_id}")
        button_approve = types.InlineKeyboardButton(text="✅", callback_data=f"approve_new_unique_vacancy_{chat_id}")
        markup = types.InlineKeyboardMarkup().add(button_delete, button_approve)
        self.bot.send_message(self.admin_manager.get_main_admin_id(), self.users_vacancies.get(chat_id), reply_markup=markup)

    def delete_new_unique_vacancy(self, call):
        chat_id = int(call.data.split('_')[-1])
        self.bot.send_message(chat_id, "На жаль, ваша вакансія:\n\n" + str(self.users_vacancies.get(chat_id)) + "\nНе пройшла модерування")
        del self.users_vacancies[chat_id]
        self.bot.edit_message_reply_markup(chat_id=self.admin_manager.get_main_admin_id(), message_id=call.message.message_id, reply_markup=None)
        self.bot.send_message(self.admin_manager.get_main_admin_id(), "Вакансію видалено.")

    def approve_new_unique_vacancy(self, call):
        chat_id = int(call.data.split('_')[-1])
        result = self.users_vacancies.get(chat_id).add_unique_vacancy_to_db(self.db_manager)
        self.bot.send_message(chat_id, "Вітаємо, ваша вакансія пройшла модерування і вже додана до унікальних вакансій!\n Вакансія має такий вигляд")
        if result:
            button = types.InlineKeyboardButton(text="❌ Видалити", callback_data=f"delete_unique_vacancy_{result}")
            markup = types.InlineKeyboardMarkup().add(button)
            self.bot.send_photo(chat_id, "https://i.ibb.co/ZW5P5PB/hot-vacancy.jpg", reply_markup=markup, caption=format_unique_vacancy(self.users_vacancies.get(chat_id).to_dict()), parse_mode='HTML')
        self.bot.edit_message_reply_markup(chat_id=self.admin_manager.get_main_admin_id(), message_id=call.message.message_id, reply_markup=None)
        self.bot.send_message(self.admin_manager.get_main_admin_id(), "Ви успішно затвердили вакансію, вона додана до DB.")
        del self.users_vacancies[chat_id]


    def handle_text(self, message):
        self.user_manager.check_and_new_add_user_to_db(message.from_user.id) #threading.Thread(target=check_and_new_add_user_to_db, args=(message.from_user.id, )).start()
        stage = STAGE(self.user_manager.get_stage(message.from_user.id))

        if message.text == "🔍 Почати пошук!" and stage==STAGE.CREATE_REQUEST:
            if self.users_requests.get(message.from_user.id).language == "":
              self.bot.send_message(message.from_user.id, "Для того, щоб почати пошук вакансій, необхідно обрати категорію пошуку. Це можна зробити натиснувши кнопку 'Категорія'")
              self.bot.send_message(message.from_user.id, "Оберіть категорію:", reply_markup=self.generate_keyboard(categories, 3))
              self.user_manager.set_stage(message.from_user.id, STAGE.NEXT_PARAM_CATEGORY.value)
            else:
              self.user_manager.set_stage(message.from_user.id, STAGE.START_SEARCH.value)

        if message.text == "Повернутися в головне меню" or message.text == "⬅️":
            self.user_manager.set_stage(message.from_user.id, STAGE.START.value)
            self.show_main_menu(message.from_user.id)
        else:
            stage = STAGE(self.user_manager.get_stage(message.from_user.id))
            print("stage = ", stage)
            handlers = {
                STAGE.START: self.handle_start,
                STAGE.CREATE_REQUEST: self.handle_create_request,
                STAGE.NEXT_PARAM_CATEGORY: self.handle_next_param_category,
                STAGE.NEXT_PARAM_LANGUAGE: self.handle_next_param_language,
                STAGE.NEXT_PARAM_CITY: self.handle_next_param_city,
                STAGE.NEXT_PARAM_POSITION: self.handle_next_param_position,
                STAGE.NEXT_PARAM_EXPERIENCE: self.handle_next_param_experience,
                STAGE.NEXT_PARAM_MIN_SALARY: self.handle_next_param_min_salary,
                STAGE.CREATE_UNIQUE_VACANCY: self.handle_create_unique_vacancy,
                STAGE.CREATE_UV_NEXT_PARAM_CATEGORY: self.handle_create_uv_next_param_category,
                STAGE.CREATE_UV_ADD_JOB_TITLE: self.handle_create_uv_add_job_title,
                STAGE.CREATE_UV_ADD_CATEGORY: self.handle_create_uv_add_category,
                STAGE.CREATE_UV_ADD_COMPANY_NAME: self.handle_create_uv_add_company_name,
                STAGE.CREATE_UV_ADD_DESCRIPTION: self.handle_create_uv_add_description,
                STAGE.CREATE_UV_ADD_SALARY: self.handle_create_uv_add_salary,
                STAGE.CREATE_UV_ADD_EXPERIENCE: self.handle_create_uv_add_experience,
                STAGE.CREATE_UV_ADD_CITY: self.handle_create_uv_add_city,
                STAGE.CREATE_UV_ADD_CONTACT: self.handle_create_uv_add_contact,
                STAGE.CREATE_UV_ADD_POSITION: self.handle_create_uv_add_position,
                STAGE.START_SEARCH: self.start_search,
            }
            handler = handlers.get(stage, self.handle_default)
            handler(message)

    def handle_default(self, message):
        self.bot.send_message(message.from_user.id, "Спробуйте ввести іншу команду. Введіть /start.")

    def handle_start(self, message):
        if message.text == "📋 Мої запити":
            self.user_manager.set_stage(message.from_user.id, STAGE.MY_REQUESTS.value)
            self.show_user_requests(message.from_user.id)
            self.user_manager.set_stage(message.from_user.id, STAGE.START.value)
        elif message.text == "📝 Створити запит":
            if self.user_manager.user_can_create_request(message.from_user.id):
              self.show_create_request_menu(message.from_user.id)
              self.user_manager.set_stage(message.from_user.id, STAGE.CREATE_REQUEST.value)
            else:
              self.bot.send_message(message.from_user.id, "Ви вичерпали ліміт запитів. Зверніться за передплатою.")
        elif message.text == "💳 Тарифи та Оплата":
           subscription_info = self.user_manager.get_subscription_info(message.from_user.id)
           self.bot.send_message(message.from_user.id, f"""
                        Ваш поточний тариф: {subscription_info}

                        Хочете мати більше можливостей у використанні нашого бота? Оберіть один з доступних тарифів:

                        🔴 Економ
                        - Дозволяє створювати до двох запитів для пошуку вакансій на місяць
                        - Ціна: $1 на місяць
                        - Для замовлення тарифу використайте команду /pay1

                        🟠 Стандарт
                        - Дозволяє створювати до чотирьох запитів для пошуку вакансій на місяць
                        - Ціна: $2 на місяць
                        - Для замовлення тарифу використайте команду /pay2

                        🟢 Бізнес
                        - Дозволяє створювати до десяти запитів для пошуку вакансій на місяць
                        - Ціна: $5 на місяць
                        - Для замовлення тарифу використайте команду /pay3

                        Оберіть підходящий для вас тариф, щоб отримати доступ до більшого обсягу вакансій та інших корисних функцій.
                        """)
        elif message.text == "ℹ️ Про бот":
            about_bot_message = """
            <b>Про нашого бота з пошуку роботи:</b>

            Наш бот створений для того, щоб полегшити пошук роботи для вас. Він допомагає швидко знайти актуальні вакансії з різних сайтів, заощаджуючи ваш час та зусилля.

            <b>Можливості бота:</b>

            🔹 <b>Скрапінг даних:</b>
            Наш бот збирає вакансії з популярних сайтів, таких як Work.ua, Robota.ua, Djinni.co, Dou.ua, Jooble.ua. Завдяки цьому ви отримуєте найсвіжіші вакансії, які оновлюються кожні 10 хвилин.

            🔹 <b>Безкоштовний запит:</b>
            При першому використанні ви отримуєте один безкоштовний запит. Це дозволяє вам спробувати всі можливості бота без жодних зобов'язань.

            🔹 <b>Тарифи та оплата:</b>
            Якщо ви хочете збільшити кількість запитів, натисніть кнопку <b>Тарифи та оплата</b>. Ви зможете обрати підходящий тарифний план та оплатити його для отримання додаткових запитів.

            🔹 <b>Унікальні вакансії для роботодавців:</b>
            Роботодавці можуть запропонувати свої унікальні вакансії, які матимуть спеціальний дизайн та будуть виділятися серед інших. Для цього натисніть кнопку <b>Запропонувати вакансію</b>. Ваша вакансія буде показуватися користувачам протягом 14 днів з моменту підтвердження.

            🔹 <b>Мої запити:</b>
            Ви можете переглядати та керувати своїми запитами, натиснувши кнопку <b>Мої запити</b>. Тут ви зможете видалити або переглянути свої попередні запити.

            🔹 <b>Оперативність:</b>
            Наш бот оновлює вакансії кожні 10 хвилин, що дозволяє вам бачити найновіші пропозиції роботи та реагувати на них максимально швидко.

            🔹 <b>Як користуватися ботом:</b>
            1. Використовуйте кнопки в головному меню для навігації.
            2. Введіть необхідні дані для створення запиту.
            3. Отримуйте результати та реагуйте на них.

            🔹 <b>Служба підтримки:</b>
            Якщо у вас є питання або пропозиції, натисніть кнопку <b>Служба підтримки</b> для зв'язку з нашою підтримкою.

            Дякуємо за використання нашого бота! Бажаємо успіху у пошуку роботи!
            """

            self.bot.send_message(message.from_user.id, about_bot_message, parse_mode="HTML")
        elif message.text == "💼 Запропонувати вакансію":
            send_job_offer_instructions(self, message.from_user.id)
            self.user_manager.set_stage(message.from_user.id, STAGE.CREATE_UNIQUE_VACANCY.value)
            self.show_create_UV_required_fields_menu(message.from_user.id)
            self.users_vacancies[message.from_user.id] = UniqueVacancy()
        elif message.text == "📞 Служба підтримки":
          contact_info = f"""
<b>Графік роботи служби підтримки:</b>
    Пн-Пт: <b>з 10:00 до 20:00</b>
    Сб-Нд: <b>з 11:00 до 16:00</b>

<b>Служба підтримки:</b>
  📞 <a href="tel:+380999999999">+380 (99) 999 99 99</a>
  📧 <a href="mailto:jobhunthelpersupport@gmail.com">jobhunthelpersupport@gmail.com</a>

<i>Щоб зв'язатися з менеджером, натисніть кнопку нижче:</i>
  """
                # Відправлення повідомлення з контактною інформацією
          button =  types.InlineKeyboardButton(text="📱 Зв'язатися з менеджером", url="https://t.me/anneti_net")
          # Створення клавіатури з цією кнопкою
          markup =  types.InlineKeyboardMarkup().add(button)
          self.bot.send_message(message.from_user.id, contact_info, reply_markup=markup, parse_mode="HTML")
          # # Відправлення повідомлення разом з клавіатурою
          # self.bot.send_message(chat_id, "Щоб зв'язатися з менеджером, натисніть кнопку нижче:", reply_markup=markup)
        else:
          self.show_main_menu(message.from_user.id)

    def handle_create_request(self, message):
        if message.from_user.id not in self.users_requests:
          self.users_requests[message.from_user.id] = Request()
        print(self.users_requests.get(message.from_user.id))
        if message.text == "📂 Категорія":
            self.bot.send_message(message.from_user.id, "Оберіть категорію:", reply_markup=self.generate_keyboard(categories, 3))
            self.user_manager.set_stage(message.from_user.id, STAGE.NEXT_PARAM_CATEGORY.value)
        elif message.text == "🏙 Місто":
            self.bot.send_message(message.from_user.id, "Виберіть місто для пошуку:", reply_markup=self.generate_keyboard(cities, 3))
            self.user_manager.set_stage(message.from_user.id, STAGE.NEXT_PARAM_CITY.value)
        elif message.text == "💼 Позиція":
            self.bot.send_message(message.from_user.id, "Виберіть вашу позицію:", reply_markup=self.generate_keyboard(positions, 2))
            self.user_manager.set_stage(message.from_user.id, STAGE.NEXT_PARAM_POSITION.value)
        elif message.text == "⏳ Досвід роботи":
            self.bot.send_message(message.from_user.id, "Вкажіть кількість років досвіду:")
            self.user_manager.set_stage(message.from_user.id, STAGE.NEXT_PARAM_EXPERIENCE.value)
        elif message.text == "💰 Зарплата":
            self.bot.send_message(message.from_user.id, "Вкажіть мінімальну зарплату (грн):")
            self.user_manager.set_stage(message.from_user.id, STAGE.NEXT_PARAM_MIN_SALARY.value)

    def handle_next_param_category(self, message):
        if message.text == "Розробка":
            self.bot.send_message(message.from_user.id, "Оберіть мову програмування для пошуку:", reply_markup=self.generate_keyboard(programming_languages, 3))
            self.user_manager.set_stage(message.from_user.id, STAGE.NEXT_PARAM_LANGUAGE.value)
        elif message.text == "Технічні":
            self.bot.send_message(message.from_user.id, "Оберіть технічну спеціальність для пошуку:", reply_markup=self.generate_keyboard(technical_specialties, 3))
            self.user_manager.set_stage(message.from_user.id, STAGE.NEXT_PARAM_LANGUAGE.value)
        elif message.text == "Нетехнічні":
            self.bot.send_message(message.from_user.id, "Оберіть нетехнічну спеціальність для пошуку:", reply_markup=self.generate_keyboard(nontechnical_specialties, 3))
            self.user_manager.set_stage(message.from_user.id, STAGE.NEXT_PARAM_LANGUAGE.value)

    def set_stage_create_request_and_show_menu(self, chat_id):
        self.user_manager.set_stage(chat_id, STAGE.CREATE_REQUEST.value)
        self.show_create_request_menu(chat_id)

    def handle_next_param_language(self, message):
        self.users_requests.get(message.from_user.id).set_language(message.text)
        self.set_stage_create_request_and_show_menu(message.from_user.id)

    def handle_next_param_city(self, message):
        self.users_requests.get(message.from_user.id).set_city(message.text)
        self.set_stage_create_request_and_show_menu(message.from_user.id)

    def handle_next_param_position(self, message):
        self.users_requests.get(message.from_user.id).set_position(message.text)
        self.set_stage_create_request_and_show_menu(message.from_user.id)

    def handle_next_param_experience(self, message):
        self.users_requests.get(message.from_user.id).set_experience(message.text)
        self.set_stage_create_request_and_show_menu(message.from_user.id)

    def handle_next_param_min_salary(self, message):
        self.users_requests.get(message.from_user.id).set_min_salary(message.text)
        self.set_stage_create_request_and_show_menu(message.from_user.id)

    def handle_create_unique_vacancy(self, message):
        if message.text == "⬅️":
            self.user_manager.set_stage(message.from_user.id, STAGE.START.value)
            self.show_main_menu(message.from_user.id)
        elif message.text == "Повернутись назад":
            self.user_manager.set_stage(message.from_user.id, STAGE.CREATE_UNIQUE_VACANCY.value)
            self.show_create_UV_required_fields_menu(message.from_user.id)
        elif message.text == "Додати назву вакансії":
            instructions = """
    📝 <b>Як назвати вакансію правильно?</b>

    - Використовуйте зрозумілі терміни та уникайте абревіатур, які можуть бути незрозумілі.
    - Вкажіть рівень позиції, якщо це необхідно (наприклад, Junior, Middle, Senior).

    <b>Приклад:</b>
    - Junior Python Developer
    - Senior Project Manager
    - Marketing Specialist

    <i>Напишіть назву вакансії:</i>
    """
            self.bot.send_message(message.from_user.id, instructions, parse_mode="HTML")
            self.user_manager.set_stage(message.from_user.id, STAGE.CREATE_UV_ADD_JOB_TITLE.value)
        elif message.text == "Додати категорію":
            self.bot.send_message(message.from_user.id, "Оберіть категорію з запропонованого списку", reply_markup=self.generate_keyboard(categories, 3))
            self.user_manager.set_stage(message.from_user.id, STAGE.CREATE_UV_NEXT_PARAM_CATEGORY.value)
        elif message.text == "Додати позицію":
            self.bot.send_message(message.from_user.id, "Виберіть позицію із запропонованого списку:", reply_markup=self.generate_keyboard(positions, 2))
            self.user_manager.set_stage(message.from_user.id, STAGE.CREATE_UV_ADD_POSITION.value)
        elif message.text == "Додати назву компанії":
            self.bot.send_message(message.from_user.id, "🏢 Будь ласка, введіть назву вашої компанії або ПІБ роботодавця")
            self.user_manager.set_stage(message.from_user.id, STAGE.CREATE_UV_ADD_COMPANY_NAME.value)
        elif message.text == "Додати опис вакансії":
            instructions = """
    📄 <b>Як написати опис вакансії правильно?</b>

    Опис вакансії допомагає кандидатам зрозуміти, що саме очікується від них на цій посаді, а також які навички та досвід необхідні для успішної роботи.

    <b>Основні поради:</b>
    - Вкажіть ключові обов'язки та задачі, які буде виконувати працівник.
    - Описуйте необхідні навички та кваліфікацію.
    - Зазначте умови праці, можливості для розвитку та кар'єрного росту.
    - Уникайте загальних фраз, надавайте конкретні деталі.

    <b>Приклад:</b>
    <i>
    Обов'язки:
    - Розробка та підтримка веб-додатків на Python.
    - Співпраця з командою розробників для інтеграції нових функцій.
    - Написання технічної документації.

    Вимоги:
    - Досвід роботи з Python від 2 років.
    - Знання фреймворків Django або Flask.
    - Вміння працювати з системами контролю версій (Git).

    Ми пропонуємо:
    - Конкурентну заробітну плату.
    - Гнучкий графік роботи та можливість працювати віддалено.
    - Можливості для професійного розвитку та кар'єрного росту.
    </i>

    ✏️ <i>Напишіть опис вакансії:</i>
    """
            self.bot.send_message(message.from_user.id, instructions, parse_mode="HTML")
            self.user_manager.set_stage(message.from_user.id, STAGE.CREATE_UV_ADD_DESCRIPTION.value)
        elif message.text == "Додати заробітню плату":
            instructions = """
    💵 <b>Як правильно вказати заробітну плату?</b>

    Вказування заробітної плати є важливим елементом вакансії, оскільки це може значно вплинути на кількість та якість кандидатів, які відгукнуться на вашу пропозицію.

    <b>Основні поради:</b>
    - Вказуйте заробітну плату в місячному або річному еквіваленті.
    - Зазначайте валюту (наприклад, UAH, USD, EUR).
    - Можна вказувати діапазон, якщо точна сума залежить від кваліфікації кандидата.

    <b>Приклади:</b>
    - 20,000 - 30,000 UAH
    - Від 50,000 USD на рік
    - 25,000 UAH

    📝 <i>Напишіть заробітну плату, яку ви пропонуєте:</i>
    """
            self.bot.send_message(message.from_user.id, instructions, parse_mode="HTML")
            self.user_manager.set_stage(message.from_user.id, STAGE.CREATE_UV_ADD_SALARY.value)
        elif message.text == "Додати місто роботи":
            self.bot.send_message(message.from_user.id, "Оберіть місто роботи з запропонованого списку або введіть самостійно:", reply_markup=self.generate_keyboard(cities, 3))
            self.user_manager.set_stage(message.from_user.id, STAGE.CREATE_UV_ADD_CITY.value)
        elif message.text == "Додати контакт для зв'язку":
            self.bot.send_message(message.from_user.id, " Напишіть контакт для зв'язку, який допоможе кандидатам зв'язатися з вами щодо вакансії. Ви можете вказати будь-який зручний спосіб зв'язку, такий як електронна пошта, номер телефону або логін в Telegram.")
            self.user_manager.set_stage(message.from_user.id, STAGE.CREATE_UV_ADD_CONTACT.value)
        elif message.text == "Додати досвід роботи":
            self.bot.send_message(message.from_user.id, "Напишіть необіхдну кількість років досвіду роботи")
            self.user_manager.set_stage(message.from_user.id, STAGE.CREATE_UV_ADD_EXPERIENCE.value)
        elif message.text == "Оберіть позицію із запропонованого списку":
            self.bot.send_message(message.from_user.id, "Оберіть позицію:", reply_markup=self.generate_keyboard(positions, 2))
            self.user_manager.set_stage(message.from_user.id, STAGE.CREATE_UV_ADD_POSITION.value)
        elif message.text == "➡️":
            if self.check_all_required_fields_filled(message.from_user.id):
                self.user_manager.set_stage(message.from_user.id, STAGE.CREATE_UNIQUE_VACANCY.value)
                self.show_create_UV_optional_fields_menu(message.from_user.id)
        elif message.text == "✅Готово":
            print(self.users_vacancies.get(message.from_user.id))
            self.send_new_vacancy_to_admin(message.from_user.id)
            confirmation_message = """
Дякуємо, ваша вакансія відправлена на перевірку до адміністратора.\n
🕒 Підтвердження або відмова надійдуть протягом одного робочого дня.\n
Якщо ваша вакансія буде відхилена, ми надамо детальні пояснення щодо причин цього рішення.\n
"""
            self.bot.send_message(message.from_user.id, confirmation_message, parse_mode="HTML")
            self.user_manager.set_stage(message.from_user.id, STAGE.START.value)
            self.show_main_menu(message.from_user.id)

    def check_all_required_fields_filled(self, chat_id):
        is_all_required_fields_filled = True
        str_to_user = "Ми не можемо надіслати вашу вакансію на опрацювання менеджеру, адже ви не заповнили наступні обов'язкові поля: \n"
        if self.users_vacancies.get(chat_id).title == "":
          is_all_required_fields_filled = False
          str_to_user += "- Назва\n"
        if self.users_vacancies.get(chat_id).category == "":
          is_all_required_fields_filled = False
          str_to_user += "- Категорія\n"
        if self.users_vacancies.get(chat_id).contact == "":
          str_to_user += "- Контакт\n"
          is_all_required_fields_filled = False
        if not is_all_required_fields_filled:
          self.bot.send_message(chat_id, str_to_user)
        return is_all_required_fields_filled

    def handle_create_uv_next_param_category(self, message):
        if message.text == "Розробка":
            self.bot.send_message(message.from_user.id, "Оберіть мову програмування:", reply_markup=self.generate_keyboard(programming_languages, 3))
            self.user_manager.set_stage(message.from_user.id, STAGE.CREATE_UV_ADD_CATEGORY.value)
        elif message.text == "Технічні":
            self.bot.send_message(message.from_user.id, "Оберіть технічну спеціальність:", reply_markup=self.generate_keyboard(technical_specialties, 3))
            self.user_manager.set_stage(message.from_user.id, STAGE.CREATE_UV_ADD_CATEGORY.value)
        elif message.text == "Нетехнічні":
            self.bot.send_message(message.from_user.id, "Оберіть нетехнічну спеціальність:", reply_markup=self.generate_keyboard(nontechnical_specialties, 3))
            self.user_manager.set_stage(message.from_user.id, STAGE.CREATE_UV_ADD_CATEGORY.value)

    def set_stage_create_unique_vacancy_and_show_menu(self, chat_id, is_optional):
        self.user_manager.set_stage(chat_id, STAGE.CREATE_UNIQUE_VACANCY.value)
        if not is_optional:
            self.show_create_UV_required_fields_menu(chat_id)
        else:
            self.show_create_UV_optional_fields_menu(chat_id)

    def handle_create_uv_add_job_title(self, message):
        self.users_vacancies.get(message.from_user.id).set_title(message.text)
        self.set_stage_create_unique_vacancy_and_show_menu(message.from_user.id, is_optional = False)

    def handle_create_uv_add_category(self, message):
        self.users_vacancies.get(message.from_user.id).set_category(message.text)
        self.set_stage_create_unique_vacancy_and_show_menu(message.from_user.id, is_optional = False)

    def handle_create_uv_add_company_name(self, message):
        self.users_vacancies.get(message.from_user.id).set_company(message.text)
        self.set_stage_create_unique_vacancy_and_show_menu(message.from_user.id, is_optional = True)

    def handle_create_uv_add_description(self, message):
        self.users_vacancies.get(message.from_user.id).set_description(message.text)
        self.set_stage_create_unique_vacancy_and_show_menu(message.from_user.id, is_optional = True)

    def handle_create_uv_add_salary(self, message):
        self.users_vacancies.get(message.from_user.id).set_salary(message.text)
        self.set_stage_create_unique_vacancy_and_show_menu(message.from_user.id, is_optional = True)

    def handle_create_uv_add_experience(self, message):
        self.users_vacancies.get(message.from_user.id).set_experience(message.text)
        self.set_stage_create_unique_vacancy_and_show_menu(message.from_user.id, is_optional = True)

    def handle_create_uv_add_city(self, message):
        self.users_vacancies.get(message.from_user.id).set_city(message.text)
        self.set_stage_create_unique_vacancy_and_show_menu(message.from_user.id, is_optional = True)

    def handle_create_uv_add_contact(self, message):
        self.users_vacancies.get(message.from_user.id).set_contact(message.text)
        self.set_stage_create_unique_vacancy_and_show_menu(message.from_user.id, is_optional = False)

    def handle_create_uv_add_position(self, message):
        self.users_vacancies.get(message.from_user.id).set_position(message.text)
        self.set_stage_create_unique_vacancy_and_show_menu(message.from_user.id, is_optional = True)

    def start_search(self, message):
        self.show_main_menu(message.from_user.id)
        print("start_search_and_send_unique_vacancy")
        if self.users_requests.get(message.from_user.id).add_request_to_db(message.from_user.id, self.db_manager):
          #stop_scheduler()
          self.job_search.start_search_and_send_unique_vacancy(self.users_requests.get(message.from_user.id), message.from_user.id)
          threads = []
          threads.append(threading.Thread(target=self.job_search.start_search_and_send_workua_vacancy, args=(self.users_requests.get(message.from_user.id),message.from_user.id)))
          threads.append(threading.Thread(target=self.job_search.start_search_and_send_dou_vacancy, args=(self.users_requests.get(message.from_user.id), message.from_user.id)))
          threads.append(threading.Thread(target=self.job_search.start_search_and_send_djinni_vacancy, args=(self.users_requests.get(message.from_user.id), message.from_user.id)))
          threads.append(threading.Thread(target=self.job_search.start_search_and_send_robota_vacancy, args=(self.users_requests.get(message.from_user.id), message.from_user.id)))
          threads.append(threading.Thread(target=self.job_search.start_search_and_send_jooble_vacancy, args=(self.users_requests.get(message.from_user.id), message.from_user.id)))

          for thread in threads:
              thread.start()

          for thread in threads:
              thread.join()
           #start_scheduler()
          self.user_manager.set_stage(message.from_user.id, STAGE.START.value)
          del self.users_requests[message.from_user.id]
        else:
          self.bot.send_message(message.from_user.id, "Такий запит вже існує.")
          self.user_manager.set_stage(message.from_user.id, STAGE.START.value)
          del self.users_requests[message.from_user.id]

