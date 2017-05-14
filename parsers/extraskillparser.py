#!/usr/bin/python

from parsers.baseparser import BaseParser
from parsers.common.passives import parse_extra_skill


class ExtraSkillParser(BaseParser):
    """Parser for extra skill data.

    Expects 'extra skill', and 'dict' in the raw data.
    """

    required_data = ['extra skill', 'dict']

    def __init__(self, **data):
        super(self.__class__, self).__init__(**data)
        self.file_name = "es.json"

    def run(self):
        # Check if we have all the data we need
        if not all(name in self.data for name in self.required_data):
            raise AttributeError("Failed to find all required data")

        is_foreign = self.data['isForeign']
        self.parsed_data = {}
        for es_id in self.data['extra skill']:
            es_data = parse_extra_skill(
                self.data['extra skill'][es_id], self.data['dict'], is_foreign)
            self.parsed_data[es_id] = es_data
