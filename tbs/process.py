#-*- coding: UTF-8 -*-
#__author__='christie'
import sys,optparse,multiprocessing
reload(sys)
sys.setdefaultencoding('utf-8')
from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log,signals
from taisha.spiders.discoveryspider import discoveryspider
from scrapy.utils.project import get_project_settings

def startspider(name):
    spider = discoveryspider(name)
    crawler = Crawler(get_project_settings())
    crawler.signals.connect(reactor.stop,signal=signals.spider_closed)
    crawler.configure()
    crawler.crawl(spider)
    crawler.start()
    log.start()
    reactor.run()
    print crawler

if __name__ == '__main__':
    parse = optparse.OptionParser()
    parse.add_option("-n","--name",action="store" ,type="string",dest="uname")
    parse.set_defaults(uname=None)
    opts,args = parse.parse_args()
    if opts.uname is None:
        exit(0)
    processlist=[]
    for x in opts.uname.split(','):
        if len(x)>0:
            p=None
            p=multiprocessing.Process(target=startspider,args=(x,))
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


