import re
import csv
import time
import json
import random
import requests
from lxml.html import etree  # pip install lxml
from fake_useragent import UserAgent  # pip install fake-useragent
from fake_useragent.errors import FakeUserAgentError

# fake_useragent.errors.FakeUserAgentError: Maximum amount of retries reached
try:
    UserAgent()
except FakeUserAgentError:
    pass


class JobCrawler:
    # headers
    columns = ['company name', 'phone', 'company trade', 'company link']
    # match telephone
    phone_ptn = re.compile('\d{11}')
    tel_ptn = re.compile('[0-9-]{12}')

    def __init__(self, start_urls=[], filename='job.csv'):
        self.ua = UserAgent()
        self.start_urls = start_urls
        self.f = open(filename, 'w', newline='')
        self.writer = csv.writer(self.f)
        # write headers
        self.writer.writerow(self.columns)
        self.urls_set = set()
        self.com_set = set()

    def request(self, url):
        try:
            resp = requests.get(url, headers={'User-Agent': self.ua.random}, timeout=3)
            # be friendly
            time.sleep(random.random()*1)
            return resp
        except:
            return

    def parse_page_num(self, tree):
        # total number of pages
        if tree is None:
            return 1
        page_txt = tree.xpath('//div[@class="p_in"]/span/text()')[0]
        page_num = int(page_txt.split('页')[0].strip('共'))
        return page_num

    def generate_page_urls(self, url, page_num):
        # generate page url by keyword and total page number
        a, b = url.split('.html')
        a = ','.join(a.split(',')[:-1]) + ','
        b = '.html' + b
        return [''.join((a, str(i), b)) for i in range(1, page_num+1)]


    def parse_resp_to_tree(self, resp):
        try:
            # UnicodeEncodeError: 'gbk' codec can't encode character '\xa0' in position 69: illegal multibyte sequence
            text = resp.content.decode('gbk')
            tree = etree.HTML(text)
            return tree
        except:
            return

    def parse_page(self, tree):
        # extract job links in this page
        if tree is None:
            return
        jobs_urls = tree.xpath('//div[@id="resultList"]/div[@class="el"]/p/span/a/@href')
        for url in jobs_urls:
            self.urls_set.add(url)

    def extract_info(self, tree, xp, by_xp=True, default=''):
        # extract information by xpath or regex
        info = tree.xpath(xp) if by_xp is True else tree.findall(xp)
        info = info or ''
        if info:
            info = ','.join([i.strip() for i in info if i.strip()])
        return info.replace('\xa0', '')
    
    def parse_job(self, tree):
        # parse job information
        com_name = self.extract_info(tree, '//a[contains(@class, "com_name")]/p/@title')
        com_link = self.extract_info(tree, '//a[contains(@class, "com_name")]/@href')
        _, _, com_trade = tree.xpath('//div[contains(@class, "com_tag")]/p/@title')
        job_msg = self.extract_info(tree, '//div[contains(@class, "job_msg")]/p/text()')
        com_msg = self.extract_info(tree, '//div[starts-with(@class, "tmsg")]/text()')
        phone = self.extract_info(self.phone_ptn, job_msg+com_msg, False)
        tel = self.extract_info(self.tel_ptn, job_msg+com_msg, False)
        phone = ','.join([phone, tel]).strip(',')
        return [com_name, phone, com_trade, com_link]
    
    def generate_urls(self):
        # filter urls
        for url in self.start_urls:
            resp = self.request(url)
            tree = self.parse_resp_to_tree(resp)
            page_num = self.parse_page_num(tree)
            urls = self.generate_page_urls(url, page_num)
            for page in urls:
                resp = self.request(page)
                tree = self.parse_resp_to_tree(resp)
                self.parse_page(tree)

    def _crawl(self, url):
        pass

        
    def crawl(self):
        # crawl job information with given keyword
        self.generate_urls()
        for link in self.urls_set:
            # every job
            if not link.startswith('https://jobs.51job.com'):
                continue
            # 解析错误
            try:
                resp = self.request(link)
                tree = self.parse_resp_to_tree(resp)
                job_details = self.parse_job(tree)
            except:
                continue
            com_link = job_details[-1]
            if com_link in self.com_set:
                continue
            self.com_set.add(com_link)
            self.writer.writerow(job_details)
            print(job_details)