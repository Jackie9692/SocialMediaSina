# -*- coding= utf-8 -*-
import datetime
from model import Comment
from userHandler import UserManager
from util import datatimeFormat, databaseConnector

class CommentManager:
    def __init__(self):
        #连接到默认数据库
        databaseConnector.connect()
    def find_comment_exist(self, commentId):
        #根据comment_id 查找是否已经存在
        comment_exist = Comment.objects(comment_id=commentId).first()
        return comment_exist

    def save_comment(self, commentsOfStatusDict,statusId):
        """
            status_id:微博id
            commentsOfStatusDict:一条微博的所有评论
            :return comments_ids
        """
        commentsReferenceList=[]    #comments_ids
        if commentsOfStatusDict:
            for comment in commentsOfStatusDict:
                commentId = comment.get('id')
                comment_existed = self.find_comment_exist(commentId)
                created_at_str = comment.get('created_at').decode('utf-8')
                created_at_time = datatimeFormat.strip_status_created_time(created_at_str)
                createdTime=datetime.datetime.strptime(created_at_time, '%a %b %d %H:%M:%S %Y')
                if comment_existed:#该条评论已经存在
                    if commentId in commentsReferenceList:
                        pass
                    else:
                        commentsReferenceList.append(commentId)
                else:
                    commentAuthorDict = comment.get('user')
                    userSimple={'user_id': commentAuthorDict.get('id'),
                            'name': commentAuthorDict.get('name'),
                            'location': commentAuthorDict.get('location'),
                            'followers_count': commentAuthorDict.get('followers_count')
                            }
                    newComment = Comment(
                        comment_id=comment.get('id'), text=comment.get('text'), created_at=createdTime, \
                        source=comment.get('source'), comment_status_id=statusId,
                        reply_comment_id=comment.get('reply_comment_id'), \
                        user_simple=userSimple
                    )
                    userManager = UserManager()
                    userManager.save_user(comment.get('id'), commentAuthorDict,  id_of_status=False)
                    newComment.save()
                    commentsReferenceList.append(commentId)
        return commentsReferenceList