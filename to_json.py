import json

class NoIndent(object):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        if not isinstance(self.value, (list, tuple)):
            return repr(self.value)
        else:  # assume it's a list or tuple of coordinates stored as dicts
            delimiters = '[]' if isinstance(self.value, list) else '()'
            return delimiters[0] + ', '.join(str(x) for x in self.value) + delimiters[1]

class IndentlessEncoder(json.JSONEncoder):
    def default(self, obj):
        return(repr(obj) if isinstance(obj, NoIndent) else
               json.JSONEncoder.default(self, obj))