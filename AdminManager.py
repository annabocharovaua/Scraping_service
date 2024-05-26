class AdminManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def is_admin(self, chat_id):
        result = self.db_manager.execute_query(f"SELECT * FROM admins WHERE admin_id = {chat_id}")
        if not result:
          return False
        return True

    def get_main_admin_id(self):
        result = self.db_manager.execute_query("SELECT admin_id FROM admins")
        return result[0][0]