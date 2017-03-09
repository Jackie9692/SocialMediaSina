from mongoengine import *
class DataCleaningTask(DynamicDocument):
    name = StringField(required=True)
    source_db = StringField(required=True)
    destination_db = StringField(required=True)
    cleaning_strategy = StringField(required=True)
    keywords = ListField(required=True)
    task_state = StringField(required=True)
    task_type = StringField(required=True)
    cycle_type = StringField(required=False)
    interval_minutes = IntField(required=False)
    specific_time = ListField(required=False)
    meta = {
          'collection': 'tasks'
       }
class DataCleaningLog(DynamicDocument):
    task_name = StringField(required=True)
    cleanedTimestamp = LongField(required=True)
