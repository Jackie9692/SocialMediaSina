# coding =utf-8
import time
import datetime
from model import Status
from util import datatimeFormat, databaseConnector
class StatusManager:
    def __init__(self):
        databaseConnector.connect()
    def find_status_exist(self, statusId):
        """
        checking the status is all ready exist in the status collection
        """
        status_existed = Status.objects(status_id=statusId).first()
        return status_existed
    def update_comments(self,status,commentids):
        status.update(comments=commentids)

    def append_comment(self, status, commentid):
        comments = status.comments
        if commentid not in comments:
            comments.append(commentid)
        status.update(comments=comments)
    def format_created_at(self,created_at,formatStr):
        if isinstance(created_at, unicode):
            created_at = created_at.encode()
        if created_at.find("+0800"):
            createdTimeStr = datatimeFormat.strip_status_created_time(created_at)
            createdTime = datetime.datetime.strptime(createdTimeStr,formatStr)
        return createdTime
    def get_simple_user(self,statusDic):
        statusAuthor=statusDic.get('user')
        if statusAuthor:
            userSimple = {'user_id': statusAuthor.get('id'),
                          'name': statusAuthor.get('name'),
                          'location': statusAuthor.get('location'),
                          'followers_count': statusAuthor.get('followers_count')}
            return userSimple
    def add_status_fromAPI(self,statusDic, commentsIds=None):
        status_id = statusDic.get('id')
        created_at = self.format_created_at(statusDic.get('created_at'), "%a %b %d %H:%M:%S %Y")
        retrieveTimestamp = time.time()
        usersimple = self.get_simple_user(statusDic)
        status_exist = self.find_status_exist(status_id)
        user_id = usersimple.get('user_id')
        if user_id:
            statusURL="http://api.weibo.com/2/statuses/go?uid="+str(user_id)+"&id="+(str(status_id))
        if not status_exist:
            newStatus = Status(status_id=statusDic.get('id'),
                               text=statusDic.get('text'),
                               created_at=created_at,
                               geo=statusDic.get('geo'),
                               source=statusDic.get('source'),
                               reposts_count=statusDic.get('reposts_count'),
                               comments_count=statusDic.get('comments_count'),
                               attitudes_count=statusDic.get('attitudes_count'),
                               user_simple=usersimple,
                               comments=commentsIds,
                               userType=statusDic.get('userType'),
                               pic_urls=statusDic.get('pic_urls'),
                               isLongText=statusDic.get('isLongText'),
                               bmiddle_pic=statusDic.get('bmiddle_pic'),
                               original_pic=statusDic.get('original_pic'),
                               thumbnail_pic=statusDic.get('thumbnail_pic'),
                               textLength=statusDic.get('textLength'),
                               retrievedTimestamp=retrieveTimestamp,
                               statusurl=statusURL,
                               keywords=statusDic.get('key_words'))
            if statusDic.get('retweeted_status'):
                newStatus.retweeted_status_id = statusDic.get('retweeted_status').get('id')
            newStatus.save()
    def get_simpleUser(self,userDic):
        userSimple = {'user_id': userDic.get("id"),
                      'name': userDic.get('screen_name'),
                      'location': userDic.get('location'),
                      'followers_count': userDic.get('followers_count')}
        return userSimple

    def add_status_fromCrawler(self, authorDic,statusToMerge, commentsIds=None):
        status_id = statusToMerge.status_id
        usersimple = self.get_simpleUser(authorDic)
        status_exist = self.find_status_exist(status_id)
        user_id = usersimple.get('user_id')
        if user_id:
            statusURL = "http://api.weibo.com/2/statuses/go?uid=" + str(user_id) + "&id=" + (str(status_id))
        else:
            statusURL=statusToMerge.statusurl
        pic_url_list = statusToMerge.pic_urls
        pic_url_dic_list = []
        for pic_url in pic_url_list:
            pic_url_dic = {'thumbnail_pic': pic_url}
            pic_url_dic_list.append(pic_url_dic)
        if not status_exist:
            newStatus = Status(status_id=status_id,
                               text=statusToMerge.text,
                               created_at=statusToMerge.date,
                               geo=statusToMerge.geo,
                               source=statusToMerge.source,
                               reposts_count=statusToMerge.repost_count,
                               comments_count=statusToMerge.comments_count,
                               attitudes_count=statusToMerge.attitude_count,
                               user_simple=usersimple,
                               comments=commentsIds,
                               pic_urls=pic_url_dic_list,
                               scrapedTimeStamp=statusToMerge.timestamp,
                               statusurl=statusURL,
                               keywords=statusToMerge.keywords)
            newStatus.save()
