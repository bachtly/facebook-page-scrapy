from operator import pos
import scrapy
from scrapy.utils.project import get_project_settings
from scrapy_splash import SplashRequest
import json
from Crawl_Data_FaceBook.items import CrawlData, PostItem, PostInfoItem

Page_Id = ['WHOVietnam', 'xahoi.com.vn', 'sao247new', 'tintucvtv24', 'tintucthoisu24giohomnay']
Page_Name = ['World Health Organization Viet Nam - Tổ chức Y tế Thế giới Việt Nam']
idx=0

class FacebookPagePostsSpider(scrapy.Spider):
    name = 'FaceBook_page_posts'
    def __init__(self, scrolls="800", the_uuid='', user_id='', **kwargs):
        self.scrolls = scrolls
        self.user_id = user_id
        self.the_uuid = the_uuid
        super().__init__(**kwargs)
        self.xpath_view_more_info = "a[#u_0_72_Ne]"
        self.xpath_cmt = "_15kq _77li"

    # This will setup settings variable to get constant from settings.py
    settings = get_project_settings()
    # xpath_view_more_info = "more"
    # Lua script to interact with js in the website while crawling

    def start_requests(self):
        script_link = '''
                function main(splash, args)
                    splash:init_cookies(splash.args.cookies)
                    assert(splash:go{
                        splash.args.url,
                        headers=splash.args.headers
                    })
                    
                    assert(splash:wait(5))
                    
                    splash:set_viewport_full()
                    
                    local scroll_to = splash:jsfunc("window.scrollTo")
                    local get_body_height = splash:jsfunc(
                        "function() {return document.body.scrollHeight;}"
                    )
                    
                    for _ = 1, ''' +self.scrolls +''' do
                        scroll_to(0, get_body_height())
                        assert(splash:wait(1))
                    end 
                    
                    assert(splash:wait(5))

                    --local divs = splash:select_all("div.text_exposed_hide span")
                    --for _, _div in ipairs(divs) do
                        --local _div = splash:select("div.text_exposed_hide span")
                        --if _div ~= nil then
                            --assert(_div:mouse_click())
                            --assert(splash:wait(2))
                        --end
                    --end

                    local entries = splash:history()
                    local last_response = entries[#entries].response

                    return {
                        cookies = splash:get_cookies(),
                        headers = last_response.headers,
                        html = splash:html(),
                        url = splash.url()
                    }
                end
            '''


        # Send splash request with facebook cookie and lua script to check if cookie is logged in or not
        with open('./cookies/cookie_bach.json', 'r') as jsonfile:
            cookies = json.load(jsonfile)["cookies"]
               
        # g_id = Page_Name[idx]
        g_id = Page_Id[idx]
        # print(f"CRAWLING {g_id}")
        yield SplashRequest(
            url=f"https://m.facebook.com/{g_id}/posts",
            # url=f"https://m.facebook.com/search/posts/?q={g_id}",
            callback=self.parse,
            session_id="test",
            meta={
                "splash": {
                    "endpoint": "execute", 
                        "endpoint": "execute", 
                    "endpoint": "execute", 
                        "endpoint": "execute", 
                    "endpoint": "execute", 
                        "endpoint": "execute", 
                    "endpoint": "execute", 
                    "args": {
                        "lua_source": script_link,
                        "cookies": cookies,
                        "timeout":3600,
                    }
                }
            }
        )

    def parse(self, response):
        # If login is fail, delete cookie and ask for new one
        # client = MongoClient(CONNECTION_STRING)
        # db_name = client["Posts"]
        # collection_name = db_name["Post"]

        with open('./homepage/html/PostInPagePost.html', 'w+', encoding='utf-8') as out:
            out.write(response.text)

        root = scrapy.Selector(response)
        item = PostItem()
        item['info'] = PostInfoItem()
        
        posts = root.xpath("""//*[@class="_55wo _5rgr _5gh8 _3drq async_like"]""")
        
        for post in posts:
            body = post.xpath("div")
            footer = post.xpath("footer")
        
            ### post id
            dataft = eval(post.attrib['data-ft'])
            item['post_id'] = dataft['mf_story_key']
            item['page_id'] = dataft['page_id']
            
            ### PIL image
            
            ### source url  
            source_url = "https://www.facebook.com/permalink.php?"+\
                        f"story_fbid={dataft['mf_story_key']}&id={dataft['page_id']}"
            item['source_url'] = source_url
            
            ### metadata: post time, # emotions, # comments, # share
            n_reacts = footer.xpath("div/div[1]/a/div/div[1]/div//text()")
            item['info']['number_of_reacts'] = n_reacts.get()
            
            n_comments = footer.xpath("div/div[1]/a/div/div[2]/span[1]//text()")
            item['info']['number_of_comments'] = n_comments.get()
            
            n_shares = footer.xpath("div/div[1]/a/div/div[2]/span[2]//text()")
            item['info']['number_of_shares'] = n_shares.get()
            
            date = body.xpath("header/div[2]/div/div/div[1]/div/a/abbr//text()")
            item['info']['date'] = date.get()
            
            ### comments
            ### shared post
        
            ### text
            content = body.xpath("""div/div""")
            # print(i.get())
            exposed = content.xpath("""span//text()""")
            background = content.xpath("""div/span[2]//text()""")
            # hidden = content.xpath("""span/div//text()""")
            item['text'] = " ".join([i for i in exposed.getall() if i!="Xem thêm"]) \
                        + " ".join([i for i in background.getall() if i!="Xem thêm"])
            yield item



# --local divs = splash:select_all(" ''' + self.xpath_view_more_info + ''' ")
# --for _, _ in ipairs(divs) do
# --    local _div = splash:select(" ''' + self.xpath_view_more_info + ''' ")
# --    if _div ~= nil then
# --        assert(_div:mouse_click())
# --        assert(splash:wait(2))
# --    end
# --end