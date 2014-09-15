#-*- coding: UTF-8 -*-
#__author__='christie'
import sys,time,hashlib,os,re,chardet,datetime,time
reload(sys)
sys.setdefaultencoding('utf-8')
import MySQLdb,nltk
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from urlparse import urlparse
from urlparse import urljoin
from urlparse import urlunparse
from posixpath import normpath
#from HTMLParser import HTMLParser
#from BeautifulSoup import BeautifulSoup,Tag,NavigableString,Comment
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from urllib import urlretrieve
from urlparse import urlsplit
#from scrapy.item import Item
from tbs.items import TbsItem              # import self declared items

from tbs.pmemcache import pmemcache


class tbs3(BaseSpider):
    name = 'tbs3'
    defult_strip_start_tag = 'body'
    striptag=['scripts','script','style']
    default_encoding_confidence=0.9
    max_page=200
    default_crawl_stats='200'
    res=['?','+','.','#','^','*','{','}',',','(',')','<','>','...','!','|','\'']
    keyword='mzy'


    def __init__(self):
        self.memcache = pmemcache()
        self.databaseobject = initcrwal()
        self.start_urls=[]
        for x in range(1,11):
            self.start_urls.append('http://mzy.100ppi.com/price/list---'+str(x)+'.html')
        self.allowed_domains=['100ppi.com']


    def parse(self,response):
          links =[]
          hxs = HtmlXPathSelector(response)
          for x in range(2,31):
            mname=''.join(hxs.select('//*[@class="lp-table"]/tr['+str(x)+']/td[1]/div/a/text()').extract())
            style=''.join(hxs.select('//*[@class="lp-table"]/tr['+str(x)+']/td[2]/text()').extract())
            priceandunit=''.join(hxs.select('//*[@class="lp-table"]/tr['+str(x)+']/td[3]/text()').extract())
            unit = priceandunit[-3:len(priceandunit)]
            price = priceandunit[:-3]
            spec=(''.join(hxs.select('//*[@class="lp-table"]/tr['+str(x)+']/td[4]/text()').extract())).lstrip()
            spec = spec[3:]
            orgin=(''.join(hxs.select('//*[@class="lp-table"]/tr['+str(x)+']/td[5]/div/text()').extract())).lstrip()
            issuestime=''.join(hxs.select('//*[@class="lp-table"]/tr['+str(x)+']/td[6]/text()').extract())
            insertsql = 'INSERT INTO `mzy_price` ( `id` , `name` , `style` , `price` , `unit` , `spec` , `origin` , `issuestime` , `issuestimestamp`, `source` , `crawldate` )\
                         VALUES (\
                         NULL , \''+mname+'\', \''+style+'\', \''+price+'\', \''+unit+'\', \''+spec+'\', \''+orgin+'\', \''+issuestime+'\',\''+str(int(time.mktime(time.strptime(issuestime, "%Y-%m-%d"))))+'\'' \
                         ', \''+response.url+'\', \''+self.to_GMT_timestamp(None)+'\'\
                         )'
            try:
               self.databaseobject.cursor.execute(insertsql)
               links.append(''.join(hxs.select('//*[@class="lp-table"]/tr['+str(x)+']/td[1]/div/a/@href').extract()))
               #mid = self.databaseobject.cursor.connection.insert_id()
            except Exception as e:
               #mid = None
               print e
               pass
          for l in links:
               if self.memcache.get(self.get_url_hash_no_fragment(l)) != 1:
                    yield Request(l,meta={'refer': response.url},callback=self.parse_detail,errback=self.parse_error)
               else:
                   continue

    def parse_detail(self,response):
          item = TbsItem()
          headers = response.headers
          print response.url
          self.set_items_value(item,'character',self.get_page_character(response.body))
          self.set_items_value(item,'crawl_stats',self.default_crawl_stats)
          self.set_items_value(item,'searchkeywords',self.keyword)
          self.set_items_value(item,'spiderid',self.name)
          self.set_items_value(item,'refer',response.meta['refer'])
          self.set_items_value(item,'url_hash_no_fragment', self.get_url_hash_no_fragment(response.url))
          self.set_items_value(item,'url', self.parseurl(response.url))
          self.set_items_value(item,'root_domain',urlparse(response.url).hostname)
          self.set_items_value(item,'Expires',self.to_GMT_timestamp(headers['Expires']) if 'Expires' in headers.keys() else self.to_GMT_timestamp(None))
          self.set_items_value(item,'LastModified',self.to_GMT_timestamp(headers['Last-Modified']) if 'Last-Modified' in headers.keys() else self.to_GMT_timestamp(None))
          try:
               hxs = HtmlXPathSelector(response)
               self.set_items_value(item,'title',','.join(hxs.select('//title/text()').extract()))
               self.set_items_value(item,'desc',','.join(hxs.select('//meta[@name="description"]/@content').extract()))
               self.set_items_value(item,'keyword',','.join(hxs.select('//meta[@name="keywords"]/@content').extract()))
          except:
               self.set_items_value(item,'title',' ')
               self.set_items_value(item,'desc',' ')
               self.set_items_value(item,'keyword',' ')
          self.set_items_value(item,'body',response.body)
          self.set_items_value(item,'stripedbody',nltk.clean_html(self.strip_body(response.body)))
          return item
    def get_page_character(self,html):
        characterinfo = chardet.detect(html)
        character = characterinfo['encoding'] if characterinfo['confidence']>=self.default_encoding_confidence and characterinfo else 'utf8'
        return character
    def get_url_hash_no_fragment(self,url):
          hashobject = hashlib.md5()
          hashobject.update(self.parseurl(url))
          return hashobject.hexdigest()

    def escape_str(self,v):     #not run at here,run@pipelines
            if type(v) is not str:
                return False
                #return False
            returnstr=''
            for x in v:
                if x in self.res:
                    returnstr = returnstr+'\\'+x if len(returnstr)>0 else '\\'+x
                else:
                     returnstr = returnstr+x if len(returnstr)>0 else x
            return returnstr

    def strip_body(self,html):
        characterinfo = chardet.detect(html)
        character = characterinfo['encoding'] if characterinfo['confidence']>=self.default_encoding_confidence and characterinfo else 'utf8'
        character = 'gbk' if character == 'gb2312' else character
        html=html.decode(character,'ignore').encode('utf-8')
        return html
    def set_items_value(self,itemobject,key,value):
           try:
               itemobject[key]=value
           except KeyError:
               itemobject[key]=''
           return itemobject

    def to_GMT_timestamp(self,date):
           if date is None:
               return str(int(time.mktime(time.gmtime())))
           datefomat = '%a, %d %b %Y %H:%M:%S %Z'
           try:
               d = datetime.datetime.strptime(date,datefomat)
               return str(int(time.mktime(d.timetuple())))
           except Exception:
               return str(int(time.mktime(time.gmtime())))


    def parse_error(self,response):
           return response


    def parseurl(self,url):
           try:
               ob = urlparse(url)
               return urlunparse((ob.scheme, ob.netloc, ob.path,ob.params, ob.query,'')) #take away url fragment
           except Exception:
               return url


class initcrwal():
     def __init__(self):
         self.dbinfo={}
         self.dbinfo['host']='localhost'
         self.dbinfo['user']='root'
         self.dbinfo['passwd']=''
         self.dbinfo['db']='tbs1'

         self.dbconn = MySQLdb.connect(host=self.dbinfo['host'],user=self.dbinfo['user'],passwd=self.dbinfo['passwd'],db=self.dbinfo['db'],charset="utf8")
         self.cursor = self.dbconn.cursor()


     def __del__(self):
         self.cursor.close()
         self.dbconn.close()



