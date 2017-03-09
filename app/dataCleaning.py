from flask import json
from mongoengine import connect
from model import DataCleaningTask
from flask import redirect,url_for
import datetime

def getTasks():
	connect('cleaning_tasks_db')
	tasks = DataCleaningTask.objects()
	if len(tasks) < 1:
		tasks = False
	else:
		tasks = json.loads(tasks.to_json())
	return json.dumps({"taskList": tasks})

def addTask(task):
	task_name = task['name']
	source_db_name = task['sourceDb']
	des_db_name = task['destinationDb']
	cleaning_strategy = task['cleaningStrategy']
	keywords = task['keywords']
	task_type = task['taskType']
	cycle_type = task['cycleType']
	time_interval = task['fixTimeInterval']
	hour = task['specificTime']['h']
	minute = task['specificTime']['m']
	second = task['specificTime']['s']

	keywordsList=task['keywords'].split(u' ')
	keywordsDictList=[]
	for keywords in keywordsList:
		keywordsCombinationList=keywords.split('&')
		keywordsDict={"keyword":keywordsCombinationList}
		keywordsDictList.append(keywordsDict)
		# print keywordsDict
	specific_time={"hour":int(hour),"minute":int(minute),"second":int(second)}
	specific_time_list=[]
	specific_time_list.append(specific_time)
	if time_interval:
		time_interval=int(time_interval)
	else:
		time_interval=0

	connect('cleaning_tasks_db')
	new_task=DataCleaningTask(
		name=task_name,
		source_db = source_db_name,
		destination_db=des_db_name,
		cleaning_strategy = cleaning_strategy,
		keywords = keywordsDictList,
		task_state = 'created',
		task_type = task_type,
		cycle_type = cycle_type,
		interval_minutes = time_interval,
		specific_time = specific_time_list,
		created_time=datetime.datetime.now(),
		displayed_created_time=datetime.datetime.now().strftime("%Y-%m-%d")
	)
	new_task.save()

	settings = {}
	with open("settings.json", "r") as f:
		settings = json.load(f)
	settings['cleanedDb'].append(des_db_name)
	with open("settings.json", "w") as f:
		json.dump(settings, f)


	return json.dumps(True)

