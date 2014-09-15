#-*- coding: UTF-8 -*-
#__author__='christie'
import sys,time,hashlib,os,re,chardet,datetime,time
import memcache
reload(sys)
sys.setdefaultencoding('utf-8')

class pmemcache():
    Memcache_server = '127.0.0.1'
    Memcache_port = '11211'
    Memcache_debug_mode = 0  #no debug
    Memcache_default_value = 1
    #Memcache_default_live = 900
    Memcache_discovery_spider_default_live = 86400

    def __init__(self,live=900):
        try:
            self.memcache =memcache.Client([self.Memcache_server+':'+self.Memcache_port], debug=self.Memcache_debug_mode)
        except:
            self.memcache = None
        self.Memcache_default_live = 900 if live is None else live

    def set(self,key,value,live=0):
        live = self.Memcache_default_live if live==0 else live
        self.memcache.set(key,value,live)

    def get(self,key):
        return self.memcache.get(key)

