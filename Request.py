from Experience import EXPERIENCE


class Request:
  def __init__(self, language='', city='', position='', min_salary=0, experience=EXPERIENCE.DEFAULT_VALUE.value):
    self.language = language
    self.city = city
    self.position = position
    self.min_salary = int(min_salary)
    self.experience = int(experience)

  def __str__(self):
    return (f"Request(Language: {self.language}, City: {self.city}, "
            f"Position: {self.position}, Min Salary: {self.min_salary}, "
            f"Experience: {self.experience})")

  def set_language(self, language):
    self.language = language

  def set_city(self, city):
    self.city = city

  def set_position(self, position):
    self.position = position

  def set_min_salary(self, min_salary):
    try:
      self.min_salary = int(min_salary)
    except ValueError:
      print("Min salary must be a valid integer string")

  def set_experience(self, experience):
    try:
      self.experience = int(experience)
    except ValueError:
      print("Experience must be a valid integer string")


  def add_request_to_db(self, chat_id, db_manager):
    existing_request = db_manager.execute_query("SELECT * FROM requests WHERE chat_id = %s AND technology = %s AND position = %s AND city = %s AND min_salary = %s AND experience = %s", (chat_id, self.language, self.position, self.city, self.min_salary, self.experience))
    if not existing_request:
                db_manager.execute_query(f"UPDATE users SET num_of_used_request = num_of_used_request + 1 WHERE chat_id = {chat_id}")
                db_manager.execute_query("INSERT INTO requests (chat_id, technology, position, city, min_salary, experience) VALUES (%s, %s, %s, %s, %s, %s)", (chat_id, self.language, self.position, self.city, self.min_salary, self.experience))
    else:
      return False
    return True