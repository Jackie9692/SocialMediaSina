from mongoengine import *

class lastAnalisedTimstamp(DynamicDocument):
    lastAnalisedTimstamp=LongField(required=True)