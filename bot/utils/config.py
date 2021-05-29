import json, codecs

class Config():
    def __init__(self):
        with codecs.open('config.json', 'r', encoding='utf-8-sig') as File:
            self.config = json.load(File)

    def save_config(self):
        with codecs.open('config.json', 'w', encoding='utf-8-') as File:
            json.dump(self.config, File, sort_keys=True, indent=4, ensure_ascii=False)
        