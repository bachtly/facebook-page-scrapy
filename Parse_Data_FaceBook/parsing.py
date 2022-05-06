import os
import re
import json
import copy
from tokenize import group
import lxml.html
import numpy as np
import pandas as pd
from time import time
from tqdm import tqdm
from time import sleep

from Parse_Data_FaceBook.Parser import Parser
from Parse_Data_FaceBook.config import *
# from config import LOCK


def log(s):
    if LOG: print(f'-----   {s}   -----')

def extract_post_dirs():    
    group_ids = None
    groups = [
        i for i in os.listdir(INPUT_DIR) 
        if not group_ids or i in group_ids]

    for group_id in groups:
        group_dir = os.path.join(INPUT_DIR, group_id)
        post_paths = [
            os.path.join(group_dir, 'posts', i) 
            for i in os.listdir(os.path.join(group_dir, 'posts'))]
        yield (group_id, post_paths)

def get_htmls(path, file_name=None):
    if file_name:
        src = open(os.path.join(path, file_name), 'r', encoding='utf8').read()
        return [src]
        
        
    htmls = []
    if not os.path.isdir(path): return htmls
    for f in os.listdir(path):
        f_path = os.path.join(path, f)
        if not os.path.isfile(f_path): continue
        if not re.search(r'\.html', f): continue
        src = open(f_path, 'r', encoding='utf8').read()
        htmls += [src]
    return htmls

def get_comments(cmt_parts):    
    cmt_objs = []
    cmt_divs = [div for part in cmt_parts for div in part.xpath('div')]
    for cmt_div in cmt_divs:
        if re.search('more', cmt_div.attrib['id'] ): continue
        new_cmt = copy.deepcopy(COMMENT_OBJ)
        
        ### comment text
        new_cmt['text'] = Parser.parse_cmt_text(cmt_div)
        
        ### id
        new_cmt['comment_id'] = Parser.parse_cmt_id(cmt_div)
        
        cmt_objs += [new_cmt]
    return cmt_objs

def get_post(group_id, post_id, post_path):
    new_post = copy.deepcopy(POST_OBJECT)

    src = get_htmls(post_path, post_id+'.html')[0]
    emote_src = get_htmls(post_path, 'reaction.html')[0]
    cmt_path = os.path.join(post_path, 'comments')
    cmt_srcs = get_htmls(cmt_path)
    
    root = lxml.html.fromstring(src)
    emote_root = lxml.html.fromstring(emote_src)
    cmt_roots = [lxml.html.fromstring(i) for i in cmt_srcs]
    
    post = root.xpath('''//*[@id="m_story_permalink_view"]''')[0]
    emote_bar = emote_root.xpath(
        '''//*[@id="root"]/table[1]/tbody[1]/tr[1]/td[1]/div[1]/div[1]'''
    )[0]
    cmt_parts = [
        cmt_r.xpath('''//*[@id="m_story_permalink_view"]/div[2]/div[1]/div[5]''')
        for cmt_r in [root] + cmt_roots]
    cmt_parts = [i[0] for i in cmt_parts if i]
    
    ### images
    start=time()
    new_post['images'] = [np.array(img).tolist() for img in Parser.parse_img(post)]
    TIME_OBJ['images'] += time()-start
    
    ### texts
    start=time()
    new_post['text'] = Parser.parse_text(post)
    TIME_OBJ['text'] += time()-start
    
    ### post/page id
    start=time()
    new_post['page_id'] = group_id
    new_post['post_id'] = Parser.parse_post_id(post)
    TIME_OBJ['id'] += time()-start
    
    ### url
    start=time()
    page_url = f'http://mbasic.facebook.com/groups/{new_post["page_id"]}'
    new_post['post_url'] = page_url +f'/posts/{new_post["post_id"]}'
    TIME_OBJ['text'] += time()-start
    
    ### info reactions
    start=time()
    new_post['info']['reactions'] = Parser.parse_emotes(emote_bar)
    new_post['info']['reaction_count'] = sum(
        [i for _, i in new_post['info']['reactions'].items()]
    )
    TIME_OBJ['reactions'] += time()-start
    
    ### shares
    
    ### comments
    start=time()
    new_post['comments_full'] = get_comments(cmt_parts)
    new_post['info']['comments'] = len(new_post['comments_full'])
    TIME_OBJ['comments'] += time()-start
    
    return new_post

 
def main():
    for group_id, post_paths in extract_post_dirs():
        log(f'PARSE GROUP ID = {group_id}')
        posts = [get_post(post_p) for post_p in tqdm(post_paths[10:20])] 
        json.dump(posts, open(os.path.join(OUTPUT_DIR, f'{group_id}.json'), 'w'))    
 
    log(TIME_OBJ)
 
if __name__ == "__main__":
    # main()
    pass
    