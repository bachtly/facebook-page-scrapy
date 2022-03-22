# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

# from importlib_metadata import metadata
# from matplotlib.pyplot import sca
import scrapy


class FacebookPageItem(scrapy.Item):
    page_id = scrapy.Field()
    content = scrapy.Field()

class CrawlDataFacebookItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class CrawlDataFaceBook(scrapy.Item):
    page = scrapy.Field()

class PostInfoItem(scrapy.Item):
    date = scrapy.Field()
    number_of_reacts = scrapy.Field()
    number_of_comments = scrapy.Field()
    number_of_shares = scrapy.Field()

class PostItem(scrapy.Item):
    text = scrapy.Field()
    info = scrapy.Field()
    post_id = scrapy.Field()
    page_id = scrapy.Field()
    source_url = scrapy.Field()

class CrawlData(scrapy.Item):
    post = scrapy.Field()