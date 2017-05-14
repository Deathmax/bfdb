#!/usr/bin/python

from parsers.baseparser import BaseParser
from parsers.common.evos import parse_unit, parse_evo, parse_item


class EvoParser(BaseParser):
    """Parser for evolution data.

    Expects 'unit', 'evo', 'items' and 'dict' in the raw data.
    """

    required_data = ['unit', 'evo', 'items', 'dict']

    def __init__(self, **data):
        super(self.__class__, self).__init__(**data)
        self.file_name = "evo_list.json"

    def run(self):
        # Check if we have all the data we need
        if not all(name in self.data for name in self.required_data):
            raise AttributeError("Failed to find all required data")

        is_foreign = self.data['isForeign']
        units_data = {}
        for unit in self.data['unit']:
            unit_data = parse_unit(unit, self.data['dict'], is_foreign)
            units_data[unit_data['id']] = unit_data

        items_data = {}
        for item in self.data['items']:
            item_data = parse_item(item, self.data['dict'], is_foreign)
            items_data[item_data['id']] = item_data

        evos_data = {}
        for evo in self.data['evo']:
            evo_data = parse_evo(evo, units_data, items_data, self.data['dict'])
            evos_data[evo_data['unit_id']] = evo_data
            evo_data.pop('unit_id')

        self.parsed_data = evos_data

