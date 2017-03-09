# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from . import sentiment
import trie

class SentimentAnalysis(object):

    def __init__(self, doc):
        self.doc = doc

    @property
    def sentiments(self):
        return sentiment.classify(self.doc)
