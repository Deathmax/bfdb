#!/usr/bin/python

from parsers.baseparser import BaseParser
from parsers.common.feskills import parse_category, parse_fe_skill, parse_unit_skill
from utils.util import *


class FeSkillParser(BaseParser):
    """Parser for fe skill data.

    Expects 'fe skill', 'unit fe skill', 'unit fe cat' and 'dict' in the raw data.
    """

    required_data = ['extra skill', 'dict']

    def __init__(self, **data):
        super(self.__class__, self).__init__(**data)
        self.file_name = "feskills.json"

    def run(self):
        # Check if we have all the data we need
        if not all(name in self.data for name in self.required_data):
            raise AttributeError("Failed to find all required data")

        is_foreign = self.data['isForeign']
        self.parsed_data = {}

        fe_skills_data = {}
        for fe_id in self.data['fe skill']:
            ls_data = parse_fe_skill(
                self.data['fe skill'][fe_id], self.data['dict'], jp=is_foreign, id=fe_id)
            fe_skills_data[fe_id] = ls_data

        self.parsed_data = {}
        for unit_skill in self.data['unit fe skill']:
            if unit_skill[UNIT_ID] in self.parsed_data:
                self.parsed_data[unit_skill[UNIT_ID]]['skills'].append(
                    parse_unit_skill(unit_skill, fe_skills_data))
            else:
                self.parsed_data[unit_skill[UNIT_ID]] = {
                    'skills': [], 'category': {}}
                self.parsed_data[unit_skill[UNIT_ID]]['skills'].append(
                    parse_unit_skill(unit_skill, fe_skills_data))

        for category in self.data['unit fe cat']:
            self.parsed_data[category[UNIT_ID]
                             ]['category'][category[FE_CAT_ID]] = parse_category(category)
