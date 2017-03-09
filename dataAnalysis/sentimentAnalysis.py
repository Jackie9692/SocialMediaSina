# -*- coding: utf-8 -*-
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import time
import sched
from mongoengine import *
from model import lastAnalisedTimstamp
from util import databaseConnector
from dataCollector.apiCollector.model import Status
from sentiment_analysis import sentiment
from sentiment_analysis import SentimentAnalysis

class sentiment_analyser():
    def __init__(self):
        # self.analysis_status(u'我很伤心')
        databaseConnector.connect()
        self.analysisScheduler = sched.scheduler(time.time, time.sleep)
    def get_statuses_need_nalysis(self):
        last_analysis_timestamp = lastAnalisedTimstamp.objects().first()
        current_timestamp = time.time()
        if not last_analysis_timestamp:
            analysis_timestamp = 0
            last_analysis_timestamp = lastAnalisedTimstamp(lastAnalisedTimstamp=current_timestamp)
            last_analysis_timestamp.save()
        else:
            analysis_timestamp = last_analysis_timestamp.lastAnalisedTimstamp
            last_analysis_timestamp.update(lastAnalisedTimstamp=current_timestamp)
        statuses_need_analysis = Status.objects(Q(retrievedTimestamp__gte=analysis_timestamp) | Q(scrapedTimeStamp__gte=analysis_timestamp)).timeout(False)
        return statuses_need_analysis

    def analysis_statuses(self):
        statuses = self.get_statuses_need_nalysis()
        # print len(statuses)
        for status in statuses:
            status_text = status.text
            status_sentiment_score = self.analysis_status(status_text)
            status.update(sentimentScore=status_sentiment_score)
        self.analysisScheduler.enter(60, 0, self.analysis_statuses, ())
    def analysis_status(self,statusText):
        s = SentimentAnalysis(statusText)
        return s.sentiments

    def train(self):
        sentiment.train('neg.txt', 'pos.txt')
        sentiment.save('./sentiment_analysis/sentiment/sentiment.marshal')
    def start_analysis(self):
        self.analysisScheduler.enter(0, 0, self.analysis_statuses, ())
        self.analysisScheduler.run()
if __name__ == "__main__":
    sentimentAnalyser = sentiment_analyser()
    sentimentAnalyser.start_analysis()