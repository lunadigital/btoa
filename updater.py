from html.parser import HTMLParser
import urllib.request
import ssl
import re

class Version:
    def __init__(self, *args):
        self.value = args

    def __to_raw_string(self):
        return ''.join(str(i) for i in self.value)
    
    def to_int(self):
        return int(f'{self.__to_raw_string()}')

    def to_string(self):
        return '.'.join(str(i) for i in self.value)

class ArnoldUpdater(HTMLParser):
    def __init__(self, version=None):
        super().__init__()
        self.current_version = version
        self.latest_version = None
        self.all_versions = []

        ssl._create_default_https_context = ssl._create_unverified_context
        fp = urllib.request.urlopen("https://www.arnoldforblender.com/downloads/")
        mybytes = fp.read()
        html = mybytes.decode("utf8")
        fp.close()

        self.feed(html)

    def handle_data(self, data):
        result = re.search("^\d+(\.\d+)*\/$", data)

        if result:
            result = result.group(0)[:-1].replace("/", "")
            result = result.split(".")
            result = Version(*result)

            if not self.latest_version or result.to_int() > self.latest_version.to_int():
                self.latest_version = result
            
            self.all_versions.append(result)
    
    def update_available(self):
        return self.current_version.to_int() < self.latest_version.to_int()