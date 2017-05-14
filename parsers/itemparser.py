#!/usr/bin/python

from parsers.baseparser import BaseParser
from parsers.common.items import parse_item

class ItemParser(BaseParser):
    """Parser for item data.

    Expects 'items' and 'dict' in the raw data. 

    Optional data include either 'recipe_f' or 'recipe_m'.
    """

    required_data = ['items', 'dict']

    def __init__(self, **data):
        super(self.__class__, self).__init__(**data)
        self.file_name = "items.json"

    def run(self):
        # Check if we have all the data we need
        if not all(name in self.data for name in self.required_data):
            raise AttributeError("Failed to find all required data")

        recipes = None
        if 'recipe_f' in self.data:
            recipes = self.data['recipe_f']
        elif 'recipe_m' in self.data:
            recipes = self.data['recipe_m']

        if recipes == None:
            self.file_name = "items_light.json"

        is_foreign = self.data['isForeign']
        self.parsed_data = {}
        for item in self.data['items']:
            item_data = parse_item(item, recipes, self.data['dict'], is_foreign)
            self.parsed_data[str(item_data['id'])] = item_data
