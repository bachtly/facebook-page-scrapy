# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

# from importlib_metadata import metadata
# from matplotlib.pyplot import sca
import scrapy

class Item(scrapy.Item):
    page_id = scrapy.Field()    
    post_id = scrapy.Field()
    html_path = scrapy.Field()
    fetched_time = scrapy.Field()

class PostItem(Item):
    pass
    
class CmtItem(Item):
    pass
    
class ReactionItem(Item):
    pass

class DebugEmptyTextItem(Item):
    pass