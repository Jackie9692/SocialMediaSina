import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import json
import re
from mongoengine import *
from util import configReader, databaseConnector
from model import DataCleaningTask
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
class cleaningTaskScaner():
    def __init__(self, task_database_name=None):
        self.task_database_host = configReader.getOptionValue('task_db', 'db_host')
        self.task_database_port = configReader.getOptionValue('task_db', 'db_port')
        self.task_database_name = configReader.getOptionValue('task_db', 'task_save_db')
        self.conn_alias = configReader.getOptionValue('task_db', 'connect_alias')
        databaseConnector.connect(dbname=self.task_database_name, host=self.task_database_host,port=int(self.task_database_port),alias=self.conn_alias)
        self.insert_default_task()
    def get_need_start_tasks(self):
        tasks_need_start = DataCleaningTask.objects(task_state="created")
        return tasks_need_start

    def reactive_tasks_need(self):
        tasks_need_reactive = DataCleaningTask.objects(Q(task_state="running") | Q(task_state="waiting"))
        for task in tasks_need_reactive:
            task.update(task_state="created")
        return tasks_need_reactive

    def insert_default_task(self):
        default_cleaning_task = configReader.getSectionAsDict('default_cleaning_task')
        default_task = DataCleaningTask.objects(name=default_cleaning_task.get('name')).first()
        if not default_task:
            keywords = default_cleaning_task.get("keywords").strip()
            keywords = re.sub(r"(,?)(\w+?)\s+?:", r"\1'\2' :", keywords)
            keywords = keywords.replace("'", "\"")
            keywords_list = json.loads(keywords)
            # print keywords_list
            default_task = DataCleaningTask(
                name=default_cleaning_task.get("name"),
                source_db=default_cleaning_task.get("source_db"),
                destination_db=default_cleaning_task.get("destination_db"),
                cleaning_strategy=default_cleaning_task.get("cleaning_strategy"),
                keywords=keywords_list,
                task_state=default_cleaning_task.get("task_state"),
                task_type=default_cleaning_task.get("task_type"),
                cycle_type=default_cleaning_task.get("cycle_type"),
                interval_minutes=default_cleaning_task.get("interval_minutes"),
            )
            default_task.save()

if __name__ == "__main__":
    cleaningScanner = cleaningTaskScaner()
    cleaningScanner.get_tasks_need_reactive()