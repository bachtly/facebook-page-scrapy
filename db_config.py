from datetime import datetime
import urllib.parse

uri = f"mongodb+srv://{urllib.parse.quote('edwardly1002')}:{urllib.parse.quote('Ltb123!@#')}@cluster0.lqbbu.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
DB_NAME = 'fakenews'
COLL_POST = 'testpost'
COLL_CMT = 'testcmt'

COLL_POST_VAL = {
    '$jsonSchema': {
        'bsonType': 'object',
        'additionalProperties': True,
        'required': ['info', 'post_id', 'page_id'],
        'properties': {
            'info': {
                'bsonType': 'object',
                'properties': {
                    'time': {'bsonType': 'date'},
                    'reaction_count': {'bsonType': 'int'},
                    'comments': {'bsonType': 'int'},
                    'shares': {'bsonType': 'int'},
                    'reactors': {'bsonType': 'array'},
                    'reactions': {
                        'bsonType': 'object',
                        'properties': {
                            'Thích': {'bsonType': 'int'},
                            'Yêu thích': {'bsonType': 'int'},
                            'Thương thương':{'bsonType': 'int'},
                            'Haha':{'bsonType': 'int'},
                            'Wow': {'bsonType': 'int'},
                            'Buồn': {'bsonType': 'int'},
                            'Phẫn nộ':{'bsonType': 'int'},
                        }
                    },
                }
            },
            'comments_full': {'bsonType': 'array'},
            'post_id': {'bsonType': 'string'},
            'page_id': {'bsonType': 'string'},
            'post_url': {'bsonType': 'string'},
            'text': {'bsonType': 'string'},
            'images': {'bsonType': 'array'},
            'medical_label': {'bsonType': 'bool'},
            'username': {'bsonType': 'string'},
            'fetched_time': {'bsonType': 'date'},
            'user_id': {'bsonType': 'string'}
        }
    }
}

COLL_CMT_VAL = {
    '$jsonSchema': {
        'bsonType': 'object',
        'additionalProperties': True,
        'required': ['info', 'text', 'comment_id', 'post_id', 'page_id'],
        'properties': {
            'info': {
                'bsonType': 'object',
                'required': ['reaction_count', 'comments'],
                'properties': {
                    'time': {'bsonType': 'date'},
                    'reaction_count': {'bsonType': 'int'},
                    'comments': {'bsonType': 'int'},
                    'reactors': {'bsonType': 'array'},
                    'reactions': {
                        'bsonType': 'object',
                        'properties': {
                            'Thích': {'bsonType': 'int'},
                            'Yêu thích': {'bsonType': 'int'},
                            'Thương thương':{'bsonType': 'int'},
                            'Haha':{'bsonType': 'int'},
                            'Wow': {'bsonType': 'int'},
                            'Buồn': {'bsonType': 'int'},
                            'Phẫn nộ':{'bsonType': 'int'},
                        }
                    },
                }
            },
            'text': {'bsonType': 'string'},
            'page_id': {'bsonType': 'string'},
            'post_id': {'bsonType': 'string'},
            'comment_id': {'bsonType': 'string'},
            'comments_full': {'bsonType': 'array'},
            'username': {'bsonType': 'string'},
            'user_id': {'bsonType': 'string'}
        }
    }
}

POST_OBJECT = {
    'info': {
        'time': None,
        'reaction_count': 0,
        'reactions': 
        {
            'Thích': None,
            'Yêu thích': None,
            'Thương thương':None,
            'Haha':None,
            'Wow': None,
            'Buồn': None,
            'Phẫn nộ':None,
        },
        'comments': 0,
        'shares': 0,
        'reactors': [],
        'complete_crawl_comment': False,
    },
    'comments_full': [],
    'post_id': None,
    'page_id': None,
    'post_url': None,
    'text': '',
    'images': None,
    'medical_label': None,
    'username': None,
    'fetched_time': None,
    'user_id': None,
}

COMMENT_OBJ = {
    'info': {
        'time': None,
        'reaction_count': 0,
        'comments': 0,
        'reactions': None,
        'reactors': None,
        'complete_crawl_comment': False,
    },
    'text': '',
    'comment_id': None,
    'post_id': None,
    'page_id': None,
    'comments_full': None,
    'username': None,
    'user_id': None,
}

REACTION_MAP = {
    'Thích': 'Like',
    'Yêu thích': 'Love',
    'Thương thương': 'Care',
    'Haha': 'Haha',
    'Wow': 'Wow',
    'Buồn': 'Sad',
    'Phẫn nộ': 'Angry',
}

MON_TO_NUM = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

STD_RULES = {}
STD_RULES.update(REACTION_MAP)

DB_DEBUG=True