import os
import concurrent.futures
import logging
import re
import sys

ALLOWED_EXTENSIONS = [".java", ".html", ".css", ".js", ".xml", "jsp"]
keywords = ["security", "StpUtil", "shiro", "OAuth", "Permission"]

class JavaScanner:

    def __init__(self, root_path, keywords):
        self.root_path = root_path
        self.keywords = keywords
        self.results = []

    def read_java_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
            return code
        except FileNotFoundError as e:
            logging.warning(f"File not found: {file_path}")
            return None

    def scan_java_file(self, code, file_path):
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
                    found_keywords.setdefault(keyword, {}).setdefault(current_method, []).append(line_number)
            line_number += 1
        if found_keywords:
            self.results.append((file_path, found_keywords))

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
                if code is not None:
                    self.scan_java_file(code, file_path)
            except Exception as e:
                logging.error(e)

    def generate_html_report(self, output_file="output.html"):
        with open(output_file, "w", encoding="utf-8") as html_file:
            html_file.write("<html><head><title>Java Code Scanner Results</title></head><body>")
            for file_path, found_keywords in self.results:
                html_file.write(f"<h4>{file_path}</h4>")
                for keyword, methods in found_keywords.items():
                    html_file.write(f"<h4>{keyword}</h4>")
                    for method, line_numbers in methods.items():
                        line_numbers_str = ','.join(map(str, line_numbers))
                        html_file.write(
                            f"<p>{method} -> {line_numbers_str} -> {keyword}</p>")
            html_file.write("</body></html>")
            logging.info(f"HTML report generated: {output_file}")


if __name__ == "__main__":
    root_path = sys.argv[1]
    scan = JavaScanner(root_path, keywords)
    scan.scan_java_files()
    scan.generate_html_report(output_file="output.html")
