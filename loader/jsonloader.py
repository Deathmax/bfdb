import glob
import json
import os
import io

class JsonLoader:
    @staticmethod
    def loadjsonfiles(**parameter_list):
        loadedfiles = {}
        for typename, data in parameter_list.iteritems():
            loader = JsonLoader(typename, **data)
            loader.loadfile()
            # Check if we loaded the file
            if loader.json != None:
                loadedfiles[typename] = loader
        return loadedfiles


    def __init__(self, typename, filename, idkey=None):
        self.typename = typename
        self.filename = filename
        self.idkey = idkey
        self.json = None

    @staticmethod
    def key_by_id(lst, id_str):
        return {obj[id_str]: obj for obj in lst}

    def loadfile(self):
        try:
            print "loading " + self.typename
            with open(max(glob.iglob(self.filename), key=os.path.getctime)) as f:
                if f.name.split('.')[-1] == 'txt' or f.name.split('.')[-1] == 'csv':
                    self.json = dict([
                        line.split('^')[:2] for line in f.readlines()  if len(line.split('^')) >= 2
                    ])
                else:
                    self.json = json.load(f)
                    if self.idkey != None:
                        self.json = JsonLoader.key_by_id(self.json, self.idkey)
        except (ValueError, IOError):
            print "Failed to load " + self.filename
