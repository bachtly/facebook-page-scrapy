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

CR_PAGE=1
CR_POST=2
CR_COMMENT=3
CR_REACTION=4

DEBUG = SCRAPY_DEBUG
GET_BACKUP_QUEUES = True

class FacebookGroupReactionSpider(scrapy.Spider):
    name = 'facebook_group_reaction'
    settings = get_project_settings()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cookies_dir = './cookies/mbasic'
        self.cookies_name = [
            i for i in os.listdir(self.cookies_dir) 
            if i not in ['chanvo.json', 'quangtran.json'] ]
        self.cookies = [
            json.load(open(os.path.join(self.cookies_dir, i), "r"))['cookies'] 
            for i in self.cookies_name]
        self.cookie_idx = np.random.randint(0, len(self.cookies))
        
        self.page_urls = []
        self.post_urls = []
        self.comment_urls = []
        self.reaction_urls = []
        self.url = ''
        
        self.group_id = ''
        self.post_id = ''
        
        self.sleep_time = SLEEP_TIME
        self.log_file = './log.txt'
        # self.index_file = 'index.csv'
        
        self.mode = CR_PAGE
        
    def log(self, s):
        if not DEBUG: return 
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f'{str(datetime.now())}: {s}\n')
        
    def get_cookie(self):
        self.log(f"Use cookie {self.cookies_name[self.cookie_idx]}")
        cookie = self.cookies[self.cookie_idx]
        self.cookie_idx = (self.cookie_idx + 1) % len(self.cookies)
        return cookie     
    
    def backup_queues(self):
        pickle.dump({
            'page_urls': self.page_urls,
            'post_urls': self.post_urls,
            'comment_urls': self.comment_urls,
            'reaction_urls': self.reaction_urls
        }, open('backup/queues.pkl', 'wb'))
    
    def get_backup_queues(self):
        df = pickle.load(open('backup/queues.pkl', 'rb'))
        self.page_urls = df['page_urls']
        self.post_urls = df['post_urls']
        self.reaction_urls = df['reaction_urls']
        self.comment_urls = df['comment_urls']
    
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

            while self.url is None:
                if self.gen_next_url() is False:
                    return None
            
        self.log(f"Sleep {self.sleep_time}s before crawling . . .")
        time.sleep(self.sleep_time)
        
        yield Request(
            url=self.url,
            cookies=self.get_cookie(),
            callback=self.parse,
        )

    def gen_next_url(self):
        if len(self.reaction_urls) > 0:
            self.group_id, self.post_id, self.url = self.reaction_urls[0]
            self.reaction_urls = self.reaction_urls[1:]
            self.mode = CR_REACTION
        elif len(self.comment_urls) > 0:
            self.group_id, self.post_id, self.url = self.comment_urls[0]
            self.comment_urls = self.comment_urls[1:]
            self.mode = CR_COMMENT
        elif len(self.post_urls) > 0:
            self.group_id, self.url = self.post_urls[0]
            self.post_urls = self.post_urls[1:]
            self.mode = CR_POST
        elif len(self.page_urls) > 0:
            self.group_id, self.url = self.page_urls[0]
            self.page_urls = self.page_urls[1:]
            self.mode = CR_PAGE
        else:
            self.log("Queues empty")
            self.url = None
            return False
            
        return True

    def get_dir(self, dir):
        if not os.path.isdir(dir):
            os.makedirs(dir)
        return dir

    def get_html_page(self, response):
        page_dir = self.get_dir(f'./html/{self.group_id}')
        # page_file = os.path.join(page_dir, 'pages.txt')
        html_file = os.path.join(page_dir, 'page.html')
        # self.log(f"Save url {self.url} to {page_file}")
        # with open(page_file, 'a') as f:
        #     f.write(f'{self.url}\n')
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(response.text)

        root = scrapy.Selector(response)
        ### add post urls
        posts = root.xpath('//*[@id="m_group_stories_container"]/div[1]/div')
        if not posts: return None
        for post in posts:
            more = post.xpath('div')[-1]
            more = more.xpath('div[2]/a')
            if more:
                hrefs = [i.attrib["href"] for i in more 
                         if re.search(r'^https://mbasic.facebook', i.attrib["href"])]
                self.post_urls += [(self.group_id, hrefs[0])]
                
        ### add nextpage url
        more_page = root.xpath("""//*[@id="m_group_stories_container"]/div[2]/a""")    
        if more_page:
            href = more_page[0].attrib["href"]
            self.page_urls += [(self.group_id, f"https://mbasic.facebook.com{href}")]


    def get_html_post(self, response):
        # if self.post_id: self.check_complete_crawl()
        
        posts_dir = self.get_dir(f'./html/{self.group_id}/posts')
        root = scrapy.Selector(response)
        post = root.xpath('''//*[@id="m_story_permalink_view"]''')
        if post: post = post[0]
        else: return None
        data_ft = eval( post.xpath('''div[1]/div[1]''')[0].attrib['data-ft'] )
        self.post_id = str(int(data_ft['top_level_post_id']))
        
        post_dir = self.get_dir(os.path.join(posts_dir, self.post_id))
        post_file = os.path.join(post_dir, self.post_id + '.html')
        
        with open(post_file, 'w+', encoding='utf-8') as f:
            f.write(f"<!-- {self.url} -->\n{response.text}")
            self.log(f"Save post to {post_file}")
        
        ### get reactions link
        # reactions = root.xpath("""//*[@id="m_story_permalink_view"]/div[2]/div[1]/div[3]/a[1]""")
        # if reactions:
        #     href = reactions[0].attrib["href"].split('&')[0]
        #     self.reaction_urls += [(self.group_id, self.post_id, f"https://mbasic.facebook.com{href}")]
            
        ### get comments link
        # div_comments = root.xpath("""//*[@id="m_story_permalink_view"]/div[2]/div[1]/div[5]/div""")
        # comments = None if not div_comments else div_comments[-1].xpath("""a[1]""")
        # attrib_d = '' if not comments else dict(comments[0].attrib)
        # if not comments or re.search('see_next', attrib_d.setdefault('id', '')):
        #     div_comments = root.xpath("""//*[@id="m_story_permalink_view"]/div[2]/div[1]/div[4]/div""")
        #     comments = None if not div_comments else div_comments[-1].xpath("""a[1]""")
        
        # if comments:
        #     href = comments[0].attrib["href"].split('&')[0]
        #     self.comment_urls += [(self.group_id, self.post_id, href)]
            
        return post_file
    
    def get_html_comment(self, response):
        posts_dir = self.get_dir(f'./html/{self.group_id}/posts')
        post_dir = os.path.join(posts_dir, self.post_id)
        
        comment_dir = self.get_dir(os.path.join(post_dir, 'comments'))
            
        file_index = len(os.listdir(comment_dir))
        comment_file = os.path.join(comment_dir, format(file_index, '06d') + '.html')
        
        with open(comment_file, 'w+', encoding='utf-8') as f:
            f.write(f"<!-- {self.url} -->\n{response.text}")
            self.log(f"Save comment to {comment_file}")
            
        ### get comments link
        root = scrapy.Selector(response)
        div_comments = root.xpath("""//*[@id="m_story_permalink_view"]/div[2]/div[1]/div[5]/div""")
        comments = None if not div_comments else div_comments[-1].xpath("""a[1]""")
        attrib_d = '' if not comments else dict(comments[0].attrib)
        if not comments or re.search('see_next', attrib_d.setdefault('id', '')):
            div_comments = root.xpath("""//*[@id="m_story_permalink_view"]/div[2]/div[1]/div[4]/div""")
            comments = None if not div_comments else div_comments[-1].xpath("""a[1]""")
        
        if comments:
            href = comments[0].attrib["href"].split('&')[0]
            self.comment_urls += [(self.group_id, self.post_id, href)]
        
        return comment_file
    
    
    def get_html_reaction(self, response):
        posts_dir = self.get_dir(f'./html/{self.group_id}/posts')
        post_dir = os.path.join(posts_dir, self.post_id)
            
        reaction_file = os.path.join(post_dir, 'reaction.html')
        
        with open(reaction_file, 'w+', encoding='utf-8') as f:
            f.write(f"<!-- {self.url} -->\n{response.text}")
            self.log(f"Save reaction to {reaction_file}")
            
        return reaction_file

    def parse(self, response):
        ### Save html
        if self.mode == CR_POST: 
            ret_path = self.get_html_post(response)
            ret_items = [PostItem(), CmtItem()]
        elif self.mode == CR_REACTION: 
            ret_path = self.get_html_reaction(response)
            ret_items = [ReactionItem()]
        elif self.mode == CR_COMMENT: 
            ret_path = self.get_html_comment(response)
            ret_items = [CmtItem()]
        elif self.mode == CR_PAGE: ret_path = self.get_html_page(response)

        self.log(f"Post | Page | Reaction | Comment queue: {len(self.post_urls)} | {len(self.page_urls)} | {len(self.reaction_urls)}| {len(self.comment_urls)}")
        
        if ret_path:
            for ret_item in ret_items:
                ret_item['fetched_time'] = datetime.timestamp(datetime.now())
                ret_item['html_path'] = ret_path
                ret_item['page_id'] = self.group_id
                ret_item['post_id'] = self.post_id
                yield ret_item
        self.backup_queues()
        
        if self.gen_next_url() is False:
            return None

        while self.url is None:
            if self.gen_next_url() is False:
                return None
            
        self.log(f"Sleeping {self.sleep_time}s before crawling . . .")
        time.sleep(self.sleep_time)

        yield Request(
            url=self.url,
            cookies=self.get_cookie(),
            callback=self.parse,
        )



