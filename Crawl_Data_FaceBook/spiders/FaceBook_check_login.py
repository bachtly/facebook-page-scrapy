import scrapy
from scrapy.utils.project import get_project_settings
from scrapy_splash import SplashRequest
import json
import os


class FacebookCheckLoginSpider(scrapy.Spider):
    name = 'FaceBook_check_login'

    def __init__(self, user_id='', **kwargs):
        self.user_id = user_id
        super().__init__(**kwargs)

    # This will setup settings variable to get constant from settings.py

    settings = get_project_settings()

    # Lua script to interact with js in the website while crawling

    script_login = """
        function main(splash, args)
            splash:init_cookies(splash.args.cookies)
            assert(splash:go{
                splash.args.url,
                headers=splash.args.headers
            })
            assert(splash:wait(5))
            splash:set_viewport_full()
            local not_login = false
            
            local element = splash:select('input[name=pass]')
            if element ~= nil then not_login = true end
            local entries = splash:history()
            local last_response = entries[#entries].response
            return {
                not_login_status = not_login,
                html = splash:html()
            }
        end
    """
    
    def start_requests(self):

        # Send splash request with facebook cookie and lua script to check if cookie is logged in or not

        try:
            with open('./cookies/cookie_1.json', 'r') as jsonfile:
                cookies = json.load(jsonfile)["cookies"]

                if os.path.exists("./cookies/cookie.txt"):
                    os.remove("./cookies/cookie.txt")
               

                yield SplashRequest(
                    url="https://www.facebook.com/login",
                    callback=self.parse_login,
                    session_id="test",
                    meta={
                        "splash": {
                            "endpoint": "execute", 
                            "args": {
                                "lua_source": self.script_login,
                                "cookies": cookies,
                                "timeout": 90
                            }
                        }
                    }
                )

        except Exception as e:
            print('invalid json: %s' % e)
            os.remove("./cookies/cookie_1.json")

    def parse_login(self, response):

        # If login is fail, delete cookie and ask for new one

        with open('./homepage/html/homepage.html', 'w+') as out:
            out.write(response.text)

        if (response.data['not_login_status']):
            os.remove("./cookies/cookie_1.json")
        else:
            with open("./cookies/cookie.txt", 'w+') as f:
                f.write("1")
