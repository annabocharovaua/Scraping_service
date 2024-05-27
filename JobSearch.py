import time
from selenium import webdriver
from telebot.apihelper import ApiTelegramException
from Request import Request
from UniqueVacancy import get_unique_vacancies_from_db
from UrlManager import UrlManager
from random import randint
import re
from bs4 import BeautifulSoup as BS
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from Vacancy import format_unique_vacancy, format_vacancy


class JobSearch:
    def __init__(self, headers, db_manager, bot):
        self.headers = headers
        self.bot = bot
        self.db_manager = db_manager
        self.url_manage = UrlManager()

    def convert_uah_to_usd_for_djinni(self, uah_amount, exchange_rate):
        # Визначаємо список значень для округлення
        round_values = [1500, 2500, 3500, 4500, 5500, 6500, 7500, 8500]
        usd_amount = uah_amount / exchange_rate
        if (usd_amount < 1500):
            return ''
        rounded_down_value = max([value for value in round_values if value <= usd_amount], default=min(round_values))
        return rounded_down_value

    def work(self, url):
        jobs = []
        errors = []
        domain = 'https://www.work.ua'
        if url:
            resp = requests.get(url, headers=self.headers[randint(0, 2)])
            if resp.status_code == 200:
                soup = BS(resp.content, 'html.parser')
                main_div = soup.find('div', id='pjax-job-list')
                if main_div:
                    div_lst = main_div.find_all('div', attrs={'class': 'job-link'})
                    target_p = soup.find('p', class_='text-default-7 add-bottom')

                    result_divs = []
                    if target_p:
                        for div in target_p.find_all_previous('div', class_='job-link'):
                            result_divs.append(div)
                    else:
                        result_divs = div_lst

                    for div in result_divs:
                        title = div.find('h2')
                        href = title.a['href']
                        content = div.p.text
                        description = re.sub(r'\s+', ' ', content).strip()
                        img_div = div.find('div', class_='add-bottom')

                        spans = div.find_all('span', class_='strong-600')
                        salary = '0'
                        if len(spans) == 2:
                            salary = spans[0].text
                            company = spans[1].text
                        else:
                            company = spans[0].text

                        if img_div:
                            img_tag = img_div.find('img')
                            if img_tag:
                                img_src = img_tag['src']
                            else:
                                img_src = 'https://st.work.ua/i/work-ua-knowledge-graph.jpg'

                        jobs.append({'title': title.text, 'img_source': img_src, 'url': domain + href,
                                     'description': description, 'company': company,
                                      'salary': salary, 'site': "workua"})
                else:
                    errors.append({'url': url, 'title': "Div does not exists"})
            else:
                errors.append({'url': url, 'title': "Page do not response"})

        return jobs, errors

    def dou_image(self, url):
        image_src = ''
        if url:
            resp = requests.get(url, headers=self.headers[randint(0, 2)])
            if resp.status_code == 200:
                soup = BS(resp.content, 'html.parser')
                comp_div = soup.find('div', attrs={'class': 'b-compinfo'})
                if comp_div:
                    a = comp_div.find('a', attrs={'class': 'logo'})
                    image_src = a.img['src']

        return image_src

    def dou(self, url, city=None, language=None):
        jobs = []
        errors = []

        if url:
            resp = requests.get(url, headers=self.headers[randint(0, 2)])
            if resp.status_code == 200:
                soup = BS(resp.content, 'html.parser')
                main_div = soup.find('div', id='vacancyListId')
                if main_div:
                    li_lst = main_div.find_all('li', attrs={'class': 'l-vacancy'})
                    for li in li_lst:
                        title = li.find('div', attrs={'class': 'title'})
                        href = title.a['href']
                        cont = li.find('div', attrs={'class': 'sh-info'})
                        content = cont.text
                        company = 'No name'
                        salary = '0'
                        a = title.find('a', attrs={'class': 'company'})
                        img_src = self.dou_image(href)
                        if a:
                            company = a.text
                        jobs.append({'title': title.text, 'img_source': img_src, 'url': href,
                                     'description': content, 'company': company,
                                     'city_id': city, 'language_id': language, 'salary': salary, 'site': "dou"})
                else:
                    errors.append({'url': url, 'title': "Div does not exists"})
            else:
                errors.append({'url': url, 'title': "Page do not response"})

        return jobs, errors

    def djinni(self, url, city=None, language=None):
        jobs = []
        errors = []
        domain = 'https://djinni.co'
        if url:
            resp = requests.get(url, headers=self.headers[randint(0, 2)])
            if resp.status_code == 200:
                soup = BS(resp.content, 'html.parser')
                main_ul = soup.find('ul', attrs={'class': 'list-unstyled list-jobs mb-4'})
                if main_ul:
                    li_lst = main_ul.find_all('li',
                                              attrs={'class': 'list-jobs__item'})
                    for li in li_lst:
                        title_div = li.find('div',
                                            attrs={'class': 'job-list-item__title'})
                        if title_div:
                            title = title_div.a
                            href = title['href']

                        else:
                            print("Div з класом 'job-list-item__title' не знайдено.")

                        cont = li.find('div', attrs={'class': 'job-list-item__description'})
                        span = cont.find('div', attrs={'class': 'js-truncated-text'})
                        content = span.text
                        company = 'No name'
                        span_salary = li.find('span', attrs={'class': 'public-salary-item'})
                        if span_salary:
                            salary = span_salary.text
                        else:
                            salary = '0'
                        comp = li.find('a', attrs={'class': 'mr-2'})

                        img_div = li.find('div', attrs={
                            'class': 'userpic-wrapper userpic-color_2 userpic_xs userpic-transparent userpic--logo'})
                        if img_div:
                            img_src = img_div.img['src']
                        else:
                            img_src = 'https://sourcingsummit.net/sosutech/wp-content/uploads/sites/30/2017/07/djinnix505x235-1.jpg'

                        if comp:
                            company = comp.text

                        jobs.append({'title': title.text, 'img_source': img_src, 'url': domain + href,
                                     'description': content, 'company': company,
                                     'city_id': city, 'language_id': language, 'salary': salary, 'site': "djinni"})
                else:
                    errors.append({'url': url, 'title': "Div does not exists"})
            else:
                errors.append({'url': url, 'title': "Page do not response"})

        return jobs, errors

    def robota(self, url, language=None):
        jobs = []
        errors = []
        domain = 'https://robota.ua'

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=chrome_options)

        try:
            driver.get(url)
    
            for i in range(10):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            time.sleep(5)

            page_source = driver.page_source
            soup = BS(page_source, 'html.parser')

            job_divs = soup.find_all('alliance-vacancy-card-desktop')
            for job_div in job_divs:
                a = job_div.find('a', class_='card')
                if a:
                    href = a['href']
                else:
                    href = ''

                title_tag = job_div.find('h2', class_='santa-typo-h3')
                if title_tag:
                    title = title_tag.text.strip()
                else:
                    title = ''

                spans = job_div.find_all('span', class_='ng-trigger')
                salary = '0'
                company = ''
                for span in spans:
                    text = span.text.strip()
                    if '₴' in text:
                        salary = text
                    else:
                        company = text
                        break

                img_div = job_div.find('div', attrs={'class': 'company-logo'})
                img_src = 'https://play-lh.googleusercontent.com/mr-SZKDW5xmXOinA1cQWz6VeQ10BMKS_UfjGpSxrtoRAl9tNe6HPq5ALFCBAQE2Gw8A'
                if img_div:
                    img_tag = img_div.find('img')
                    if img_tag:
                        img_src = img_tag['src']

                content_divs = job_div.find_all('div', attrs={'class': 'badge'})
                content = ''
                if content_divs:
                    for div in content_divs:
                        content += div.text + "."
                    content += ".."
                if self.robota_help(driver, domain + href, language):
                    jobs.append({'title': title, 'img_source': img_src, 'url': domain + href,
                                 'description': content, 'company': company,
                                 'salary': salary, 'site': "robota"})

        except Exception as e:
            errors.append({'url': url, 'title': str(e)})

        finally:

            driver.quit()

        return jobs, errors














    # url = 'https://robota.ua/zapros/java-junior/kyiv'
    # print(url)
    # jobs, errors = robota(url)
    # print(jobs)
    # print(errors)

    def robota_help(self, driver, url, language):
        driver.get(url)
        # Отримання HTML-вмісту сторінки
        page_source = driver.page_source
        # print(page_source)

        soup = BS(page_source, 'html.parser')
        description = soup.find('div', class_='full-desc')
        if description:
            return self.contains_language(description.get_text(), language)
        else:
            return False

    def contains_language(self, description, language):
        return language.lower() in description.lower()

    def jooble(self, url):
        jobs = []
        errors = []
        if url:
            resp = requests.get(url, headers=self.headers[randint(0, 2)])
            if resp.status_code == 200:
                soup = BS(resp.content, 'html.parser')
                main_div = soup.find('div', class_='infinite-scroll-component ZbPfXY _serpContentBlock')
                if main_div:
                    div_lst = main_div.find_all('div', attrs={'data-test-name': '_jobCard'})

                    for div in div_lst:
                        a = div.find('a', class_='hyperlink_appearance_undefined')
                        href = a['href']
                        title = a.text
                        div_info = div.find('div', class_='slQ-DR')
                        salary = '0'
                        p_salary = div_info.find('p')
                        if p_salary:
                            salary = p_salary.text
                        description = div_info.find('div', class_='PAM72f')
                        div_title = div.find('div', class_='L4BhzZ')
                        p_company = div.find('p', class_='z6WlhX')
                        company = ''
                        if p_company:
                            company = p_company.text
                        img = div.find('img', class_='_3hk3rl')
                        if img and len(img['src']) < 2048:
                            img_src = img['src']
                        else:
                            img_src = 'https://play-lh.googleusercontent.com/JCQ1opom-Kay8f3xVs9VfKmDKsKD3md5uKLJf93gsYAawE6UpzgN_2fALgS0mKOcNw=s256-rw'
                        # print(jooble_help(href, language))
                        if len(href) < 2048:
                            jobs.append({'title': title, 'img_source': img_src, 'url': href,
                                         'description': description.text, 'company': company,
                                         'salary': salary, 'site': "jooble"})
                else:
                    errors.append({'url': url, 'title': "Div does not exists"})
            else:
                errors.append({'url': url, 'title': "Page do not response"})

        return jobs, errors

    def start_search_and_send_unique_vacancy(self, request: Request, chat_id, on_the_background: bool = False):
        unique_vacancies = get_unique_vacancies_from_db(request, self.db_manager)
        print(unique_vacancies)
        if not on_the_background:
            self.add_vacancies_to_db(request, chat_id, unique_vacancies, "unique")
            self.submit_vacancy(unique_vacancies, chat_id, is_unique_vacancy=True)
        else:
            return unique_vacancies

    def start_search_and_send_workua_vacancy(self, request: Request, chat_id, on_the_background: bool = False):
        if not on_the_background:
            days = 125  # вакансії за останній місяць
        else:
            days = 122  # вакансії за останній день
        url_work = self.url_manage.build_url_workua(
            language=request.language,
            city=request.city,  # ТУТ ПОХОДУ УКРАЇНСЬКОЮ НЕ МОЖНА, ТРЕБА ВИПРАВИТИ
            position=request.position,
            min_salary=request.min_salary,
            experience=request.experience,
            days=days
        )
        print("WORKUA URL: ", url_work)
        jobs_work, errors_work = self.work(url_work)
        print("WORKUA: ", jobs_work)
        print("WORKUA: ", errors_work)
        if not on_the_background:
            self.add_vacancies_to_db(request, chat_id, jobs_work, "workua")
            self.submit_vacancy(jobs_work, chat_id)
        else:
            return jobs_work, errors_work

    def start_search_and_send_dou_vacancy(self, request: Request, chat_id, on_the_background: bool = False):
        url_dou = self.url_manage.build_url_dou(search=request.language, position=request.position, city=request.city,
                                                exp=request.experience)  # в доу можна скрапить і по 0-1 і по 1-3, тоже нужно решить проблему
        print("DOU URL: ", url_dou)
        jobs_dou, errors_dou = self.dou(url_dou)
        print("DOU", jobs_dou)
        print("DOU", errors_dou)
        if not on_the_background:
            self.add_vacancies_to_db(request, chat_id, jobs_dou, "dou")
            self.submit_vacancy(jobs_dou, chat_id)
        else:
            return jobs_dou, errors_dou

    def start_search_and_send_djinni_vacancy(self, request: Request, chat_id, on_the_background: bool = False):
        url_djinni = self.url_manage.build_url_djinni(
            # all_keywords=request.language,
            primary_keyword=request.language,
            region="UKR",
            location=request.city,
            exp_level=request.experience,
            exp_rank=request.position,
            salary=self.convert_uah_to_usd_for_djinni(request.min_salary, 39.1),
            keywords=request.language
        )
        print("DJINNI URL: ", url_djinni)
        jobs_djinni, errors_djinni = self.djinni(url_djinni)
        self.add_vacancies_to_db(request, chat_id, jobs_djinni, "djinni")
        print("DJINNI", jobs_djinni)
        print("DJINNI", errors_djinni)
        if not on_the_background:
            self.submit_vacancy(jobs_djinni, chat_id)
        else:
            return jobs_djinni, errors_djinni

    def start_search_and_send_robota_vacancy(self, request: Request, chat_id, on_the_background: bool = False):
        url_robota = self.url_manage.build_url_robota(language=request.language, city=request.city,
                                                      position=request.position, salary=request.min_salary,
                                                      experience=request.experience)
        print("ROBOTA URL: ", url_robota)
        jobs_rabota, errors_robota = self.robota(url_robota, language=request.language)
        print("ROBOTA: ", jobs_rabota)
        print("ROBOTA: ", errors_robota)
        if not on_the_background:
            self.add_vacancies_to_db(request, chat_id, jobs_rabota, "robota")
            self.submit_vacancy(jobs_rabota, chat_id)
        else:
            return jobs_rabota, errors_robota

    def start_search_and_send_jooble_vacancy(self, request: Request, chat_id, on_the_background: bool = False):
        if not on_the_background:
            date = 3  # вакансії за останню неділлю
        else:
            date = 8  # вакансії за останній день
        url_jooble = self.url_manage.build_url_jooble(date=date,
                                                      rgns=request.city,
                                                      salaryMin=request.min_salary,
                                                      ukw=request.position + ' ' + request.language,
                                                      workExp=request.experience
                                                      )
        print("JOOBLE URL: ", url_jooble)
        jobs_jooble, errors_jooble = self.jooble(url_jooble)
        # print("JOOBLE: ", jobs_jooble)
        # print("JOOBLE: ", errors_jooble)
        if not on_the_background:
            self.add_vacancies_to_db(request, chat_id, jobs_jooble, "jooble")
            self.submit_vacancy(jobs_jooble, chat_id)
        else:
            return jobs_jooble, errors_jooble

    def submit_vacancy(self, jobs, chat_id, is_unique_vacancy=False):
        print("submit_vacancy")
        for job in jobs:
            #print(job)
            try:
                # print("job['img_source'] = ", job['img_source'])
                if is_unique_vacancy:
                    caption_ = format_unique_vacancy(job)
                    self.bot.send_photo(chat_id, job['img_source'], caption=caption_, parse_mode='HTML')
                else:
                    caption_, markup_ = format_vacancy(job)
                    self.bot.send_photo(chat_id, job['img_source'], caption=caption_, reply_markup=markup_,
                                   parse_mode='HTML')
            except ApiTelegramException as e:
                print(f"An error occurred while sending the photo: {e}. URL: {job['img_source']}. Skip vacancy.")

    def check_db_has_such_vacancy(self, request_id, site, title, company):
        # Проверяем, существует ли уже такая вакансия в базе данных
        check_query = """
            SELECT COUNT(*) FROM vacancies
            WHERE request_id = %s AND site = %s AND title = %s AND company = %s
            """
        check_params = (request_id, site, title, company)
        check_result = self.db_manager.execute_query(check_query, check_params)
        if check_result[0][0] == 0:
            return False
        else:
            return True

    def add_NEW_vacancy_to_db(self, request_id, site, title, company, description):
        insert_query = """
                        INSERT INTO vacancies (request_id, site, title, company, description) VALUES(%s, %s, %s, %s, %s)
                        """
        insert_params = (request_id, site, title, company, description)
        insert_result = self.db_manager.execute_query(insert_query, insert_params)
        return insert_result

    def add_vacancies_to_db(self, request: Request, chat_id, vacancies, site):
        query = """
            SELECT request_id FROM requests
            WHERE chat_id = %s AND technology = %s AND position = %s AND city = %s AND min_salary = %s AND experience = %s
            """
        params = (chat_id, request.language, request.position, request.city, request.min_salary, request.experience)
        result = self.db_manager.execute_query(query, params)

        if result:
            for vacancy in vacancies:  # [:5]:  # Обрабатываем только первые 5 вакансий. НЕТ. ПОКА ЧТО будем добавлять ВСЕ вакансии в дб, чтобы потом не было проблем
                db_has_such_vacancy = self.check_db_has_such_vacancy(result[0][0], site, vacancy['title'],
                                                                     (vacancy['company'] or '').strip())
                # Если вакансия не найдена, добавляем её в базу данных
                if db_has_such_vacancy == False:  # Проверяем, что вакансия в бд не найдена
                    insert_result = self.add_NEW_vacancy_to_db(result[0][0], site, vacancy['title'],
                                                               (vacancy['company'] or '').strip(),
                                                               vacancy.get('description', ''))
                    print("Вакансия добавлена:", insert_result)
                else:
                    print("Вакансия уже существует в базе данных")

    def process_vacancy(self, vacancy, request_item, is_unique_vacancy=False):
        print("vacancy: ", vacancy)
        if self.check_db_has_such_vacancy(request_item[0], vacancy['site'], vacancy['title'],
                                          (vacancy['company'] or '').strip()) == False:
            print("Find new vacancy! Add to db and submit to chat")
            insert_result = self.add_NEW_vacancy_to_db(request_item[0], vacancy['site'], vacancy['title'],
                                                       (vacancy['company'] or '').strip(),
                                                       vacancy.get('description', ''))
            print("Вакансия добавлена:", insert_result)
            self.submit_vacancy([vacancy], int(request_item[1]), is_unique_vacancy)  # request_item[1] - це chat_id
        else:
            print("This vacancy is already in the database")
            # bot.send_message(request_item[1], "Nothing new. I'm working...")
