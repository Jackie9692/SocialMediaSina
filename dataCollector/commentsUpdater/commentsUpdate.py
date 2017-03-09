# coding=utf-8
import os.path
import time
import datetime
import sched
from threading import Thread
from mongoengine import *
from dataCollector.apiCollector.weibo import APIClient
from util import databaseConnector, configReader, logger
from dataCollector.apiCollector.model import Status
from dataCollector.apiCollector.commentsHandler import CommentManager

class statusScanner(Thread):
    def __init__(self):
        Thread.__init__(self)
        databaseConnector.connect()
        self.logFile = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, "logs","recollect_comments_error.log"))
        self.status_care_period = int(configReader.getOptionValue('time_spand', 'time_in_days'))
        self.scheduler = sched.scheduler(time.time, time.sleep)

    def zero_not_care_statuses_attention(self, start_time):
        """
        查找创建时间距离当前时间超过指定天数的微博，并更新微博关注度为0
        #待解决问题：mongoengine 不等于过滤条件
       """
        statuses_not_care = Status.objects(Q(created_at__lte=start_time)& Q(statusAttention__ne=0)).timeout(False)
        for status in statuses_not_care:
            status.statusAttention = 0
            status.save()

    def get_care_statuses(self, current_time):
        """
        获取距离当前时间小于某个天数的所有微博数据
        """
        startDateTime = current_time - datetime.timedelta(days=self.status_care_period)
        self.zero_not_care_statuses_attention(start_time=startDateTime)
        statuses_care_about = Status.objects(Q(created_at__gte=startDateTime) & Q(created_at__lte=current_time))
        return statuses_care_about

    def get_status_freshmision(self, status, current_time):
        status_created_at = status.created_at
        timedelta = current_time - status_created_at
        seconds_status_created = timedelta.total_seconds()
        hours_status_created = seconds_status_created / 3600
        status_freshmision = (self.status_care_period*24-hours_status_created)/(self.status_care_period*24)
        if status_freshmision < 0:
            status_freshmision = 0
        return status_freshmision

    def update_comments_density(self, status, comments_num=0):
        comments_density = status.commentsDensity
        if comments_density == None:#未设置此字段
            comments_count = len(status.comments)
            status.commentsDensity = comments_count
            status.save()
        else:#更新comments_density字段为
            if comments_num:
                status.commentsDensity = comments_num
                status.save()
            else:
                status.commentsDensity=0
                status.save()
        return status.commentsDensity
    def compute_update_status_attention(self,status,current_time):
        status_freshmision = self.get_status_freshmision(status, current_time)
        status_comments_density = status.commentsDensity
        if status_comments_density == None:
            status_comments_density = self.update_comments_density(status)
        if status_freshmision < 0:
            status.update(statusAttention=0)
        else:
            status_attention = status_freshmision + status_comments_density
            status.statusAttention =status_attention
            status.save()
        return status.statusAttention

    def compute_update_comments_freshmison(self, status, current_time):
        """
         根据微博评论的更新的时间（更新或获取）与当前时间的差值作为评论的新鲜程度的一个影响因子
         新鲜程度与微博评论的获取时间成反比（配置评论新鲜程度的衰减速度）
         微博评论新鲜程度的另一个影响因子是评论的受关注程度，微博的受关注程度越高，评论的新鲜度衰减的更快速
         """
        status_retrieve_timestamp = status.retrievedTimestamp
        status_scrap_timestamp = status.scrapedTimeStamp
        comments_update_timestamp = status.commentsUpdateTimestamp
        current_timestamp = int(time.mktime(datetime.datetime.timetuple(current_time)))
        status_attention = status.statusAttention
        if status_attention==None:
            status_attention = self.compute_update_status_attention(status, current_time)
        if  comments_update_timestamp== None:
            comments_update_timestamp = max(status_retrieve_timestamp, status_scrap_timestamp)
        comments_updated_seconds = int(current_timestamp-comments_update_timestamp)
        comments_updated_hours = comments_updated_seconds/3600
        most_fresh_value = float(configReader.getOptionValue('comment_freshmision', 'most_fresh_value'))
        decay_period_hour = float(configReader.getOptionValue('comment_freshmision', 'decay_period_hour'))
        comments_freshmison = most_fresh_value-(most_fresh_value/decay_period_hour)*status_attention*comments_updated_hours
        status.update(commentsFreshmison=comments_freshmison)

    def compute_all_statuses_attention_comments_freshmison(self, statuses, current_time):
        """
         根据微博的创建时间、评论的线性密度（统计增量时间内评论的增量）计算微博的受关注程度。
         受关注程度受两个影响因子的影响：1.与微博的创建时间成反比，即创建时间越久，受关注程度越低
                                        2、评论数线性密度越大，代表微博受关注程度越高
        """
        if statuses:
            # compute and update the status_attention of each status
            for status in statuses:
                self.compute_update_status_attention(status, current_time)
                self.compute_update_comments_freshmison(status, current_time)
        else:
            pass
    def compute_status(self):
        """
         1、获取关心的微博列表（创建时间距离当前时刻不超过180天）
         2、计算每条微博的attention & comments_freshmision
            2.1 计算status的attention
            2.2 计算status的comments_freshmision
         """
        current_time = datetime.datetime.now()
        statuses = self.get_care_statuses(current_time)
        self.compute_all_statuses_attention_comments_freshmison(statuses, current_time)
        interval = int(configReader.getOptionValue('comment_freshmision', 'compute_status_interval_hours'))*3600
        self.scheduler.enter(interval, 0, self.compute_status, ())
    def run(self):
        self.scheduler.enter(0, 0, self.compute_status, ())
        self.scheduler.run()
