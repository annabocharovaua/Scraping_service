class UserManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def check_and_new_add_user_to_db(self, chat_id):
        result = self.db_manager.execute_query(f"SELECT * FROM users WHERE chat_id = {chat_id}")
        if not result:
            self.db_manager.execute_query(
                f"INSERT INTO users (chat_id, paid_subscription, max_num_of_request, num_of_used_request) VALUES ({chat_id}, 0, 2, 0);")

    def user_can_create_request(self, chat_id):
        user_info = self.db_manager.execute_query(
            f"SELECT num_of_used_request, max_num_of_request FROM users WHERE chat_id = {chat_id}")
        if user_info:
            num_of_used_request, max_num_of_request = user_info[0]
            if num_of_used_request >= max_num_of_request:
                return False
            else:
                return True
        return False

    def get_stage(self, chat_id):
        query = f"SELECT stage FROM users WHERE chat_id = '{chat_id}' "
        result = self.db_manager.execute_query(query)
        return result[0][0]

    def set_stage(self, chat_id, stage):
        result = self.db_manager.execute_query(f"UPDATE users SET stage = {stage} WHERE chat_id = {chat_id}")

    def get_subscription_info(self, chat_id):
        result = self.db_manager.execute_query("SELECT paid_subscription FROM users WHERE chat_id = %s", (chat_id,))
        if result:
            subscription_level = result[0][0]
            if subscription_level == 0:
                return "Ви ще не обрали жодного тарифу."
            elif subscription_level == 1:
                return "Ваш поточний тариф: 🔴 Економ."
            elif subscription_level == 2:
                return "Ваш поточний тариф: 🟠 Стандарт."
            elif subscription_level == 3:
                return "Ваш поточний тариф: 🟢 Бізнес."
        else:
            return "Ви ще не обрали жодного тарифу."

# user_manager = UserManager(db_manager)
# print(user_manager.get_stage(535434829))
# user_manager.set_stage(535434829, 0)
