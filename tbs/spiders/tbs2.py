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


class tbs2(BaseSpider):
    name = 'tbs2'
    default_encoding_confidence=0.9
    max_page=200
    default_crawl_stats='200'
    res=['?','+','.','#','^','*','{','}',',','(',')','<','>','...','!','|','\'']
    default_memcache_live = 86400


    def __init__(self,starturl,keyword=None):
        self.memcache = pmemcache(live=self.default_memcache_live)
        self.outurl = None
        #self.limit = limit if isinstance(limit,int) else None
        self.limit = None
        if isinstance(starturl,list):
             self.start_urls=starturl
        elif isinstance(starturl,str):
             self.start_urls=[]
             self.start_urls.append(starturl)
        self.keyword = keyword if keyword is not None else ''
        #self.start_urls=['http://12582.10086.cn/sn/AgroInfo/Detail/12513322']
        self.allowed_domains=[] if self.outurl is None else self.getdomain()



    def parse(self,response):
       links =[]
       try:
              #linkextracts =  SgmlLinkExtractor(allow='^http://www\.baidu\.com/link\?.*',allow_domains=self.allowed_domains).extract_links(response)
              linkextracts =  SgmlLinkExtractor(allow_domains=self.allowed_domains).extract_links(response)
       except:
              return
       for link in linkextracts:
              links.append(link.url)
       #links.append(response.url) if response.url not in links else links
       count = 0
       for l in links:
            if self.limit is not None and count > self.limit:
                break
            if self.memcache.get(self.get_url_hash_no_fragment(l)) != 1:
                 if self.limit is not None:
                     count +=1
                 yield Request(l,meta={'refer': response.url},callback=self.parse_detail,errback=self.parse_error)
            else:
                continue

    def parse_detail(self,response):
          item = TbsItem()
          headers = response.headers
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
    '''
    def strip_html_tags1(self,html,soupobject=None,frist=True):

           if isinstance(html,Tag):
               html = str(html)

           if frist is True:
               characterinfo = chardet.detect(html)
               character = characterinfo['encoding'] if characterinfo['confidence']>=self.default_encoding_confidence and characterinfo else 'utf8'
               character = 'gbk' if character == 'gb2312' else character
               html=html.decode(character,'ignore').encode('utf-8')
           else:
               html = html.encode('utf-8')
           soupobject = BeautifulSoup(html) if soupobject is None else soupobject
           htmlbody = getattr(soupobject,self.defult_strip_start_tag)
           try:
                comments = htmlbody.findAll(text=lambda text:isinstance(text,Comment))  #get rid of html comment
           except AttributeError as e:
               print e
               #return ''
           [comment.extract() for comment in comments]
           page = ''.join(htmlbody.findAll(text=True))
           page = ' '.join(page.split())
           print page

           #print comments
           rv=''
           for x in htmlbody:
               if isinstance(x,NavigableString) and x !='\n':
                   rv = x if len(rv)==0 else str(rv)+' '+str(x)
               elif isinstance(x,Tag) and x.name not in self.striptag:
                   print x
                   #rv = self.strip_html_tags1(x,frist=False) if len(rv)==0 else str(rv)+' '+str(self.html_tag_iterator(x))
           return rv


    def html_tag_iterator(self,htmlobject,):
           rv=''
           if isinstance(htmlobject,Tag) is False:
               pass
               #raise MYEXCEPTION('HTML_TYPE_ERROR')
           else:
               for x in htmlobject.contents:
                   if isinstance(x,NavigableString) and x !='\n':
                       rv = x if rv=='' else rv+' '+str(x)
                       #print rv
                   elif isinstance(x,Tag) and x.name not in self.striptag:
                       rv = self.html_tag_iterator(x) if rv=='' else rv+' '+str(self.html_tag_iterator(x))
           return rv

    '''
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
    def getdomain(self,url):
        returnlist=[]
        try:
               ob = urlparse(url)
               returnlist.append(urlunparse(('',ob.netloc,'','','','')))
               return returnlist
        except Exception:
               return ' '

    def parseurl(self,url):
           try:
               ob = urlparse(url)
               return urlunparse((ob.scheme, ob.netloc, ob.path,ob.params, ob.query,'')) #take away url fragment
           except Exception:
               return url




