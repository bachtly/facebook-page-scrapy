import os
import json
import numpy as np
from datetime import datetime

class ScrapyUtils:
    def __init__(self, log_file='tmp_log.txt', DEBUG=True, cookies_dir = './cookies/test'):
        self.log_file = log_file
        self.DEBUG = DEBUG
        self.cookies_dir = cookies_dir
    
    def log(self, s):
        if not self.DEBUG: return 
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f'{str(datetime.now())}: {s}\n')
    
    def get_dir(self, dir):
        if not os.path.isdir(dir):
            os.makedirs(dir)
        return dir
    
    def prepare_cookie(self):
        self.cookies_name = [i for i in os.listdir(self.cookies_dir)]
        self.log(f"List of cookies used: {self.cookies_name}")
        self.sleep_time = 120/len(self.cookies_name)
        self.log(f"Modify the sleep time: {self.sleep_time}")
        self.cookies = [
            json.load(open(os.path.join(self.cookies_dir, i), "r"))['cookies'] 
            for i in self.cookies_name]
        self.cookie_idx = np.random.randint(0, len(self.cookies))  
        
    def get_cookie(self):
        self.prepare_cookie()
        self.log(f"Use cookie {self.cookies_name[self.cookie_idx]}")
        cookie = self.cookies[self.cookie_idx]
        self.cookie_idx = (self.cookie_idx + 1) % len(self.cookies)
        return cookie
            
    