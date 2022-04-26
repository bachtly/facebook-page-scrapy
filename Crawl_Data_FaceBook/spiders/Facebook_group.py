import scrapy
from scrapy.http import Request
from scrapy.utils.project import get_project_settings

import os
import re
import time
import json
import numpy as np
from datetime import datetime

group_ids = ['VietnamProjectsConstructionGROUP', 
           'tinnonghoi.vn', 
           'tinnongbaomoi24h', 
           'tintuc2', 
           '714257262432794', 
           '171952859547317', 
           '348017149108768', 
           '273257912789357', 
           'u23fanclub']
group_idx=4

CR_PAGE=1
CR_POST=2
CR_COMMENT=3
CR_REACTION=4

class FacebookGroupSpider(scrapy.Spider):
    name = 'facebook_group'
    settings = get_project_settings()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cookies_dir = './cookies/mbasic'
        self.cookies_name = [ i for i in os.listdir(self.cookies_dir) if i not in ['chanvo.json', 'quangtran.json'] ]
        self.cookies = [json.load(open(os.path.join(self.cookies_dir, i), "r"))['cookies'] for i in self.cookies_name]
        self.cookie_idx = np.random.randint(0, len(self.cookies))
        
        self.start_urls = []
        self.page_urls = []
        self.post_urls = []
        self.comment_urls = []
        self.reaction_urls = []
        self.url = ''
        self.crt_post_idx = 0
        
        self.sleep_time = 30
        self.log_file = './log.txt'
        self.g_id = group_ids[group_idx]
        
        self.obj_crawling = CR_PAGE
        self.html_post_dir = f'./homepage/html/{self.g_id}/posts'
        self.html_page_file = f'./homepage/html/{self.g_id}/pages.txt'
        
    def log(self, s):
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(str(datetime.now()))
            f.write(s)
            f.write('\n')   
        
    def get_cookie(self):
        self.log(f"---------- Use cookie {self.cookies_name[self.cookie_idx]}")
        cookie = self.cookies[self.cookie_idx]
        self.cookie_idx = (self.cookie_idx + 1) % len(self.cookies)
        return cookie     
    
    def start_requests(self):
        if not os.path.isdir(self.html_post_dir):         
            os.makedirs(self.html_post_dir)
        
        self.start_urls += [f"https://mbasic.facebook.com/groups/{self.g_id}"]
        # self.start_urls += ['https://mbasic.facebook.com/groups/714257262432794?bacr=1645354766%3A1273891376469377%3A1273891376469377%2C0%2C39%3A7%3AKw%3D%3D&multi_permalinks&refid=18']
                            
        url = self.start_urls[0]
            
        self.log(f"---------- Sleeping {self.sleep_time}s before crawling . . .")
        time.sleep(self.sleep_time)
        
        self.url = url
        yield Request(
            url=url,
            cookies=self.get_cookie(),
            callback=self.parse,
        )

    def get_html_page(self, response):
        self.log(f"---------- Save url {self.url} to {self.html_page_file}")
        with open(self.html_page_file, 'a') as f:
            f.write(self.url)
            f.write('\n') 
        with open(self.html_page_file[:-3]+'html', 'w', encoding='utf-8') as f:
            f.write(response.text)

        root = scrapy.Selector(response)
        ### add post urls
        posts = root.xpath("""//*[@id="m_group_stories_container"]/div[1]/div""")
        for post in posts:
            more = post.xpath("""div""")[-1]
            more = more.xpath("""div[2]/a""")
            if more:
                hrefs = [i.attrib["href"] for i in more 
                         if re.search(r'^https://mbasic.facebook', i.attrib["href"])]
                self.post_urls += [hrefs[0]]
                
        ### add nextpage url
        more_page = root.xpath("""//*[@id="m_group_stories_container"]/div[2]/a""")    
        if more_page:
            href = more_page[0].attrib["href"]
            self.page_urls += [f"https://mbasic.facebook.com{href}"]


    def get_html_post(self, response):
        file_index = len(os.listdir(self.html_post_dir))
        self.crt_post_idx = file_index
            
        post_dir = os.path.join(self.html_post_dir, format(file_index, '06d'))
        if not os.path.isdir(post_dir):
            os.makedirs(post_dir)
        post_file = os.path.join(post_dir, format(file_index, '06d') + '.html')
        
        with open(post_file, 'w+', encoding='utf-8') as f:
            url_text_line = f"<!-- {self.url} -->\n"
            f.write(url_text_line)
            f.write(response.text)
            self.log(f"---------- Save post to {post_file}")
            
        root = scrapy.Selector(response)
        
        ### get reactions link
        reactions = root.xpath("""//*[@id="m_story_permalink_view"]/div[2]/div[1]/div[3]/a[1]""")
        if reactions:
            href = reactions[0].attrib["href"].split('&')[0]
            self.reaction_urls += [f"https://mbasic.facebook.com{href}"]
            
        ### get comments link
        div_comments = root.xpath("""//*[@id="m_story_permalink_view"]/div[2]/div[1]/div[5]/div""")
        comments = None if not div_comments else div_comments[-1].xpath("""a[1]""")
        attrib_d = '' if not comments else dict(comments[0].attrib)
        if not comments or re.search('see_next', attrib_d.setdefault('id', '')):
            div_comments = root.xpath("""//*[@id="m_story_permalink_view"]/div[2]/div[1]/div[4]/div""")
            comments = None if not div_comments else div_comments[-1].xpath("""a[1]""")
        
        if comments:
            href = comments[0].attrib["href"].split('&')[0]
            self.comment_urls += [href]
            
    
    def get_html_comment(self, response):
        post_index = self.crt_post_idx
        post_dir = os.path.join(self.html_post_dir, format(post_index, '06d'))
        
        comment_dir = os.path.join(post_dir, 'comments')
        if not os.path.isdir(comment_dir):
            os.makedirs(comment_dir)
        file_index = len(os.listdir(comment_dir))
        comment_file = os.path.join(comment_dir, format(file_index, '06d') + '.html')
        
        with open(comment_file, 'w+', encoding='utf-8') as f:
            url_text_line = f"<!-- {self.url} -->\n"
            f.write(url_text_line)
            f.write(response.text)
            self.log(f"---------- Save comment to {comment_file}")
            
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
            self.comment_urls += [href]
    
    
    def get_html_reaction(self, response):
        post_index = self.crt_post_idx
        post_dir = os.path.join(self.html_post_dir, format(post_index, '06d'))
        reaction_dir = os.path.join(post_dir, 'reaction')
        if not os.path.isdir(reaction_dir):
            os.makedirs(reaction_dir)
        file_index = len(os.listdir(reaction_dir))
        reaction_file = os.path.join(reaction_dir, format(file_index, '06d') + '.html')
        with open(reaction_file, 'w+', encoding='utf-8') as f:
            url_text_line = f"<!-- {self.url} -->\n"
            f.write(url_text_line)
            f.write(response.text)
            self.log(f"---------- Save reaction to {reaction_file}")

    def parse(self, response):
        ### Save html
        if self.obj_crawling == CR_POST: self.get_html_post(response)
        elif self.obj_crawling == CR_REACTION: self.get_html_reaction(response)
        elif self.obj_crawling == CR_COMMENT: self.get_html_comment(response)
        elif self.obj_crawling == CR_PAGE: self.get_html_page(response)

        self.log(f"---------- Post | Page | Reaction | Comment queue: {len(self.post_urls)} | {len(self.page_urls)} | {len(self.reaction_urls)}| {len(self.comment_urls)}")
        
        if len(self.reaction_urls) > 0:
            self.url = self.reaction_urls[-1]
            self.reaction_urls = self.reaction_urls[:-1]
            self.obj_crawling = CR_REACTION
        elif len(self.comment_urls) > 0:
            self.url = self.comment_urls[-1]
            self.comment_urls = self.comment_urls[:-1]
            self.obj_crawling = CR_COMMENT
        elif len(self.post_urls) > 0:
            self.url = self.post_urls[-1]
            self.post_urls = self.post_urls[:-1]
            self.obj_crawling = CR_POST
        elif len(self.page_urls) > 0:
            self.url = self.page_urls[-1]
            self.page_urls = self.page_urls[:-1]
            self.obj_crawling = CR_PAGE
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



