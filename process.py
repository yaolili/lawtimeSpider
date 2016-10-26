#-*- coding:utf-8 -*-
# AUTHOR:   yaolili
# FILE:     process.py
# ROLE:     TODO (some explanation)
# CREATED:  2016-10-18 10:23:21
# MODIFIED: 2016-10-18 10:23:23

import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import time
import json
import MySQLdb
from datetime import datetime
from bs4 import BeautifulSoup
import re
import logging
# from respondent import Respondent

logging.basicConfig(filename='question.log', filemode='a', level=logging.INFO)

def msg_info(msg_area):
    if not msg_area or not msg_area.find('p'): 
        return None, None
    
    if not msg_area.find('p').find('a'):
        respondent = ""
    else: 
        respondent = msg_area.find('p').find('a').string
        # respondent_url = msg_area.find('p').find('a')['href']
    
    respondent_info = {}
    if len(msg_area.find_all('p')) < 2:
        respondent_info["location"] = ""
    else: respondent_info["location"] = msg_area.find_all('p')[1].string.strip()
    respondent_info["type"] = "lawyer"
    respondent_info["firm_name"] = ""
    respondent_info["intro"] = ""
    respondent_info["ID"] = ""
    return respondent, respondent_info
    
def answer_info(talk_area):
    if not talk_area or not talk_area.find('p'): return None, None
    answer = talk_area.find('p').text
    match = re.search('(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2})', talk_area.find('p', attrs={'class':'tr'}).string)
    if match:
        answer_datetime = match.group()
    else: answer_datetime = ""
    return answer, answer_datetime


def handle_webpage(urlid, url, file_path): 
    # test usage
    # url = "http://www.lawtime.cn/ask/question_5857489.html"
    # urlid = "008f054d2a80ff29ce4709de62a89f4a"
    # file_path = "/home/yaolili/lawtime/webpage/008f054d2a80ff29ce4709de62a89f4a"
    
    total_result = {}
    # res_instance = Respondent()
    item = {}
    try:
        item["src_site"] = "lawtime"
        question_id = re.search('question_(\d+)\.html', url.strip()).group(1)
        item["ID"] = "lawtime_" + question_id + "_0"
        
        webpage = open(file_path, "r").read().decode("gbk", "ignore")
        soup = BeautifulSoup(webpage, "html.parser")
        # print soup
        
        #question, title
        question_area = soup.find('div', attrs={'class': 'ltask-cont-page-title clearfix'})
        item["question"] = soup.find('div', attrs={'class': 'question-main relative'}).find('p').string
        item["question_title"] = question_area.find('div', attrs={'class': 'hauto'}).find('h1').string
        
        
        #datetime, location
        question_tr = soup.find('p', attrs={'class': 'tr cls'}).contents
        if(len(question_tr) > 1):
            question_bottom = question_tr[-1].encode("utf-8")
        else: question_bottom = question_tr[0].encode("utf-8")
        item["question_datetime"] = re.search('(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2})', question_bottom).group()
        item["question_location"] = re.search(r'问题来自：(.+)悬赏'.encode("utf-8"), question_bottom).group().replace(r"问题来自：", "").replace(r"悬赏","").strip()
        
        #catas
        catas_area_url = soup.find('div', attrs={'class': 'ltask-tip'}).find('div', attrs={'class': 'tip-l fl'}).find_all('a')
        item["QA_Catas"] = ""
        for i in range(0, len(catas_area_url)):
            item["QA_Catas"] += catas_area_url[i].string
            if i != len(catas_area_url) - 1:
                item["QA_Catas"] += ";"
                
        #best answer
        item["question_best"] = 1
        if soup.find('div', attrs={'class': 'best-answer-a'}):
            best_answer_area = soup.find('div', attrs={'class': 'best-answer-a'}).find('dd', attrs={'class': 'clearfix'})
            
            talk_area = best_answer_area.find('div', attrs={'class': 'alywer-talk-t relative clearfix'})
            item["answer"], item["answer_datetime"] = answer_info(talk_area)
            
            # print "talk_area done!"
            
            msg_area = best_answer_area.find('div', attrs={'class': 'laywer-msg fl'})
            item["answer_respondent"], item["answer_respondent_info"] = msg_info(msg_area)
            
            # print "msg_area done!"
            # remain to fix
            # item["answer_respondent"]["type"], item["answer_respondent"]["firm_name"], item["answer_respondent"]["intro"], item["answer_respondent"]["ID"] = res_instance.get_respondent_info(answer_respondent_url, 0)
            
            total_result[item["ID"]] = json.dumps(item)
        
        #other answer
        if not soup.find('div', attrs={'class': 'ltask-cont-page-main clearfix'}): 
            #print total_result
            return total_result
        other_area = soup.find('div', attrs={'class': 'ltask-cont-page-main clearfix'}).find('dl', attrs={'class':'page-main-list clearfix'}).find_all('dd', attrs={'class':'clearfix'})
        
        count = 0
        for each in other_area:
            count += 1
            item["ID"] = "lawtime_" + question_id + "_" + str(count)
            item["question_best"] = 0
            talk_area = each.find('div', attrs={'class': 'alywer-talk-t relative clearfix'})
            item["answer"], item["answer_datetime"] = answer_info(talk_area)

            msg_area = each.find('div', attrs={'class': 'laywer-msg fl'})
            item["answer_respondent"], item["answer_respondent_info"] = msg_info(msg_area)
            total_result[item["ID"]] = json.dumps(item)
        # print total_result
        return total_result
    except Exception, e:
        print e
        logging.info(urlid + "\t" + url + "\t" + file_path + "\n")

def connect_db():
    try:
        conn = MySQLdb.connect(host   = 'localhost',
                               user   = 'root',
                               passwd = 'webkdd',
                               db     = 'lawtime',
                               port   = 3306)
        cur=conn.cursor()
        process_line = 0
        
        while(True):
            cur.execute('SELECT * FROM question WHERE is_process = 0 limit 1000')
            rows = cur.fetchall()
            if len(rows) == 0: break
            for row in rows:
                urlid       = row[0]
                url         = row[1]
                file_path   = row[2] 
                create_time = row[3]
                update_time = row[4]
                is_process  = row[5]
                
                print urlid
                print url
                
                json_list = handle_webpage(urlid, url, file_path)
                for key in json_list:
                    # print json_list[key]
                    cur.execute("""
                    INSERT INTO response(id, url, qr_pair)
                    VALUES(%s, %s, %s)
                    """, (key, url, json_list[key])) 
                # exit()
                now = datetime.utcnow().replace(microsecond=0).isoformat(' ')
                cur.execute('UPDATE question SET update_time = %s, is_process = 1 WHERE urlid = %s', (now, urlid))
                conn.commit()  
            process_line += 1000
            print '--------------process %d rows--------------' % process_line
            
        cur.close()
        conn.close()
    except Exception, e:
        print e 
        logging.info(urlid + "\t" + url + "\t" + file_path)
       

if __name__ == "__main__":
    connect_db()