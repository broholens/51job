import tkinter as tk
from tkinter import ttk
import threading
from job import JobCrawler

root = tk.Tk()
root.title('51job')
root.geometry("300x250")
root.resizable(0, 0)

ttk.Label(root, text="输入选好条件后的网址").pack(expand=1)

url = tk.StringVar()
url_entry = ttk.Entry(root, textvariable=url)
url_entry.pack()

def _crawl(urls):
    JobCrawler(urls).crawl()

def crawl():
    urls = [url.get().strip()]
    run.configure(text="查找中...")
    t = threading.Thread(target=_crawl, args=(urls,))
    t.setDaemon(True)
    t.start()

run = ttk.Button(root, text='查找', command=crawl)
run.pack(expand=5)

root.mainloop()

# https://search.51job.com/list/200200,000000,0000,00,3,06,%2B,1,1.html?lang=c&stype=1&postchannel=0000&workyear=02&cotype=99&degreefrom=04&jobterm=99&companysize=02&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare=