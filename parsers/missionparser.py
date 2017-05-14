#!/usr/bin/python

from parsers.baseparser import BaseParser


class MissionParser(BaseParser):
    """Parser for mission data.

    Expects 'mission', 'dungeon', 'area', 'land', and 'dict' in the raw data.
    """

    required_data = ['mission', 'dungeon', 'area', 'land', 'dict']

    def __init__(self, **data):
        super(self.__class__, self).__init__(**data)
        self.file_name = "missions.json"

    def run(self):
        # Check if we have all the data we need
        if not all(name in self.data for name in self.required_data):
            raise AttributeError("Failed to find all required data")

        is_foreign = self.data['isForeign']
        self.parsed_data = {}
        lands = {}
        for land in self.data['land']:
            lands[land['9C64Qwe0']] = parse_land(
                land, land['9C64Qwe0'], self.data['dict'], is_foreign)

        areas = {}
        for area in self.data['area']:
            areas[area['VjCY7rX4']] = parse_area(
                area, area['VjCY7rX4'], lands, self.data['dict'], is_foreign)

        dungeons = {}
        for dungeon in self.data['dungeon']:
            dungeons[dungeon['MHx05sXt']] = parse_dungeon(
                dungeon, dungeon['MHx05sXt'], areas, lands, self.data['dict'], is_foreign)

        self.parsed_data = {}
        for mission in self.data['mission']:
            mission_data = parse_mission(
                mission, dungeons, areas, lands, self.data['dict'], is_foreign)
            self.parsed_data[mission_data['id']] = mission_data


def parse_land(land, id, dictionary, jp=True):
    data = {}
    if jp:
        data['name'] = dictionary.get(land['y1pHwW54'], land['y1pHwW54'])
        data['desc'] = dictionary.get(land['qp37xTDh'], land['qp37xTDh'])
    else:
        data['name'] = dictionary.get(
            'MST_DUNGEONS_CONTINENT_' + id + '_NAME', land['y1pHwW54'])
        data['desc'] = dictionary.get(
            'MST_DUNGEONS_CONTINENT_' + id + '_DESCRIPTION', land['qp37xTDh'])
    data['type'] = int(land['7Lx3qcDU'])
    data['x'] = int(land['SnNtTh51'])
    data['y'] = int(land['M6C1aXfR'])
    return data


def parse_area(area, id, lands, dictionary, jp=True):
    data = {}
    if jp:
        data['name'] = dictionary.get(area['V84mzqoX'], area['V84mzqoX'])
        data['desc'] = dictionary.get(area['qp37xTDh'], area['qp37xTDh'])
    else:
        data['name'] = dictionary.get(
            'MST_DUNGEONS_AREA_' + id + '_NAME', area['V84mzqoX'])
        data['desc'] = dictionary.get(
            'MST_DUNGEONS_AREA_' + id + '_DESCRIPTION', area['qp37xTDh'])
    data['land'] = land = lands.get(
        area['9C64Qwe0'], {'name': area['9C64Qwe0']})
    data['type'] = int(area['3v1qg7Uj'])
    return data


def parse_dungeon(dungeon, id, areas, lands, dictionary, jp=True):
    data = {}
    if jp:
        data['name'] = dictionary.get(dungeon['bWsLFP96'], dungeon['bWsLFP96'])
        data['desc'] = dictionary.get(dungeon['qp37xTDh'], dungeon['qp37xTDh'])
    else:
        data['name'] = dictionary.get(
            'MST_DUNGEONS_DUNGEON_' + id + '_NAME', dungeon['bWsLFP96'])
        data['desc'] = dictionary.get(
            'MST_DUNGEONS_DUNGEON_' + id + '_DESCRIPTION', dungeon['qp37xTDh'])
    data['land'] = lands.get(dungeon['9C64Qwe0'], {
                             'name': dungeon['9C64Qwe0']})
    data['area'] = areas.get(dungeon['VjCY7rX4'], {
                             'name': dungeon['VjCY7rX4']})
    data['type'] = int(dungeon['3hPeI1RV'])
    return data


