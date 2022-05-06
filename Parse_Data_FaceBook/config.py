INPUT_DIR = 'html'
OUTPUT_DIR = 'data'
POST_OBJECT = {
    "info": {
        "time": "",
        "reaction_count": 0,
        "reactions": {
            "like": 0,
            "haha": 0,
            "love": 0, 
            "sad": 0
        },
        "comments": 0,
        "shares": 0
    },
    "comments_full": [],
    "post_id": "",
    "page_id": "",
    "post_url": "",
    "text": "",
    "images": [],
    "medical_label": None
}

COMMENT_OBJ = {
    "info": {
        "time": "",
        "reaction_count": 0,
        "comments": 0
    },
    "text": "",
    "comment_id": "",
}

TIME_OBJ = {
    "images": 0,
    "text": 0, 
    "id": 0,
    "reactions": 0,
    "comments":0,
}
LOG = True