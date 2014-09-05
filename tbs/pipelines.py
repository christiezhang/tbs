#-*- coding: UTF-8 -*-
# __author__ = 'christie'
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from twisted.enterprise import adbapi
from scrapy.http import Request
from scrapy.exceptions import DropItem
import time,hashlib
import MySQLdb
import MySQLdb.cursors
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
class TaishaPipeline(object):
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool('MySQLdb',db='crawl',user='root',passwd='123456',cursorclass=MySQLdb.cursors.DictCursor,charset='utf8',use_unicode=False)
        #self.timestamp = str(int(time.mktime(time.gmtime())))
    def process_item(self, item, spider):
        if spider.name =='singlecrawl':
              query = self.dbpool.runInteraction(self.singlecrawl_conditional_insert, item)
        elif spider.name == 'discoveryspider':
              query = self.dbpool.runInteraction(self.discoveryspider_conditional_insert, item)
        #print item['stripedbody']
        return item
    def singlecrawl_conditional_insert(self,tx,item):
        #tx.execute('set character set utf8')
        try :
            tx.execute('insert into `collect_page`(`pid`,`k`,`url`,`lmdate`,`expires`,`getdate`)values(NULL,%s,%s,%s,%s,%s)',(str(item['url_hash_no_fragment']),str(item['url']),str(item['LastModified']),str(item['Expires']),str(int(time.mktime(time.gmtime())))))
            insertid = tx.connection.insert_id()
            try:
                 tx.execute('insert into collect_html (pid,text,title,keywords,description,html)values(%s,%s,%s,%s,%s,%s)',(str(insertid),item['stripedbody'],item['title'],item['keyword'],item['desc'],item['body']))

            except Exception as e:
                 tx.execute('insert into collect_error_log (id,url,errorlog,date)values(NULL,%s,%s,%s)',(item['url'],e,str(int(time.mktime(time.gmtime())))))
                 tx.execute('delete from collect_page where pid=%s',(insertid))
        except Exception as e:
                 tx.execute('insert into collect_error_log (id,url,errorlog,date)values(NULL,%s,%s,%s)',(item['url'],e,str(int(time.mktime(time.gmtime())))))

    def discoveryspider_conditional_insert(self,tx,item):
        dnhashobject = hashlib.md5()
        dnhashobject.update(item['domain_name'])
        dnhashvalue = dnhashobject.hexdigest()
        try :
            tx.execute('insert into `collect_page_'+str(dnhashvalue)+'`(`pid`,`k`,`url`,`lmdate`,`expires`,`getdate`)values(NULL,%s,%s,%s,%s,%s)',(str(item['url_hash_no_fragment']),str(item['url']),str(item['LastModified']),str(item['Expires']),str(int(time.mktime(time.gmtime())))))
            insertid = tx.connection.insert_id()
            try:
                 tx.execute('insert into collect_html_'+str(dnhashvalue)+' (pid,text,title,keywords,description,html)values(%s,%s,%s,%s,%s,%s)',(str(insertid),item['stripedbody'],item['title'],item['keyword'],item['desc'],item['body']))

            except Exception as e:
                 tx.execute('insert into collect_error_log (id,url,errorlog,date)values(NULL,%s,%s,%s)',(item['url'],e,str(int(time.mktime(time.gmtime())))))
                 tx.execute('delete from collect_page_'+str(dnhashvalue)+' where pid=%s',(insertid))
        except Exception as e:
                 tx.execute('insert into collect_error_log (id,url,errorlog,date)values(NULL,%s,%s,%s)',(item['url'],e,str(int(time.mktime(time.gmtime())))))
