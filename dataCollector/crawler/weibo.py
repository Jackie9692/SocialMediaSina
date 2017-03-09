# -*- coding: utf-8 -*-
import requests
import json
import re
import rsa
import base64
import binascii
import time
import selenium
from selenium import webdriver
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.keys import Keys
import re
import random
import threading
import Queue
from collections import deque
from datetime import datetime

user_url_que = deque()

#Browser for parsing search page
search_driver = webdriver.Firefox()
wait = ui.WebDriverWait(search_driver,10)
search_handle = search_driver.current_window_handle

#Browser for parsing user page
user_driver = webdriver.Firefox()
wait = ui.WebDriverWait(user_driver,10)
user_handle = user_driver.current_window_handle

keyword_pos = 0
keywords_list = [ ['奥的斯'], ['奥的斯','电梯'], ['奥的斯', '扶梯'],['奥的斯','事故'], ['奥的斯','服务'], ['奥的斯', '安全'], ['奥的斯', '维保']
                      ,['奥的斯', '问题'], ['奥的斯', '中国'], ['奥的斯', '地铁']
                      ,['蒂森克虏伯'], ['蒂森克虏伯', '电梯'], ['蒂森克虏伯', '扶梯'], ['蒂森克虏伯', '事故'], ['蒂森克虏伯', '服务'], ['蒂森克虏伯', '安全']
                      ,['蒂森克虏伯', '维保'], ['蒂森克虏伯', '地铁']
                      ,['迅达', '电梯'], ['迅达', '扶梯'], ['迅达', '电梯', '服务'], ['迅达', '电梯', '事故'], ['迅达', '电梯', '安全']
                      ,['迅达', '电梯', '维保'], ['迅达', '电梯', '地铁']
                      ,['通力', '电梯'], ['通力', '扶梯'], ['通力', '电梯', '服务'], ['通力', '电梯', '事故'], ['通力', '电梯', '安全']
                      ,['通力', '电梯', '维保'], ['通力', '电梯', '地铁']
                      ,['三菱', '电梯'], ['三菱', '扶梯'], ['三菱', '电梯', '服务'], ['三菱', '电梯', '事故'], ['三菱', '电梯', '安全']
                      ,['三菱', '电梯', '维保'], ['三菱', '电梯', '地铁']
                      ,['日立', '电梯'], ['日立', '扶梯'], ['日立', '电梯', '服务'], ['日立', '电梯', '事故'], ['日立', '电梯', '安全']
                      ,['日立', '电梯', '维保'], ['日立', '电梯', '地铁'] ]

class Status:
    status_id = None
    user_simple = {}
    text = None
    date = None
    userurl = None
    source = None
    repost_count = None
    comments_count = None
    attitude_count = None
    statusurl = None
    geo = {}
    pic_urls = []
    keywords = []
    timestamp = None

    def tojson(self):
        status = { 'status_id': self.status_id, 'user_simple': self.user_simple, 'text': self.text, 'date': self.date, 'userurl': self.userurl,
        'source': self.source, 'repost_count': self.repost_count, 'comments_count': self.comments_count, 'attitude_count': self.attitude_count,
        'statusurl': self.statusurl, 'keywords': self.keywords, 'pic_urls': self.pic_urls, 'geo' : self.geo, 'timestamp': self.timestamp}
        return status

class Users:
    name = None
    user_id = None
    friends_count = 0
    followers_count = 0
    statuses_count = 0
    timestamp = None

    def tojson(self):
        test = { 'name': self.Name, 'user_id': self.user_id, 'friends_count': self.friends_count, 'followers_count': self.followers_count,\
                    'status_count': self.statuses_count, 'timestamp': self.timestamp}
        return test


