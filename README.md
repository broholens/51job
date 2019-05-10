# 51job
crawl job information from 51job.com by given keywords

- job.py是根据特定需求完成的.只获取了公司名称、行业、公司链接,且只将有联系方式的公司信息存入csv文件中
- job51.py解析了职位的详细信息，包含字段如下：'salary', 'telephone', 'education', 'job name', 'experience', 'location', 'addr', 'job details', 'company name', 'company flag', 'company people count', 'company trade', 'company information', 'url'，最后将职位信息存入csv文件中


# TODO
- multi thread
- ~~complete comment~~
- handle exception
- search by region
- parse more information
- ~~GUI~~
