
import scrapy
from scrapy.utils.project import get_project_settings
from scrapy_splash import SplashRequest
import json
import os
import time
from datetime import datetime, timedelta
import uuid
from pymongo import MongoClient

CONNECTION_STRING = "mongodb+srv://DucKhoan:Khoan25032001@cluster.lr6v6.mongodb.net/test"

class FacebookPostSpider(scrapy.Spider):
    def _convert_to_timestamp(self, the_input):

        ts = -1

        for each in  ["Hôm qua"]:
            if each in the_input:
                today = datetime.now()

                the_time = the_input.split(" ")[-1].split(":")

                d = datetime(year=today.year, month=today.month, day=today.day, hour=int(the_time[0]), minute=int(the_time[1])) - timedelta(days=1)

                ts = int(time.mktime(d.utctimetuple()))

                return ts
        
        for each in  ["tháng"]:
            if each in the_input:
                if "," in the_input:

                    the_time = the_input.split(" ")

                    the_hrs_mins = the_time[-1].split(":")

                    d = datetime(year=int(the_time[3]), month=int(the_time[2].replace(",","")), day=int(the_time[0]), hour=int(the_hrs_mins[0]), minute=int(the_hrs_mins[1]))

                    ts = int(time.mktime(d.utctimetuple()))

                    return ts

                else:

                    today = datetime.now()

                    the_time = the_input.split(" ")

                    the_hrs_mins = the_time[-1].split(":")

                    d = datetime(year=today.year, month=int(the_time[2].replace(",","")), day=int(the_time[0]), hour=int(the_hrs_mins[0]), minute=int(the_hrs_mins[1]))

                    ts = int(time.mktime(d.utctimetuple()))

                    return ts
        
        for each in  ["giờ"]:
            if each in the_input:

                today = datetime.now()

                the_time = the_input.split(" ")

                d = datetime(year=today.year, month=today.month, day=today.day, hour=today.hour, minute=today.minute, second=today.second) - timedelta(hours=int(the_time[0]))

                ts = int(time.mktime(d.utctimetuple()))

                return ts
        
        for each in  ["phút"]:
            if each in the_input:

                today = datetime.now()

                the_time = the_input.split(" ")

                d = datetime(year=today.year, month=today.month, day=today.day, hour=today.hour, minute=today.minute, second=today.second) - timedelta(minutes=int(the_time[0]))

                ts = int(time.mktime(d.utctimetuple()))

                return ts
        
        for each in  ["giây"]:
            if each in the_input:

                today = datetime.now()

                the_time = the_input.split(" ")

                d = datetime(year=today.year, month=today.month, day=today.day, hour=today.hour, minute=today.minute, second=today.second) - timedelta(seconds=int(the_time[0]))

                ts = int(time.mktime(d.utctimetuple()))
        
                return ts

    name = 'FaceBook_post'

    def __init__(self, scrolls='', the_uuid='', user_id='', **kwargs):
        self.scrolls = scrolls
        self.user_id = user_id
        self.the_uuid = the_uuid
        super().__init__(**kwargs)

    # This will setup settings variable to get constant from settings.py

    settings = get_project_settings()

    xpath_view_more_info = "oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl oo9gr5id gpro0wi8 lrazzd5p"
    # Lua script to interact with js in the website while crawling

    
    def start_requests(self):

        script_link = """
                function main(splash, args)
                    splash:init_cookies(splash.args.cookies)
                    assert(splash:go{
                        splash.args.url,
                        headers=splash.args.headers
                    })
                    assert(splash:wait(5))
                    splash:set_viewport_full()
                    assert(splash:go{"https://www.facebook.com/groups/Batdongsansaigonthuanviet/"})
                    assert(splash:wait(5))
                    local scroll_to = splash:jsfunc("window.scrollTo")
                    local get_body_height = splash:jsfunc(
                        "function() {return document.body.scrollHeight;}"
                    )
                    for _ = 1, 20 do
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
                        html = splash:html()
                    }
                end
            """


        # Send splash request with facebook cookie and lua script to check if cookie is logged in or not
        with open('./cookies/cookie_1.json', 'r') as jsonfile:
            cookies = json.load(jsonfile)["cookies"]
               
        with open('./homepage/html/homepage_BDS.html', 'w+') as out:
            out.write('')

        yield SplashRequest(
            url="https://www.facebook.com/login",
            callback=self.parse,
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

    def parse(self, response):

        
        # If login is fail, delete cookie and ask for new one
        client = MongoClient(CONNECTION_STRING)
        db_name = client["Posts"]
        collection_name = db_name["Post"]

        with open('./homepage/html/homepage_BDS.html', 'w+') as out:
            out.write(response.text)

        htmls = scrapy.Selector(response)
        user = htmls.css("h2.gmql0nx0.l94mrbxd.p1ri9a11.lzcic4wl.aahdfvyu.hzawbc8m a::attr(href)").extract()
        post_info = htmls.css("div.ecm0bbzt.hv4rvrfc.ihqw7lf3.dati1w0a")
        
        for i in range(len(user)):
            now = datetime.now()
            timestamp = int(datetime.timestamp(now))
            the_uuid = uuid.uuid4()
            post = {
                "the_uuid": str(the_uuid),
                "datetime": now.strftime("%m/%d/%Y, %H:%M:%S"),
            }
            post["post_user_id"] = str(user[i]).split("?")[0].split("/")[-2]
            post["post_message"] = "\n".join(post_info[i].css("::text").extract())
            collection_name.insert_one(post)