class Weibo(object):

    def __init__(self):
        self.status = Status()
        self.user = Users()

    def LoginWeibo(self, username, password,driver):
        global search_handle
        if driver == search_driver:
            print "switch to search handle"
            search_driver.switch_to_window(search_handle)
        elif driver == user_driver:
            print "switch to user handle"
            user_driver.switch_to_window(user_handle)

        print u'prepare to login Sina...'
        # driver.get("http://login.weibo.cn/login/")
        driver.get("http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)")

        while True:
            try:
                elem_user = driver.find_element_by_name("username")
                elem_user.send_keys(username)#fill in username
                elem_pwd = driver.find_element_by_name("password")
                elem_pwd.send_keys(password)#fill in password

                time.sleep(5)

                elem_sub = driver.find_element_by_class_name("btn_submit_m")
                elem_sub.click()#click login button
                time.sleep(2)

                cookies = driver.get_cookies()  #get cookies

                print u'login successfully...'
                time.sleep(random.uniform(2,4))
                # time.sleep(3)
                now_handle = driver.current_window_handle
                if driver == search_driver:
                    while True:
                        try:
                            #For the browser to parse search page, switch to weibo.com
                            weibo_btn = driver.find_element_by_class_name("weibo").find_element_by_xpath('.//a')
                            weibo_btn.click()
                            all_handles = driver.window_handles
                            for handle in all_handles:
                                if handle != now_handle:
                                    driver.switch_to_window(handle)
                                    driver.add_cookie(cookies)
                                    search_handle = handle
                            print "switch to weibo"
                            break
                        except Exception,e:
                            print "Error: ",e
                            try:
                                elem_sub.click()
                            except Exception,e:
                                print "Error: ",e
                elif driver == user_driver:
                    try:
                        weibo_btn = driver.find_element_by_class_name("weibo").find_element_by_xpath('.//a')
                    except Exception,e:
                        print "Error: ",e
                        try:
                            elem_sub.click()
                        except Exception,e:
                            print "Error: ",e
                break

            except Exception,e:
                print "Error: ",e
            finally:
                print u'End LoginWeibo!\n\n'

    def parse_search_page(self):

        print "parse search page"
        # search_driver.switch_to_window(search_handle)
        results = search_driver.find_elements_by_xpath('//div[@class="WB_cardwrap S_bg2 clearfix"]')
        # print results
        # write_file = open("search.json", "a")
        status_count = 0
        # try:
        #     no_result = search_driver.find_elements_by_xpath('div[@class="pl_noresult"]')
        #     search_driver.refresh()
        #     time.sleep(random.uniform(4,6))
        # except Exception,e:
        #     print "Error: ",e

        #Parse search result page in a for loop
        for node in results:
            try:
                if node.find_element_by_xpath('.//div[@action-type="feed_list_item"]') != []:
                    print "find one"
                    status_count += 1

                    #status id
                    self.status.status_id = node.find_element_by_xpath('.//div[@action-type="feed_list_item"]').get_attribute("mid") #id
                    print self.status.status_id

                    #user simple and user url
                    if node.find_element_by_xpath('.//a[@class="W_texta W_fb"]') != []:
                        self.status.user_simple["name"] = (node.find_element_by_xpath('.//a[@class="W_texta W_fb"]')).text.replace(" ","")#username
                        self.status.userurl = node.find_element_by_xpath('.//a[@class="W_texta W_fb"]').get_attribute("href") #userurl
                        # self.parse_user_page(self.status.userurl)
                        global user_url_que
                        if self.status.userurl not in user_url_que:
                            user_url_que.append(self.status.userurl)
                        print self.status.user_simple["name"]
                        print self.status.userurl

                    #comment text
                    if node.find_element_by_xpath('.//p[@class="comment_txt"]') != []:
                        self.status.text = node.find_element_by_xpath('.//p[@class="comment_txt"]').text#text
                        print self.status.text

                    #date and status url
                    if node.find_element_by_xpath('.//a[@node-type="feed_list_item_date"]') != []:
                        self.status.date = node.find_element_by_xpath('.//a[@node-type="feed_list_item_date"]').get_attribute("title") #date
                        self.status.statusurl = node.find_element_by_xpath('.//a[@node-type="feed_list_item_date"]').get_attribute("href")#statusurl
                        print self.status.date
                        print self.status.statusurl

                    #source
                    if node.find_element_by_xpath('.//a[@rel="nofollow"]') != []:
                        self.status.source = node.find_element_by_xpath('.//a[@rel="nofollow"]').get_attribute("text") #source
                        print self.status.source

                    #repost count
                    try:
                        repost_count = node.find_element_by_xpath('.//a[@action-type="feed_list_forward"]').find_element_by_xpath('.//em').text
                        if repost_count != "":
                            self.status.repost_count = repost_count
                        else:
                            self.status.repost_count = 0
                    except:
                        self.status.repost_count = 0
                    print self.status.repost_count

                    #comments count
                    try:
                        # if node.find_element_by_xpath('.//a[@action-type="feed_list_comment"]').find_element_by_xpath('.//em') != []:
                        comments_count = node.find_element_by_xpath('.//a[@action-type="feed_list_comment"]').find_element_by_xpath('.//em').text
                        if comments_count != "":
                            self.status.comments_count = comments_count
                        else:
                            self.status.comments_count = 0
                    except Exception,e:
                        print "Error: ", e
                        self.status.comments_count = 0
                    print self.status.comments_count

                    #attitude count
                    try:
                        attitude_count = node.find_element_by_xpath('.//a[@action-type="feed_list_like"]').find_element_by_xpath('.//em').text
                        if attitude_count != "":
                            self.status.attitude_count = attitude_count
                        else:
                                self.status.attitude_count = 0
                    except Exception,e:
                        print "Error: ", e
                        self.status.attitude_count = 0
                    print self.status.attitude_count

                    # if node.find_element_by_xpath('.//a[@class="W_textb"]') != []:
                    #     self.status.statusurl = node.find_element_by_xpath('.//a[@class="W_textb"]').get_attribute("href")#statusurl

                    #geo
                    try:
                        if node.find_element_by_xpath('.//span[@class="W_btn_tag"]') != []:
                            self.status.geo["address"] = node.find_element_by_xpath('.//span[@class="W_btn_tag"]').get_attribute("title")#geo
                    except Exception,e:
                        print "Error: ", e
                        self.status.geo = {}

                    #keywords
                    self.status.keywords = search_driver.find_element_by_class_name("searchInp_form").get_attribute("value").split(" ")#keywords

                    try:
                        self.status.pic_urls = []
                        pic_results = node.find_elements_by_xpath('.//img[@class="bigcursor"]')
                        for pic in pic_results:
                            self.status.pic_urls.append(pic.get_attribute("src").encode("utf-8"))
                    except Exception,e:
                        print "Error: ", e

                    #timestamp
                    self.status.timestamp = time.time()

                    # write_file.write(json.dumps(self.status.tojson(), sort_keys=True, indent=4, separators=(',', ': '),skipkeys=True))

            except Exception,e:
                print "Error: ", e

        # write_file.close()

        #wait 20 ~ 40 seconds to pare next page
        time.sleep(random.uniform(20,40))
        self.next_page()

    def parse_user_page(self,userurl):#Parse user page
        time.sleep(random.uniform(2,8))
        user_driver.switch_to_window(user_handle)
        user_driver.get(userurl)
        # write_file = open("user.json", "a")
        while True:
            try:
                user = Users()
                if user_driver.current_url == "http://weibo.com/u/3344505284/home?wvr=5":
                    break
                print "user info:"

                #user name
                user.Name = user_driver.find_element_by_xpath('//h1[@class="username"]').text

                #user id
                user.user_id = self.get_userid_using_re(user_driver.find_element_by_xpath('//div[@node-type="focusLink"]').get_attribute("action-data"))

                #fiends count, followers count and statues count
                count_table = user_driver.find_element_by_xpath('//table[@class="tb_counter"]').find_elements_by_xpath(".//td")
                for i,count in enumerate(count_table):
                    count_number = count.find_element_by_xpath(".//strong").text
                    if i == 0:
                        user.friends_count = count_number
                        print user.friends_count
                    elif i == 1:
                        user.followers_count = count_number
                        print user.followers_count
                    elif i == 2:
                        user.statuses_count = count_number
                        print user.statuses_count
                    else:
                        pass
                #timestamp
                user.timestamp = time.time()

                # write_file.write(json.dumps(user.tojson(), sort_keys=True, indent=4, separators=(',', ': '),skipkeys=True))
                # write_file.close()

                break
            except Exception,e:
                print "Error: ", e
                #user_driver.send_keys(Keys.ENTER)
                # user_driver.refresh()
                try:
                    home_page_btn = user_driver.find_element_by_xpath('//table[@class="tb_tab"]').find_element_by_xpath(".//a")
                    home_page_btn.click()
                except Exception,e:
                    print "Error: ", e
                    user_driver.refresh()


    def start_search(self,keywords):
        search_driver.switch_to_window(search_handle)
        while True:
            try:
                search_area = search_driver.find_element_by_class_name('gn_search_v2')
                print "start search"
                search_input = search_area.find_element_by_xpath('.//input[@node-type="searchInput"]')
                print "insert keyword"
                while True:
                    try:
                        #Put all keywords in a combination into a string
                        keyword_comb = ""
                        for keyword in keywords:
                            keyword_comb = keyword_comb + " " + keyword
                        search_input.send_keys(keyword_comb.decode('utf-8'))
                        break
                    except Exception,e:
                        print "Error: ", e
                search_input.send_keys(Keys.ENTER)
                # search_btn = search_area.find_element_by_xpath('.//a[@node-type="searchSubmit"]')
                # search_btn.click()

                try:
                    list_count = len(search_driver.find_element_by_xpath('//div[@class="layer_menu_list W_scroll"]')\
                                     .find_elements_by_xpath(".//li"))
                    more_result_btn = search_driver.find_element_by_xpath('//div[@class="search_rese clearfix"]')\
                            .find_element_by_xpath(".//a")
                    if list_count <= 30 and more_result_btn:
                        print "click more result button"
                        more_result_btn.click()
                        time.sleep(random.uniform(1,3))
                except Exception,e:
                    print "Error: ", e

                self.parse_search_page()
                break
            except Exception,e:
                print "Error: ", e

    def next_page(self):
        try:
            time.sleep(2)
            next_page_btn = search_driver.find_element_by_xpath('//a[@class="page next S_txt1 S_line1"]')
            next_page_btn.click()#switch to next page

            try:
                search_driver.find_element_by_class_name("noresult_support")
                time.sleep(random.uniform(3,6))
                search_driver.refresh()
                # search_driver.send_keys(Keys.ENTER)
            except Exception,e:
                pass

            print "parse next page"
            self.parse_search_page()
        except Exception,e:
            print "Error: ", e

    def shuffle_keyword_list(self):#disorder the list of keywords
        list = keywords_list
        random.shuffle (list)
        for keyword in list:
            for node in keyword:
                print node

    def prepare_log_in(self,username,password,type):
        if type == "search":
            self.LoginWeibo(username,password,search_driver)
        elif type == "user":
            self.LoginWeibo(username,password,user_driver)
        else:
            print "Wrong log in"

    def get_userid_using_re(self,string):#extract user id from page element
        pattern = re.compile('(?<=uid\=)[0-9]*(?=\&)')
        id = pattern.search(string)
        if id:
            id = id.group()
        print id
        return id

    def split_keyword(self,keywords):
        return keywords.split(" ")