def parse_mission(mission, dungeons, areas, lands, dictionary, jp=True):
    data = {}
    land = lands.get(mission['9C64Qwe0'], {'name': mission['9C64Qwe0']})
    area = areas.get(mission['VjCY7rX4'], {'name': mission['VjCY7rX4']})
    dungeon = dungeons.get(mission['MHx05sXt'], {'name': mission['MHx05sXt']})
    data['id'] = mission['j28VNcUW']
    if jp:
        data['name'] = dictionary.get(mission['0iAIR2LP'], mission['0iAIR2LP'])
        data['desc'] = dictionary.get(mission['qp37xTDh'], mission['qp37xTDh'])
    else:
        data['name'] = dictionary.get(
            'MST_DUNGEONS_MISSION_' + mission['j28VNcUW'] + '_NAME', mission['0iAIR2LP'])
        data['desc'] = dictionary.get(
            'MST_DUNGEONS_MISSION_' + mission['j28VNcUW'] + '_DESCRIPTION', mission['qp37xTDh'])
    data['dungeon'] = dungeon['name']
    data['area'] = area['name']
    data['land'] = land['name']
    data['difficulty'] = int(mission['24biyLHp'])
    data['battle_count'] = int(mission['69vnphig'])
    data['energy_use'] = int(mission['A8DEK5ob'])
    data['mimic_info'] = parse_mimic_info(mission['wHN6nfh9'])
    if mission['HSRhkf70'] != '0' and mission['HSRhkf70'] != '':
        data['requires'] = mission['HSRhkf70']
    data['xp'] = int(mission['d96tuT2E'])
    data['zel'] = int(mission['Rs7bCE3t'])
    data['karma'] = int(mission['HTVh8a65'])
    data['continue'] = mission['HeA4I2dN'] == '1'
    data['clear_bonus'] = parse_clear_bonus(mission['SiYs27Cj'])
    return data


def parse_clear_bonus(params):
    bonuses = {}
    rawbonuses = params.split(',')
    if (len(rawbonuses) != 5):
        return parse_new_clear_bonus(params)
    if rawbonuses[0] != '0':
        bonuses['zel'] = rawbonuses[0]
    if rawbonuses[1] != '0':
        bonuses['karma'] = rawbonuses[1]
    if rawbonuses[3] != '0':
        bonuses['gem'] = rawbonuses[3]
    if rawbonuses[2] != '0:0':
        parts = rawbonuses[2].split(':')
        bonuses['item'] = {'id': parts[0], 'count': parts[1]}
    if rawbonuses[4] != '0:0:0':
        parts = rawbonuses[4].split(':')
        bonuses['unit'] = {'id': parts[0], 'count': parts[1], 'type': parts[2]}
    return bonuses


def parse_new_clear_bonus(params):
    bonuses = []
    for bonus in params.split(','):
        param = bonus.split(':')
        if (len(param) < 3):
            continue
        bonusType = param[0]
        bonusParam = param[1]
        bonusCnt = param[2]
        if bonusType == '0':
            continue
        if bonusType == '1' or bonusType == '8':
            bonuses.append({'gem': bonusCnt})
        elif bonusType == '2':
            bonuses.append({'honor': bonusCnt})
        elif bonusType == '3':
            bonuses.append({'zel': bonusCnt})
        elif bonusType == '11':
            bonuses.append({'karma': bonusCnt})
        elif bonusType == '4' or bonusType == '5' or bonusType == '7':
            bonuses.append({'item': {'id': bonusParam, 'count': bonusCnt}})
        elif bonusType == '6':
            bonuses.append({'unit': {'id': bonusParam, 'count': bonusCnt}})
    return bonuses

# lots of randomness here
#[0] - something that influences randomness
#[1] - a chance modifier of some sort (chance +- ([1] % 120 + 2))
#[2]/[3] - <chance>:<monster_group>


def parse_mimic_info(param):
    data = {}
    parts = param.split(',')
    _1 = int(parts[0])
    _2 = float(parts[1])
    if _2 != 0:
        data['spawn_chance_range_maybe'] = str(
            _2) + '~' + str(_2 + ((_2 % 120) + 2) * 2)
        param1 = parts[2].split(':')
        data['group_1_monster_group'] = param1[1]
        data['group_1_chance'] = param1[0]
        param2 = parts[3].split(':')
        data['group_2_monster_group'] = param2[1]
        data['group_2_chance'] = param2[0]
    return data
