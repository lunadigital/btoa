import urllib.request
import ssl
import re
import json

class Version:
    def __init__(self, *args):
        self.value = args

    def __to_raw_string(self):
        return ''.join(str(i) for i in self.value)
    
    def to_int(self):
        return int(f'{self.__to_raw_string()}')

    def to_string(self):
        return '.'.join(str(i) for i in self.value)

class ArnoldUpdater():
    def __init__(self, version=None):
        super().__init__()
        self.current_version = version
        self.latest_version = None
        self.all_versions = []

        url = "https://www.arnoldforblender.com/api/update"

        try:
            ssl._create_default_https_context = ssl._create_unverified_context
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())

                    versions = data.get("files", [])

                    for version in versions:
                        result = version.split(".")
                        result = Version(*result)

                        if not self.latest_version or result.to_int() > self.latest_version.to_int():
                            self.latest_version = result
                        
                        self.all_versions.append(result)
                else:
                    print(f"Failed to fetch ZIPs. Status: {response.status}")
        except Exception as e:
            print(f"Error fetching ZIPs: {e}")
    
    def update_available(self):
        return self.current_version.to_int() < self.latest_version.to_int()