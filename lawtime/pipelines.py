# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import signals
from twisted.enterprise import adbapi
from datetime import datetime
from hashlib import md5
import MySQLdb
import MySQLdb.cursors
from scrapy import log
import codecs

class MySQLStorePipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool
    
    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            # use_unicode= True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)
    
    
    def process_item(self, item, spider):
        d = self.dbpool.runInteraction(self._do_upinsert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        d.addBoth(lambda _: item)
        return d
        
    def _do_upinsert(self, conn, item, spider):
        linkmd5id = self._get_linkmd5id(item)
        now = datetime.utcnow().replace(microsecond=0).isoformat(' ')
        try:
            file_path = "/home/yaolili/lawtime/webpage/" + linkmd5id
            
            conn.execute("""
                insert into question(urlid, url, file_path, create_time, update_time, is_process) 
                values(%s, %s, %s, %s, %s, %s)
                """, (linkmd5id, item['url'], file_path, now, now, 0))
            file = codecs.open(file_path, 'w')
            file.write(item["question_page"])
            file.close()
        except Exception, e:
            print "********** Exception when inserting into db **********: ", e
            print type(linkmd5id)
            print type(item['url'])
            print type(file_path)
            print type(now)

    def _get_linkmd5id(self, item):
        return md5(item['url']).hexdigest()

    def _handle_error(self, failure, item, spider):
        log.err(failure)
