import json
import pymongo
from pprint import pprint
from datetime import datetime

from db_config import *
from itemadapter import ItemAdapter
from Crawl_Data_FaceBook.items import PostItem, CmtItem, ReactionItem
from Parse_Data_FaceBook.Parser import Parser
from DatabaseUtils.DBUtils import DBUtils

DEBUG = DB_DEBUG

DB = DBUtils()

def log(s):
    if not DEBUG: return
    with open('log.txt', 'a', encoding='utf-8') as f:
        f.write(f'{str(datetime.now())}: {s}\n')

def drop_none(new_json):
    pop_keys = []
    for i,j in new_json.items():
        if type(j) is dict: 
            new_json[i] = Parser.drop_none(new_json[i])
            j = new_json[i]
        if j is None: pop_keys+=[i]
    for i in pop_keys: new_json.pop(i, None)
    return new_json

class ParsePipeline:
    def process_item(self, item, spider):
        if isinstance(item, PostItem):
            json_o = Parser.parse_post(dict(item))
        elif isinstance(item, CmtItem):
            json_o = Parser.parse_cmt(dict(item))
        elif isinstance(item, ReactionItem):
            json_o = Parser.parse_reaction(dict(item))
        # pprint(json_o)
        log(f"Successfully parse {item['html_path']}")
        return item, json_o
    
class DatabasePipeline:
    def __init__(self):
        pass

    def process_item(self, item, spider):
        item, json_o = item
        if isinstance(item, PostItem):
            existed = DB.post_exist(item['page_id'], item['post_id'])
            if existed: return
            if not DB.insert_post(json_o):
                log(f"[ERROR] Cannot insert new post. (page_id: {item['page_id']}, post_id: {item['post_id']})\n{json_o}")
                    
        elif isinstance(item, CmtItem):
            jsons = json_o
            ids = []
            for json_o in jsons:
                existed = DB.cmt_exist(json_o['page_id'], json_o['post_id'], json_o['comment_id'])
                if not existed:
                    if DB.insert_cmt(json_o): ids += [json_o['comment_id']]
                else: 
                    log(f"[ERROR] Cannot insert new cmt. (page_id: {item['page_id']}, post_id: {item['post_id']}, comment_id: {json_o['comment_id']})\n{json_o}")

            post = DB.get_post(item['page_id'], item['post_id'])
            
            if post:
                
                comments_full = [] if 'comments_full' not in post.keys() else post['comments_full'] or []
                comments_full += ids
                
                info = post['info']
                info['comments'] = len(comments_full)
                info = drop_none(info)
                
                if not DB.update_post(item['page_id'], item['post_id'], 
                    {'comments_full': comments_full, 'info': info}):
                    log(f"[ERROR] Cannot update new cmt ids. (page_id: {item['page_id']}, post_id: {item['post_id']}, comment_id: {item['comment_id']})\n{{'comments_full': comments_full, 'info': info}}")
            else:
                log(f"[ERROR] Cannot find record. (page_id: {item['page_id']}, post_id: {item['post_id']})")
            
        elif isinstance(item, ReactionItem):
            pass
            # json_o = Parser.parse_reaction(dict(item))
            # reactions = json_o
            
            # post = coll_post.find_one({
            #     'page_id': item['page_id'],
            #     'post_id': item['post_id']})
            
            # if post:
            
            #     info = post['info']
            #     info['reactions'] = reactions
            #     info['reaction_count'] = sum([j for i,j in reactions.items()])
            #     info = drop_none(info)
                
            #     coll_post.update_one({
            #         'page_id': item['page_id'],
            #         'post_id': item['post_id']
            #     }, {'$set': {'info': info}})
            #     log(f"Update reactions to DB. (page_id: {item['page_id']}, post_id: {item['post_id']})")
            # else:
            #     log(f"Cannot find record. (page_id: {item['page_id']}, post_id: {item['post_id']})")
        
        return item