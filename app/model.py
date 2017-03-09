from mongoengine import *
class DataCleaningTask(DynamicDocument):
    name=StringField(required=True)
    source_db=StringField(required=True)
    destination_db=StringField(required=True)
    cleaning_strategy=StringField(required=True)
    keywords=ListField(required=True)
    task_state=StringField(required=True,default='created')
    task_type=StringField(required=True)
    cycle_type=StringField(required=False)
    interval_minutes=IntField(required=False)
    specific_time=ListField(required=False)
    created_time=DateTimeField(required=False)
    displayed_created_time=StringField(required=False)
    meta={
        'collection':'tasks'
    }