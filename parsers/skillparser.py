#!/usr/bin/python

from parsers.baseparser import BaseParser
from parsers.common.skills import parse_skill


class SkillParser(BaseParser):
    """Parser for skill data.

    Expects 'skills', 'bbs' and 'dict' in the raw data.
    """

    required_data = ['skill', 'skill level', 'dict']

    def __init__(self, **data):
        super(self.__class__, self).__init__(**data)
        self.file_name = "bbs.json"

    def run(self):
        # Check if we have all the data we need
        if not all(name in self.data for name in self.required_data):
            raise AttributeError("Failed to find all required data")

        is_foreign = self.data['isForeign']
        self.parsed_data = {}
        for skill_id in self.data['skill']:
            skill_data = parse_skill(
                self.data['skill'][skill_id], self.data['skill level'][skill_id], self.data['dict'], is_foreign)
            self.parsed_data[skill_id] = skill_data
