#-*- coding: UTF-8 -*-
#__author__='christie'
import sys,time,hashlib,os,re,chardet,datetime,time
reload(sys)
sys.setdefaultencoding('utf-8')
import MySQLdb
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from urlparse import urlparse
from urlparse import urljoin
from urlparse import urlunparse
from posixpath import normpath
#from HTMLParser import HTMLParser
from BeautifulSoup import BeautifulSoup,Tag,NavigableString,Comment
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from urllib import urlretrieve
from urlparse import urlsplit
#from scrapy.item import Item
from tbs.items import TbsItem              # import self declared items

class tbs1(BaseSpider):
    name = 'tbs1'
    defult_strip_start_tag = 'body'
    striptag=['scripts','script','style']
    default_encoding_confidence=0.9
    max_page=1

    def __init__(self):
        self.start_urls=[]
        #self.keyword = keyword
        self.keyword = '菜籽油 市场'
        for x in range(self.max_page):
            #self.start_urls.append('http://www.baidu.com/s?wd=%E8%8F%9C%E7%B1%BD%E6%B2%B9+%E5%B8%82%E5%9C%BA&pn='+str(int(10*x)))
            self.start_urls.append('http://www.baidu.com/s?wd='+self.keyword+'&pn='+str(int(10*x)))
        self.allowed_domains=[]

    def parse(self,response):
       links =[]
       try:
              linkextracts =  SgmlLinkExtractor(allow='^http://www\.baidu\.com/link\?.*',allow_domains=self.allowed_domains).extract_links(response)
       except:
              return
       for link in linkextracts:
              links.append(link.url)
       #links.append(response.url) if response.url not in links else links
       for l in links:
            yield Request(l,callback=self.parse_detail,errback=self.parse_error)

    def parse_detail(self,response):
          print response.url
          #print response.headers
          #print response.meta
          item = TbsItem()
          headers = response.headers
          hashobject = hashlib.md5()
          hashobject.update(self.parseurl(response.url))
          self.set_items_value(item,'spidername',self.name)
          #self.set_items_value(item,'refer',self.name)
          self.set_items_value(item,'url_hash_no_fragment', hashobject.hexdigest())
          self.set_items_value(item,'url', response.url)
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
          self.set_items_value(item,'stripedbody',self.strip_html_tags1(response.body))




    def strip_html_tags1(self,html,soupobject=None):
        try:
           characterinfo = chardet.detect(html)
           character = characterinfo['encoding'] if characterinfo['confidence']>=self.default_encoding_confidence and characterinfo else 'utf8'
           html=html.decode(character,'ignore').encode('utf8')
           soupobject = BeautifulSoup(html) if soupobject is None else soupobject
           htmlbody = getattr(soupobject,self.defult_strip_start_tag)
           try:
                comments = htmlbody.findAll(text=lambda text:isinstance(text,Comment))  #get rid of html comment
           except AttributeError:
               return False
           [comment.extract() for comment in comments]
           rv=''
           for x in htmlbody:
               if isinstance(x,NavigableString) and x !='\n':
                   rv = x if rv=='' else rv+' '+str(x)
               elif isinstance(x,Tag) and x.name not in self.striptag:
                   rv = self.strip_html_tags1(x) if rv=='' else rv+' '+str(self.html_tag_iterator(x))
           return rv
        except:
            return self.filter_tags(html)

    def html_tag_iterator(self,htmlobject,):
           rv=''
           if isinstance(htmlobject,Tag) is False:
               raise MYEXCEPTION('HTML_TYPE_ERROR')
           else:
               for x in htmlobject.contents:
                   if isinstance(x,NavigableString) and x !='\n':
                       rv = x if rv=='' else rv+' '+str(x)
                       #print rv
                   elif isinstance(x,Tag) and x.name not in self.striptag:
                       rv = self.html_tag_iterator(x) if rv=='' else rv+' '+str(self.html_tag_iterator(x))
           return rv
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

    def filter_tags(self,htmlstr):
    #先过滤CDATA
        re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I) #匹配CDATA
        re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script
        re_script1=re.compile('<\s*scripts[^>]*>[^<]*<\s*/\s*scripts\s*>',re.I)
        re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
        re_table=re.compile('<\s*table[^>]*>[^<]*<\s*/\s*table\s*>',re.I)#table
        re_br=re.compile('<br\s*?/?>')#处理换行
        re_h=re.compile('</?\w+[^>]*>')#HTML标签
        re_h1=re.compile('<.*?> ')#HTML标签
        re_comment=re.compile('<!--[^>]*-->')#HTML注释
        s=re_cdata.sub('',htmlstr)#去掉CDATA
        s=re_script.sub('',s) #去掉SCRIPT
        s=re_script1.sub('',s) #去掉SCRIPT
        s=re_style.sub('',s)#去掉style
        s=re_br.sub('\n',s)#将br转换为换行
        s=re_h.sub('',s) #去掉HTML 标签
        s=re_comment.sub('',s)#去掉HTML注释
        s=re_table.sub('',s)
        s=re_h1.sub('',s)
        #去掉多余的空行
        blank_line=re.compile('\n+')
        s=blank_line.sub('\n',s)
        s=self.replaceCharEntity(s)#替换实体
        return s
    def replaceCharEntity(self,htmlstr):
        CHAR_ENTITIES={'nbsp':' ','160':' ',
                'lt':'<','60':'<',
                'gt':'>','62':'>',
                'amp':'&','38':'&',
                'quot':'"','34':'"',}
        re_charEntity=re.compile(r'&#?(?P<name>\w+);')
        sz=re_charEntity.search(htmlstr)
        while sz:
            entity=sz.group()#entity全称，如&gt;
            key=sz.group('name')#去除&;后entity,如&gt;为gt
            try:
                htmlstr=re_charEntity.sub(CHAR_ENTITIES[key],htmlstr,1)
                sz=re_charEntity.search(htmlstr)
            except KeyError:
                #以空串代替
                htmlstr=re_charEntity.sub('',htmlstr,1)
                sz=re_charEntity.search(htmlstr)
        return htmlstr

    def repalce(s,re_exp,repl_string):
        return re_exp.sub(repl_string,s)



