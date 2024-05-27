from Experience import EXPERIENCE
from urllib.parse import urlencode, quote

class UrlManager:
    def build_url(self, base_url, **params):
        # Видаляємо всі елементи, які мають None або порожнє значення
        filtered_params = {k: v for k, v in params.items() if v}
        query_string = urlencode(filtered_params)
        return f"{base_url}?{query_string}" if query_string else base_url

    def build_url_djinni(self, **params):
        base_url = "https://djinni.co/jobs/"

        params["location"] = params["location"].lower()
        if params["location"] == "remote":
            params["employment"] = "remote"
            del params["location"]

        if params["exp_level"] == EXPERIENCE.DEFAULT_VALUE.value or params["exp_level"] > EXPERIENCE.FIVE_YEAR.value:
            params["exp_level"] = ""
        else:
            params["exp_level"] = str(params["exp_level"]) + 'y'
        if params["exp_level"] == "0y":
            params["exp_level"] = "no_exp"

        params["exp_rank"] = params["exp_rank"].lower()
        return self.build_url(base_url, **params)

    def build_url_workua(self, language='', city='', position='', min_salary=0, experience=EXPERIENCE.DEFAULT_VALUE.value,
                         **params):
        base_url = "https://www.work.ua/jobs"
        if city:
            base_url += '-' + city
        if language:
            base_url += '-' + quote(language)
        if position:
            base_url += '+' + position
        base_url += '/'

        if min_salary:
            if 3000 <= min_salary and min_salary < 5000:
                params["salaryfrom"] = 2
            elif 5000 <= min_salary and min_salary < 7000:
                params["salaryfrom"] = 3
            elif 7000 <= min_salary and min_salary < 10000:
                params["salaryfrom"] = 4
            elif 10000 <= min_salary and min_salary < 15000:
                params["salaryfrom"] = 5
            elif 15000 <= min_salary and min_salary < 20000:
                params["salaryfrom"] = 6
            elif 20000 <= min_salary and min_salary < 30000:
                params["salaryfrom"] = 7
            elif min_salary > 30000:
                params["salaryfrom"] = 8

        if experience == EXPERIENCE.WITHOUT_EXPERIENCE.value:
            params["experience"] = 1
        elif experience == EXPERIENCE.STUDENT.value:
            params["student"] = 1

        return self.build_url(base_url, **params)

    def build_url_dou(self, **params):
        base_url = "https://jobs.dou.ua/vacancies/"
        if params["city"] == "remote":
            del params["city"]
            params["remote"] = 'remote'

        if params.get("position"):
            params["search"] += " " + params["position"]
            del params["position"]
        if params["exp"] == EXPERIENCE.STUDENT.value or params["exp"] == EXPERIENCE.WITHOUT_EXPERIENCE.value or params[
            "exp"] == EXPERIENCE.ONE_YEAR.value:
            params["exp"] = "0-1"
        elif params["exp"] == EXPERIENCE.TWO_YEAR.value or params["exp"] == EXPERIENCE.THREE_YEAR.value:
            params["exp"] = "1-3"
        elif params["exp"] == EXPERIENCE.FOUR_YEAR.value or params["exp"] == EXPERIENCE.FIVE_YEAR.value:
            params["exp"] = "3-5"
        elif params["exp"] > EXPERIENCE.FIVE_YEAR.value:
            params["exp"] = "5plus"
        else:
            del params["exp"]

        return self.build_url(base_url, **params)

    def build_url_robota(self, language='', city='', **params):
        base_url = "https://robota.ua/zapros/"
        if language:
            base_url += quote(language).lower()
        if params["position"]:
            base_url += '-' + params["position"].lower()
            del params["position"]
        base_url += '/'

        if city == "remote":
            params["scheduleIds"] = 3
        elif city:
            base_url += city.lower() + '/'
        else:
            base_url += "ukraine" + '/'

        if params["experience"] == EXPERIENCE.WITHOUT_EXPERIENCE.value:
            params["experienceType"] = "true"
        params["experience"] = ""

        return self.build_url(base_url, **params)

    def build_url_jooble(self, **params):
        base_url = "https://ua.jooble.org/SearchResult"

        if params["workExp"] == EXPERIENCE.STUDENT.value or params["workExp"] == EXPERIENCE.WITHOUT_EXPERIENCE.value:
            params["workExp"] = 1
        else:
            params["workExp"] = ""

        if params["rgns"] == "remote":
            params["loc"] = 2
            params["rgns"] = ""
        return self.build_url(base_url, **params)

