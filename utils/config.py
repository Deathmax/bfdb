import json
import os


class Config:
    DEFAULT_CONFIG_PATH = "config/bfdbconfig.json"

    def __init__(self, path=DEFAULT_CONFIG_PATH):
        self.path = path
        if os.path.isfile(path):
            with open(path) as f:
                x = json.load(f)
                self.directory_dat = x['directory_dat']
                self.directory_json = x['directory_json']
                self.dictionary_path = x['dictionary_path']
                self.output_path = x['output_path']
                self.cdn_url = x['cdn_url']
                self.parsers = x['parsers']
                self.foreign = x['foreign']
        else:
            print path + " not found, creating with defaults"
            self.directory_dat = "data/decoded_dat/"
            self.directory_json = "data/"
            self.dictionary_path = "data/dictionary_raw.txt"
            self.output_path = "../bravefrontier_data/"
            self.cdn_url = "http://v2.cdn.android.brave.a-lim.jp/"
            self.parsers = ['skill', 'leader skill', 'extra skill', 'fe skill', 'evo',
            'item']
            self.foreign = True
            self.save()

    def save(self):
        with open(self.path, 'w+') as f:
            json.dump(self.__dict__, f, indent=True)
            print "Saved config file to " + self.path
