from db_config import *
import pymongo

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DBUtils(metaclass=SingletonMeta):
    
    def __init__(self):
            
        self.client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
        self.db = self.client[DB_NAME]    

        list_of_collections = self.db.list_collection_names()
        if COLL_POST not in list_of_collections:
            coll_post = self.db.create_collection(COLL_POST, validator=COLL_POST_VAL)
        if COLL_CMT not in list_of_collections:
            coll_post = self.db.create_collection(COLL_CMT, validator=COLL_CMT_VAL)

        self.coll_post = self.db[COLL_POST]
        self.coll_cmt = self.db[COLL_CMT]
    
    def post_exist(self, page_id, post_id):
        existed = self.coll_post.count_documents({
            'page_id': page_id,
            'post_id': post_id
        }, limit=1)
        return existed > 0

    def cmt_exist(self, page_id, post_id, cmt_id):
        existed = self.coll_cmt.count_documents({
            'page_id': page_id,
            'post_id': post_id,
            'comment_id': cmt_id
        }, limit=1)
        return existed > 0

    def insert_post(self, json_o):
        try: self.coll_post.insert_one(json_o)
        except: return False
        return True
    
    def insert_cmt(self, json_o):
        try: self.coll_cmt.insert_one(json_o)
        except: return False
        return True
    
    def get_post(self, page_id=None, post_id=None):
        query = {
            'page_id': page_id, 
            'post_id': post_id, 
        }
        items = list(query.items())
        _ = [query.pop(i) for i,j in items]
            
        if page_id and post_id:
            return self.coll_post.find_one(query)
        return self.coll_post.find(query)
    
    def get_cmt(self, page_id=None, post_id=None, comment_id=None):
        query = {
            'page_id': page_id, 
            'post_id': post_id,
            'comment_id': comment_id 
        }
        items = list(query.items())
        _ = [query.pop(i) for i,j in items]
            
        if page_id and post_id and comment_id:
            return self.coll_cmt.find_one(query)
        return self.coll_cmt.find(query)
        
    def update_post(self, page_id, post_id, json_o):
        try:
            self.coll_post.update_one({
                'page_id': page_id,
                'post_id': post_id
            }, {'$set': json_o})
        except:
            return False
        return True
    
    def get_post_field(self, page_id, post_id, field_keys):
        post = self.get_post(page_id, post_id)
        if not post: return None
        
        for key in field_keys:
            if key not in post.keys(): return None
            
            post = post[key]
            if not post: return None
        
        return post