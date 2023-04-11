import requests
import openpyxl
import threading
import sys
import time
from tqdm import tqdm
# 将标准输出流的缓冲模式更改为无缓冲
sys.stdout = open(sys.stdout.fileno(), mode='w', buffering=1)


class URLBatchProcessor:
    def __init__(self, path_file, domain, delay, max_workers):
        self.path_file = path_file
        self.domain = domain
        self.delay = delay
        self.max_workers = max_workers
        self.workbook = openpyxl.Workbook()
        self.worksheet = self.workbook.active
        self.worksheet.append(['URL', 'Response'])
        self.lock = threading.Lock()

    def process_url(self, url):
        response = requests.get(url)
        if response.status_code == 200 and '错误' not in response.text and '400' \
                not in response.text and '404' not in response.text and '403' not in response.text:
            with self.lock:
                self.worksheet.append([url, response.text])

    def start(self):
        with open(self.path_file) as f:
            paths = f.readlines()
        for path in tqdm(paths, desc="Processing URLs"):
            urls = [self.domain.strip() + path.strip()]
            threads = []
            semaphore = threading.Semaphore(self.max_workers)
            for url in urls:
                semaphore.acquire()
                t = threading.Thread(target=self.process_url_with_semaphore, args=(semaphore, url))
                t.start()
                threads.append(t)
            for t in threads:
                t.join()
            self.workbook.save('output.xlsx')

    def process_url_with_semaphore(self, semaphore, url):
        try:
            self.process_url(url)
        finally:
            semaphore.release()  # 释放信号量
            time.sleep(self.delay)  # 添加延迟，避免过于频繁的访问


if __name__ == '__main__':
    URLBatchProcessor("url_list.txt", "https://uderptest.unionpayintl.com", 1, 5).start()
