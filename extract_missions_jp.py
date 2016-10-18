#!/usr/bin/python

import json
import glob
import sys


def parse_land(land, dictionary):
    data = dict()
    data['name'] = dictionary.get(land['y1pHwW54'], land['y1pHwW54'])
    data['desc'] = dictionary.get(land['qp37xTDh'], land['qp37xTDh'])
    data['type'] = int(land['7Lx3qcDU'])
    data['x'] = int(land['SnNtTh51'])
    data['y'] = int(land['M6C1aXfR'])
    return data

def parse_area(area, lands, dictionary):
    data = dict()
    data['name'] = dictionary.get(area['V84mzqoX'], area['V84mzqoX'])
    data['desc'] = dictionary.get(area['qp37xTDh'], area['qp37xTDh'])
    data['land'] = lands[area['9C64Qwe0']]
    data['type'] = int(area['3v1qg7Uj'])
    return data

def parse_dungeon(dungeon, areas, lands, dictionary):
    data = dict()
    data['name'] = dictionary.get(dungeon['bWsLFP96'], dungeon['bWsLFP96'])
    data['land'] = lands[dungeon['9C64Qwe0']]
    data['area'] = areas[dungeon['VjCY7rX4']]
    data['type'] = int(dungeon['3hPeI1RV'])
    data['desc'] = dictionary.get(dungeon['qp37xTDh'], dungeon['qp37xTDh'])
    return data

def parse_mission(mission, dungeons, areas, lands, dictionary):
    data = dict()
    land = lands[mission['9C64Qwe0']]
    area = areas.get(mission['VjCY7rX4'], {'name': mission['VjCY7rX4']})
    dungeon = dungeons[mission['MHx05sXt']]
    data['id'] = mission['j28VNcUW']
    data['name'] = dictionary.get(mission['0iAIR2LP'], mission['0iAIR2LP'])
    data['desc'] = dictionary.get(mission['qp37xTDh'], mission['qp37xTDh'])
    data['dungeon'] = dungeon['name']
    data['area'] = area['name']
    data['land'] = land['name']
    data['difficulty'] = int(mission['24biyLHp'])
    data['battle_count'] = int(mission['69vnphig'])
    data['energy_use'] = int(mission['A8DEK5ob'])
    data['mimic_info'] = parse_mimic_info(mission['wHN6nfh9'])
    return data

#lots of randomness here
#[0] - something that influences randomness
#[1] - a chance modifier of some sort (chance +- ([1] % 120 + 2))
#[2]/[3] - <chance>:<monster_group>
def parse_mimic_info(param):
    data = dict()
    parts = param.split(',')
    _1 = int(parts[0])
    _2 = float(parts[1])
    if _2 != 0:
        data['spawn_chance_range_maybe'] = str(_2) + '~' + str(_2 + ((_2 % 120) + 2)*2)
        param1 = parts[2].split(':')
        data['group_1_monster_group'] = param1[1]
        data['group_1_chance'] = param1[0]
        param2 = parts[3].split(':')
        data['group_2_monster_group'] = param2[1]
        data['group_2_chance'] = param2[0]
    return data

if __name__ == '__main__':
    with open(glob.glob('data/jp/decoded_dat/Ver*_4gA3WCQX.dat.json')[0]) as f:
        with open(glob.glob('data/jp/decoded_dat/23B40JNJT2.dat.json')[0]) as f3:
            with open(glob.glob('data/jp/decoded_dat/DH5H9MJ5XN.dat.json')[0]) as f4:
                with open(glob.glob('data/jp/decoded_dat/L0G2JKWH8Z.dat.json')[0]) as f5:
                    missions_js = json.load(f)
                    dungeons_js = json.load(f3)
                    areas_js = json.load(f4)
                    lands_js = json.load(f5)
                    dictionary = dict()

                    lands = dict()
                    for land in lands_js:
                        lands[land['9C64Qwe0']] = parse_land(land, dictionary)

                    areas = dict()
                    for area in areas_js:
                        areas[area['VjCY7rX4']] = parse_area(area, lands, dictionary)

                    dungeons = dict()
                    for dungeon in dungeons_js:
                        dungeons[dungeon['MHx05sXt']] = parse_dungeon(dungeon, areas, lands, dictionary)

                    missions_data = dict()
                    for mission in missions_js:
                        mission_data = parse_mission(mission, dungeons, areas, lands, dictionary)
                        #index = 2
                        #while mission_data['name'] in missions_data:
                        #    mission_data['name'] += '_'
                        #    ori = mission_data['name']
                        #    mission_data['name'] += ' ' + str(index)
                        #    if mission_data['name'] in missions_data:
                        #        mission_data['name'] = ori
                        #    else:
                        #        break
                        #    index += 1
                        #missions_data[mission_data['name']] = mission_data
                        #mission_data.pop('name')
                        missions_data[mission_data['id']] = mission_data

                    print json.dumps(missions_data, indent=4, sort_keys=True, ensure_ascii=False).encode('utf8')