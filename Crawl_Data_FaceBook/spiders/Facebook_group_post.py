import scrapy
from scrapy.http import Request
from scrapy.utils.project import get_project_settings

import os
import re
import time
import json
import pickle
import numpy as np
from datetime import datetime

from db_config import *
from scrapy_config import *
from Crawl_Data_FaceBook.items import PostItem, CmtItem, ReactionItem
from Crawl_Data_FaceBook.utils import ScrapyUtils
from DatabaseUtils.DBUtils import DBUtils

CR_PAGE=1
CR_POST=2
CR_COMMENT=3
CR_REACTION=4

DEBUG = SCRAPY_DEBUG
GET_BACKUP_QUEUES = True      

class FacebookGroupPostSpider(scrapy.Spider):
    name = 'facebook_group_post'
    settings = get_project_settings()
    
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.backup_queues_dir = './backup/queues.pkl'
        self.cookies_dir = './cookies/post'
        self.log_file = './log.txt'
        
        self.page_urls, self.post_urls = [], []
        self.url = ''
        
        self.group_id = ''
        self.post_id = ''
        
        self.sleep_time = SLEEP_TIME
        self.mode = CR_PAGE
        
        self.util = ScrapyUtils(
            log_file = self.log_file,
            DEBUG = DEBUG, 
            cookies_dir = self.cookies_dir
        )
    
    
    def handle_cookies_blocked(self):
        pass
    
    
    def is_cookies_blocked(self, root):
        is_blocked = False
        if is_blocked: self.handle_cookies_blocked()
        return is_blocked
    
    
    def backup_queues(self):
        pickle.dump({
            'page_urls': self.page_urls,
            'post_urls': self.post_urls,
        }, open(self.backup_queues_dir, 'wb'))
    
    
    def get_backup_queues(self):
        df = pickle.load(open(self.backup_queues_dir, 'rb'))
        self.page_urls = df['page_urls']
        self.post_urls = df['post_urls']
    
    
    def gen_next_url(self):
        if len(self.post_urls) > 0:
            self.group_id, self.url = self.post_urls[0]
            self.post_urls = self.post_urls[1:]
            self.mode = CR_POST
        elif len(self.page_urls) > 0:
            self.group_id, self.url = self.page_urls[0]
            self.page_urls = self.page_urls[1:]
            self.mode = CR_PAGE
        else:
            self.util.log("Queues empty")
            self.url = None
            return False
        
        if self.url is None: return self.gen_next_url()
        return True
    
    
    def start_requests(self):           
        if not GET_BACKUP_QUEUES or not os.path.isfile('backup/queues.pkl'):
            self.page_urls += [
                (g_id, f"https://mbasic.facebook.com/groups/{g_id}")
                for g_id in GROUP_IDS]   
            self.backup_queues()
            self.group_id, self.url = self.page_urls[0]
            self.page_urls = self.page_urls[1:]     
            self.mode = CR_PAGE   
        else:
            self.get_backup_queues()
            self.reaction_urls = []
            self.comment_urls = []
            
            if self.gen_next_url() is False:
                return None
            
        self.util.log(f"Sleep {self.sleep_time}s before crawling . . .")
        time.sleep(self.sleep_time)
        
        yield Request(
            url=self.url,
            cookies=self.util.get_cookie(),
            callback=self.parse,
        )

    def get_html_page(self, response):
        page_dir = self.util.get_dir(f'./html/{self.group_id}')
        page_file = os.path.join(page_dir, 'pages.txt')
        with open(page_file, 'a') as f:
            f.write(f'{self.url}\n')

        root = scrapy.Selector(response)
        if self.is_cookies_blocked(root): return None
        
        ### add post urls
        posts = root.xpath('//*[@id="m_group_stories_container"]/div[1]/div')
        if not posts: return None
        for post in posts:
            ### Get post_id
            try: 
                data_ft = eval(post.attrib['data-ft'] )
                post_id = str(int(data_ft['top_level_post_id']))
            except: 
                self.util.log(f'[ERROR] Cannot get post_id from data-ft (page)) ({self.page_id}).')
                continue
            
            ### Check post existed in db
            if DBUtils().post_exist(self.group_id, post_id): continue
            
            ### Add posts to crawl 
            more = post.xpath('div')
            if not more: continue   
            
            more = more[-1].xpath('div[2]/a')
            if not more: continue
            
            hrefs = [
                i.attrib["href"] for i in more 
                if re.search(r'^https://mbasic.facebook', i.attrib["href"])]
            self.post_urls += [(self.group_id, hrefs[0])]
                
        ### add nextpage url
        more_page = root.xpath("""//*[@id="m_group_stories_container"]/div[2]/a""")    
        if more_page:
            href = more_page[0].attrib["href"]
            self.page_urls += [(self.group_id, f"https://mbasic.facebook.com{href}")]


    def get_html_post(self, response):
        root = scrapy.Selector(response)
        post = root.xpath('//*[@id="m_story_permalink_view"]')
        if not post: return None

        article = post[0].xpath('div[1]/div[1]')
        if not article: return None
        
        try: 
            data_ft = eval( article[0].attrib['data-ft'] )
            self.post_id = str(int(data_ft['top_level_post_id']))
        except: 
            self.util.log(f'[ERROR] Cannot get post_id from data-ft of (page,post)) ({self.page_id}, {self.post_id}).')
            return None
        
        post_dir = self.util.get_dir(f'./html/{self.group_id}')
        post_file = os.path.join(post_dir, 'post.html')
        
        with open(post_file, 'w+', encoding='utf-8') as f:
            f.write(f"<!-- {self.url} -->\n{response.text}")
            
        return post_file


    def parse(self, response):
        ### Path to html
        if self.mode == CR_POST: 
            ret_path = self.get_html_post(response)
            ret_items = [PostItem(), CmtItem()]
            self.util.log(f"Done crawling post {self.group_id}/{self.post_id} with path {ret_path}.")
        elif self.mode == CR_PAGE: 
            ret_path = self.get_html_page(response)
            self.util.log(f"Done crawling page {self.group_id} with path {ret_path}.")

        self.util.log(f"Post | Page queues: {len(self.post_urls)} | {len(self.page_urls)}")
        
        ### Return Item
        if ret_path:
            for ret_item in ret_items:
                ret_item['fetched_time'] = datetime.timestamp(datetime.now())
                ret_item['html_path'] = ret_path
                ret_item['page_id'] = self.group_id
                ret_item['post_id'] = self.post_id
                yield ret_item
        self.backup_queues()
        
        ### Gen next url to crawl
        if self.gen_next_url() is False:
            return None
            
        self.util.log(f"Sleeping {self.sleep_time}s before crawling . . .")
        time.sleep(self.sleep_time)

        yield Request(
            url=self.url,
            cookies=self.util.get_cookie(),
            callback=self.parse,
        )