# -*- coding: utf-8 -*-

import sys
from flask import Flask, render_template, request, json
from elasticsearch import Elasticsearch
from searchStatus import *

from datetime import timedelta, date, datetime


reload(sys)  
sys.setdefaultencoding('utf8')

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

itemsPerPage = 10

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def generateHomeStatistics(request):
	filter = generateFilter(request)
	res = es.search(index="raw_data_db", doc_type="status",
		body={
			"query": {
				"bool": {
					"filter": filter
				},
			},
			"sort": {
				'created_at': {"order": 'desc'}
			}
		})

	pastMonthTotalRetrieved = res['hits']['total']

	res = es.search(index="raw_data_db", doc_type="status",
		body={
			"query": {
				"bool": {
					"filter": filter
				},
			},
		})

	keyword = ("电梯","扶梯")
	filter.append({"bool": {"should": [
		{"match_phrase": {"text": keyword[0]}},
		{"match_phrase": {"text": keyword[1]}}
	]}})

	res = es.search(index="raw_data_db", doc_type="status",
		body={
			"query": {
				"bool": {
					"filter": filter
				},
			},
			"sort": {
				'created_at': {"order": 'desc'}
			}
		})

	lastStatusRetrieved = []
	if res['hits']['total'] > 3:
		for i in range(min(res['hits']['total'], 3)):
			lastStatusRetrieved.append(res['hits']['hits'][i]['_source'])

	topics = [
		{
			'name':'事故', 'value': 0
		},
		{
			'name':'安全', 'value': 0
		},
		{
			'name':'维保', 'value': 0
		},
		{
			'name':'问题', 'value': 0
		},
		{
			'name':'服务', 'value': 0
		}
	]

	for topic in topics:
		tempFilter = [{"match_phrase": {"text": topic['name']}}]
		if filter != []:
			tempFilter.append(filter)

		res = es.search(index="raw_data_db", doc_type="status",
			body={
				"query": {
					"bool": {
						"filter": tempFilter
					},
				},
			})
		topic['value'] = res['hits']['total']
	print topics


	return json.dumps({
		'lastStatusRetrieved': lastStatusRetrieved,
		'pastMonthTotalRetrieved': pastMonthTotalRetrieved,
		'pastMonthTopics': topics,
	})

def generateDateArray(request):
	timePeriod = request.args.get('timePeriod')
	if timePeriod == None:
		timePeriod = {}
	else:
		timePeriod = json.loads(timePeriod)
	if not 'to' in timePeriod:
		end_date = datetime.now()
	else:
		end_date = datetime.strptime(timePeriod['to'][:10], '%Y-%m-%d')
	if not 'from' in timePeriod:
		start_date = end_date - timedelta(days=31)
	else:
		start_date = datetime.strptime(timePeriod['from'][:10], '%Y-%m-%d')

	end_date += timedelta(days=2)
	dates = []
	for single_date in daterange(start_date, end_date):
		dates.append(single_date.strftime("%Y-%m-%d"))
	return dates

def generateTimeStatistics(request):
	filter = generateFilter(request)
	dates = generateDateArray(request)

	statuses = []
	comments = []
	for n in range(len(dates)-1):
		#search
		tempFilter = [{"range": {"created_at": {"gte": dates[n], "lt": dates[n+1]}}}]
		if filter != []:
			tempFilter.append(filter)

		res = es.search(index="raw_data_db", doc_type="status",
			body={
				"query": {
					"bool": {
						"filter": tempFilter
					},
				},
			})
		statuses.append(res['hits']['total'])

		res = es.search(index="raw_data_db", doc_type="comments",
			body={
				"query": {
					"bool": {
						"filter": tempFilter
					},
				},
			})
		comments.append(res['hits']['total'])

	del dates[-1]

	return json.dumps(
		{
			'data':{
				'date': dates,
				'status': statuses,
				'comment': comments,
			},
		})

def generateSentimentStatistics(request):
	filter = generateFilter(request)
	dates = generateDateArray(request)

	data = [[[], []], [[], []], [[], []]]

	for n in range(len(dates)-1):
		#search
		tempFilter = [{"range": {"created_at": {"gte": dates[n], "lt": dates[n+1]}}}]
		if filter != []:
			tempFilter.append(filter)
		k = 0
		for sentimentFilter in [[{"range": {"sentimentScore": {"lte": 0.35}}}], [{"range": {"sentimentScore": {"gt": 0.35, "lt": 0.65}}}], [{"range": {"sentimentScore": {"gte": 0.65}}}]]:
			sentimentFilter.append(tempFilter)
			res = es.search(index="raw_data_db", doc_type="status",
				body={
					"query": {
						"bool": {
							"filter": sentimentFilter
						},
					},
				})
			data[k][0].append(res['hits']['total'])

			res = es.search(index="raw_data_db", doc_type="comments",
				body={
					"query": {
						"bool": {
							"filter": sentimentFilter
						},
					},
				})
			data[k][1].append(res['hits']['total'])

			k += 1

	del dates[-1]

	return json.dumps(
		{
			'data':{
				'date': dates,
				'negative_status': data[0][0],
				'negative_comment': data[0][1],
				'neuter_status': data[1][0],
				'neuter_comment': data[1][1],
				'positive_status': data[2][0],
				'positive_comment': data[2][1],
			},
		})

def generateLocationStatistics(request):
	filter = generateFilter(request)

	#statusOnly
	statusOnly = request.args.get('statusOnly')

	statusData = []
	commentData = []
	max = 0
	totalItems = 0
	provinceList = [u'北京', u'天津', u'上海', u'重庆',u'河北',
				u'河南',u'云南',u'辽宁',u'黑龙江',u'湖南',
				u'安徽',u'山东',u'新疆',u'江苏',u'浙江',
				u'江西',u'湖北',u'广西',u'甘肃',u'山西',
				u'内蒙古',u'陕西',u'吉林',u'福建',u'贵州',
				u'广东',u'青海',u'西藏',u'四川',u'宁夏',
				u'海南',u'台湾',u'香港',u'澳；门',u'南海诸岛']

	for province in provinceList:
		#search
		tempFilter = [{"match_phrase": {"user_simple.location": province}}]
		tempFilter.append(filter)
		res = es.search(index="raw_data_db", doc_type="status",
			body={
				"query": {
					"bool": {
						"filter": tempFilter
					},
				},
			})

		statusData.append({'name':province, 'value': res['hits']['total']})
		totalItems += res['hits']['total']
		provinceTotalStatuses = res['hits']['total']

		provinceTotalComments = 0
		if statusOnly == None or statusOnly == 'false':
			res = es.search(index="raw_data_db", doc_type="comments",
				body={
					"query": {
						"bool": {
							"filter": tempFilter
						},
					},
				})

			commentData.append({'name':province, 'value': res['hits']['total']})
			totalItems += res['hits']['total']
			provinceTotalComments = res['hits']['total']

		if max < provinceTotalStatuses + provinceTotalComments:
			max = provinceTotalStatuses + provinceTotalComments

	return json.dumps(
		{
			'totalItems': totalItems,
			'statusData': statusData,
			'commentData': commentData,
			'max': max,
		})