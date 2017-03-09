# coding: utf-8
import datetime
from mongoengine import QuerySet
from util import databaseConnector, datatimeFormat, configReader
from model import UserAccount

class UserManager:
    def __init__(self):
        databaseConnector.connect()
    def find_user_exist(self,userId,userCollection):
        """
        根据用户Id查找用户是否已经存在于集合userCollection中
        """
        oneUser = UserAccount()
        oneUser.switch_collection(userCollection)
        user_existed = QuerySet(UserAccount, oneUser._get_collection()).filter(user_id=userId).first()
        return user_existed
    def collection_name_type(self, screenName):
        userAccountType=0
        userCollectionName="user_account_follows"

        if screenName in configReader.getOptionsValus("official_users"):
            userAccountType=1      # official users
        elif screenName in configReader.getOptionsValus("media_users"):
            userAccountType=2      # individual media users
        elif screenName in configReader.getOptionsValus("individual_media_users"):
            userAccountType=3
        else:
            userCollectionName="user_account_common"
        return userCollectionName, userAccountType
    def update_user(self,userDict,userAccount,createdTime,userAccountType):

        userAccount.update(set__name=userDict.get('name'), set__screen_name=userDict.get('screen_name'),\
                set__description=userDict.get('description'), set__gender=userDict.get('gender'), set__lang=userDict.get('lang'),\
                created_at=createdTime, province=userDict.get('province'), city=userDict.get('city'),\
                set__url=userDict.get('url'), set__credit_score=userDict.get('credit_score'), set__profile_url=userDict.get('profile_url'),\
                set__domain=userDict.get('domain'), set__followers_count=userDict.get('followers_count'), \
                set__friends_count=userDict.get('friends_count'), set__statuses_count=userDict.get('statuses_count'),\
                set__favourites_count=userDict.get('favourites_count'), set__verified=userDict.get('verified'),\
                set__verified_reason=userDict.get('verified_reason'), set__block_app=userDict.get('block_app'),\
                set__location=userDict.get('location'), set__geo_enabled=userDict.get('geo_enabled'),\
                set__weihao=userDict.get('weihao'), set__allow_all_comment=userDict.get('allow_all_comment'), \
                set__star=userDict.get('star'), set__pagefriends_count=userDict.get('pagefriends_count'),\
                set__urank=userDict.get('urank'), set__profile_image_url=userDict.get('profile_image_url'),\
                set__userAccountType=userAccountType)
        return userAccount
    def add_user(self,userDict, createdTime, userAccountType, userCollectionName,statusOrCommentId, id_of_status):
        postsList=[]
        commentsList=[]
        if id_of_status:
            postsList.append(statusOrCommentId)
        else:
            commentsList.append(statusOrCommentId)
        newAuthor=UserAccount(
                user_id=userDict.get('id'), name=userDict.get('name'), screen_name=userDict.get('screen_name'),\
                description=userDict.get('description'), gender=userDict.get('gender'), lang=userDict.get('lang'),\
                created_at=createdTime, province=userDict.get('province'), city=userDict.get('city'),\
                url=userDict.get('url'), credit_score=userDict.get('credit_score'),profile_url=userDict.get('profile_url'),\
                domain=userDict.get('domain'), followers_count=userDict.get('followers_count'), \
                friends_count=userDict.get('friends_count'), statuses_count=userDict.get('statuses_count'),\
                favourites_count=userDict.get('favourites_count'), verified=userDict.get('verified'),\
                verified_reason=userDict.get('verified_reason'), block_app=userDict.get('block_app'),\
                location=userDict.get('location'), geo_enabled=userDict.get('geo_enabled'),\
                weihao=userDict.get('weihao'), allow_all_comment=userDict.get('allow_all_comment'), \
                star=userDict.get('star'), pagefriends_count=userDict.get('pagefriends_count'),\
                urank=userDict.get('urank'), profile_image_url=userDict.get('profile_image_url'),\
                userAccountType=userAccountType,comments_id_list=commentsList,post_id_list=postsList)
        newAuthor.switch_collection(userCollectionName)
        newAuthor.save()
    def appendStatusOrCommentsID(self,userUpdate,collectionName,statusOrCommentId,id_of_status=True):
        userUpdate.switch_collection(collectionName)
        commentsIDList=userUpdate.comments_id_list
        postsIDList=userUpdate.post_id_list
        if id_of_status:
            if statusOrCommentId in postsIDList:
                pass
            else:
                postsIDList.append(statusOrCommentId)
                userUpdate.save()
        else:
            if statusOrCommentId in commentsIDList:
                pass
            else:
                commentsIDList.append(statusOrCommentId)
                userUpdate.save()
    def save_user(self,statusOrCommentId,userDict,id_of_status=True):
        """
        保存选择字段用户信息
        """
        if userDict:
            screenName=userDict.get('screen_name')
            if isinstance(screenName, unicode):
                screenName=screenName.encode(encoding='utf-8')
            userCollectionName, userAccountType = self.collection_name_type(screenName)
            userId = userDict.get('id')
            user_find = self.find_user_exist(userId, userCollectionName)
            user_created_at = userDict.get("created_at")
            user_created_time_str = datatimeFormat.strip_status_created_time(user_created_at)
            createdTime = datetime.datetime.strptime(user_created_time_str, '%a %b %d %H:%M:%S %Y')

            if user_find:
                self.appendStatusOrCommentsID(user_find, userCollectionName, statusOrCommentId, id_of_status)
            else:
                self.add_user(userDict, createdTime, userAccountType, userCollectionName, statusOrCommentId, id_of_status)
