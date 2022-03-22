import scrapy
from scrapy.utils.project import get_project_settings
from scrapy_splash import SplashRequest
import json


class FacebookLoginSpider(scrapy.Spider):
    name = 'Facebook_login'

    # This will setup settings variable to get constant from settings.py

    settings = get_project_settings()

    # Lua script to interact with js in the website while crawling

    
    script_login = """
        function main(splash, args)
            assert(splash:go{
                splash.args.url,
                headers=splash.args.headers
            })
            function focus(sel)
                splash:select(sel):focus()
            end
            assert(splash:wait(3))
            focus('input[name=email]')   
            splash:send_text(args.acc)
            assert(splash:wait(0))
            focus('input[name=pass]')
            splash:send_text(args.pwd)
            assert(splash:wait(0))
            splash:select('button[name=login]'):mouse_click()
            assert(splash:wait(3))
            
            
            return {
                cookies = splash:get_cookies(),
                html = splash:html(),
            }
        end
    """

    # splash:runjs("document.getElementsByClassName('oajrlxb2 gs1a9yip g5ia77u1 mtkw9kbi tlpljxtp qensuy8j ppp5ayq2 goun2846 ccm00jje s44p3ltw mk2mc5f4 rt8b4zig n8ej3o3l agehan2d sk4xxmp2 rq0escxv nhd2j8a9 a8c37x1j mg4g778l btwxx1t3 pfnyh3mw p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x tgvbjcpo hpfvmrgz jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso l9j0dhe7 i1ao9s8h esuyzwwr f1sip0of du4w35lb lzcic4wl abiwlrkh p8dawk7l ue3kfks5 pw54ja7n uo3d90p7 l82x9zwi')[11].click()")
    #         --assert(splash:go{"https://www.facebook.com/trituenhantao.io"})
    #         --assert(splash:wait(5))
    #         --splash:runjs("document.getElementsByClassName('oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 pq6dq46d p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl l9j0dhe7 abiwlrkh p8dawk7l dwo3fsh8 ow4ym5g4 auili1gw mf7ej076 gmql0nx0 tkr6xdv7 bzsjyuwj cb02d2ww j1lvzwm4')[11].click()")
    #         assert(splash:wait(10))
    #         splash.scroll_position = {y = 3000}
    #         assert(splash:wait(2))
    
    def start_requests(self):

        # This print step is to check whether login is successfull or not base on the HTML return that is written to homepage.html

        with open('./homepage/html/homepage.html', 'w+') as out:
            out.write('')

        # Get Facebook Account from settings.py

        acc = self.settings.get("FACEBOOK_ACCOUNT")[0]

        # Send splash request with facebook accounnt and lua script to facebook login page to get logged cookie

        yield SplashRequest(
                url="https://www.facebook.com/login",
                callback=self.parse_login,
                session_id="test",
                meta={
                    "splash": {
                        "endpoint": "execute", 
                        "args": {
                            "lua_source": self.script_login,
                            "acc": acc["account"],
                            "pwd": acc["password"],
                            "timeout": 90
                        }
                    }
                }
            )

    def parse_login(self, response):
        # Store return HTML tags to homepage.html for checking

        with open('./homepage/html/homepage.html', 'w+') as out:
            out.write(response.text)

        # Store cookie to json file

        with open("./cookies/cookie.json", 'w+') as jsonfile:
            json.dump(response.data['cookies'], jsonfile, ensure_ascii=False)
