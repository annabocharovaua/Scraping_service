cities = ["Повернутися в головне меню", "remote", "Kyiv", "Vinnytsia", "Dnipro", "Ivano-Frankivsk", "Zhytomyr", "Zaporizhzhia", "Lviv", "Mykolaiv", "Odesa", "Ternopil", "Kharkiv", "Khmelnytskyi", "Cherkasy", "Chernihiv", "Chernivtsi", "Uzhhorod"]
positions = ["Повернутися в головне меню", "Trainee","Intern" , "Junior", "Middle", "Senior", "Team Lead", "Chief of", "Head of"]

categories = ["Розробка", "Технічні", "Нетехнічні"]

programming_languages = ["Повернутися в головне меню", "JavaScript", "Front-End", "Fullstack", "Java", "C#", ".NET", "Python", "PHP", "Node.js", "iOS", "Android", "React Native", "C", "C++", "Embedded", "Flutter", "Golang", "Ruby", "Scala", "Salesforce", "Rust", "Elixir", "Kotlin", "ERP Systems"]
technical_specialties = ["Повернутися в головне меню", "QA Manual", "QA Automation", "Design", "2D/3D Artist", "Illustrator", "Gamedev", "Project Manager", "Product Manager", "Product Owner", "Delivery Manager", "Scrum Master", "Agile Coach", "Architect", "CTO", "DevOps", "Security", "Sysadmin", "Business Analyst", "Data Science", "Data Analyst", "Data Engineer", "SQL", "DBA", "Technical Writing"]
nontechnical_specialties = ["Повернутися в головне меню", "Marketing", "Sales", "Lead Generation", "SEO", "HR Recruiter", "Customer Support", "Technical Support", "Head", "Chief", "Finances"]

db_config = {
    "host": "eu-cluster-west-01.k8s.cleardb.net",
    "user": "bd6b7b34a39efb",
    "password": "eff5a6b2",
    "database": "heroku_79c391832132e62"
}

# db_config = {
#     "host": "127.0.0.1",
#     "port": 3306,
#     "user": "root",
#     "password": "root",
#     "database": "scraping_service"
# }

headers = [
    {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:47.0) Gecko/20100101 Firefox/47.0',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:53.0) Gecko/20100101 Firefox/53.0',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    ]