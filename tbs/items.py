# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class TbsItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = Field()
    #link = Field()
    desc = Field()
    keyword = Field()
    stripedbody = Field()
    Expires = Field()
    LastModified = Field()
    body = Field()
    root_domain = Field()
    url_hash_no_fragment = Field()
    url = Field()
    domain_name=Field()
    refer=Field()
    character = Field()
    spiderid = Field()
    urlsetid = Field()
    searchkeywords = Field()
    crawl_stats=Field()
    MZY_name = Field()
    MZY_style = Field()
    MZY_price = Field()
    MZY_unit = Field()
    MZY_spec = Field()
    MZY_orgin = Field()
    MZY_issuestime = Field()
    MZY_source = Field()
    #dbip = Field()
    #dbname = Field()
    pass
