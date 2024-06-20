import time
from itertools import chain
from Request import Request
import schedule

class JobScheduler:
    def __init__(self, db_manager, job_search):
        self.db_manager = db_manager
        self.job_search = job_search
        self.keep_running = False

    def background_vacancy_search(self):
        print("Start working on background")
        requests_from_db = self.db_manager.get_requests_from_db()
        for request_item in requests_from_db:
          request_from_db = Request(language=request_item[2], city=request_item[4], position=request_item[3], min_salary=request_item[5], experience=request_item[6])
          print(request_from_db)
          print("Start searching on background")
          unique_vacancies = self.job_search.start_search_and_send_unique_vacancy(request_from_db, 0, on_the_background = True)
          jobs_work, errors_work = self.job_search.start_search_and_send_workua_vacancy(request_from_db, 0, on_the_background = True)
          jobs_dou, errors_dou = self.job_search.start_search_and_send_dou_vacancy(request_from_db, 0, on_the_background = True)
          jobs_djinni, errors_djinni = self.job_search.start_search_and_send_djinni_vacancy(request_from_db, 0, on_the_background = True)
          jobs_rabota, errors_robot = self.job_search.start_search_and_send_robota_vacancy(request_from_db, 0, on_the_background = True)
          jobs_jooble, errors_jooble = self.job_search.start_search_and_send_jooble_vacancy(request_from_db, 0, on_the_background = True)
          print("End searching on background")

          vacancies = list(chain(jobs_work, jobs_dou, jobs_djinni, jobs_rabota, jobs_jooble))
          #vacancies = [jobs_work]#, jobs_dou, jobs_djinni, jobs_rabota, jobs_jooble]
          print("Start checking finding vacancies")
          for vacancy in unique_vacancies:
              self.job_search.process_vacancy(vacancy, request_item, is_unique_vacancy=True)
          for vacancy in vacancies:
              self.job_search.process_vacancy(vacancy, request_item)
          print("End checking finding vacancies")

    def start_scheduler(self):
        self.keep_running = True

    def stop_scheduler(self):
        self.keep_running = False

    def run_scheduler(self):
        schedule.every(10).minutes.do(self.background_vacancy_search)
        print("start run_scheduler. keep_running = ", self.keep_running)
        while self.keep_running:
            schedule.run_pending()
            time.sleep(10)
