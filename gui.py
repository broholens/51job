import tkinter as tk
from tkinter import ttk
import threading
from job import JobCrawler

root = tk.Tk()
root.title('51job')
root.geometry("500x260")
root.resizable(0, 0)

# 提示标签
ttk.Label(root, text="输入选好条件后的网址:").pack(pady=10)

# 输入网址
url = tk.StringVar()
url_entry = ttk.Entry(root, textvariable=url, width=450)
url_entry.pack(padx=30, pady=10)

def _crawl(urls):
    # 运行任务并更新组件
    jc = JobCrawler(urls)
    state_label.configure(text='正在获取需要抓取的链接数量...')
    count = jc.get_urls_count()
    state_label.configure(text='需要抓取的链接数量为：{}'.format(count))
    for index, url in enumerate(jc.urls_set):
        job_details = ','.join(jc.crawl_one(url))
        state_text = '{}/{}  {}'.format(index, count, job_details)
        state_label.configure(text=state_text)
    state_label.configure(text='查找完毕! 共找到{}条数据'.format(jc.result_count))
    run.configure(text='查找')

def crawl():
    """button回调函数"""
    urls = [url.get().strip()]
    run.configure(text="查找中...")
    # 新建线程
    t = threading.Thread(target=_crawl, args=(urls,))
    t.setDaemon(True)
    t.start()

# 查找按钮
run = ttk.Button(root, text='查找', command=crawl)
run.pack(pady=10)

# 查找状态更新标签
state_label = ttk.Label(root, text='')
state_label.pack(pady=10)

root.mainloop()