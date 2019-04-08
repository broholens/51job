import csv
import time
import random
import datetime
from urllib.parse import quote  # quote keyword
import requests
from lxml.html import etree  # pip install lxml
from fake_useragent import UserAgent  # pip install fake-useragent
# from fake_useragent.errors import FakeUserAgentError

# fake_useragent.errors.FakeUserAgentError: Maximum amount of retries reached
try:
    UserAgent()
except:
    pass


class JobCrawler:
    # headers
    columns = ['education', 'job_name', 'experience', 'company flag', 'company name', 'job details', 'company trade', 'salary', 'address', 'url']
    # search nationwide
    url = 'https://search.51job.com/list/000000,000000,0000,00,9,99,{},2,{}.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='

    def __init__(self, filename='job.csv'):
        self.ua = UserAgent()
        self.f = open(filename, 'w', newline='')
        self.writer = csv.writer(self.f)
        # write headers
        self.writer.writerow(self.columns)


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

    def generate_page_urls(self, kw, page_num):
        # generate page url by keyword and total page number
        return [self.url.format(kw, i) for i in range(1, page_num+1)]

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

    def parse_job(self, tree):
        # parse job information
        title = tree.xpath('//div[@class="cn"]/p[contains(@class, "msg")]/@title')[0]
        addr, expe, edu = [i.strip() for i in title.split('|')[:3]]
        job_name = tree.xpath('//div[@class="cn"]/h1/@title')[0]
        salary = tree.xpath('//div[@class="cn"]/strong/text()')
        salary = salary[0] if salary else 'unknown'
        com_name = tree.xpath('//a[contains(@class, "com_name")]/p/@title')[0]
        com_flag, _, com_trade = tree.xpath('//div[contains(@class, "com_tag")]/p/@title')
        job_msg = tree.xpath('//div[contains(@class, "job_msg")]/p/text()')
        job_msg = ''.join([i for i in job_msg if i.strip()])
        return [edu, job_name, expe, com_flag, com_name, job_msg, com_trade, salary, addr]

    def crawl(self, keyword):
        # crawl job information with given keyword
        quoted_kw = quote(keyword)
        resp = self.request(self.url.format(quoted_kw, 1))
        tree = self.parse_resp_to_tree(resp)
        page_num = self.parse_page_num(tree)
        urls = self.generate_page_urls(quoted_kw, page_num)
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
                    print(job_details)
                except:
                    continue
                job_details.append(link)
                self.writer.writerow(job_details)


if __name__ == '__main__':
    keywords = ['统计专业', '统计应用', '统计系']
    crawler = JobCrawler()
    for x in keywords:
        crawler.crawl(x)