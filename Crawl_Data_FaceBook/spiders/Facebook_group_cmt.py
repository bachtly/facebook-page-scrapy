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
from Crawl_Data_FaceBook.items import PostItem, CmtItem, ReactionItem

CR_PAGE=1
CR_POST=2
CR_COMMENT=3
CR_REACTION=4

DEBUG = SCRAPY_DEBUG
GET_BACKUP_QUEUES = False
RESET_COMMENTS = True

DB = DBUtils()

class FacebookGroupCmtSpider(scrapy.Spider):
    name = 'facebook_group_cmt'
    settings = get_project_settings()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.backup_queues_dir = './backup/cmt_queues.pkl'
        self.cookies_dir = './cookies/test'
        self.log_file = './log_cmt.txt'
        
        self.comment_urls = []
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
        }, open(self.backup_queues_dir, 'wb'))
    
    
    def get_backup_queues(self):
        df = pickle.load(open(self.backup_queues_dir, 'rb'))
        self.comment_urls = df['comment_urls']
    
    
    def gen_next_url(self):
        if len(self.comment_urls) > 0:
            self.group_id, self.post_id, self.url = self.comment_urls[0]
            self.comment_urls = self.comment_urls[1:]
            self.mode = CR_COMMENT
        else:
            self.util.log("Queues empty")
            self.url = None
            return False
        
        if self.url is None: return self.gen_next_url()
        return True
    
    
    def start_requests(self):   
        if not GET_BACKUP_QUEUES or not os.path.isfile(self.backup_queues_dir):
            posts = DB.get_post()
            for post in posts:
                if 'complete_crawl_comment' not in post['info']:
                    ### update info.complete_crawl_comment and info.comments
                    comments_full = [] if 'comments_full' not in post.keys() else post['comments_full'] or []
                    
                    info = post['info']
                    info['comments'] = len(comments_full)
                    info['complete_crawl_comment'] = False
                    info = Parser.drop_none(info)
                    
                    if not DB.update_post(post['page_id'], post['post_id'], {'info': info}):
                        self.util.log(f"[ERROR] Crawler cannot update info.complete_crawl_comment. ({post['page_id']}, {post['post_id']})")
                    completed = False
                else:
                    ### check completed
                    completed = post['info']['complete_crawl_comment'] or False
                
                if completed and not RESET_COMMENTS: continue
                ### add comment url based on current # of comments crawled
                if RESET_COMMENTS:
                    comment_url = f'https://mbasic.facebook.com/groups/{post["page_id"]}/posts/{post["post_id"]}/?p=0'
                else:
                    comment_url = f'https://mbasic.facebook.com/groups/{post["page_id"]}/posts/{post["post_id"]}/?p={post["info"]["comments"]}'
                self.comment_urls += [(post['page_id'], post['post_id'], comment_url)]
                    
            self.backup_queues()
            self.group_id, self.post_id, self.url = self.comment_urls[0]
            self.comment_urls = self.comment_urls[1:]
            self.mode = CR_COMMENT
        else:
            self.get_backup_queues()
            
            if self.gen_next_url() is False:
                return None
            
        self.util.log(f"Sleep {self.sleep_time}s before crawling . . .")
        time.sleep(self.sleep_time)
        
        yield Request(
            url=self.url,
            cookies=self.util.get_cookie(self),
            callback=self.parse,
        )


    def get_dir(self, dir):
        if not os.path.isdir(dir):
            os.makedirs(dir)
        return dir
    
    
    def get_html_cmt(self, response):
        post_dir = self.get_dir(f'./html/{self.group_id}/{self.post_id}')
        cmt_file = os.path.join(post_dir, 'comments.html')
        
        with open(cmt_file, 'w+', encoding='utf-8') as f:
            f.write(f"<!-- {self.url} -->\n{response.text}")
        
        ### next cmt page    
        cmt_objs = Parser.parse_cmt({
            'html_path': cmt_file,
            'page_id': self.group_id,
            'post_id': self.post_id
        })
        if cmt_objs:
            p = int(self.url.split('?p=')[1])
            new_url = f'https://mbasic.facebook.com/groups/{self.group_id}/posts/{self.post_id}/?p={p+10}'
            self.comment_urls += [new_url]
            
        return cmt_file


    def parse(self, response):
        ### Path to html
        ### Path to html
        if self.mode == CR_COMMENT: 
            ret_path = self.get_html_cmt(response)
            ret_items = [CmtItem()]
            self.util.log(f"Done crawling comments {self.group_id}/{self.post_id} with path {ret_path}.")

        self.util.log(f"Comment queue: {len(self.comment_urls)}")
        
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
            cookies=self.util.get_cookie(self),
            callback=self.parse,
        )