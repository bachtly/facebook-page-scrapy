from tokenize import cookie_re
import scrapy
from scrapy.http import Request
from scrapy_splash import SplashRequest
from scrapy.utils.project import get_project_settings
from Crawl_Data_FaceBook.items import CrawlData, PostItem, PostInfoItem

import os
import time
import json
import numpy as np
from datetime import datetime

group_ids = ['VietnamProjectsConstructionGROUP', 
           'tinnongbaomoi24h', 
           'tintuc2', 
           '714257262432794', 
           'tinnonghoi.vn', 
           '171952859547317', 
           '348017149108768', 
           '273257912789357', 
           'u23fanclub']
group_idx=4

class FacebookGroupSpider(scrapy.Spider):
    name = 'facebook_group'
    settings = get_project_settings()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cookies_dir = './cookies/mbasic'
        self.cookies = [
            json.load(open(os.path.join(self.cookies_dir, i), "r"))['cookies'] 
            for i in os.listdir(self.cookies_dir)]
        self.cookie_idx = np.random.randint(0, len(self.cookies))
        
        self.start_urls = []
        self.page_urls = []
        self.post_urls = []
        self.url = ''
        
        self.sleep_time = 600
        self.log_file = './log.txt'
        self.g_id = group_ids[group_idx]
        
        self.is_crawling_post = False
        self.html_page_dir = f'./homepage/html/{self.g_id}/pages'
        self.html_post_dir = f'./homepage/html/{self.g_id}/posts'
        
    def log(self, s):
        with open(self.log_file, 'a') as f:
            f.write(str(datetime.now()))
            f.write(s)
            f.write('\n')   
        
    def get_cookie(self):
        self.log(f"---------- Use cookie index {self.cookie_idx}")
        cookie = self.cookies[self.cookie_idx]
        self.cookie_idx = (self.cookie_idx + 1) % len(self.cookies)
        return cookie
    
    def start_requests(self):
        if not os.path.isdir(self.html_page_dir):
            os.makedirs(self.html_page_dir)
        if not os.path.isdir(self.html_post_dir):
            os.makedirs(self.html_post_dir)
        
        self.start_urls += [f"https://mbasic.facebook.com/{self.g_id}"]
        
        url = self.start_urls[0]
            
        self.log(f"---------- Sleeping {self.sleep_time}s before crawling . . .")
        time.sleep(self.sleep_time)
        
        self.url = url
        yield Request(
            url=url,
            cookies=self.get_cookie(),
            callback=self.parse,
        )

    def parse(self, response):
        ### Save html
        if self.is_crawling_post:
            file_index = len(os.listdir(self.html_post_dir))
            new_file_name = format(file_index, '06d') + '.html'
            with open(os.path.join(self.html_post_dir, new_file_name), 'w+', encoding='utf-8') as out:
                url_text_line = f"<!-- {self.url} -->\n"
                out.write(url_text_line)
                out.write(response.text)
                self.log(f"---------- Save post to {os.path.join(self.html_post_dir, new_file_name)}")
        else:
            file_index = len(os.listdir(self.html_page_dir))
            new_file_name = format(file_index, '06d') + '.html'
            with open(os.path.join(self.html_page_dir, new_file_name), 'w+', encoding='utf-8') as out:
                url_text_line = f"<!-- {self.url} -->\n"
                out.write(url_text_line)
                out.write(response.text)
                self.log(f"---------- Save page to {os.path.join(self.html_page_dir, new_file_name)}")

        ### If crawling page, add more post and page urls
        if not self.is_crawling_post:
            root = scrapy.Selector(response)

            ### add post urls
            posts = root.xpath("""//*[@id="structured_composer_async_container"]/div[1]/div[1]/div[1]/div""")
            for post in posts:
                more = post.xpath("""div[1]/div[2]/div[1]/span[1]/a""")
                if len(more)>0:
                    href = more[0].attrib["href"]
                    self.post_urls += [f"https://mbasic.facebook.com{href}"]
                    
            ### add nextpage url
            more_page = root.xpath("""//*[@id="structured_composer_async_container"]/div[2]/a""")    
            if more_page:
                href = more_page.attrib["href"]
                self.page_urls += [f"https://mbasic.facebook.com{href}"]


        self.log("---------- Length of queues")
        self.log(f"Post queue: {len(self.post_urls)}")
        self.log(f"Page queue: {len(self.page_urls)}")
        
        if len(self.post_urls) > 0:
            self.url = self.post_urls[-1]
            self.post_urls = self.post_urls[:-1]
            self.is_crawling_post = True
        elif len(self.page_urls) > 0:
            self.url = self.page_urls[-1]
            self.page_urls = self.page_urls[:-1]
            self.is_crawling_post = False
        else:
            self.log("---------- Queues empty")
            yield None
            
        self.log(f"---------- Sleeping {self.sleep_time}s before crawling . . .")
        time.sleep(self.sleep_time)

        yield Request(
            url=self.url,
            cookies=self.get_cookie(),
            callback=self.parse,
        )



