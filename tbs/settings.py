# -*- coding: utf-8 -*-

# Scrapy settings for tbs project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'tbs'

SPIDER_MODULES = ['tbs.spiders']
NEWSPIDER_MODULE = 'tbs.spiders'
#ITEM_PIPELINES  = ['tbs.pipelines.tbsPipeline']
DOWNLOADER_MIDDLEWARES_BASE = {
    'scrapy.contrib.downloadermiddleware.robotstxt.RobotsTxtMiddleware': 100,
    'scrapy.contrib.downloadermiddleware.httpauth.HttpAuthMiddleware': 300,
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': 400,
    'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 500,
    'scrapy.contrib.downloadermiddleware.defaultheaders.DefaultHeadersMiddleware': 550,
    'scrapy.contrib.downloadermiddleware.redirect.RedirectMiddleware': 600,
    'scrapy.contrib.downloadermiddleware.cookies.CookiesMiddleware': 700,
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 750,
    'scrapy.contrib.downloadermiddleware.httpcompression.HttpCompressionMiddleware': 800,
    'scrapy.contrib.downloadermiddleware.stats.DownloaderStats': 850,
    'scrapy.contrib.downloadermiddleware.httpcache.HttpCacheMiddleware': 900,
}
DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware':{'RETRY_ENABLED':True,'RETRY_TIMES':5,'RETRY_HTTP_CODES':[302,500, 502, 503, 504, 400, 408]} ,
}
#EXTENSIONS={'scrapy.contrib.resolver.CachingResolver': 0,}
REDIRECT_ENABLED = True
METAREFRESH_DELAY = 100
REDIRECT_MAX_TIMES = 20 # uses Firefox default setting
REDIRECT_PRIORITY_ADJUST = +2
SCHEDULER_ORDER = 'BFO'
DOWNLOAD_DELAY = 2
DOWNLOAD_TIMEOUT =180
CONCURRENT_REQUESTS = 10
# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'TBS Spders '
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'tbs (+http://www.yourdomain.com)'
