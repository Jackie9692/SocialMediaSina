#coding= utf-8
import datetime
import os.path
from dataCollector.apiCollector.weibo import APIClient
from util import databaseConnector, logger, configReader
from model import LastCheckTimeStamp, UserToMerge, StatusToMerge
from dataCollector.apiCollector.userHandler import UserManager
from dataCollector.apiCollector.statusHandler import StatusManager
from dataCollector.apiCollector.commentsHandler import CommentManager


class StatusMerger():
    """
        satus 合并
        1、扫描未合并的微博及用户信息
        2.如果未命中，则调用API获取评论信息保存评论及微博信息
        3、如果命中，更新status的keywords和获取时间戳
    """
    def __init__(self, statusManage, userManage, commentManage,logFileName):
        self.errorLog = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, "logs", "merge_error.log"))
        self.statusManager = statusManage
        self.userManager = userManage
        self.commentManager = commentManage
        self.logFile = logFileName
        databaseConnector.connect()

    def mergeLog(self, message):
        logger.logging(self.logFile, message)

    def getCurrentLastCheckTimeStamp(self):
        """
            获取上次合并微博的时间戳
        """
        lastCheckTimeStamp=LastCheckTimeStamp.objects.first()
        if lastCheckTimeStamp:
            leastTimeStamp=lastCheckTimeStamp.checkedTimeStamp
            logMessage = "Now is "+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" ,untill now we have checked the statuses whose timestamp is less than : "+str(leastTimeStamp)+"\n"
            self.mergeLog(logMessage)
            return leastTimeStamp
        else:
            logMessage="Untill now we have not checked any status to merge.\n"
            self.mergeLog(logMessage)
            return 0

    def updateCurrentLastCheckTimeStamp(self, currentCheckTimeStamp):
        """
        获取微博合并微博列表后更新时间戳为当前时间戳，确保下次扫描不会扫描已经合并的微博
        """
        try:
            lastCheckTimeStamp = LastCheckTimeStamp.objects.first()
            if lastCheckTimeStamp:
                lastCheckTimeStamp.update(checkedTimeStamp=currentCheckTimeStamp)
            else:
                lastCheckTimeStamp=LastCheckTimeStamp(checkedTimeStamp=currentCheckTimeStamp)
                lastCheckTimeStamp.save()
        except Exception:
                logger.errorLog(self.errorLog)

    def getUserInfo(self, client, userName):
        try:
            #首先根据ScreenName获取API返回的部分信息
            user_account_dict = {}
            user_account_dict = client.users.show.get(screen_name=userName)
        except Exception:
            logger.errorLog(self.errorLog)
        #获取user_to_merge中查找name为userName的
        user_info_in_to_merge = UserToMerge.objects(name=userName).first()
        if user_info_in_to_merge:
            if user_info_in_to_merge.friends_count:
                user_account_dict['friends_count'] = user_info_in_to_merge.friends_count
            if user_info_in_to_merge.followers_count:
                user_account_dict['followers_count'] = user_info_in_to_merge.followers_count
            if user_info_in_to_merge.statuses_count:
                user_account_dict['statuses_count'] = user_info_in_to_merge.statuses_count
        else:
            pass
        return user_account_dict
    def retrieveCommentsOfOneStatus(self, client, statusId):
        commentsList=[]
        try:
            commentsDict = client.comments.show.get(id=statusId)
            commentsList = commentsDict['comments']
        except Exception:
            logger.errorLog(self.errorLog)
        finally:
            return commentsList

    def mergeOneStatus(self, client, statusToMerge):
        try:
            #根据status.user_simple.get('name')信息调用API获取用户信息
            statusAuhtorScreenName = statusToMerge.user_simple.get('name')
            status_author_dict = self.getUserInfo(client, statusAuhtorScreenName)
            if not status_author_dict:
                    message =" Error:Get author information failed ,the status id is "+str(statusToMerge.status_id)+".\n"
                    self.mergeLog(message)
            status_to_merge_id = statusToMerge.status_id
            if status_author_dict:
                self.userManager.save_user(status_to_merge_id, status_author_dict) #merge the user in to do collection.
            status_existed = self.statusManager.find_status_exist(status_to_merge_id) # is the status already retrieved before.
            if status_existed:
                #命中:update keywords of the status and scrap time
                logMessage="The status whose id is "+str(statusToMerge.status_id)+" already in the database! Do updating!\n"
                self.mergeLog(logMessage)
                keywords_now = status_existed.keywords
                if keywords_now:
                    keywords_scraped = statusToMerge.keywords
                    keywords_new = list(set(keywords_now).union(set(keywords_scraped)))
                else:
                    keywords_new = statusToMerge.keywords
                status_existed.update(keywords=keywords_new, scrapedTimeStamp=statusToMerge.timestamp)
            else:
                #未命中:add the status in to merge to status collection.
                #retrieve the comments of the status by the status id.
                logMessage="The status whose id is "+str(statusToMerge.status_id)+" is not in the database! Do adding!\n"
                self.mergeLog(logMessage)
                commentsNum = statusToMerge.comments_count
                commentsOfStatusDict=None
                if (commentsNum > 0):
                    commentsOfStatusDict = self.retrieveCommentsOfOneStatus(client, status_to_merge_id)  # 获取某条微博的所有评论
                commentsReferencedList= self.commentManager.save_comment(commentsOfStatusDict, status_to_merge_id)
                self.statusManager.add_status_fromCrawler(status_author_dict,statusToMerge, commentsReferencedList)
        except Exception:
                logger.errorLog(self.errorLog)
