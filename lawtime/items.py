# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class LawtimeItem(Item):
    
    question_page = Field()
    url = Field()
    
    
    '''
    src_site = Field()
    id = Field()
    
    question_datetime = Field()
    question_location = Field()
    question_title = Field()
    question = Field()
    question_best = Field()
    
    answer = Field()
    answer_datetime = Field()
    
    answer_respondent = Field()
    answer_respondent_type = Field()
    answer_respondent_firm_name = Field()
    answer_respondent_intro = Field()
    answer_respondent_location = Field()
    answer_respondent_id = Field()
    
    qa_catas = Field()
    '''
    pass