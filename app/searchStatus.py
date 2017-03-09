# -*- coding: utf-8 -*-

import sys
from flask import Flask, render_template, request, json
from elasticsearch import Elasticsearch

reload(sys)  
sys.setdefaultencoding('utf8')

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

itemsPerPage = 50


def searchStatus(request):
	#name
	status_id = request.args.get('status_id')
	if status_id != None:
		res = es.search(index="raw_data_db", doc_type='status,comments',
			body={
				"query": {
					"bool": {
						"filter": {"match_phrase": {"status_id": status_id}}
					},
				},
			})
		
		print res['hits']['total']
		return json.dumps(res['hits']['hits'][0]['_source'])
	return "Error 404"


def searchStatusList(request):
	filter = generateFilter(request)

	#statusOnly
	statusOnly = request.args.get('statusOnly')
	if statusOnly != None and statusOnly == 'true':
		collection = 'status'
	else:
		collection = 'status,comments'

	#orderBy
	sortBy = 'created_at'
	orderBy = request.args.get('orderBy')
	if orderBy == None:
		sortBy = 'created_at'
	elif orderBy == 'date':
		sortBy = 'created_at'
	elif orderBy == 'name':
		sortBy = 'name'

	orderMethod = 'desc'
	reverse = request.args.get('reverse')
	if reverse == None or reverse == 'true':
		orderMethod = 'asc'

	#search
	page = int(request.args.get('page')) * itemsPerPage

	res = es.search(index="raw_data_db", doc_type=collection, size=itemsPerPage, from_=page,
		body={
			"query": {
				"bool": {
					"filter": filter
				},
			},
			"highlight": {
				"pre_tags" : ["<em class='highlight'>"],
				"post_tags" : ["</em>"],
				"fields" : {
					"text" : {},
					"user_simple.name": {},
				}
			},
			"sort": {
				sortBy: {"order": orderMethod}
			}
		})

	print res['hits']['total']
	return json.dumps(res['hits'])


def generateFilter(request):	
	requestType = request.args.get('request')
	filter = []
	#user_id
	user_id = request.args.get('user_id')

	if user_id != None:
		filter.append({"match_phrase": {"user_simple.user_id": user_id}})

	#status_id
	status_id = request.args.get('status_id')
	if status_id != None:
		if request.args.get('getComments') == 'comments':
			filter.append({"match_phrase": {"comment_status_id": status_id}})
		elif request.args.get('getComments') == 'reposts':
			filter.append({"match_phrase": {"retweeted_status_id": status_id}})


	#keywords
	keywords = request.args.get('keywords')
	if keywords != None and keywords != "":
		for keyword in keywords.split():
			filter.append({"bool": {"should": [
				{"match_phrase": {"text": keyword}}, 
				{"match_phrase": {"user_simple.name": keyword}}
			]}})

	#location
	location = request.args.get('location')
	if location != None and location != "":
		for word in location.split():
			filter.append({"match_phrase": {"user_simple.location": word}})

	'''#topic
	topicList = request.args.get('topicList')
	if topicList != None:
		topicList = json.loads(topicList)
		allTrue = True
		allFalse = True
		for topic in topicList:
			allTrue = allTrue and topic['isSelected'] == 'true'
			allFalse = allFalse and topic['isSelected'] == 'false'

		if not allTrue and not allFalse:
			topicFilter = []
			for topic in topicList:
				if topic['isSelected'] == 'true':
					topicFilter.append({"match_phrase": {"topic": topic['value']}})
			filter.append({"bool": {"should": topicFilter}})'''

	#events
	events = request.args.get('events')
	if events != None and events != "":
		for event in events.split():
			filter.append({"match_phrase": {"events": event}})

	#mentions
	mentions = request.args.get('mentions')
	if mentions != None and mentions != "":
		for mention in mentions.split():
			filter.append({"match_phrase": {"text": '@'+mention}})

	#hashtags
	hashtags = request.args.get('hashtags')
	if hashtags != None and hashtags != "":
		for hashtag in hashtags.split():
			filter.append({"match_phrase": {"text": '#'+hashtag+'#'}})

	#timePeriod
	if requestType != "timeStatistics" and requestType != "sentimentStatistics":
		timePeriod = request.args.get('timePeriod')
		if timePeriod == None:
			timePeriod = {}
		else:
			timePeriod = json.loads(timePeriod)
		if not 'from' in timePeriod:
			timePeriod['from'] = "now-1M"
		if not 'to' in timePeriod:
			timePeriod['to'] = "now"
		filter.append({"range": {"created_at": {"gte": timePeriod['from'], "lt": timePeriod['to']}}})

	#source
	source = request.args.get('source')
	if source != None:
		source = json.loads(source)
		allTrue = True
		allFalse = True
		for item in source:
			allTrue = allTrue and source[item]
			allFalse = allFalse and not source[item]

		if not allTrue and not allFalse:
			sourceFilter = []
			for item in source:
				if source[item]:
					sourceFilter.append({"match_phrase": {"source": item}})
			filter.append({"bool": {"should": sourceFilter}})

	#feelings / sentiment
	feelings = request.args.get('feelings')
	if feelings != None and requestType != "sentimentStatistics":
		feelings = json.loads(feelings)
		allTrue = True
		allFalse = True
		for item in feelings:
			allTrue = allTrue and feelings[item]
			allFalse = allFalse and not feelings[item]

		if not allTrue and not allFalse:
			feelingsFilter = []
			if feelings['positive']:
				feelingsFilter.append({"range": {"sentimentScore": {"gte": 0.65}}})
			if feelings['neuter']:
				feelingsFilter.append({"range": {"sentimentScore": {"gt": 0.35, "lt": 0.65}}})
			if feelings['negative']:
				feelingsFilter.append({"range": {"sentimentScore": {"lte": 0.35}}})
			filter.append({"exists":{"field": "sentimentScore"}})
			filter.append({"bool": {"should": feelingsFilter}})

	return filter