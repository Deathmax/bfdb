#!/usr/bin/python

from parsers.baseparser import BaseParser
from parsers.common.passives import parse_leader_skill


class LeaderSkillParser(BaseParser):
    """Parser for leader skill data.

    Expects 'leader skill' and 'dict' in the raw data.
    """

    required_data = ['leader skill', 'dict']

    def __init__(self, **data):
        super(self.__class__, self).__init__(**data)
        self.file_name = "ls.json"

    def run(self):
        # Check if we have all the data we need
        if not all(name in self.data for name in self.required_data):
            raise AttributeError("Failed to find all required data")

        is_foreign = self.data['isForeign']
        self.parsed_data = {}
        for ls_id in self.data['leader skill']:
            ls_data = parse_leader_skill(
                self.data['leader skill'][ls_id], self.data['dict'], is_foreign)
            self.parsed_data[ls_id] = ls_data
