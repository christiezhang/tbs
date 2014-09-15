#-*- coding: UTF-8 -*-
#__author__='christie'
import sys,optparse,multiprocessing,time
reload(sys)
sys.setdefaultencoding('utf-8')
import MySQLdb
from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log,signals
from tbs.spiders.tbs2 import tbs2
from scrapy.utils.project import get_project_settings
from urlparse import urlparse
from urlparse import urljoin
from urlparse import urlunparse

class initcrwal():
     def __init__(self):
         self.dbinfo={}
         self.dbinfo['host']='localhost'
         self.dbinfo['user']='root'
         self.dbinfo['passwd']=''
         self.dbinfo['db']='tbs1'
         self.dbconn = MySQLdb.connect(host=self.dbinfo['host'],user=self.dbinfo['user'],passwd=self.dbinfo['passwd'],db=self.dbinfo['db'],charset="utf8")
         self.cursor = self.dbconn.cursor()

     def getsiteurls(self,domain):
         #sql = 'select distinct url from page_discover where url like \'%domain%\' limit '+str(int(page*count))+','+str(count)
         sql = 'select distinct url from page_discover where url like \'%'+domain+'%\''
         try:
             self.cursor.execute(sql)
             tmplist=self.cursor.fetchall()
             l=[]
             for x in tmplist:
                 l.append(x[0])
             return l
         except:
             return ' '


     def __del__(self):
         self.cursor.close()
         self.dbconn.close()


def startspider(name,keyword=None):
    spider = tbs2(name,keyword)
    crawler = Crawler(get_project_settings())
    crawler.signals.connect(reactor.stop,signal=signals.spider_closed)
    crawler.configure()
    crawler.crawl(spider)
    crawler.start()
    log.start()
    reactor.run()
def getdomain(url):
        returnlist=[]
        try:
               ob = urlparse(url)
               returnlist.append(urlunparse(('',ob.netloc,'','','','')))
               return returnlist[0][2:]
        except Exception:
               return ' '
if __name__ == '__main__':
    parse = optparse.OptionParser()
    parse.add_option("-n","--name",action="store" ,type="string",dest="uname")
    parse.set_defaults(uname=None)
    opts,args = parse.parse_args()
    #print opts.uname
    #exit(0)
    if opts.uname is None:
        exit(0)
    processlist=[]
    q=None
    q=multiprocessing.Process(target=startspider,args=(opts.uname,opts.uname))
    q.daemon = True
    q.start()
    q.join(0)
    processlist.append(q)
    while True:
        if len(processlist)==0:
            break
        for y in processlist:
            if y.is_alive() is not True:
                processlist.remove(y)
    #for x in opts.uname.split(','):
    aa=initcrwal()

    while True:

        urllist =aa.getsiteurls(getdomain(opts.uname))
        for u in range(0,len(urllist)/20):
            tmplist = urllist[(20*u):(20*(u+1))]
            p=None
            p=multiprocessing.Process(target=startspider,args=(tmplist,opts.uname))
            p.daemon = True
            p.start()
            p.join(0)
            processlist.append(p)
            print p.pid
            while True:
              if len(processlist)==0:
                   break
              for y in processlist:
                   if y.is_alive() is not True:
                        processlist.remove(y)


