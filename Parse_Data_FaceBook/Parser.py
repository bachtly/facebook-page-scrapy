from urllib.parse import urlparse, parse_qs   
from datetime import datetime
from copy import deepcopy
from db_config import *
import numpy as np
import lxml.html
import re

class Parser():
    
    def drop_none(new_json):
        pop_keys = []
        for i,j in new_json.items():
            if type(j) is dict: 
                new_json[i] = Parser.drop_none(new_json[i])
                j = new_json[i]
            if j is None: pop_keys+=[i]
        for i in pop_keys: new_json.pop(i, None)
        return new_json
    
    def parse_time(post):
        data_ft = eval( post.xpath('div[1]/div[1]')[0].attrib['data-ft'] )
        def unrol_dict(d):
            items = []
            for i, j in d.items():
                if type(j) is not dict: items += [(i, j)]
                else: items += [(t1,t2) for t1,t2 in unrol_dict(j).items()]
            return dict(items)
        data_ft_unrolled = unrol_dict(data_ft)
        publish_time = data_ft_unrolled['publish_time']
        # post_context = list(data_ft['page_insights'].values())[0]['post_context']
        # publish_time = post_context['publish_time']
        return datetime.fromtimestamp(publish_time)
    
    def parse_username(post):
        header_texts = post.xpath('div[1]/div[1]/div[1]/div[1]//text()')
        if not header_texts:
            header_texts = post.xpath('div[2]/div[1]/div[1]/div[1]//text()')
        return header_texts[0]

    def parse_user_id(post):
        header = post.xpath('div[1]/div[1]/div[1]/div[1]//h3[1]')
        a = header[0].xpath('*//a')
        href = a[0].attrib['href']
        parse_res = parse_qs(urlparse(href).query) 
        if 'id' in parse_res.keys():
            return parse_res['id'][0]
        return href.split('?')[0][1:] 
        # data_ft = eval( post.xpath('div[1]/div[1]')[0].attrib['data-ft'] )
        # return data_ft['content_owner_id_new']
    
    def parse_img(post):
        # from PIL import Image
        # import requests

        img_urls = post.xpath('div[1]//img')
        imgs = []
        for src in [img_tag.attrib['src'] for img_tag in img_urls]:
            try: 
                # imgs += [Image.open(requests.get(src, stream=True).raw)]
                imgs += [src]
            except: pass
        return imgs
    
    def parse_text(post):
        text_divs = post.xpath('div[1]/div[1]/div[1]/div')
        texts = [div.xpath('*//text()') for div in text_divs[1:]]
        texts = ['\n'.join(i) for i in texts if len(i)>0]
        return '\n'.join(texts)
    
    def parse_post_id(post):
        data_ft = eval( post.xpath('div[1]/div[1]')[0].attrib['data-ft'] )
        return str(data_ft['top_level_post_id'])
    
    def parse_page_id(post):
        data_ft = eval( post.xpath('div[1]/div[1]')[0].attrib['data-ft'] )
        return str(data_ft['page_id'])
    
    def parse_emotes(emote_bar):
        img_tags = emote_bar.xpath('a/img[1]')
        span_tags = emote_bar.xpath('a/span[1]')
        keys = [tag.attrib['alt'] for tag in img_tags]
        vals = [int(tag.text) for tag in span_tags]
        return dict(zip(keys, vals))
    
    def parse_cmt_username(cmt_div):
        a = cmt_div.xpath('div[1]/h3[1]/a[1]')
        username = a[0].text if a and a[0].text else ''
        return username
    
    def parse_cmt_user_id(cmt_div):
        a = cmt_div.xpath('div[1]/h3[1]/a[1]')
        if not a: return None
        
        href = a[0].attrib['href']
        parse_res = parse_qs(urlparse(href).query) 
        if 'id' in parse_res.keys():
            return parse_res['id'][0]
        return href.split('?')[0][1:]
    
    def parse_subcmt_user_id(cmt_div):
        a = cmt_div.xpath('div[1]/h3[1]/a[1]')
        if not a: return None
        
        href = a[0].attrib['href']
        parse_res = parse_qs(urlparse(href).query) 
        if 'id' in parse_res.keys():
            return parse_res['id'][0]

        return href.split('?')[0].split('/')[-1]
    
    def parse_cmt_text(cmt_div):
        text_div = cmt_div.xpath('div[1]/div[1]')
        if text_div:
            text = text_div[0].text if text_div[0].text else ''
            text += '\n'.join(text_div[0].xpath('*//text()'))
        else: text = ''
        return text
    
    def parse_cmt_id(cmt_div):
        return cmt_div.attrib['id']
    
    def parse_cmt_url(cmt_div):
        rep_bar = cmt_div.xpath('div[1]/div[3]/a')
        if not rep_bar: return None
        
        for a in rep_bar:
            href = a.attrib['href']
            if re.search(r'/replies', href): return f'https://mbasic.facebook.com/{href}'
        return None
    
    def parse_post(item):
        new_post = deepcopy(POST_OBJECT)

        src = open(item['html_path'], 'r', encoding='utf8').read()
        root = lxml.html.fromstring(src)
        
        post = root.xpath('//*[@id="m_story_permalink_view"]')[0]
        
        ### time
        new_post['fetched_time'] = datetime.fromtimestamp(item['fetched_time'])
        new_post['info']['time'] = Parser.parse_time(post)
        
        ### username - user_id
        new_post['username'] = Parser.parse_username(post)
        new_post['user_id'] = Parser.parse_user_id(post)
        
        ### images
        new_post['images'] = [np.array(img).tolist() for img in Parser.parse_img(post)]
        
        ### texts
        new_post['text'] = Parser.parse_text(post)
        
        ### post/page id
        new_post['page_id'] = item['page_id']
        new_post['post_id'] = item['post_id']
        
        ### url
        page_url = f'http://mbasic.facebook.com/groups/{new_post["page_id"]}'
        new_post['post_url'] = page_url +f'/posts/{new_post["post_id"]}'
        
        ### shares
        ### reactions
        ### comments
        return Parser.drop_none(new_post)
    
    def parse_cmt(item):
        src = open(item['html_path'], 'r', encoding='utf8').read()
        root = lxml.html.fromstring(src)
        
        cmt_divs = root.xpath('//*[@id="m_story_permalink_view"]/div[2]/div[1]/div[5]/div')
        if not cmt_divs or re.search('prev|next|actions|placeholder|sentence|composer', dict(cmt_divs[0].attrib).setdefault('id', '')):
            cmt_divs = root.xpath('//*[@id="m_story_permalink_view"]/div[2]/div[1]/div[4]/div')
        
        cmt_objs = []
        for cmt_div in cmt_divs:
            if re.search('more|next|compose|prev', dict(cmt_div.attrib).setdefault('id', '') ): continue
            new_cmt = deepcopy(COMMENT_OBJ)
            
            ### comment text
            new_cmt['text'] = Parser.parse_cmt_text(cmt_div)
            
            ### id
            new_cmt['comment_id'] = Parser.parse_cmt_id(cmt_div)
            new_cmt['page_id'] = item['page_id']
            new_cmt['post_id'] = item['post_id']
            
            ### username user_id
            new_cmt['username'] = Parser.parse_cmt_username(cmt_div)
            new_cmt['user_id'] = Parser.parse_cmt_user_id(cmt_div)
            
            ### comment url
            new_cmt['comment_url'] = Parser.parse_cmt_url(cmt_div)
            
            cmt_objs += [new_cmt]
        return [Parser.drop_none(i) for i in cmt_objs]
    
    def parse_subcmt(item):
        src = open(item['html_path'], 'r', encoding='utf8').read()
        root = lxml.html.fromstring(src)
        
        ### choose the right cmt panel
        inner_divs = root.xpath('//*[@id="root"]/div[1]/div')
        if not inner_divs: return []
        cmt_divs = None
        for inner_div in inner_divs:
            possible_cmts = inner_div.xpath('div')
            if not possible_cmts: continue
            if 'id' in dict(possible_cmts[0].attrib).keys():
                cmt_divs = possible_cmts
        
        
        if not cmt_divs: return []
        
        cmt_objs = []
        for cmt_div in cmt_divs:
            if re.search('more|next|compose|prev', dict(cmt_div.attrib).setdefault('id', '') ): continue
            new_cmt = deepcopy(COMMENT_OBJ)
            
            ### comment text
            new_cmt['text'] = Parser.parse_cmt_text(cmt_div)
            
            ### id
            new_cmt['comment_id'] = Parser.parse_cmt_id(cmt_div)
            new_cmt['page_id'] = item['page_id']
            new_cmt['post_id'] = item['post_id']
            
            ### username user_id
            new_cmt['username'] = Parser.parse_cmt_username(cmt_div)
            new_cmt['user_id'] = Parser.parse_subcmt_user_id(cmt_div)
            
            cmt_objs += [new_cmt]
        return [Parser.drop_none(i) for i in cmt_objs]
    
    def parse_reaction(item):
        src = open(item['html_path'], 'r', encoding='utf8').read()
        root = lxml.html.fromstring(src)
        emote_bar = root.xpath(
            '//*[@id="root"]/table[1]/tbody[1]/tr[1]/td[1]/div[1]/div[1]'
        )[0]
        reactions = Parser.parse_emotes(emote_bar)
        return reactions