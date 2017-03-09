# coding=utf-8
from __future__ import with_statement
import os.path
from weibo import APIClient
from model import LastRetrieveState
from userHandler import UserManager
from statusHandler import StatusManager
from commentsHandler import CommentManager
from util import configReader, logger
class Sensor():
    def __init__(self):
        self.errorLog = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, "logs","api_error.log"))
        self._userManager = UserManager()
        self._statusManager = StatusManager()
        self._commentManager = CommentManager()

    def getLastRetrieveState(self, userType):
        """
        获取特定类型用户当前最新获取的微博的ID
        """
        since_id = 0
        lastRetrieveState = LastRetrieveState.objects(userType=userType).first()
        if lastRetrieveState != None:
            since_id = lastRetrieveState.since_id
        return since_id, lastRetrieveState

    def retrieveAccountsData(self, accountType):
        """
        获取特定类型用户的微博及评论信息
        :param accountType: 用户类型（official\media）
        :return: status
        """
        appClient = self.getAppClient(accountType)#1.获取AccessToken配置信息
        since_id, lastRetrieveState = self.getLastRetrieveState(accountType)    #获取上次
        pageCount = 100
        statusList, since_id = self.retrieveStatus(appClient, pageCount, since_id)#2.调用新浪API获取最多PageCount条微博
        self.updateLastRetrieveState(accountType, since_id, lastRetrieveState)#当调用API获取微博信息后更新最新ID信息
        self.persistentStatsuList(appClient, statusList)
        return len(statusList)
    def getAppClient(self,accountType):
        app_key = configReader.getOptionValue(accountType, 'appKey')
        app_secret = configReader.getOptionValue(accountType, 'appSecret')
        callback = configReader.getOptionValue(accountType, 'callbackUrl')
        access_token = configReader.getOptionValue(accountType, 'access_token')
        expires = configReader.getOptionValue(accountType, 'expireIn')
        appClient = APIClient(app_key=app_key, app_secret=app_secret, redirect_uri=callback)
        appClient.set_access_token(access_token=access_token, expires=expires)
        return appClient
    def retrieveStatus(self, client, pageCount,sinceId):
        statusList = []
        since_id = 0
        try:
            statusesDict = client.statuses.friends_timeline.get(count=pageCount, since_id=sinceId)
            statusList = statusesDict.get('statuses')
            since_id = statusesDict.get('since_id')
        except Exception:
            logger.errorLog( self.errorLog)
        finally:
            return statusList, since_id
    def retrieveCommentsOfOneStatus(self, client, statusId):
        commentsList=[]
        max_id=0
        try:
            commentsDict=client.comments.show.get(id=statusId, count=200, max_id=max_id)
            if commentsDict:
                max_id = commentsDict['max_id']
                commentsList.extend(commentsDict['comments'])
            while max_id != 0:
                commentsDict=client.comments.show.get(id=statusId, count=200, max_id=max_id)
                max_id = commentsDict['max_id']
                commentsList.extend(commentsDict['comments'])
        except Exception:
            logger.errorLog( self.errorLog)
        finally:
            return commentsList
    def persistentStatsuList(self,client,statusList):
        for statusDic in statusList:  #逐条保存取回的微博信息
            self.persistentOneStatusDic(client, statusDic, self._userManager, self._statusManager, self._commentManager)

    def persistentOneStatusDic(self, client, statusDic, userManager, statusManager,commentManager):
         try:
            commentsNum = statusDic.get('comments_count')
            commentsOfStatusDict = None
            if (commentsNum > 0):
                commentsOfStatusDict = self.retrieveCommentsOfOneStatus(client, statusDic.get('id'))  # 获取某条微博的所有评论
            statusAuthorDict = statusDic['user']
            commentsIdList = commentManager.save_comment(commentsOfStatusDict, statusDic.get('id'))
            userManager.save_user(statusDic.get('id'), statusAuthorDict)
            if statusDic.get('retweeted_status'):  # 存储转发微博
                retweetedStatusDic = statusDic['retweeted_status']# 1.存储被转发的微博
                self.persistentOneStatusDic(client, retweetedStatusDic, userManager, statusManager, commentManager)
                statusManager.add_status_fromAPI(statusDic, commentsIdList) # 2.存储转发微博
            else:
                statusManager.add_status_fromAPI(statusDic, commentsIdList)
         except Exception:
            logger.errorLog( self.errorLog)
    def updateLastRetrieveState(self, userType, since_id, lastRetrieveState):
        if since_id == 0:
            pass
        else:
            if lastRetrieveState!=None:
                lastRetrieveState.since_id = since_id
                lastRetrieveState.save()
            else:
                lastRetrieveState_new=LastRetrieveState(userType=userType, since_id=since_id)
                lastRetrieveState_new.save()

