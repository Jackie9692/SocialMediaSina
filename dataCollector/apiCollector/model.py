from mongoengine import *
class UserAccount(DynamicDocument):
      user_id = LongField(required=True)
      name=StringField(required=False)
      screen_name = StringField(required=False)
      description=StringField(required=False)
      gender=StringField(required=False)
      lang=StringField(required=False)
      created_at=DateTimeField(required=True)
      province=IntField(required=False)
      city=IntField(required=False)
      url=StringField(required=False)
      credit_score = IntField(required=False)
      profile_url=StringField(required=False)
      domain=StringField(required=False)
      followers_count=IntField(required=False)
      friends_count=IntField(required=False)
      statuses_count=IntField(required=False)
      favourites_count=IntField(required=False)
      verified=BooleanField(required=False)
      verified_reason=StringField(required=False)
      block_app=IntField(required=False)
      location=StringField(required=False)
      geo_enabled = BooleanField(required=False)
      weihao=StringField(required=False)
      allow_all_comment=BooleanField(required=False)
      star=IntField(required=False)
      pagefriends_count=IntField(required=False)
      urank = IntField(required=False)
      post_id_list = ListField(default=[])
      comments_id_list=ListField(default=[])
      category=StringField(required=False, default=None)
      rate=StringField(required=False, default=None)
      profile_image_url=URLField(required=False)
      retrievedTimestamp=LongField(required=False)
      userAccountType=IntField(required=False, default=0)
      isValidated = BooleanField(required=False)
      meta={
             'collection': 'user_account_common',
             'indexes': [
             'user_id',
             '$name'
            ]
      }
class Comment(DynamicDocument):
      comment_id=LongField(required=True)
      text=StringField(required=False)
      created_at=DateTimeField(required=False)
      source=StringField(required=False)
      user_simple=DictField(required=True)
      retrievedTimestamp=LongField(required=False)
      comment_status_id=LongField(required=True, default=None)
      reply_comment_id=LongField(required=False, default=None)
      isValidated=BooleanField(required=False)
      sourceType=StringField(required=False)
      meta = {
          'collection': 'comments',
          'indexes': ['comment_id']
      }
class Status(DynamicDocument):
       status_id=LongField(required=True)
       text=StringField(required=True)
       created_at=DateTimeField(required=False)
       geo=DictField(required=False, default=None)
       source=StringField(required=False)
       reposts_count=IntField(required=False)
       comments_count=IntField(required=False)
       attitudes_count=IntField(required=False)
       user_simple = DictField(required=True)
       retweeted_status_id = LongField(required=False, default=None)
       comments=ListField(LongField(), default=None)
       userType=IntField(required=False)
       pic_urls=ListField(required=False, default=list)
       textLength=IntField(required=False, default=None)
       bmiddle_pic=StringField(required=False,   default=None)
       original_pic=StringField(required=False,  default=None)
       thumbnail_pic=StringField(required=False, default=None)
       keywords=ListField(StringField(), required=False, default=None)
       feelings=StringField(required=False, default=None)
       pertinence=StringField(required=False)
       retrievedTimestamp=LongField(required=False)
       scrapedTimeStamp=LongField(required=False)
       statusurl = URLField(required=False)
       sourceType = StringField(default=None, required=False)
       statusAttention = FloatField(default=None, required=False)
       commentsUpdateTimestamp=LongField(default=None, required=False)
       commentsFreshmison= FloatField(default=None, required=False)
       commentsDensity=IntField(default=None, required=False)
       sentimentScore=FloatField(required=False,default=None)
       isValidated = BooleanField(required=False)
       meta = {
          'collection': 'status',
          'indexes': ['status_id']
       }
class LastRetrieveState(Document):
      userType = StringField(required=True, unique=True)
      since_id = LongField(required=True)