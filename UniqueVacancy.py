from datetime import datetime

from dateutil.relativedelta import relativedelta

from Experience import EXPERIENCE


class UniqueVacancy:
    def __init__(self, title="", company="", category="", description="", salary=0, position="", experience=0, city="",
                 contact="", status="active", photo=None):
        self.title = title
        self.company = company
        self.category = category
        self.description = description
        self.salary = salary
        self.position = position
        self.experience = experience
        self.city = city
        self.contact = contact
        self.status = status  # По замовчуванню вакансія активна
        self.photo = photo  # Зображення вакансії (якщо є)

    def set_title(self, title):
        if not title:
            raise ValueError("Назва вакансії не може бути порожньою.")
        self.title = title

    def set_company(self, company):
        self.company = company

    def set_category(self, category):
        self.category = category

    def set_description(self, description):
        self.description = description

    def set_position(self, position):
        self.position = position

    def set_salary(self, salary):
        self.salary = salary

    def set_experience(self, experience):
        self.experience = experience

    def set_city(self, city):
        self.city = city

    def set_contact(self, contact):
        self.contact = contact

    def set_status(self, status):
        self.status = status

    def __str__(self):
        info = f"Назва вакансії: {self.title}\n"
        info += f"Назва компанії: {self.company}\n"
        info += f"Категорія: {self.category}\n"
        info += f"Опис: {self.description}\n"
        info += f"Заробітня плата: {self.salary}\n"
        info += f"Позиція: {self.position}\n"
        info += f"Досвід роботи: {self.experience}\n"
        info += f"Місто: {self.city}\n"
        info += f"Контакт: {self.contact}\n"
        info += f"Статус: {self.status}\n"
        if self.photo:
            info += "Зображення: Додано\n"
        else:
            info += "Зображення: Не додано\n"
        return info

    def convert_to_dictionary(self):
        end_date = datetime.now().date() + relativedelta(days=14)
        return {
            "technology": self.category,
            "position": self.position,
            "city": self.city,
            "salary": self.salary,
            "experience": self.experience,
            "title": self.title,
            "company": self.company,
            "description": self.description,
            "contact": self.contact,
            "end_date": end_date
        }

    def add_unique_vacancy_to_db(self, db_manager):
        insert_query = """
                        INSERT INTO unique_vacancies (technology, position, city, salary, experience, title, company, description, contacts, end_date)
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                        """
        end_date = datetime.now().date() + relativedelta(days=14)
        insert_params = (
        self.category, self.position, self.city, self.salary, self.experience, self.title, self.company,
        self.description, self.contact, end_date)
        insert_result = db_manager.execute_query(insert_query, insert_params)

        if not insert_result:
            select_query = """
                    SELECT vacancy_id
                    FROM unique_vacancies
                    WHERE title = %s AND technology = %s AND position = %s AND salary = %s AND description = %s
                    """
            select_params = (self.title, self.category, self.position, self.salary, self.description)
            result = db_manager.execute_query(select_query, select_params)[0][0]
            return result
        return insert_result


def get_unique_vacancies_from_db(request, db_manager):
    query = f"SELECT * FROM unique_vacancies \
            WHERE technology = '{request.language}' "
    if request.position: query += f"and (position = '{request.position}' or position is null) "
    if request.city: query += f"and (city = '{request.city}' or city is null) "
    if request.min_salary: query += f"and (salary > {request.min_salary} or salary = 0) "
    if request.experience != EXPERIENCE.DEFAULT_VALUE.value: query += f"and (experience = {request.experience} or experience = -2)";
    # print(query)
    result = db_manager.execute_query(query)
    formatted_vacancies = []
    for vacancy in result:
        # print(vacancy)
        vacancy_dict = {
            'technology': vacancy[1],
            'position': vacancy[2],
            'city': vacancy[3],
            'salary': vacancy[4],
            'experience': vacancy[5],
            'title': vacancy[6],
            'company': vacancy[7],
            'description': vacancy[8],
            'contact': vacancy[10],
            'img_source': vacancy[9],
            'site': "unique"
        }
        formatted_vacancies.append(vacancy_dict)
    return formatted_vacancies