class commentsUpdater(Thread):
    def __init__(self):
        Thread.__init__(self)
        databaseConnector.connect()
        self.comments_manager = CommentManager()
        self.scheduler = sched.scheduler(time.time, time.sleep)
    def getAPPClient(self):
        accessTokenInfo = configReader.getSectionAsDict('scraper')
        appClient= APIClient(app_key=accessTokenInfo['app_key'], app_secret=accessTokenInfo['app_secret'],
        redirect_uri=accessTokenInfo['callback_url'])
        appClient.set_access_token(access_token=accessTokenInfo['access_token'], expires=accessTokenInfo['expire_in'])
        return appClient
    def scanStausNeddUpdate(self):
        most_fresh_value = float(configReader.getOptionValue('comment_freshmision', 'most_fresh_value'))
        comment_update_percent = float(configReader.getOptionValue('comment_freshmision', 'comment_update_percent'))
        need_update_fresh_value = most_fresh_value*comment_update_percent/100
        statuses_need_update_comments = Status.objects(Q(commentsFreshmison__lt=need_update_fresh_value)&Q(commentsFreshmison__exists=True))
        return statuses_need_update_comments
    def update_comments_one_status(self, status, appClient):
        current_timestamp = time.time()
        if status:
                status_id = status.status_id
                try:
                    comments_return_by_api = appClient.comments.show.get(id=status_id)
                    comments_list = comments_return_by_api['comments']
                    comments_count_before_update = len(status.comments)
                    comments_count_after_update = len(comments_list)
                    comments_ids = self.comments_manager.save_comment(comments_list, status_id)
                    status.update(comments=comments_ids)
                    comments_density = comments_count_after_update-comments_count_before_update
                    if comments_density < 0:
                        comments_density = 0
                    status.update(commentsDensity=comments_density)#更新评论密度信息
                    status.update(commentsUpdateTimestamp=current_timestamp)#更新微博更新时间戳
                except Exception:
                    logger.errorLog(self.logFile)

        else:
            pass
    def update_comments(self):
        """
         1、扫描需要更新评论的微博列表
         2、逐条更新评论信息
        """
        statuses_need_udpate = self.scanStausNeddUpdate()
        client = self.getAPPClient()
        for status in statuses_need_udpate:
            self.update_comments_one_status(status, client)
            time.sleep(5)
        interval = int(configReader.getOptionValue('comment_freshmision', 'compute_status_interval_hours'))*3600
        self.scheduler.enter(interval, 0, self.update_comments, ())
    def run(self):
        self.scheduler.enter(0, 0, self.update_comments, ())
        self.scheduler.run()
def start_comments_updater():
    status_computer = statusScanner()
    status_computer.start()
    comments_updater = commentsUpdater()
    comments_updater.start()
if __name__ == "__main__":
    start_comments_updater()