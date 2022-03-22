import scrapy


class DataFacebookSpider(scrapy.Spider):
    name = 'Data_FaceBook'
    allowed_domains = ['facebook.com']
    start_urls = ['https://www.facebook.com/khoan.le.35325']

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], callback = self.parse)

    def parse(self, response):
        pass
