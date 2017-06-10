"""Contains the base class BaseParser for all parsers
"""

import os
import json
from utils.to_json import IndentlessEncoder


class BaseParser(object):
    """Base class for which all the parsers should inherit.

    Attributes:
        data: A dictionary of raw data to feed into the parser
        parsed_data: A dictionary of parsed data
    """

    def __init__(self, **data):
        """Inits the parser with raw data"""
        self.data = data
        self.parsed_data = None
        self.file_name = None

    def run(self):
        """Runs the parser"""
        raise NotImplementedError

    def get_parsed_data(self):
        """
        Returns:
            Dictionary of data that has been parsed
        """
        return self.parsed_data

    def save(self, directory):
        """Saves parsed data into directory

        Args:
            directory: Directory to save JSON data in
        """
        print "Saving {} elements".format(len(self.parsed_data))
        json_str = json.dumps(self.parsed_data,
                              sort_keys=True,
                              indent=4,
                              cls=IndentlessEncoder,
                              ensure_ascii=False).encode('utf8').replace('""[', '[').replace(']""', ']')
        with open(os.path.join(os.path.normcase(directory), self.file_name), 'w+') as f:
            f.write(json_str)
