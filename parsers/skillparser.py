#!/usr/bin/python

from parsers.baseparser import BaseParser
from parsers.common.skills import parse_skill
import os
import json
from utils.to_json import IndentlessEncoder


class SkillParser(BaseParser):
    """Parser for skill data.

    Expects 'skills', 'bbs' and 'dict' in the raw data.
    """

    required_data = ['skill', 'skill level', 'dict']

    def __init__(self, **data):
        super(self.__class__, self).__init__(**data)
        self.file_name = "bbs_"

    def run(self):
        # Check if we have all the data we need
        if not all(name in self.data for name in self.required_data):
            raise AttributeError("Failed to find all required data")

        is_foreign = self.data['isForeign']
        self.parsed_data = {}
        for skill_id in self.data['skill']:
            if skill_id not in self.data['skill level']:
                print ('Warning: skill level data missing for', skill_id)
                continue
            skill_data = parse_skill(
                self.data['skill'][skill_id], self.data['skill level'][skill_id], self.data['dict'], is_foreign, id=skill_id)
            self.parsed_data[skill_id] = skill_data

    def save(self, directory):
        """Saves parsed data into directory

        Args:
            directory: Directory to save JSON data in
        """
        print "Saving {} elements".format(len(self.parsed_data))
        for starting_index in range(0, 10):
            json_str = json.dumps(dict((k, v) for k, v in self.parsed_data.items() if k.startswith(str(starting_index))),
                                sort_keys=True,
                                indent=4,
                                cls=IndentlessEncoder,
                                ensure_ascii=False).encode('utf8').replace('\"\\\"[', '[').replace(']\\\"\"', ']')
            with open(os.path.join(os.path.normcase(directory), self.file_name + str(starting_index)) + '.json', 'w+') as f:
                f.write(json_str)
