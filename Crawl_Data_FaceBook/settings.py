# Scrapy settings for Crawl_Data_FaceBook project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'Crawl_Data_FaceBook'

SPIDER_MODULES = ['Crawl_Data_FaceBook.spiders']
NEWSPIDER_MODULE = 'Crawl_Data_FaceBook.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
### OF KHOAN
# USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
### OF HUYNHNGOCTHIEN
# USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
### OF GOOOGLE
# USER_AGENT = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
### OF MYAGENT
USER_AGENT = 'Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'

# SPLASH
SPLASH_URL = 'http://localhost:8050'

COOKIES_ENABLED = True 
SPLASH_COOKIES_DEBUG = True

RETRY_TIMES = 200

FORMAT_TYPES = 'json'
FEED_EXPORT_ENCODING = 'utf-8'

FEED_FORMAT = 'json'
URLLENGTH_LIMIT = 5000

GROUP_IDS = ['VietnamProjectsConstructionGROUP', 
    'tinnonghoi.vn', 
    'tinnongbaomoi24h', 
    'tintuc2', 
    '714257262432794', 
    '171952859547317', 
    '348017149108768', 
    '273257912789357', 
    'u23fanclub']

ITEM_PIPELINES = {
    'Crawl_Data_FaceBook.pipelines.ParsePipeline': 100,
    'Crawl_Data_FaceBook.pipelines.DatabasePipeline': 200,
}