#Initiate two Weibo instance for search page and user page
search_weibo = Weibo()
user_weibo = Weibo()

def parse_status():#thread for parsing search page
    global keyword_pos
    while True:
        keyword_comb = keywords_list[keyword_pos]
        for keyword in keyword_comb:
            print keyword
        search_weibo.start_search(keyword_comb)
        time.sleep(random.uniform(1200, 2400))
        # print keywords_list[keyword_pos]
        if keyword_pos < len(keywords_list) - 1:
            keyword_pos += 1
        else:
            time.sleep(random.uniform(21600, 36000))
            random.shuffle(keywords_list)
            keyword_pos = 0

def parse_user():#thread for parsing user page
    print "start user thread"
    while True:
        time.sleep(random.uniform(10, 30))
        try:
            while user_url_que:
                user_url = user_url_que.popleft()
                print "Try to parse" + user_url
                user_weibo.parse_user_page(user_url)
        except:
            pass

if __name__ == "__main__":
    random.shuffle(keywords_list)#disorder the list of keywords

    print "login search"
    search_weibo.prepare_log_in("qinyidan423@126.com","bebvbf499325858","search")

    user_driver.switch_to_window(user_driver.current_window_handle)
    print "login user"
    user_weibo.prepare_log_in("17701734924","utrcc002","user")

    #place parsing search page and parsing user page into two threads
    threads = []
    search_thread = threading.Thread(target=parse_status)
    threads.append(search_thread)
    user_thread = threading.Thread(target=parse_user)
    threads.append(user_thread)

    #Start thread
    search_thread.start()
    user_thread.start()
