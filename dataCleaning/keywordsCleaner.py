#coding=utf-8
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from threading import Thread
import sched
import time
import datetime
from mongoengine.context_managers import switch_collection, switch_db
from mongoengine import *
from util import databaseConnector
from model import DataCleaningLog
from dataValidation import validator
from dataCollector.apiCollector.model import Status, Comment, UserAccount

class keywordsCleaner(Thread):
    """
        keywords cleaner：
    """
    def __init__(self, dataCleaningTask):
        Thread.__init__(self)
        self.task = dataCleaningTask
        self.validator = validator()
        self.scheduler = sched.scheduler(time.time, time.sleep)

    def connect_db_(self, databaseName, conn_alias, db_port=27017, db_host='127.0.0.1'):
        """
            连接数据库
        """
        databaseConnector.connect(dbname=databaseName, alias=conn_alias, host=db_host, port=db_port)

    def validateComment(self, comment):
        # print "in validate comment in clear",comment._get_collection()
        comment_validated = comment.isValidated
        if not comment_validated:
            sourceText, source_type = self.validator.validateComment(comment)
            comment.update(source=sourceText, sourceType=source_type, isValidated=True)

    def validateUserProfile(self,userProfile):
        # print "in validateUserProfile function in clear",userProfile._get_collection()
        user_validated = userProfile.isValidated
        if not user_validated:
            url = self.validator.validateUserProfile(userProfile)
            userProfile.update(url=url,isValidated=True)
    def relevantCheckByKeywords(self,source_database_name,statuses):
        """
            status text 字段包含任意一个关键字或者某一关键词组合中的所有关键字，则相关；
            如果status text 字段不包括
            """
        with switch_db(Comment, source_database_name + "_conn") as Comment_in_source_db:
            for status in statuses:
                status_text = status.text  # 微博的文本字段
                comments_ids = status.comments
                comments = []
                for comment_id in comments_ids:
                    comment = Comment_in_source_db.objects(comment_id=comment_id).first()
                    if comment:
                        comments.append(comment)
                comments_num = len(comments)  # 微博评论条数
                comments_relevant_num = 0
                if self.is_relevant(status_text):
                    # 如果微博内容包含关键字，则转存数据
                    self.transportRelevantData(status, comments)
                else: #如果status本身不包含关键词，如果comments本身多余20%的comments包含关键词则保留微博与评论
                    for comment in comments:
                        comment_text = comment.text
                        if self.is_relevant(comment_text):
                            comments_relevant_num += 1
                    if comments_num > 0:
                        if float(comments_relevant_num) / float(comments_num) > 0.2:
                            self.transportRelevantData(status, comments)

    def validateStatus(self, status):
        # print "in validateStatus funciotn of cleaner",status._get_collection()
        status_validated = status.isValidated
        if not status_validated:
            geo, sourceText,sourceType, statusURL=self.validator.validateStatus(status)
            status.update(geo=geo, source=sourceText, sourceType=sourceType, statusurl=statusURL, isValidated=True)

    def validateData(self, source_database_name, statuses):
        """
        预处理所有的微博相关的所有数据：包括微博、评论、作者信息
        """
        #更新任务状态为"running"
        for status in statuses:
            #数据预处理
            status_isvalidated=status.isValidated
            if not status_isvalidated:
                comments_ids = status.comments
                status_author_id = status.user_simple.get("user_id")
                self.validateStatus(status)
                with switch_db(UserAccount, source_database_name+"_conn") as UserProfile_in_source_db:
                    with switch_collection(UserProfile_in_source_db, "user_account_common") as Common_user_in_source_db:
                        status_author = Common_user_in_source_db.objects(user_id=status_author_id).first()
                        if not status_author:
                            with switch_collection(UserProfile_in_source_db, "user_account_follows") as Follow_user_in_source_db:
                                status_author = Follow_user_in_source_db.objects(user_id=status_author_id).first()
                                if status_author:
                                    self.validateUserProfile(status_author)
                        else:
                            self.validateUserProfile(status_author)
                with switch_db(Comment, source_database_name+"_conn") as Comment_in_source_db:
                        for comment_id in comments_ids:
                            comment = Comment_in_source_db.objects(comment_id=comment_id).first()
                            if comment:
                                self.validateComment(comment)   #预处理评论信息
                                comment_author_id = comment.user_simple.get('user_id')
                                with switch_db(UserAccount, source_database_name + "_conn") as UserProfile_in_source_db:
                                    with switch_collection(UserProfile_in_source_db,"user_account_common") as Common_user_in_source_db:
                                        comment_author = Common_user_in_source_db.objects(user_id=comment_author_id).first()
                                        if not comment_author:
                                            with switch_collection(UserProfile_in_source_db, "user_account_follows") as Follow_user_in_source_db:
                                                comment_author = Follow_user_in_source_db.objects(user_id=comment_author_id).first()
                                                if comment_author:
                                                    self.validateUserProfile(comment_author)
                                        else:
                                            self.validateUserProfile(comment_author)
            return statuses

    def cleanData(self):
        """
            1、获取对应任务未清理的微博数据\评论\作者信息
            2、判断微博数据是否已经预处理
            3、相关性检验
                3.1：关键词 检验；微博相关、微博不相关
                3.2：如果关联，保存并清理掉
        """
        # #扫描未清洗的微博数据
        self.task.update(task_state="running")
        source_database_name = self.task.source_db  # 该清洗任务的源数据库
        self.connect_db_(source_database_name, source_database_name + '_conn')  # 获取源数据库的连接
        task_name = self.task.name  # task名称
        taskCleanLog = DataCleaningLog.objects(task_name=task_name).first()  # 查找当前清洗任务所对应的清洗记录
        cleanedTimestamp = 0  # 上次清洗时间戳
        if taskCleanLog != None:  # 如果存在该任务的清洗记录信息
            cleanedTimestamp = taskCleanLog.cleanedTimestamp  # 获取记录的清洗时间戳
        with switch_db(Status, source_database_name + "_conn") as Status_in_source_db:
                # 从源数据库获取上次清洗后获得的微博
                statuses_to_clean = Status_in_source_db.objects(Q(retrievedTimestamp__gte=cleanedTimestamp) | Q(scrapedTimeStamp__gte=cleanedTimestamp)).timeout(False)
                if taskCleanLog:   # update cleanTimestamp 为当前时刻
                    taskCleanLog.update(cleanedTimestamp=time.time())
                else:
                    taskCleanLog = DataCleaningLog(task_name=self.task.name, cleanedTimestamp=time.time())
                    taskCleanLog.save()
                self.validateData(source_database_name, statuses_to_clean)#数据预处理
                self.relevantCheckByKeywords(source_database_name, statuses_to_clean)#数据相关性检验并保存相关微博

    def transportUserprofile(self, destination_db_alias, user_id):
            """
                从源数据库中获取用户信息，然后转存到filtered库
            """
            def transportUserAccount(userProfile):
                # 获取当前用户信息的所在集合的信息
                collection_name=userProfile._get_collection().name
                #将数据库连接切换到目标数据库
                with switch_db(UserAccount, destination_db_alias) as UserProfile_in_des_db:

                    with switch_collection(UserProfile_in_des_db, collection_name) as UserProfile:
                        user = UserProfile(
                            id=userProfile.id,
                            user_id=userProfile.user_id,
                            name=userProfile.name,
                            screen_name=userProfile.screen_name,
                            description=userProfile.description,
                            gender=userProfile.gender,
                            lang=userProfile.lang,
                            created_at=userProfile.created_at,
                            province=userProfile.province,
                            city=userProfile.city,
                            url=userProfile.url,
                            credit_score=userProfile.credit_score,
                            profile_url=userProfile.profile_url,
                            domain=userProfile.domain,
                            followers_count=userProfile.followers_count,
                            friends_count=userProfile.friends_count,
                            statuses_count=userProfile.statuses_count,
                            favourites_count=userProfile.favourites_count,
                            verified=userProfile.verified,
                            verified_reason=userProfile.verified_reason,
                            block_app=userProfile.block_app,
                            location=userProfile.location,
                            geo_enabled=userProfile.geo_enabled,
                            weihao=userProfile.weihao,
                            allow_all_comment=userProfile.allow_all_comment,
                            star=userProfile.star,
                            pagefriends_count=userProfile.pagefriends_count,
                            urank=userProfile.urank,
                            post_id_list=userProfile.post_id_list,
                            comments_id_list=userProfile.comments_id_list,
                            category=userProfile.category,
                            rate=userProfile.rate,
                            profile_image_url=userProfile.profile_image_url,
                            retrievedTimestamp=userProfile.retrievedTimestamp,
                            userAccountType=userProfile.userAccountType,
                            isValidated=userProfile.isValidated
                        )
                        user.save()

            source_database_name = self.task.source_db
            with switch_db(UserAccount, source_database_name + "_conn") as UserProfile_in_source_db:
                with switch_collection(UserProfile_in_source_db, "user_account_common") as Common_user_in_source_db:
                    user_profile = Common_user_in_source_db.objects(user_id=user_id).first()
                    if not user_profile:
                        with switch_collection(UserProfile_in_source_db,
                                               "user_account_follows") as Follow_user_in_source_db:
                            user_profile = Follow_user_in_source_db.objects(user_id=user_id).first()
                            if user_profile:
                                transportUserAccount(user_profile)
                    else:
                        transportUserAccount(user_profile)

    def transportStatus(self, detination_db_alias, status):
        """
        从原始库将领域相关的微博数据复制到目标数据库
        """
        with switch_db(status.__class__, detination_db_alias) as Status_in_destination:
            status_new = Status_in_destination(
                id=status.id,
                status_id=status.status_id,
                text=status.text,
                created_at=status.created_at,
                geo = status.geo,
                source = status.source,
                reposts_count = status.reposts_count,
                comments_count = status.comments_count,
                attitudes_count = status.attitudes_count,
                user_simple = status.user_simple,
                retweeted_status_id = status.retweeted_status_id,
                comments = status.comments,
                userType = status.userType,
                pic_urls = status.pic_urls,
                textLength = status.textLength,
                bmiddle_pic = status.bmiddle_pic,
                original_pic = status.original_pic,
                thumbnail_pic = status.thumbnail_pic,
                keywords = status.keywords,
                feelings = status.feelings,
                pertinence = status.pertinence,
                retrievedTimestamp = status.retrievedTimestamp,
                scrapedTimeStamp = status.scrapedTimeStamp,
                statusurl = status.statusurl,
                sourceType = status.sourceType,
                statusAttention = status.statusAttention,
                commentsUpdateTimestamp = status.commentsUpdateTimestamp,
                commentsFreshmison = status.commentsFreshmison,
                commentsDensity = status.commentsDensity,
                sentimentScore = status.sentimentScore,
                isValidated =status.isValidated
            )
            status_new.save()
    def transportComments(self,destination_db_alias,comments):
        """
        将相关微博的评论信息复制到目标数据库
        """
        def transportComment(comment):
            with switch_db(Comment, destination_db_alias) as Comment_in_des_db:
                new_comment = Comment_in_des_db(
                id= comment.id,
                comment_id=comment.comment_id,
                text = comment.text,
                created_at = comment.created_at,
                source = comment.source,
                user_simple = comment.user_simple,
                retrievedTimestamp = comment.retrievedTimestamp,
                comment_status_id = comment.comment_status_id,
                reply_comment_id = comment.reply_comment_id,
                isValidated = comment.isValidated,
                sourceType = comment.sourceType
                )
                new_comment.save()
        for comment in comments:
            transportComment(comment)
            comment_author_id = comment.user_simple.get("user_id")
            self.transportUserprofile(destination_db_alias, comment_author_id)

    def transportRelevantData(self, status, comments):
        """
        将相关数据转存到目标数据库
            1.去除脏数据（无效评论数据）
            2.保存微博，评论、用户信息到目标数据库
        """
        # print "saving relevant status", status.status_id
        destination_database_name = self.task.destination_db
        destination_database_alias = destination_database_name+"_conn"
        self.connect_db_(destination_database_name, destination_database_alias)

        # #保存微博内容
        self.transportStatus(destination_database_alias, status)
        # # #保存微博作者信息
        status_author_id = status.user_simple.get("user_id")
        self.transportUserprofile(destination_database_alias, status_author_id)
        # # #保存微博评论
        self.transportComments(destination_database_alias, comments)


    def is_relevant(self, text):
        """
        :param text: 需要check的文本信息
        :return:是否相关
        """
        relevant = False
        keyWordsDictList = self.task.keywords
        for keyWordDict in keyWordsDictList:
            keywordsList = keyWordDict.get('keyWord')
            includeAllKeyWords = True
            for keyword in keywordsList:
                if keyword in text:
                    pass
                else:
                    includeAllKeyWords = False
            if includeAllKeyWords:
                relevant = True
                break
        return relevant

    def cyclic_clean_specific_time(self):
        """
            对于每天的定时任务，第一次执行后，每隔24小时执行一次。
        """
        self.cleanData()
        interval = 24 * 60 * 60
        self.scheduler.enter(interval, 0, self.cyclic_clean_specific_time, ())

    def cyclic_clean(self):
        """
            周期清洗
        """

        cyclic_type = self.task.cycle_type
        if  cyclic_type == "specific_interval":
            cyclic_interval = self.task.interval_minutes
            cyclic_seconds = int(cyclic_interval)*60
            self.cleanData()
            self.task.update(task_state="waiting")
            self.scheduler.enter(cyclic_seconds, 0, self.cyclic_clean, ())
        else:
            now = datetime.datetime.now()
            for specific_time in self.task.specific_time:
                hour = specific_time.get("hour")
                minute = specific_time.get("minute")
                second = specific_time.get("second")
                delyDateTime = now.replace(hour=hour, minute=minute, second=second)
                delaySeconds = (delyDateTime - now).total_seconds()
                interval = 24 * 60 * 60
                if delaySeconds < 0:
                    delaySeconds = interval + delaySeconds
                self.scheduler.enter(delaySeconds, 0, self.cyclic_clean_specific_time, ())

    def run(self):
        #线程启动后，对应的任务改成waiting
        self.task.update(task_state="waiting")
        if self.task.task_type == "cyclic":
            self.scheduler.enter(0, 0, self.cyclic_clean, ())
            self.scheduler.run()
        else:
            self.cleanData()
            self.task.update(task_state="finish")

if __name__ == "__main__":
    print os.path.abspath(os.path.join(os.path.dirname(__file__)))
    print os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir))