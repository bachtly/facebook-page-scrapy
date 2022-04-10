from operator import pos
import scrapy
from scrapy.utils.project import get_project_settings
from scrapy_splash import SplashRequest
from scrapy.http import Request
import json
from Crawl_Data_FaceBook.items import CrawlData, PostItem, PostInfoItem

page_ids = ['tintuc2', 'botruongboyte.vn', 'thongtinchinhphu']
idx=0

class FacebookPageSpider(scrapy.Spider):
    name = 'facebook_page'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    settings = get_project_settings()

    def start_requests(self):
        with open('./cookies/cookie_bach.json', 'r') as jsonfile:
            cookies = json.load(jsonfile)["cookies"]
               
        g_id = Page_Id[idx]
        yield Request(
            url=f"https://mbasic.facebook.com/{g_id}",
            cookies=cookies,
            callback=self.parse,
            meta={'page_id': g_id}
        )

    def parse(self, response):
        # If login is fail, delete cookie and ask for new one
        # client = MongoClient(CONNECTION_STRING)
        # db_name = client["Posts"]
        # collection_name = db_name["Post"]

        with open('./homepage/html/PostInPage.html', 'w+', encoding='utf-8') as out:
            out.write(response.text)

        root = scrapy.Selector(response)
        # item = PostItem()
        # item['info'] = PostInfoItem()
        
        # posts = root.xpath("""//*[@class="_55wo _5rgr _5gh8 async_like _1tl-"]""")
        
        # for post in posts:
        #     body = post.xpath("div")
        #     footer = post.xpath("footer")
        
        #     ### post id
        #     dataft = eval(post.attrib['data-ft'])
        #     item['post_id'] = dataft['mf_story_key']
        #     item['page_id'] = dataft['page_id']
            
        #     ### PIL image
            
        #     ### source url  
        #     source_url = "https://www.facebook.com/permalink.php?"+\
        #                 f"story_fbid={dataft['mf_story_key']}&id={dataft['page_id']}"
        #     item['source_url'] = source_url
            
        #     ### metadata: post time, # emotions, # comments, # share
        #     n_reacts = footer.xpath("div/div[1]/a/div/div[1]/div//text()")
        #     item['info']['number_of_reacts'] = n_reacts.get()
            
        #     n_comments = footer.xpath("div/div[1]/a/div/div[2]/span[1]//text()")
        #     item['info']['number_of_comments'] = n_comments.get()
            
        #     n_shares = footer.xpath("div/div[1]/a/div/div[2]/span[2]//text()")
        #     item['info']['number_of_shares'] = n_shares.get()
            
        #     date = body.xpath("header/div[2]/div/div/div[1]/div/a/abbr//text()")
        #     item['info']['date'] = date.get()
            
        #     ### comments
        #     ### shared post
        
        #     ### text
        #     content = body.xpath("""div/div""")
        #     # print(i.get())
        #     exposed = content.xpath("""span//text()""")
        #     background = content.xpath("""div/span[2]//text()""")
        #     # hidden = content.xpath("""span/div//text()""")
        #     item['text'] = " ".join([i for i in exposed.getall() if i!="Xem thêm"]) \
        #                 + " ".join([i for i in background.getall() if i!="Xem thêm"])
        #     yield item



