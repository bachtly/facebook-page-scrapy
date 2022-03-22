
import scrapy
from scrapy.utils.project import get_project_settings
from scrapy_splash import SplashRequest
import json
from pymongo import MongoClient
from datetime import datetime
import uuid
from Crawl_Data_FaceBook.items import CrawlDataFaceBook

CONNECTION_STRING = "mongodb+srv://DucKhoan:Khoan25032001@cluster.lr6v6.mongodb.net/test"

class FacebookPostPrivateSpider(scrapy.Spider):
    name = 'FaceBook_post_private'

    # def __init__(self, scrolls='', the_uuid='', user_id='', **kwargs):
    #     self.scrolls = scrolls
    #     self.user_id = user_id
    #     self.the_uuid = the_uuid
    #     super().__init__(**kwargs)

    # settings = get_project_settings()

    # xpath_view_more_cmt = "j83agx80 fv0vnmcu hpfvmrgz"

    # xpath_view_more_info = "oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl oo9gr5id gpro0wi8 lrazzd5p"
    # # Lua script to interact with js in the website while crawling
    
    # def start_requests(self):

    #     # This print step is to check whether login is successfull or not base on the HTML return that is written to homepage.html

            
    #     script_login = """
    #         function main(splash, args)
    #             splash:init_cookies(splash.args.cookies)
    #             assert(splash:go{
    #                 splash.args.url,
    #                 headers=splash.args.headers
    #             })
    #             assert(splash:wait(5))
    #             splash:set_viewport_full()          
    #             assert(splash:go("https://www.facebook.com/pler.united"))

    #             splash:set_viewport_full()
    #             local scroll_to = splash:jsfunc("window.scrollTo")
    #             local get_body_height = splash:jsfunc(
    #                 "function() {return document.body.scrollHeight;}"
    #             )
    #             for _ = 1, 10 do
    #                 scroll_to(0, get_body_height())
    #                 assert(splash:wait(5))
    #             end
    
    #             assert(splash:wait(1))
    #             local more = 0
    #             while (true)
    #             do
    #                 local spans = splash:select_all("span[class='""" + self.xpath_view_more_cmt + """']")
    #                 for _, _span in ipairs(spans) do
    #                     assert(_span:mouse_click())
    #                     assert(splash:wait(5))
    #                 end
    #                 more = more +1
    #                 if more == 10 then break end
    #             end
    #             assert(splash:wait(5))
    #             splash:set_viewport_full()
    #             local scroll_to = splash:jsfunc("window.scrollTo")
    #             local get_body_height = splash:jsfunc(
    #                 "function() {return document.body.scrollHeight;}"
    #             )
    #             scroll_to(0, get_body_height())
    #             assert(splash:wait(5))
                
    #             local divs = splash:select_all("div[class='""" + self.xpath_view_more_info + """']")
    #             for _, _ in ipairs(divs) do
    #                 local _div = splash:select("div[class='""" + self.xpath_view_more_info + """']")
    #                 if _div ~= nil then
    #                     assert(_div:mouse_click())
    #                     assert(splash:wait(3))
    #                 end
    #             end
    #             assert(splash:wait(5))
                
    #             return {
    #                 cookies = splash:get_cookies(),                
    #                 html = splash:html(),
    #                 url = splash:url(),
    #                 acc = args.acc
    #             }
    #         end
    #     """

    #     with open('./cookies/cookie_1.json', 'r') as jsonfile:
    #         cookies = json.load(jsonfile)["cookies"]
               
    #     with open('./homepage/html/homepage_NTML.html', 'w+') as out:
    #         out.write('')

    #     # Send splash request with facebook accounnt and lua script to facebook login page to get logged cookie

    #     yield SplashRequest(
    #             url="https://www.facebook.com/login",
    #             callback=self.parse_login,
    #             session_id="test",
    #             meta={
    #                 "splash": {
    #                     "endpoint": "execute", 
    #                     "args": {
    #                         "lua_source": script_login,
    #                         "cookies": cookies,
    #                         "timeout": 3600
    #                     }
    #                 }
    #             }
    #         )

    # def parse_login(self, response):
    #     # Store return HTML tags to homepage.html for checking

    #     client = MongoClient(CONNECTION_STRING)
    #     db_name = client["Posts"]
    #     collection_name = db_name["Post"]

    #     with open('./homepage/html/homepage_NTML.html', 'w+') as out:
    #         out.write(response.text)

    #     h = scrapy.Selector(response)
    #     post_info = h.css("div.du4w35lb.k4urcfbm.l9j0dhe7.sjgh65i0")

    #     for product in post_info:
    #         now = datetime.now()
    #         the_uuid = uuid.uuid4()
    #         item = {
    #             "the_uuid": str(the_uuid),
    #             "datetime": now.strftime("%m/%d/%Y, %H:%M:%S"),
    #         }
    #         item["post_message"] = " ".join(product.css("div.ecm0bbzt.hv4rvrfc.ihqw7lf3.dati1w0a ::text").extract())
    #         item["post_image_link"] = product.css('img.i09qtzwb.n7fi1qx3.datstx6m.pmk7jnqg.j9ispegn.kr520xx4.k4urcfbm.bixrwtb6').xpath('@src').getall()
    #         item["post_image_alt"] = product.css("img.i09qtzwb.n7fi1qx3.datstx6m.pmk7jnqg.j9ispegn.kr520xx4.k4urcfbm.bixrwtb6").xpath("@alt").extract()
            
    #         post_total_reactions= product.css("span.gpro0wi8.cwj9ozl2.bzsjyuwj.ja2t1vim ::text").extract()
    #         if len(post_total_reactions) == 0:
    #             item["post_total_reactions"] = '0'
    #         else:
    #             item["post_total_reactions"] = post_total_reactions[0]

    #         comments_and_shares = product.css("div.bp9cbjyn.j83agx80.pfnyh3mw.p1ueia1e ::text").extract()
            
    #         if len(comments_and_shares) > 0:

    #             item["post_total_comments"] = (comments_and_shares[0].split(" "))[0]
            
    #         else:

    #             item["post_total_comments"] = "0"
            
    #         if len(comments_and_shares) > 1:
                
    #             item["post_total_shares"] = (comments_and_shares[1].split(" "))[0]

    #         else:

    #             item["post_total_shares"] = "0"


    #         post_comments = {}
    #         comments = product.css("div.cwj9ozl2.tvmbv18p > ul > li")
    #         # user_id = 0
    #         for comment in comments:
    #             post_comment_user_id = comment.css("span.nc684nl6 a::attr(href)").extract_first()
    #             user_id = str(post_comment_user_id).split("?")[0].split("/")[-1]
    #             if user_id=='profile.php':
    #                 user_id = str(post_comment_user_id).split("&")[0].split("?")[-1][3:]
    #             post_comments[str(user_id)] = []   

    #             each = {}

    #             each["post_comment_message"] = comment.css("div.l9j0dhe7.ecm0bbzt.rz4wbd8a.qt6c0cv9.dati1w0a.j83agx80.btwxx1t3.lzcic4wl div.ecm0bbzt.e5nlhep0.a8c37x1j ::text").extract_first()
                
    #             links = comment.css("div.l9j0dhe7.ecm0bbzt.rz4wbd8a.qt6c0cv9.dati1w0a.j83agx80.btwxx1t3.lzcic4wl > div.ecm0bbzt.e5nlhep0.a8c37x1j > a")

    #             for link in links:
    #                 link = link.xpath("@href").extract_first()

    #                 each["post_comment_tags"] = []
    #                 each["post_comment_links"] = []

    #                 if "user" in link:

    #                     link = str(link).split("/?")[0].split("/")[-1]

    #                     each["post_comment_tags"].append(link)
                    
    #                 else:

    #                     each["post_comment_links"].append(link)


    #             post_comment_image_link = comment.css("div.j83agx80.bvz0fpym.c1et5uql img").xpath('@src').extract()
                
    #             if len(post_comment_image_link) > 0:

    #                 each["post_comment_image_link"] = post_comment_image_link[0]

    #             post_comment_image_alt = comment.css("div.j83agx80.bvz0fpym.c1et5uql img").xpath("@alt").extract()

    #             if len(post_comment_image_alt) > 0:

    #                 each["post_comment_image_alt"] = post_comment_image_alt[0]                                                                                                      

    #             post_comment_reactions = comment.css("div.l9j0dhe7.ecm0bbzt.rz4wbd8a.qt6c0cv9.dati1w0a.j83agx80.btwxx1t3.lzcic4wl div._680y span.g0qnabr5.hyh9befq.qt6c0cv9.n8tt0mok.jb3vyjys.j5wam9gi.knj5qynh.e9vueds3.m9osqain ::text").extract()

    #             if len(post_comment_reactions) > 0:
    #                 each["post_comment_reactions"] = post_comment_reactions[0]
            
                                
                
    #             # Replies

    #             reps = comment.css("div.kvgmc6g5.jb3vyjys.rz4wbd8a.qt6c0cv9.d0szoon8 > ul > li")

    #             post_rep = {}

    #             if len(reps) > 0:
    #                 # rep_user_id = 0
    #                 for rep in reps:
    #                     post_rep_user_id= rep.css("span.nc684nl6 a::attr(href)").extract_first()
    #                     rep_user_id = str(post_rep_user_id).split("?")[0].split("/")[-1]
    #                     if rep_user_id=='profile.php':
    #                         rep_user_id = str(post_rep_user_id).split("&")[0].split("?")[-1][3:]
    #                     post_rep[str(rep_user_id)] = []
    #                     each_rep = {}

    #                     each_rep["post_reply_message"] = "".join(rep.css("div.ecm0bbzt.e5nlhep0.a8c37x1j ::text").extract())
    #                     post_rep[str(rep_user_id)].append(each_rep)
    #                     # rep_user_id += 1


    #             each["post_comment_replies"] = post_rep
                
    #             post_comments[str(user_id)].append(each)
    #             # user_id +=1


            
    #         item["post_comments"] = post_comments


    #         collection_name.insert_one(item)
        
    


    def __init__(self, scrolls='', the_uuid='', user_id='', **kwargs):
        self.scrolls = scrolls
        self.user_id = user_id
        self.the_uuid = the_uuid
        super().__init__(**kwargs)



    settings = get_project_settings()

    # xpath_view_more_info = "oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl oo9gr5id gpro0wi8 lrazzd5p"
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
                    for _ = 1, 5 do
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
                    
        # script_link = """
        #         function main(splash, args)
        #             splash:init_cookies(splash.args.cookies)
        #             assert(splash:go{
        #                 splash.args.url,
        #                 headers=splash.args.headers
        #             })
        #             assert(splash:wait(5))
        #             splash:set_viewport_full()
        #             assert(splash:wait(5))
        #             local scroll_to = splash:jsfunc("window.scrollTo")
        #             local get_body_height = splash:jsfunc(
        #                 "function() {return document.body.scrollHeight;}"
        #             )
        #             for _ = 1, 1 do
        #                 scroll_to(0, get_body_height())
        #                 assert(splash:wait(2))
        #             end 
                    
        #             assert(splash:wait(5))

        #             local divs = splash:select_all("div[class='""" + self.xpath_view_more_info + """']")
        #             for _, _ in ipairs(divs) do
        #                 local _div = splash:select("div[class='""" + self.xpath_view_more_info + """']")
        #                 if _div ~= nil then
        #                     assert(_div:mouse_click())
        #                 end
        #             end
                    
        #             local entries = splash:history()
        #             local last_response = entries[#entries].response

        #             return {
        #                 cookies = splash:get_cookies(),
        #                 headers = last_response.headers,
        #                 html = splash:html()
        #             }
        #         end
        #     """


        # Send splash request with facebook cookie and lua script to check if cookie is logged in or not
        with open('./cookies/cookie_1.json', 'r') as jsonfile:
            cookies = json.load(jsonfile)["cookies"]
               
        with open('./homepage/html/homepage_NTML.html', 'w+') as out:
            out.write('')

        # yield SplashRequest(
        #     url="https://m.facebook.com/groups/Batdongsansaigonthuanviet/",
        #     callback=self.parse,
        #     session_id="test",
        #     meta={
        #         "splash": {
        #             "endpoint": "execute", 
        #             "args": {
        #                 "lua_source": script_link,
        #                 "cookies": cookies,
        #                 "timeout":3600,
        #             }
        #         }
        #     }
        # )

        acc = self.settings.get("FACEBOOK_ACCOUNT")[0]

        # Send splash request with facebook accounnt and lua script to facebook login page to get logged cookie
        id = ['100002816113052','100017206484600','100026241090835','100027963022760','100056799280787','100005410774650','100031622685153','100008198104980','100028445889201', '100003869139855', '100006278772757', '100068721739609', '100067878651038', '100069069380287', '100070715265013', '100069204429193', '100068506120698', '100068259768037', '100068423130552', '100070640161459', '100069019641080', '100066800115925', '100067971245592', '100064106085316']
        for i in id:
            yield SplashRequest(
                # PAGE  https://m.facebook.com/timeline/app_collection/?collection_token={}%3A2409997254%3A96
                    url="https://m.facebook.com/timeline/app_section/?section_token={}%3A302324425790".format(str(i)),
                    callback=self.parse,
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

    def parse(self, response):

        
        # If login is fail, delete cookie and ask for new one
        # client = MongoClient(CONNECTION_STRING)
        # db_name = client["Posts"]
        # collection_name = db_name["Post"]

        with open('./homepage/html/homepage_NTML.html', 'w+') as out:
            out.write(response.text)

        # htmls = scrapy.Selector(response)
        # user = htmls.css("h2.gmql0nx0.l94mrbxd.p1ri9a11.lzcic4wl.aahdfvyu.hzawbc8m a::attr(href)").extract()
        # post_info = htmls.css("div.ecm0bbzt.hv4rvrfc.ihqw7lf3.dati1w0a")
        
        # for i in range(len(user)):
        #     # now = datetime.now()
        #     # timestamp = int(datetime.timestamp(now))
        #     # the_uuid = uuid.uuid4()
        #     # post = {
        #     #     "the_uuid": str(the_uuid),
        #     #     "datetime": now.strftime("%m/%d/%Y, %H:%M:%S"),
        #     # }
        #     post = CrawlDataFaceBook()
        #     # post["post_user_id"] = str(user[i]).split("?")[0].split("/")[-2]
        #     post["post_message"] = "\n".join(post_info[i].css("::text").extract())
        #     # collection_name.insert_one(post)
        
        #Crawl like page

        # h = scrapy.Selector(response)
        # post_info = h.css("div._1a5p")
        # item = CrawlDataFaceBook()
        # for product in post_info:
 
        #     item["page"] = " ".join(product.css("div._1a5r ::text").extract())
        #     yield item
        

        h = scrapy.Selector(response)
        post_info = h.css("div.primarywrap")
        item = CrawlDataFaceBook()
        for product in post_info:
 
            item["page"] = " ".join(product.css("div.title.allowWrap.mfsm.fcb ::text").extract())
            yield item

