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

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'Crawl_Data_FaceBook.middlewares.CrawlDataFacebookSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    # 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 400,
    # 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    # 'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    # 'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
    # 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 500,
    # 'scrapy_useragents.downloadermiddlewares.useragents.UserAgentsMiddleware': 500,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'Crawl_Data_FaceBook.pipelines.CrawlDataFacebookPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

# DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'

DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'

# SPLASH
SPLASH_URL = 'http://localhost:8050'

COOKIES_ENABLED = True 
SPLASH_COOKIES_DEBUG = True

FACEBOOK_ACCOUNT = [
    {
        "account": "ltb1002.aff@gmail.com",
        "password": "deepAI140421"
    }
]

SCROLLS = 2
GROUPS = [
    # "https://m.facebook.com/groups/1065116420221723",
    # "https://m.facebook.com/groups/241769123373305",
    "https://m.facebook.com/groups/mogivietnam"
]

SEARCH_QUERY = [
    {
        "key": "vng",
        "filter": "eyJlbXBsb3llcjowIjoie1wibmFtZVwiOlwidXNlcnNfZW1wbG95ZXJcIixcImFyZ3NcIjpcIjE2OTE3MTkyMjc2OFwifSJ9"
    },
    {
        "key": "zalo",
        "filter": "eyJlbXBsb3llcjowIjoie1wibmFtZVwiOlwidXNlcnNfZW1wbG95ZXJcIixcImFyZ3NcIjpcIjQ3MjM5ODQ0OTQzNzM2NVwifSJ9"
    },
    {
        "key": "tiki",
        "filter": "eyJlbXBsb3llcjowIjoie1wibmFtZVwiOlwidXNlcnNfZW1wbG95ZXJcIixcImFyZ3NcIjpcIjE2OTE3MTkyMjc2OFwifSJ9"
    }
]


SEARCH_LINK = "https://facebook.com/search/people?q="

RETRY_TIMES = 200

FORMAT_TYPES = 'json'
FEED_EXPORT_ENCODING = 'utf-8'

FEED_FORMAT = 'json'