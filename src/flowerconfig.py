from dotenv import dotenv_values

config = dotenv_values(".env")

#flower config
port = 5555
max_tasks = 10000
auto_refresh = True
#db = 'flower.db' # SQLite database file for storing task results and states

# Authentication
basic_auth = [f'admin:{config["CELERY_FLOWER_PASSWORD"]}']
