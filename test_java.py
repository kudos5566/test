import os
import concurrent.futures
import logging
import sys

class JavaScanner:

    def __init__(self, root_path, keywords):
        self.root_path = root_path
        self.keywords = keywords

    def read_java_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        return code

    def scan_java_file(self, code):
        results = []
        line_number = 1
        for line in code.splitlines():
            for keyword in self.keywords:
                if keyword in line:
                    results.append({
                        "keyword": keyword,
                        "line_number": line_number,
                    })
            line_number += 1
        return results

    def scan_java_files(self):
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        results = []
        for root, dirs, files in os.walk(self.root_path):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.splitext(file)[1] in ALLOWED_EXTENSIONS:
                    try:
                        task = executor.submit(self.read_java_file, file_path)
                        results.append(task)
                    except FileNotFoundError:
                        logging.warning(f"File not found: {file_path}")

        for task in results:
            try:
                code = task.result()
                results = self.scan_java_file(code)
                for result in results:
                    print(f"{file_path}:{result['line_number']}: {result['keyword']}")
            except Exception as e:
                logging.error(e)


if __name__ == "__main__":
    ALLOWED_EXTENSIONS = [".java", ".html", ".css", ".js", ".xml", "jsp"]
    root_path = sys.argv[1]
    keywords = [
        "security", "StpUtil", "shiro", "OAuth", "Permission"
    ]
    scan = JavaScanner(root_path, keywords)
    scan.scan_java_files()