def getScrapyClient():
    accessTokenInfo = configReader.getSectionAsDict('scraper')
    appClient= APIClient(app_key=accessTokenInfo['app_key'], app_secret=accessTokenInfo['app_secret'],
    redirect_uri=accessTokenInfo['callback_url'])
    appClient.set_access_token(access_token=accessTokenInfo['access_token'], expires=accessTokenInfo['expire_in'])
    return appClient
def checkStatusInTODO(interval,statusMerger,scrpyerClient,mergeScheduler):
    haveCheckScrapeTimeStamp = statusMerger.getCurrentLastCheckTimeStamp()
    logMessage="Check Status In TO Merge whose timestamp is bigger than "+str(haveCheckScrapeTimeStamp)+"\n"
    statusMerger.mergeLog(logMessage)
    statusNotCheckedInTODO=StatusToMerge.objects(timestamp__gt=haveCheckScrapeTimeStamp).order_by('timestamp+')
    logMessage="There are "+str(len(statusNotCheckedInTODO))+" statuses wait to be merged"
    statusMerger.mergeLog(logMessage)
    for status in statusNotCheckedInTODO:
        largestTimeStamp = status.timestamp
        statusMerger.updateCurrentLastCheckTimeStamp(largestTimeStamp)
        statusMerger.mergeOneStatus(scrpyerClient, status)
    #执行一次扫描后，再次将自身加入待执行队列，等待执行。
    mergeScheduler.enter(interval, 0, checkStatusInTODO, (interval, statusMerger, scrpyerClient, mergeScheduler))
def mergerStart(mergeScheduler):
    #merge Log 文件路径
    mergeLogFile=os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, "logs","data_merger.log"))
    statusManager=StatusManager()
    userManager=UserManager()
    commentManager=CommentManager()
    #创建merge对象
    statusMerger= StatusMerger(statusManager, userManager, commentManager, mergeLogFile)
    scrpyerClient=getScrapyClient()
    intervalCheck=int(configReader.getOptionValue("retrieve_interval_seconds", "interval"))
    #将此次执行任务加入调度队列，等待执行
    mergeScheduler.enter(0, 0, checkStatusInTODO, (intervalCheck, statusMerger, scrpyerClient, mergeScheduler))
if __name__ == "__main__":
    mergerStart()