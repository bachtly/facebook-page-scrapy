import scrapy
from scrapy.utils.project import get_project_settings
from scrapy_splash import SplashRequest
import json
from Crawl_Data_FaceBook.items import CrawlDataFaceBook, CrawlData

Customer_Id = ['100056799280787']
Group_Id = ['606213853219261']

class TestSpider(scrapy.Spider):
    name = 'test'

    def __init__(self, scrolls='', the_uuid='', user_id='', **kwargs):
        self.scrolls = scrolls
        self.user_id = user_id
        self.the_uuid = the_uuid
        super().__init__(**kwargs)

    settings = get_project_settings()

    xpath_view_more_info = "text_exposed_hide"
    def start_requests(self):

        script_login = """
                function main(splash, args)
                    assert(splash:go{
                        splash.args.url,
                        headers=splash.args.headers
                    })
                    assert(splash:wait(2))
                    function focus(sel)
                        splash:select(sel):focus()
                    end
        
                    focus('input[name=email]')   
                    splash:send_text(args.acc)
                    assert(splash:wait(1))
                    focus('input[name=pass]')
                    splash:send_text(args.pwd)
                    assert(splash:wait(1))
                    splash:select('button[name=login]'):mouse_click()
                    assert(splash:wait(6))
                    local scroll_to = splash:jsfunc("window.scrollTo")
                    local get_body_height = splash:jsfunc(
                        "function() {return document.body.scrollHeight;}"
                    )
                    for _ = 1, 2 do
                        scroll_to(0, get_body_height())
                        assert(splash:wait(2))
                    end     
                    assert(splash:wait(5))  

                    local divs = splash:select_all("span[class='""" + self.xpath_view_more_info + """']")
                    for _, _ in ipairs(divs) do
                        local _div = splash:select("div[class='""" + self.xpath_view_more_info + """']")
                        if _div ~= nil then
                            assert(_div:mouse_click())
                        end
                    end
                    

                    return {
                        cookies = splash:get_cookies(),                
                        html = splash:html(),
                        url = splash:url(),
                        acc = args.acc
                    }
                end
            """
        
        script_link = """
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
                    for _ = 1, 2 do
                        scroll_to(0, get_body_height())
                        assert(splash:wait(1))
                    end 
                    
                    assert(splash:wait(5))

                    local divs = splash:select_all("div[class='""" + self.xpath_view_more_info + """']")
                    for _, _ in ipairs(divs) do
                        local _div = splash:select("div[class='""" + self.xpath_view_more_info + """']")
                        if _div ~= nil then
                            assert(_div:mouse_click())
                        end
                    end
                    
                    local entries = splash:history()
                    local last_response = entries[#entries].response

                    return {
                        cookies = splash:get_cookies(),
                        headers = last_response.headers,
                        html = splash:html(),
                        url = splash.url()
                    }
                end
            """
        for k in range(1,3):
            if k==1:
                acc = self.settings.get("FACEBOOK_ACCOUNT")[0]

                # Send splash request with facebook accounnt and lua script to facebook login page to get logged cookie
                id = ['100056799280787','100056799280787','100017206484600','100026241090835','100027963022760','100056799280787' ]
                for i in id:
                    yield SplashRequest(
                            url="https://m.facebook.com/timeline/app_collection/?collection_token={}%3A2409997254%3A96".format(str(i)),
                            callback=self.parse_1,
                            session_id="test",
                            meta={
                                "splash": {
                                    "endpoint": "execute", 
                                    "args": {
                                        "lua_source": script_login,
                                        "acc": acc["account"],
                                        "pwd": acc["password"],
                                        "timeout": 3600
                                    }
                                }
                            }
                        )
            elif k==2:
                with open('./cookies/cookie_1.json', 'r') as jsonfile:
                    cookies = json.load(jsonfile)["cookies"]
                    
                with open('./homepage/html/homepage_BDS.html', 'w+') as out:
                    out.write('')
                    #Lấy list id 
                for g_id in Group_Id:
                    yield SplashRequest(
                        url="https://m.facebook.com/profile.php?id={}&groupid={}".format(Customer_Id[0], g_id),
                        callback=self.parse_2,
                        session_id="test",
                        meta={
                            "splash": {
                                "endpoint": "execute", 
                                "args": {
                                    "lua_source": script_link,
                                    "cookies": cookies,
                                    "timeout":3600,
                                }
                            }
                        }
                    )


    def parse_1(self, response):

        with open('./homepage/html/homepage_NTML.html', 'w+') as out:
            out.write(response.text)

        h = scrapy.Selector(response)
        post_info = h.css("div._1a5p")
        item = CrawlDataFaceBook()
        for product in post_info:
 
            item["page"] = " ".join(product.css("div._1a5r ::text").extract())
            yield item
    
    def parse_2(self, response):

        with open('./homepage/html/PostInGroup.html', 'w+') as out:
            out.write(response.text)

        h = scrapy.Selector(response)
        post_info = h.css("div._4gur._5t8z")
        item = CrawlData()
        for product in post_info:
            item["post"] = " ".join(product.css("div._il ::text").extract())
            yield item

