import threading
import telebot
from AdminManager import AdminManager
from BotManager import BotManager
from DatabaseManager import DatabaseManager
from JobScheduler import JobScheduler
from PaymentManager import PaymentManager
from Request import Request
from UserManager import UserManager
from config import db_config

TOKEN = '7161535193:AAG2EDGz-thMU4zFHRS0ZC3OoqnmGr9L79E'
PAYMENTS_PROVIDER_TOKEN = '1661751239:TEST:mU24-EUf1-h8WQ-vwr0'

bot = telebot.TeleBot(TOKEN)
request = Request()

db_manager = DatabaseManager(db_config)
user_manager = UserManager(db_manager)
admin_manager = AdminManager(db_manager)

bot_manager = BotManager(TOKEN, PAYMENTS_PROVIDER_TOKEN, db_manager, user_manager, admin_manager)

scheduler = JobScheduler(db_manager, bot_manager.job_search)
scheduler.start_scheduler()
threading.Thread(target=scheduler.run_scheduler).start()

bot_manager.run()
