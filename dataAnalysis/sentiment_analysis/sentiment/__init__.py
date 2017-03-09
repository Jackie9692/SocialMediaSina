
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import codecs
from ..bayes import Bayes
from .. import normal
import jieba

data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'sentiment.marshal')

stop_words = []

class Sentiment(object):

    def __init__(self):
        # self.prepare_stop_words_list("/Users/chenweiyi/Desktop/UTRCC/topic model/stop_words.txt")
        self.classifier = Bayes()

    def save(self, fname, iszip=True):
        self.classifier.save(fname, iszip)

    def load(self, fname=data_path, iszip=True):
        self.classifier.load(fname, iszip)

    def handle(self, doc):
        words = jieba.lcut(doc, cut_all=False)
        # words = self.stop_words_filter(words)
        words = normal.filter_stop(words)
        return words

    def stop_words_filter(self,texts):
        texts = [text for text in texts if text not in stop_words]
        # for text in texts:
        #     print text
        return texts

    def prepare_stop_words_list(self,file_path):
        global stop_words
        for line in open(file_path):
            stop_words.append(line.decode('utf-8').replace('\n',''))
        # print stop_words

    def train(self, neg_docs, pos_docs):
        data = []
        for sent in neg_docs:
            data.append([self.handle(sent), 'neg'])
        for sent in pos_docs:
            data.append([self.handle(sent), 'pos'])
        self.classifier.train(data)

    def classify(self, sent):
        ret, prob = self.classifier.classify(self.handle(sent))
        if ret == 'pos':
            return prob
        return 1-prob

classifier = Sentiment()
classifier.load()


def train(neg_file, pos_file):
    neg_docs = codecs.open(neg_file, 'r', 'utf-8').readlines()
    pos_docs = codecs.open(pos_file, 'r', 'utf-8').readlines()
    global classifier
    classifier = Sentiment()
    classifier.train(neg_docs, pos_docs)


def save(fname, iszip=True):
    classifier.save(fname, iszip)


def load(fname, iszip=True):
    classifier.load(fname, iszip)


def classify(sent):
    return classifier.classify(sent)