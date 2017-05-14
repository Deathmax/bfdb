#!/usr/bin/python

from parsers.baseparser import BaseParser
from parsers.common.ai import merge_action_data


class AiParser(BaseParser):
    """Parser for AI data.

    Expects 'ai', and 'dict' in the raw data.

    Does not work with EU's custom AI format
    """

    required_data = ['ai', 'dict']

    def __init__(self, **data):
        super(self.__class__, self).__init__(**data)
        self.file_name = "ai.json"

    def run(self):
        # Check if we have all the data we need
        if not all(name in self.data for name in self.required_data):
            raise AttributeError("Failed to find all required data")

        self.parsed_data = merge_action_data(self.data['ai'])
