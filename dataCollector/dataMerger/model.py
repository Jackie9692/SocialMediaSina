from mongoengine import *
class StatusToMerge(DynamicDocument):
    status_id = LongField(required=True)
    user_simple = DictField(required=True)
    text = StringField(required=True)
    date = DateTimeField(required=True)
    userurl = URLField(required=False)
    source = StringField(required=False)
    repost_count =IntField(required=False)
    comments_count =IntField(required=False)
    attitude_count = IntField(required=False)
    statusurl = URLField(required=False)
    geo =DictField(required=False)
    pic_urls =ListField(required=True)
    keywords =ListField(required=True)
    timestamp = LongField(required=True)
    meta = {
          'collection': 'status_to_merge',
          'indexes': ['status_id']
       }
class UserToMerge(DynamicDocument):
    Name = StringField(required=False)
    friends_count = IntField(required=False)
    followers_count = IntField(required=False)
    statuses_count = IntField(required=False)
    timestamp = IntField(required=False)
    meta = {
          'collection': 'user_to_merge'
       }

class LastCheckTimeStamp(Document):
    checkedTimeStamp = LongField(required=True)