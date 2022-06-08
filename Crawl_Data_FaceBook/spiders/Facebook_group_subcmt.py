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
from DatabaseUtils.DBUtils import DBUtils
from Parse_Data_FaceBook.Parser import Parser
from Crawl_Data_FaceBook.utils import ScrapyUtils
from Crawl_Data_FaceBook.items import PostItem, CmtItem, ReactionItem, SubcmtItem

CR_PAGE=1
CR_POST=2
CR_COMMENT=3
CR_REACTION=4

DEBUG = SCRAPY_DEBUG
GET_BACKUP_QUEUES = False
RESET_COMMENTS = False

DB = DBUtils()

class FacebookGroupSubCmtSpider(scrapy.Spider):
    name = 'facebook_group_subcmt'
    settings = get_project_settings()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.backup_queues_dir = './backup/subcmt_queues.pkl'
        self.cookies_dir = './cookies/test'
        self.log_file = './log_subcmt.txt'
        
        self.comment_id = ''
        self.comment_urls = []
        self.comment_queues = {}
        self.url = ''
        
        self.group_id = ''
        self.post_id = ''
        
        self.sleep_time = SLEEP_TIME
        self.mode = CR_COMMENT
        
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
            'comment_urls': self.comment_urls,
            'comment_queues': self.comment_queues
        }, open(self.backup_queues_dir, 'wb'))
    
    
    def get_backup_queues(self):
        df = pickle.load(open(self.backup_queues_dir, 'rb'))
        self.comment_urls = df['comment_urls']
        self.comment_queues = df['comment_queues']
    
    
    def gen_next_url(self):
        if sum([len(j) for i,j in self.comment_queues.items()])==0: return None
        
        cookie = self.util.get_cookie(self)
        cookie_name = self.util.cookie_name
        
        while len(self.comment_queues[cookie_name]) == 0: 
            cookie = self.util.get_cookie(self)
            cookie_name = self.util.cookie_name

        self.group_id, self.post_id, self.comment_id, self.url = self.comment_queues[cookie_name][0]
        self.comment_queues[cookie_name] = self.comment_queues[cookie_name][1:]
        self.mode = CR_COMMENT
        
        if self.url is None: return self.gen_next_url()
        return cookie
    
    
    def start_requests(self):   
        if not GET_BACKUP_QUEUES or not os.path.isfile(self.backup_queues_dir):
            cmts = DB.get_cmt()
            for cmt in cmts:
                if 'comment_url' not in cmt.keys(): continue
                if 'complete_crawl_comment' not in cmt['info'].keys():
                    ### update info.complete_crawl_comment and info.comments
                    comments_full = [] if 'comments_full' not in cmt.keys() else cmt['comments_full'] or []
                    
                    info = cmt['info']
                    info['comments'] = len(comments_full)
                    info['complete_crawl_comment'] = False
                    info = Parser.drop_none(info)
                    
                    if not DB.update_cmt(cmt['page_id'], cmt['post_id'], cmt['comment_id'], {'info': info}):
                        self.util.log(f"[ERROR] Crawler cannot update info.complete_crawl_comment. ({cmt['page_id']}, {cmt['post_id']}, {cmt['comment_id']})")
                    completed = False
                else:
                    ### check completed
                    completed = cmt['info']['complete_crawl_comment'] or False
                
                if completed and not RESET_COMMENTS: continue
                
                ### add cmt_url to queue
                try:
                    cookie = cmt['cookie']
                    self.comment_queues[cookie] = self.comment_queues.setdefault(cookie, []) + [(cmt['page_id'], cmt['post_id'], cmt['comment_id'], cmt['comment_url'])]
                except:
                    self.util.log(f'[ERROR] Object do not have cookie {cmt}')
                     
            self.backup_queues()
        else:
            self.get_backup_queues()
            
        cookie = self.gen_next_url()
        if cookie is None:
            return None
        self.util.log(f"Sleep {self.sleep_time}s before crawling . . .")
        time.sleep(self.sleep_time)
        
        yield Request(
            url=self.url,
            cookies=self.util.cookie,
            callback=self.parse,
        )

    
    def get_html_subcmt(self, response):
        ### What to do here
        ### 2. Gen new url with "view_older_cmts"
        ### 3. Return file for pipeline to crawl subcmt
        
        post_dir = self.util.get_dir(f'./html/{self.group_id}/{self.post_id}')
        cmt_file = os.path.join(post_dir, 'sub_comments.html')
        
        self.util.log(f"!@# Current id {self.comment_id}")
        self.util.log(f"!@# Current url {self.url}")
        self.util.log(f"!@# Current cookie {self.util.cookie_name}")
        
        with open(cmt_file, 'w+', encoding='utf-8') as f:
            f.write(f"<!-- {self.url} -->\n{response.text}")
        
        subcmt_objs = Parser.parse_subcmt({
            'html_path': cmt_file,
            'page_id': self.group_id,
            'post_id': self.post_id,
            'comment_id': self.comment_id
        })
        
        ### view_previous_cmts
        self.util.log(f"!@# Have {len(subcmt_objs)} subcmt")
        if subcmt_objs:
            root = scrapy.Selector(response)
            cmt_divs = root.xpath('//*[@id="root"]/div[1]/div[2]/div[1]')   
            if cmt_divs and 'id' in dict(cmt_divs[0].attrib).keys() and re.search('more', cmt_divs[0].attrib['id']): 
                a = cmt_divs[0].xpath('a')
                if a:
                    href = a.attrib['href']
                    self.comment_queues[self.util.cookie_name] = [(self.group_id, self.post_id, self.comment_id, href)] + self.comment_queues[self.util.cookie_name]
        else:
            ### update complete crawl comment = True
            cmt = DB.get_cmt(self.group_id, self.post_id,self.comment_id)
            comments_full = [] if 'comments_full' not in cmt.keys() else cmt['comments_full'] or []
            if cmt:
                info = cmt['info']
                info['comments'] = len(comments_full)
                info['complete_crawl_comment'] = True
                info = Parser.drop_none(info)
                if not DB.update_cmt(self.group_id, self.post_id, self.comment_id, 
                    {'info': info}):
                    self.util.log(f"[ERROR] Cannot update comment info. ({self.group_id}, {self.post_id}, {self.comment_id})")
        
        return cmt_file


    def parse(self, response):
        self.util.log("")
        
        ### Path to html
        if self.mode == CR_COMMENT: 
            ret_path = self.get_html_subcmt(response)
            ret_items = [SubcmtItem()]
            self.util.log(f"Done crawling comments {self.group_id}/{self.post_id} with path {ret_path}.")

        self.util.log(f"Comment urls, queues: {len(self.comment_urls)}, {[len(j) for _, j in self.comment_queues.items()]}")
        
        ### Return Item
        if ret_path:
            for ret_item in ret_items:
                ret_item['fetched_time'] = datetime.timestamp(datetime.now())
                ret_item['html_path'] = ret_path
                ret_item['page_id'] = self.group_id
                ret_item['post_id'] = self.post_id
                ret_item['comment_id'] = self.comment_id
                ret_item['cookie'] = self.util.cookie_name
                yield ret_item
        self.backup_queues()
        
        ### Gen next url to crawl
        if self.gen_next_url() is None:
            return None
            
        self.util.log(f"Sleeping {self.sleep_time}s before crawling . . .")
        time.sleep(self.sleep_time)

        yield Request(
            url=self.url,
            cookies=self.util.cookie,
            callback=self.parse,
        )