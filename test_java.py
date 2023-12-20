import os
import concurrent.futures
import logging
import re
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
        found_keywords = {}
        current_method = None
        line_number = 1
        for line in code.splitlines():
            method_match = re.search(r"(public|protected|private|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *(\{"
                                     r"?|[^;])", line)
            if method_match:
                current_method = method_match.group(2)
            for keyword in self.keywords:
                keyword_regex = r"%s" % keyword
                if re.search(keyword_regex, line) and current_method:
                    if keyword not in found_keywords:
                        found_keywords[keyword] = {}
                    if current_method not in found_keywords[keyword]:
                        found_keywords[keyword][current_method] = []
                    found_keywords[keyword][current_method].append(line_number)
            line_number += 1
        return found_keywords

    def scan_java_files(self):
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        result = []
        for root, dirs, files in os.walk(self.root_path):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.splitext(file)[1] in ALLOWED_EXTENSIONS:
                    try:
                        task = executor.submit(self.read_java_file, file_path)
                        result.append((file_path, task))
                    except FileNotFoundError:
                        logging.warning(f"File not found: {file_path}")

        for file_path, task in result:
            try:
                code = task.result()
                results = self.scan_java_file(code)
                for keyword, methods in results.items():
                    for method, line_numbers in methods.items():
                        print(f"{file_path}-> {method}：{','.join(map(str, line_numbers))} = {keyword}")
            except Exception as e:
                logging.error(e)


if __name__ == "__main__":
    ALLOWED_EXTENSIONS = [".java", ".html", ".css", ".js", ".xml", "jsp"]
    root_path = sys.args[1]
    keywords = [
        "security", "StpUtil", "shiro", "OAuth", "Permission"
    ]
    scan = JavaScanner(root_path, keywords)
    scan.scan_java_files()
