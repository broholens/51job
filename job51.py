import re
import csv
import time
import json
import random
import datetime
from urllib.parse import quote  # quote keyword
import requests
from lxml.html import etree  # pip install lxml
from fuzzywuzzy import process  # pip install fuzzywuzzy
from fake_useragent import UserAgent  # pip install fake-useragent
# from fake_useragent.errors import FakeUserAgentError

# fake_useragent.errors.FakeUserAgentError: Maximum amount of retries reached
try:
    UserAgent()
except:
    pass


def get_area_codes():
    # request area and code mapping table.
    url = 'https://js.51jobcdn.com/in/js/2016/layer/area_array_c.js?20180319'
    resp = requests.get(url)
    code_str = resp.text.split('{')[-1].split('}')[0]
    code_str = '{' + code_str + '}'
    codes = json.loads(code_str)
    # convert {code: area} to {area: code}
    codes = {j: i for i, j in codes.items()}
    codes.update({'全国': '000000'})
    return codes


class JobCrawler:
    # headers
    columns = ['salary', 'telephone', 'education', 'job name', 'experience', 'company flag', 'company name', 'job details', 'company trade', 'location', 'addr', 'company information', 'url']
    # search url
    url = 'https://search.51job.com/list/{},000000,0000,00,9,99,{},2,{}.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='
    
    def __init__(self, filename='job.csv'):
        self.ua = UserAgent()
        self.f = open(filename, 'w', newline='')
        self.writer = csv.writer(self.f)
        # write headers
        self.writer.writerow(self.columns)
        # match telephone
        self.phone_ptn = re.compile('\d{11}')
        self.tel_ptn = re.compile('[0-9-)]{12, 18}')
        # save error url
        self.error_f = open('error.txt', 'w')
        # load area codes
        self.area_codes = get_area_codes()

    def request(self, url):
        try:
            resp = requests.get(url, headers={'User-Agent': self.ua.random}, timeout=3)
            # be friendly
            time.sleep(random.random()*3)
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

    def generate_page_urls(self, code, kw, page_num):
        # generate page url by keyword and total page number
        return [self.url.format(code, kw, i) for i in range(1, page_num+1)]

    def parse_resp_to_tree(self, resp):
        try:
            # UnicodeEncodeError: 'gbk' codec can't encode character '\xa0' in position 69: illegal multibyte sequence
            text = resp.content.decode('gbk').replace('\xa0', '')
            tree = etree.HTML(text)
            return tree
        except:
            return

    def parse_page(self, tree):
        # extract job links in this page
        if tree is None:
            return []
        jobs_urls = tree.xpath('//div[@id="resultList"]/div[@class="el"]/p/span/a/@href')
        return jobs_urls

    def extract_info_by_xp(self, tree, xp, default=''):
        # extract information by xpath
        info = tree.xpath(xp) or default
        if info:
            info = ','.join(info)
        return info.strip().replace('\xa0', '')

    def extract_info_by_regex(self, ptn, msg, default=''):
        # extract information by regex
        info = ptn.findall(msg) or ''
        if info:
            info = ','.join(info)
        return info.strip().replace('\xa0', '')
    

    def parse_job(self, tree):
        # parse job information
        title = tree.xpath('//div[@class="cn"]/p[contains(@class, "msg")]/@title')[0]
        loca, expe, edu = [i.strip() for i in title.split('|')[:3]]
        if '招' in edu:
            edu = ''
        job_name = self.extract_info_by_xp(tree, '//div[@class="cn"]/h1/@title')
        salary = self.extract_info_by_xp(tree, '//div[@class="cn"]/strong/text()')
        if '千' in salary:
            salary = salary.split('千')[0]
            low, high = salary.split('-')
            salary = str(round(float(low)/10, 1)) + '-' + str(round(float(high)/10, 1))
        elif '万' in salary:
            salary = salary.split('万')[0]
        com_name = self.extract_info_by_xp(tree, '//a[contains(@class, "com_name")]/p/@title')
        com_flag, _, com_trade = tree.xpath('//div[contains(@class, "com_tag")]/p/@title')
        job_msg = tree.xpath('//div[contains(@class, "job_msg")]/p/text()')
        job_msg = ''.join([i for i in job_msg if i.strip()]).replace('\xa0', '')
        com_msg = self.extract_info_by_xp(tree, '//div[starts-with(@class, "tmsg")]/text()')
        addr = self.extract_info_by_xp(tree, '//div[@class="bmsg inbox"]/p/text()')
        phone = self.extract_info_by_regex(self.phone_ptn, job_msg+com_msg)
        tel = self.extract_info_by_regex(self.tel_ptn, job_msg+com_msg)
        phone = ','.join([phone, tel]).strip(',')
        return [salary, phone, edu, job_name, expe, com_flag, com_name, job_msg, com_trade, loca, addr, com_msg]

    def crawl(self, keyword, area='全国'):
        # crawl job information with given keyword
        quoted_kw = quote(keyword)
        area = process.extractOne(area, self.area_codes.keys())[0]
        # default is nationwide
        code = self.area_codes.get(area, '000000')
        resp = self.request(self.url.format(code, quoted_kw, 1))
        tree = self.parse_resp_to_tree(resp)
        page_num = self.parse_page_num(tree)
        urls = self.generate_page_urls(code, quoted_kw, page_num)
        for page_url in urls:
            # every page
            resp = self.request(page_url)
            tree = self.parse_resp_to_tree(resp)
            urls = self.parse_page(tree)
            for link in urls:
                # every job
                print(datetime.datetime.now(), link)
                if not link.startswith('https://jobs.51job.com'):
                    continue
                resp = self.request(link)
                tree = self.parse_resp_to_tree(resp)
                try:
                    job_details = self.parse_job(tree)
                    job_details.append(link)
                    self.writer.writerow(job_details)
                    print(job_details)
                except:
                    self.error_f.write(link+'\n')
                    continue


if __name__ == '__main__':
    keywords = ['电气工程师']
    area = '西安'
    crawler = JobCrawler()
    for x in keywords:
        crawler.crawl(x, area)