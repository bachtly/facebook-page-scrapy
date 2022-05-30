# FacebookPageScraping

## Components

There are 3 main components
- **Crawlers**: in charge of scraping html from urls and storing them in local files. They are also called spiders, which source codes are in folder `Crawl_Data_FaceBook\spiders`.
- **Parser**: in charge of parsing html from local files. This class read html from local file, parsing them by xpaths and return an object with data structure specified in `db_utils.py`. The *Parser* class is defined in `Parse_Data_FaceBook\Parser.py`.
- **Database**: in charge of updating objects to cloud database. The class *DBUtils* is defined in `DatabaseUtils\DBUtils.py`

The program flow is serial as following steps:
- **Step 1**: A spider is called through a system command. For example: 
```
scrapy crawl facebook_group_post
```
The *facebook_group_post* is the name of the spider, specified in the spider's class. 
- **Step 2**: The spider runs its *start_requests()* method, which will generate initial urls to scrape.
- **Step 3**: The spider runs its *parse()* method, which is usually used to parse object from html source. However, in this project, we use it to store the html source.
- **Step 4**: The spider return control to pipeline, which source code is stored in `Crawl_Data_FaceBook\pipelines.py`. In order to use the pipeline classes, we need to config first, by modifying file `Crawl_Data_FaceBook\settings.py`. Add these lines:
```
ITEM_PIPELINES = {
    'Crawl_Data_FaceBook.pipelines.ParsePipeline': 100,
    'Crawl_Data_FaceBook.pipelines.DatabasePipeline': 200,
}
```
This means *ParsePipeline* will be used right after the spider return an item, and *DatabasePipeline* will run after that. The order is based on their weights (100 and 200).
- **Step 5**: *ParsePipeline* come to work. It call *Parser* object to parse the html source which directory returned from the spider.
- **Step 6**

## Structure of facebook posts and comments

Post: {
    Comments: {
        Comments:{}
    }
}

A post will have many comments. A comment may have some comments replying to it, called subcomment. 

## Crawlers

- Facebook Group Post: crawl posts from groups on facebook. A post is stored in the database with basic fields like text, username, user_id, comments (the id only), ...
- Facebook Group Cmt: crawl comments coresponding to a specific post. A cmt is stored in the database with basic fields like text, username, user_id, reply_to
- Facebook Group Subcmt: crawl comments that reply to a specific comment. This subcmt would be stored in the same database as normal comments.


# 30/5/2022

1. Dùng J2team cookies để get cookie
	- đăng nhập facebook
	- lấy cookie

2. Bị chặn nếu crawl quá thường xuyên => 2 phút crawl 1 lần

3. Spider: crawl 1 loại object
	- Flow tổng quát: spider lấy html từ url, lưu về file local -> pipeline: parse cái html từ file local xong update lên DB
		1. Spider: start_request() scrape html về -> parse(): lưu lại html về local. Sau khi hoàn thành, trả control về cho pipeline (set up trong Crawl_Data_Facebook/settings.py)
		2. Pipeline Parse: parse html tuwf file local

```
scrapy crawl facebook_group_post
scrapy crawl facebook_group_cmt
scrapy crawl facebook_group_subcmt
```