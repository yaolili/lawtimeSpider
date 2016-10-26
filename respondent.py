#-*- coding:utf-8 -*-
# AUTHOR:   yaolili
# FILE:     respondent.py
# ROLE:     TODO (some explanation)
# CREATED:  2016-10-18 15:42:13
# MODIFIED: 2016-10-18 15:42:14


import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from bs4 import BeautifulSoup
import requests
import logging
import re

logging.basicConfig(filename="respondent.log")

class Respondent(object):
    def __init__(self):
        self.type = "lawyer"
        self.firm_name = ""
        self.intro = ""
        self.id = ""
    
    def _crawl(self, url):
        s = requests.session()
        s.keep_alive = False
        return s.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
        }).content
        
        
    def _parse_lawtime(self, url, webpage):
        soup = BeautifulSoup(webpage, "html.parser")
        print type(soup)
        print "in parse lawtime"
        try:
            #self.firm_name, self.id
            info_area = soup.find('div', attrs={'class':'lawyer-info'}).find_all('p')
            self.id = re.search('(\d{17})', info_area[6].text).group()
            print self.id
            print info_area[7].string.encode("utf-8")
            self.firm_name = re.search(r'执业机构：(.+)'.encode("utf-8"), info_area[7].string.encode("utf-8")).group().replace(r"执业机构：", "").strip()
            
            #self.intro
            intro_url = soup.find('div', attrs={'class':'cont-a-p'}).find('a')['href']
            intro_page = self._crawl(intro_url)
            intro_soup = BeautifulSoup(intro_page, "html.parser")
            cont_area = intro_soup.find('div', attrs={'class': 'article-cont'})
            self.intro = cont_area.find_all('p')[3].text.strip()
        except Exception, e:
            print e
            logging.info(url + "\n")
        
    def _parse_law110(self, url, webpage):    
        soup = BeautifulSoup(webpage, "html.parser")
    
    #type = 0 for lawtime, type = 1 for law110
    def get_respondent_info(self, url, type):
        webpage = self._crawl(url)
        if type == 0:
            self._parse_lawtime(url, webpage)
        else: self._parse_law110(url, webpage)
        return self.type, self.firm_name, self.intro, self.id
 

# test usage 
if __name__ == "__main__":
    res = Respondent()
    url = "http://www.lawtime.cn/lawyer/lll706308711402"
    a = res.get_respondent_info(url, 0)
    print a
        