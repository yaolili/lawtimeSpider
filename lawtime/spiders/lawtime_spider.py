#-*- coding:utf-8 -*-
# AUTHOR:   yaolili
# FILE:     lawtime_spider.py
# ROLE:     TODO (some explanation)
# CREATED:  2016-10-17 10:05:43
# MODIFIED: 2016-10-17 10:05:44


from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http.request import Request
from scrapy.selector import Selector
from lawtime.items import LawtimeItem

import re
import codecs
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class Lawtime_spider(CrawlSpider):
    name = "lawtime_spider"
    allowed_domains = ["www.lawtime.cn"]
    start_urls = []
    
    def start_requests(self):
        for year in range(2007, 2017):
            for month in range(1, 13):
                if year == 2007 and month < 10: continue
                cur_url = "http://www.lawtime.cn/ask/browse_d" + str(year) + str(month) + "_t2.html"
                self.start_urls.append(cur_url)
        # cur_url = "http://www.lawtime.cn/ask/browse_d200801_t2.html"
        # self.start_urls.append(cur_url)
        
        for each_url in self.start_urls:
            yield Request(url=each_url, callback=self.parse)
        
    
    def parse(self, response):
        try:
            page = response.body.decode("utf-8", "ignore")
            
            # get question page url by regex
            mode = re.compile("http://www\.lawtime\.cn/ask/question_\d+\.html")
            question_list = re.findall(mode, page)
            if question_list:
                for question in question_list:
                    yield Request(url=question, callback=self.parse_question)

            # get next page 
            next_page = response.xpath('//div[@class="paging paging-a"]/a/@href').extract()
            if next_page:
                next_page_url = "http://www.lawtime.cn" + next_page[-1]
                yield Request(url=next_page_url, callback=self.parse)
            
        except Exception, e:
            print e
    
            
    def parse_question(self, response):
        item = LawtimeItem()
        item["question_page"] = response.body
        item["url"] = response.url
        return item
        
        
   
    