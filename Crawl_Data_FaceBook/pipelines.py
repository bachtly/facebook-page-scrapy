import pymongo
from pprint import pprint
from datetime import datetime

from db_config import *
from itemadapter import ItemAdapter
from Crawl_Data_FaceBook.items import PostItem, CmtItem, ReactionItem
from Parse_Data_FaceBook.Parser import Parser

DEBUG = DB_DEBUG

client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]

list_of_collections = db.list_collection_names()
if COLL_POST not in list_of_collections:
    coll_post = db.create_collection(COLL_POST, validator=COLL_POST_VAL)
if COLL_CMT not in list_of_collections:
    coll_post = db.create_collection(COLL_CMT, validator=COLL_CMT_VAL)

coll_post = db[COLL_POST]
coll_cmt = db[COLL_CMT]

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
            existed = coll_post.count_documents({
                    'page_id': json_o['page_id'],
                    'post_id': json_o['post_id']
                }, limit=1)
            if not existed:
                try: 
                    x = coll_post.insert_one(json_o)
                    log(f"Insert new post to DB. (page_id: {json_o['page_id']}, post_id: {json_o['post_id']})")
                except: 
                    log(f"ERROR: cannot insert new post. (page_id: {json_o['page_id']}, post_id: {json_o['post_id']})")
                    
        elif isinstance(item, CmtItem):
            jsons = json_o
            ids = []
            for json_o in jsons:
                existed = coll_cmt.count_documents({
                        'page_id': json_o['page_id'],
                        'post_id': json_o['post_id'],
                        'comment_id': json_o['comment_id']
                    }, limit=1)
                if not existed:
                    coll_cmt.insert_one(json_o)
                    ids += [json_o['comment_id']]
                    # try: 
                    #     x = coll_cmt.insert_one(json_o)
                    #     ids += [x['_id']]
                    #     log(f"Insert new comment to DB. (page_id: {json_o['page_id']}, post_id: {json_o['post_id']}, comment_id: {json_o['comment_id']})")
                    # except: 
                    #     log(f"ERROR: cannot insert new comment. (page_id: {json_o['page_id']}, post_id: {json_o['post_id']}, comment_id: {json_o['comment_id']})")

            post = coll_post.find_one({
                'page_id': item['page_id'],
                'post_id': item['post_id']})
            
            if post:
                
                comments_full = [] if 'comments_full' not in post.keys() else post['comments_full'] or []
                comments_full += ids
                
                info = post['info']
                info['comments'] = len(comments_full)
                info = drop_none(info)
                
                coll_post.update_one({
                    'page_id': item['page_id'],
                    'post_id': item['post_id']
                }, {'$set': {'comments_full': comments_full, 'info': info}})
                log(f"Update new comment_ids to DB. (page_id: {item['page_id']}, post_id: {item['post_id']})")
            else:
                log(f"Cannot find record. (page_id: {item['page_id']}, post_id: {item['post_id']})")
            
        elif isinstance(item, ReactionItem):
            json_o = Parser.parse_reaction(dict(item))
            reactions = json_o
            
            post = coll_post.find_one({
                'page_id': item['page_id'],
                'post_id': item['post_id']})
            
            if post:
            
                info = post['info']
                info['reactions'] = reactions
                info['reaction_count'] = sum([j for i,j in reactions.items()])
                info = drop_none(info)
                
                coll_post.update_one({
                    'page_id': item['page_id'],
                    'post_id': item['post_id']
                }, {'$set': {'info': info}})
                log(f"Update reactions to DB. (page_id: {item['page_id']}, post_id: {item['post_id']})")
            else:
                log(f"Cannot find record. (page_id: {item['page_id']}, post_id: {item['post_id']})")
        
        return item