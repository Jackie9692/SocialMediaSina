#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Fri May 13 14:55:21 2016

@author: Pierre
"""

"""
msmt.py
Functions to access the Microsoft Translator API HTTP Interface, using python's urllib/urllib2 libraries
"""

import urllib, urllib2
import requests
import json
import re

from datetime import datetime
class microsofttranslator:
    def datestring (self, display_format="%a, %d %b %Y %H:%M:%S", datetime_object=None):
        """Convert the datetime.date object (defaults to now, in utc) into a string, in the given display format"""
        if datetime_object is None:
            datetime_object = datetime.utcnow()
        return datetime.strftime(datetime_object, display_format)
    
    def get_access_token (self, client_id, client_secret):
        """Make an HTTP POST request to the token service, and return the access_token,
        as described in number 3, here: http://msdn.microsoft.com/en-us/library/hh454949.aspx
        """
    
        data = urllib.urlencode({
                'client_id' : client_id,
                'client_secret' : client_secret,
                'grant_type' : 'client_credentials',
                'scope' : 'http://api.microsofttranslator.com'
                })
    
        try:
    
            request = urllib2.Request('https://datamarket.accesscontrol.windows.net/v2/OAuth2-13')
            request.add_data(data) 
    
            response = urllib2.urlopen(request)
            response_data = json.loads(response.read())
    
            if response_data.has_key('access_token'):
                return response_data['access_token']
    
        except urllib2.URLError, e:
            if hasattr(e, 'reason'):
                print self.datestring(), 'Could not connect to the server:', e.reason
            elif hasattr(e, 'code'):
                print self.datestring(), 'Server error: ', e.code
        except TypeError:
            print self.datestring(), 'Bad data from server'
    
    supported_languages = { # as defined here: http://msdn.microsoft.com/en-us/library/hh456380.aspx
        'ar' : ' Arabic',
        'bg' : 'Bulgarian',
        'ca' : 'Catalan',
        'zh-CHS' : 'Chinese (Simplified)',
        'zh-CHT' : 'Chinese (Traditional)',
        'cs' : 'Czech',
        'da' : 'Danish',
        'nl' : 'Dutch',
        'en' : 'English',
        'et' : 'Estonian',
        'fi' : 'Finnish',
        'fr' : 'French',
        'de' : 'German',
        'el' : 'Greek',
        'ht' : 'Haitian Creole',
        'he' : 'Hebrew',
        'hi' : 'Hindi',
        'hu' : 'Hungarian',
        'id' : 'Indonesian',
        'it' : 'Italian',
        'ja' : 'Japanese',
        'ko' : 'Korean',
        'lv' : 'Latvian',
        'lt' : 'Lithuanian',
        'mww' : 'Hmong Daw',
        'no' : 'Norwegian',
        'pl' : 'Polish',
        'pt' : 'Portuguese',
        'ro' : 'Romanian',
        'ru' : 'Russian',
        'sk' : 'Slovak',
        'sl' : 'Slovenian',
        'es' : 'Spanish',
        'sv' : 'Swedish',
        'th' : 'Thai',
        'tr' : 'Turkish',
        'uk' : 'Ukrainian',
        'vi' : 'Vietnamese',
    }
    
    def print_supported_languages (self):
        """Display the list of supported language codes and the descriptions as a single string
        (used when a call to translate requests an unsupported code)"""
    
        codes = []
        for k,v in self.supported_languages.items():
            codes.append('\t'.join([k, '=', v]))
        return '\n'.join(codes)
    
    def to_bytestring (self, s):
        """Convert the given unicode string to a bytestring, using utf-8 encoding,
        unless it's already a bytestring"""
    
        if s:
            if isinstance(s, str):
                return s
            else:
                return s.encode('utf-8')
    
    def translate (self, access_token, text, to_lang, from_lang=None):
        """Use the HTTP Interface to translate text, as described here:
        http://msdn.microsoft.com/en-us/library/ff512387.aspx
        and return an xml string if successful
        """
    
        if not access_token:
            print 'Sorry, the access token is invalid'
        else:
            if to_lang not in self.supported_languages.keys():
                print 'Sorry, the API cannot translate to', to_lang
                print 'Please use one of these instead:'
                print self.print_supported_languages()
            else:
                data = { 'text' : self.to_bytestring(text), 'to' : to_lang }
    
                if from_lang:
                    if from_lang not in self.supported_languages.keys():
                        print 'Sorry, the API cannot translate from', from_lang
                        print 'Please use one of these instead:'
                        print self.print_supported_languages()
                        return
                    else:
                        data['from'] = from_lang
    
                try:
    
                    request = urllib2.Request('http://api.microsofttranslator.com/v2/Http.svc/Translate?'+urllib.urlencode(data))
                    request.add_header('Authorization', 'Bearer '+access_token)
    
                    response = urllib2.urlopen(request)
                    return response.read()
                
                except urllib2.URLError, e:
                    if hasattr(e, 'reason'):
                        print self.datestring(), 'Could not connect to the server:', e.reason
                    elif hasattr(e, 'code'):
                        print self.datestring(), 'Server error: ', e.code
                    
def translate(text, to_lang):
    return microsofttranslator().translate(access_token, text, to_lang)[68:-9]

def extractEntities_en(text):
    res = requests.get("https://api.dandelion.eu/datatxt/nex/v1/?text="+text+"&min_confidence=0.2&lang=en&include=types,categories,abstarct,image,lod,alternate_labels&token="+token).json()
    places = []
    if 'annotations' in res:
        for item in res['annotations']:
            if 'http://dbpedia.org/ontology/Place' in item['types']:
                places.append((item['label'], translate(item['label'], "zh-CHS")))
    else:
        print "Error"
    return places

TAG_RE = re.compile(r'<[^>]+>')
def remove_tags(text):
    return TAG_RE.sub('', text)
    
def extractEntities(text):
    text = remove_tags(text.translate(None, '!@#$'))
    return extractEntities_en(translate(text, "en"))

#init APIs keys
token = "c45f4e5426e54f37a0c5ffe1cd1ba75d"
access_token = microsofttranslator().get_access_token('test_app846215462', 'PW58hS8kBEj/s/9hKCOM/QGNjSCRcTp8bJrIxCcCyP0=')

#demo
#text = "【<em class='highlight'>用</em><em class='highlight'>好</em><em class='highlight'>84</em><em class='highlight'>消</em><em class='highlight'>毒</em><em class='highlight'>液</em>，<em class='highlight'>别</em><em class='highlight'>让</em>“<em class='highlight'>消</em><em class='highlight'>毒</em>”变“投毒”！】#健康提示#1984年，北京第一传染病医院（地坛医院的前身）成功研制了一款能迅速杀灭各类肝炎病毒的消毒液，定名为“84”肝炎洗消液，后更名为“84消毒液”。上海市疾控中心告诉你：如此强大的84消毒液，在使用时要注意以下几点，确保安全和有效↓@上海发布"
#print extractEntities(text)

