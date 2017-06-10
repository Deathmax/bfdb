import json
import uuid

class NoIndent(object):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        if not isinstance(self.value, (list, tuple)):
            return repr(self.value)
        else:  # assume it's a list or tuple of coordinates stored as dicts
            delimiters = '[]' if isinstance(self.value, list) else '()'
            return delimiters[0] + ', '.join(self.getStr(x) for x in self.value) + delimiters[1]
    def getStr(self, x):
        if type(x) is not int:
            return 'herpderp123' + str(x) + 'herpderp123'
        else:
            return str(x)

class IndentlessEncoder(json.JSONEncoder):
    def encode(self, o):
        result = json.JSONEncoder.encode(self, o)
        return result.replace('herpderp123', '""')
    def default(self, obj):
        return(repr(obj) if isinstance(obj, NoIndent) else
               json.JSONEncoder.default(self, obj))
