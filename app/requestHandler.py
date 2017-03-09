# -*- coding: utf-8 -*-

from flask import request, json

from searchUser import *
from searchStatus import *
from generateStatistics import *
from geolocationEstimation import extractEntities

itemsPerPage = 10

def handleRequest(request, loggedIn):
	print "Search request received:"
	requestType = request.args.get('request')

	#res = json.dumps({"hits": [{"sort": [1464723418000], "_type": "comments", "_source": {"text": "\u524d\u4e00\u9635\u5b50\u7f51\u4e0a\u8fd8\u6709\u89c6\u9891\u7fa1\u6155\u5fb7\u56fd\u505c\u8f66\u573a\uff0c\u73b0\u5728\u8be5\u522b\u4eba\u7fa1\u6155\u4e2d\u56fd\u4e86\uff0c\u4e2d\u56fd\u521b\u9020\u503c\u5f97\u9a84\u50b2\u3002", "created_at": "2016-05-31T19:36:58", "comment_id": 3981280146175379, "source": "<a href=\"http://app.weibo.com/t/feed/2y7Irr\" rel=\"nofollow\">UC\u6d4f\u89c8\u5668Android\u7248</a>", "user_simple": {"followers_count": 35, "user_id": 2561180317, "name": "\u8c01\u5077\u4e86\u6211\u7684\u540d\u5b57\u8bf7\u901f\u8fd8", "location": "\u5176\u4ed6"}, "comment_status_id": 3981270947692734}, "_score": "null", "_index": "raw_data_db", "_id": "574e4cd3207e848324f20cc1"}, {"sort": [1464723416000], "_type": "comments", "_source": {"text": "\u4ed6\u906d\u4eba\u6697\u7b97\u4e86\u5427", "created_at": "2016-05-31T19:36:56", "comment_id": 3981280137782225, "source": "<a href=\"http://app.weibo.com/t/feed/3jskmg\" rel=\"nofollow\">iPhone 6s</a>", "user_simple": {"followers_count": 4, "user_id": 3625700997, "name": "\u7528\u62373625700997", "location": "\u5176\u4ed6"}, "comment_status_id": 3981271312367765}, "_score": "null", "_index": "raw_data_db", "_id": "574e4cd2207e848324f20c7a"}, {"sort": [1464723415000], "_type": "comments", "_source": {"text": "\u8bdd\u8bf4\u6211\u53ef\u7231\u770b\u5b98\u65b9\u8f9f\u8c23\u4e86\uff0c\u6309\u60ef\u4f8b\u53ea\u8981\u5b98\u65b9\u4e00\u8f9f\u8c23\u8fd9\u4e8b\u513f\u5c31\u516b\u4e5d\u4e0d\u79bb\u5341\u4e86\u3002", "created_at": "2016-05-31T19:36:55", "comment_id": 3981280133383042, "source": "<a href=\"http://weibo.com/\" rel=\"nofollow\">\u5fae\u535a weibo.com</a>", "user_simple": {"followers_count": 2154, "user_id": 1871836530, "name": "\u8001\u5934\u5409\u7965", "location": "\u6cb3\u5317 \u79e6\u7687\u5c9b"}, "comment_status_id": 3981273841908792}, "_score": "null", "_index": "raw_data_db", "_id": "574e4ccd207e848324f20b74"}, {"sort": [1464723412000], "_type": "comments", "_source": {"text": "\u70b9\u8d5e\uff5e\u7adf\u5fcd\u4e0d\u4f4f\u611f\u52a8\u5730\u60f3\u54ed\uff5e\u597d\u5b69\u5b50\uff0c[\u7231\u4f60]", "created_at": "2016-05-31T19:36:52", "comment_id": 3981280116242192, "source": "<a href=\"http://app.weibo.com/t/feed/5yiHuw\" rel=\"nofollow\">iPhone 6 Plus</a>", "user_simple": {"followers_count": 290, "user_id": 1808693420, "name": "Kissbaby\u5c0f\u9e7f", "location": "\u5e7f\u897f \u6842\u6797"}, "comment_status_id": 3981275984991504}, "_score": "null", "_index": "raw_data_db", "_id": "574e4cca207e848324f20acb"}, {"sort": [1464723409000], "_type": "comments", "_source": {"text": "\u786e\u5b9e\u675c\u64b0\uff0c\u4ed6\u5173\u62bc\u5728\u4e9a\u6d32\u76d1\u72f1\u3002", "created_at": "2016-05-31T19:36:49", "comment_id": 3981280108194215, "source": "<a href=\"http://app.weibo.com/t/feed/c66T5g\" rel=\"nofollow\">Android\u5ba2\u6237\u7aef</a>", "user_simple": {"followers_count": 128, "user_id": 1170546515, "name": "\u4ee5\u4e3a\u4eba\u7b28", "location": "\u9655\u897f \u897f\u5b89"}, "comment_status_id": 3981273841908792}, "_score": "null", "_index": "raw_data_db", "_id": "574e4ccd207e848324f20b76"}, {"sort": [1464723406000], "_type": "comments", "_source": {"text": "@\u5c31\u662f\u4f60\u7238\u7238\u5440", "created_at": "2016-05-31T19:36:46", "comment_id": 3981280100001012, "source": "<a href=\"http://app.weibo.com/t/feed/3o33sO\" rel=\"nofollow\">iPhone 6</a>", "user_simple": {"followers_count": 24, "user_id": 1979257953, "name": "\u5c0f\u5c0f\u5c0f\u742a\u59d0\u59d0", "location": "\u5176\u4ed6"}, "comment_status_id": 3981275888839807}, "_score": "null", "_index": "raw_data_db", "_id": "574e4ccc207e848324f20b23"}, {"sort": [1464723403000], "_type": "comments", "_source": {"text": "\u73b0\u5728\u5b98\u65b9\u7684\u8f9f\u8c23\u65b9\u5f0f\u4e5f\u662f\u5947\u7279\u3002\u82ae\u6210\u94a2\u71d5\u57ce\u76d1\u72f1\u670d\u5211\u610f\u5916\u6b7b\u4ea1\uff0c\u4ed6\u8ddf\u4f60\u8bf4\u82ae\u6210\u94a2\u538b\u6839\u6ca1\u5728\u71d5\u57ce\u76d1\u72f1\u670d\u5211\uff0c\u8fd9\u4e00\u70b9\u4e0d\u5b9e\u6240\u4ee5\u6574\u4e2a\u4f20\u95fb\u662f\u8c23\u8a00\u3002\u3002\u3002\u3002\u3002\u82ae\u6210\u94a2\u5230\u5e95\u6b7b\u4e86\u6ca1\u6709\u5462\uff1f", "created_at": "2016-05-31T19:36:43", "comment_id": 3981280087752800, "source": "<a href=\"http://app.weibo.com/t/feed/9ksdit\" rel=\"nofollow\">iPhone\u5ba2\u6237\u7aef</a>", "user_simple": {"followers_count": 245, "user_id": 1459150943, "name": "\u53e4\u4f26\u6728vs\u6b27\u5df4", "location": "\u56db\u5ddd \u5185\u6c5f"}, "comment_status_id": 3981271312367765}, "_score": "null", "_index": "raw_data_db", "_id": "574e4cd2207e848324f20c7b"}, {"sort": [1464723400000], "_type": "comments", "_source": {"text": "\u6211\u5173\u6ce8\u7684\u662f\u4ec0\u4e48\u9b3c\uff0c\u4e0d\u8fc7\u8fd8\u662f\u8c22\u8c22", "created_at": "2016-05-31T19:36:40", "comment_id": 3981280070619652, "source": "<a href=\"http://app.weibo.com/t/feed/9ksdit\" rel=\"nofollow\">iPhone\u5ba2\u6237\u7aef</a>", "user_simple": {"followers_count": 72, "user_id": 2504845540, "name": "\u516b\u6212\u8bf4\u4f60\u662f\u732a", "location": "\u798f\u5efa \u6cc9\u5dde"}, "comment_status_id": 3981277889900360}, "_score": "null", "_index": "raw_data_db", "_id": "574e4cc7207e848324f20a29"}, {"sort": [1464723399000], "_type": "status", "_source": {"reposts_count": 0, "original_pic": "http://ww3.sinaimg.cn/large/6486a91ajw1f4est3zsqej20iz0nk0w0.jpg", "status_id": 3981280065905700, "thumbnail_pic": "http://ww3.sinaimg.cn/thumbnail/6486a91ajw1f4est3zsqej20iz0nk0w0.jpg", "text": "\u3010\u4e3a\u8ba9\u513f\u5b50\u53cd\u7701 \u65e5\u672c\u7236\u6bcd\u5c06\u5b69\u5b50\u6254\u5728\u718a\u51fa\u6ca1\u5c71\u6797\u3011\u65e5\u672c\u4e00\u5bf9\u7236\u6bcd\u4e0a\u5468\u516d\u62a5\u8b66\u79f0\u4ed6\u4eec7\u5c81\u7684\u5b69\u5b50\u7530\u91ce\u5188\u5927\u548c\uff08Yamato Tanooka\uff09\u8d70\u5931\u5728\u5317\u6d77\u9053\u4e00\u7247\u718a\u51fa\u6ca1\u7684\u5c71\u6797\u4e2d\u3002\u8b66\u65b9\u4e24\u5929\u641c\u7d22\u672a\u679c\u540e\uff0c\u8fd9\u5bf9\u7236\u6bcd\u627f\u8ba4\uff0c\u4e3a\u4e86\u8ba9\u5411\u8fc7\u8def\u7684\u8f66\u548c\u884c\u4eba\u6295\u63b7\u77f3\u5757\u7684\u5927\u548c\u53cd\u7701\uff0c\u4ed6\u4eec\u5c06\u5927\u548c\u6254\u5728\u4e86\u68ee\u6797\u91cc\uff0c\u800c\u5f53\u4ed6\u4eec\u5f00\u8f66\u79bb\u5f00500\u7c73\u540e\u518d\u60f3\u5bfb\u627e\u5927\u548c\u65f6...\u5168\u6587\uff1a http://m.weibo.cn/1686546714/3981280065905700", "created_at": "2016-05-31T19:36:39", "textLength": 403, "bmiddle_pic": "http://ww3.sinaimg.cn/bmiddle/6486a91ajw1f4est3zsqej20iz0nk0w0.jpg", "retrievedTimestamp": 1464749253, "comments": [], "userType": 0, "attitudes_count": 0, "comments_count": 0, "source": "<a href=\"http://weibo.com/\" rel=\"nofollow\">\u5fae\u535a weibo.com</a>", "user_simple": {"followers_count": 1098385, "user_id": 1686546714, "name": "\u73af\u7403\u7f51", "location": "\u5317\u4eac \u671d\u9633\u533a"}, "isLongText": True, "pic_urls": [{"thumbnail_pic": "http://ww3.sinaimg.cn/thumbnail/6486a91ajw1f4est3zsqej20iz0nk0w0.jpg"}, {"thumbnail_pic": "http://ww2.sinaimg.cn/thumbnail/6486a91ajw1f4est4lf7qj20hm0b0gmf.jpg"}, {"thumbnail_pic": "http://ww3.sinaimg.cn/thumbnail/6486a91ajw1f4est59ujmj20hm0brmz4.jpg"}, {"thumbnail_pic": "http://ww4.sinaimg.cn/thumbnail/6486a91ajw1f4est5waxnj20hm0cz768.jpg"}, {"thumbnail_pic": "http://ww1.sinaimg.cn/thumbnail/6486a91ajw1f4est6i4suj20hm0brwg3.jpg"}, {"thumbnail_pic": "http://ww3.sinaimg.cn/thumbnail/6486a91ajw1f4est3cnhrj20hm0br0uq.jpg"}]}, "_score": "null", "_index": "raw_data_db", "_id": "574e4cc5207e848324f209ca"}, {"sort": [1464723397000], "_type": "comments", "_source": {"text": "\u9a6c\u82f1\u4e5d\uff1a\u505a\u4eba\u884c\uff0c\u7528\u4eba\u4e0d\u884c\uff1b\u505a\u4e8b\u884c\uff0c\u505a\u5b98\u4e0d\u884c\uff1b\u8138\u86cb\u884c\uff0c\u810a\u67f1\u4e0d\u884c\uff1b\u53e3\u624d\u884c\uff0c\u817f\u811a\u4e0d\u884c\uff1b\u5b66\u6cd5\u884c\uff0c\u73a9\u6cd5\u4e0d\u884c\uff1b\u9a97\u5927\u9646\u884c\uff0c\u8499\u53f0\u6e7e\u4e0d\u884c\uff1b\u641e\u53f0\u72ec\u884c\uff0c\u8c08\u7edf\u4e00\u7edd\u5bf9\u4e0d\u884c\uff1b\u6253\u51fb\u6df1\u84dd\u884c\uff0c\u78b0\u5230\u7eff\u86c6\u4e0d\u884c\uff1b\u5229\u7528\u90b1\u6bc5\u884c\uff0c\u91cd\u7528\u90b1\u6bc5\u4e0d\u884c\uff1b\u9677\u5bb3\u90ed\u51a0\u82f1\u884c\uff0c\u5bf9\u4ed8\u738b\u91d1\u5e73\u4e0d\u884c\uff1b\u505a\u5e02\u957f\u884c\uff0c\u505a\u7701\u957f\u4e0d\u884c\uff1b\u5f53\u592a\u5e73\u5b98\u884c\uff0c\u9047\u5230\u5929\u707e\u4eba\u7978\u4e0d\u884c\u3002", "created_at": "2016-05-31T19:36:37", "comment_id": 3981280058759672, "source": "<a href=\"http://app.weibo.com/t/feed/3IfBuR\" rel=\"nofollow\">\u534e\u4e3aAscend G7</a>", "user_simple": {"followers_count": 253, "user_id": 5843883866, "name": "\u7ea2\u76ae\u7eff\u9aa8\u517b\u80a5\u4e86\u53f0\u72ec", "location": "\u4e0a\u6d77"}, "comment_status_id": 3981272617746170}, "_score": "null", "_index": "raw_data_db", "_id": "574e4ccf207e848324f20bfa"}], "total": 123454, "max_score": "null"})
	#return res

	if requestType != None:
		print requestType
		print "------------------------"

		if requestType == "homeStatistics":
			return generateHomeStatistics(request)
		elif not loggedIn:
			return "404"
		elif requestType == "status":
			return searchStatus(request)
		elif requestType == "statusList":
			return searchStatusList(request)
		elif requestType == "user":
			return searchUser(request)
		elif requestType == "userList":
			return searchUserList(request)
		elif requestType == "homeStatistics":
			return generateHomeStatistics(request)
		elif requestType == "timeStatistics":
			return generateTimeStatistics(request)
		elif requestType == "sentimentStatistics":
			return generateSentimentStatistics(request)
		elif requestType == "locationStatistics":
			return generateLocationStatistics(request)
		elif requestType == "geolocation":
			text = request.args.get('text').encode('utf-8')
			if text != None:
				res = json.dumps(extractEntities(text))
				return res
			return "Error 404"
		else:
			print "Unknown request"
	else:
		print "Unknown request"
	return "Error  404"
