from telebot import types
class FormatVacancy:
    def format_vacancy(job):
        # Инициализация сообщения с заголовком вакансии
        vacancy_message = f"💼 <b>{job['title'].strip()}</b>\n\n"

        # Проверка и добавление компании
        if 'company' in job and job['company'].strip():
            vacancy_message += f"🏢 <b>Компанія:</b> {job['company'].strip()}\n\n"

        # Проверка и добавление зарплаты, если она не пустая и не равна '0'
        salary = job.get('salary', '')
        if salary and salary not in ['0', '']:
            vacancy_message += f"💵 <b>Зарплата:</b> {salary}\n\n"

        # Проверка и добавление описания вакансии
        description = job.get('description', '')
        if description.strip():
            vacancy_message += f"📝 <b>Опис вакансії:</b>\n{description.strip()}\n\n"

        # Добавление строки с информацией о кнопке
        vacancy_message += "<i>Щоб детальніше ознайомитися з вакансією, натисніть кнопку нижче:</i>"

        site = job.get('site', '')
        if site == 'workua':
            button_text = "Переглянути на Work.ua"
        elif site == 'robota':
            button_text = "Переглянути на Robota"
        elif site == 'djinni':
            button_text = "Переглянути на Djinni"
        elif site == 'jooble':
            button_text = "Переглянути на Jooble"
        elif site == 'dou':
            button_text = "Переглянути на DOU"
        else:
            button_text = "Переглянути"

        button = types.InlineKeyboardButton(text=button_text, url=job['url'])
        markup = types.InlineKeyboardMarkup().add(button)

        return vacancy_message, markup


    def format_unique_vacancy(job):
        info = f"🔥 <b>{job['title']}</b>\n\n"
        if job['company']:
            info += f"🏢 <b>Компанія:</b> {job['company']}\n\n"
        if job['position']:
            info += f"👨‍💼 <b>Позиція:</b> {job['position']}\n\n"
        if job['city']:
            info += f"🏙 <b>Місто:</b> {job['city']}\n\n"

        if int(job['salary']) > 0:
            info += f"💰 <b>Заробітна плата:</b> {job['salary']} \n\n"

        if job['description']:
            info += f"📝 <b>Опис:</b> {job['description']}\n\n"

        info += f"📞 <b>Контакт:</b> {job['contact']}\n\n"
        return info
