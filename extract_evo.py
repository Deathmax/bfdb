#!/usr/bin/python

import json
import glob
import sys
import os
from util import *

UNIT_NAME = 'utP1c0CD'
UNIT_ELEMENT = 'iNy0ZU5M'
UNIT_RARITY = '7ofj5xa1'
UNIT_BASE_HP = 'UZ1Bj7w2'
UNIT_LORD_HP = '3WMz78t6'
UNIT_BASE_ATK = 'i9Tn7kYr'
UNIT_LORD_ATK = 'omuyP54D'
UNIT_BASE_DEF = 'q78KoWsg'
UNIT_LORD_DEF = '32INDST4'
UNIT_BASE_REC = '92ij6UGB'
UNIT_LORD_REC = 'X9P3AN5d'
UNIT_IMP = 'imQJdg64'
UNIT_ID = 'pn16CNah'
UNIT_GUIDE_ID = 'XuJL4pc5'
UNIT_EXP_PATTERN_ID = '5UvTp7q1'
EVO_UNIT_ID = '74VFwuTd'
EVO_TYPE = 'dV3qji4I'
EVO_AMOUNT = 'Rs7bCE3t'
EVO_MAT_IDS = ['5it4IozN',
               'p5ZhN6Lk',
               '5F1qmcgX',
               'RHo1m0f6',
               'r9SEG7tR']
EVO_JP_MAT_TYPES = ['Xyt6rhx2',
                    '0tna4Idu',
                    '6GwnugW3',
                    'hdF8ND2H',
                    'nB7pFdR0',
                    'IZUvR489',
                    'bNRUuatB',
                    '2BFgYLjg',
                    '18Oz7z8k',
                    'EK7jR4rB']
EVO_JP_MAT_IDS = ['85X6JHQA',
                  'wh3YRU08',
                  '7MxucW2J',
                  'j7fTS3ca',
                  'Hb8yfmv7',
                  'Voht18AP',
                  '3g8brFoq',
                  'agp4CKEV',
                  'eKPWNoLn',
                  'MVidsUNV']


def get_unit_name(dictionary, name, id, jp=True):
    if jp:
        return dictionary.get(name, name)
    else:
        return dictionary.get('MST_UNIT_' + id + '_NAME', name)


def parse_unit(unit, dictionary, jp=True):
    data = dict()

    data['name'] = get_unit_name(dictionary, unit[UNIT_NAME], unit[UNIT_ID], jp)#dictionary.get(unit[UNIT_NAME], unit[UNIT_NAME])
    data['rarity'] = int(unit[UNIT_RARITY])
    data['id'] = unit[UNIT_ID]
    data['guide_id'] = int(unit[UNIT_GUIDE_ID])
    data['exp_pattern'] = int(unit[UNIT_EXP_PATTERN_ID])
    data['type'] = 'unit'

    return data

def parse_item(unit, dictionary, jp=True):
    data = dict()

    data['name'] = get_item_name(dictionary, unit['kixHbe54'], unit['c7Z6xDB2'], jp)#dictionary.get(unit['c7Z6xDB2'], unit['c7Z6xDB2'])
    data['id'] = unit['kixHbe54']
    data['type'] = 'item'

    return data


def parse_evo(evo, units, items, dictionary):
    data = dict()

    unit = units.get(evo[UNIT_ID], {'name': UNIT_ID, 'rarity': 0})
    evo_unit = units.get(evo[EVO_UNIT_ID], {'name': EVO_UNIT_ID, 'rarity': 0})
    data['name'] = unit['name']
    data['rarity'] = unit['rarity']
    data['unit_id'] = int(evo[UNIT_ID])
    data['evo'] = {'name': evo_unit['name'],
                   'rarity': evo_unit['rarity'],
                   'id':int(evo[EVO_UNIT_ID])}
    data['amount'] = int(evo[EVO_AMOUNT])
    data['mats'] = []
    idx = 0
    if EVO_MAT_IDS[0] in evo:
        for mat_id in EVO_MAT_IDS:
            if evo[mat_id] != None and int(evo[mat_id]) != 0:
                mat_unit = units.get(evo[mat_id], {'name': evo[mat_id], 'id': evo[mat_id]})
                data['mats'].append({'name': mat_unit['name'], 'id': mat_unit['id']})
    else:
        for mat_id in EVO_JP_MAT_IDS:
            if mat_id in evo and evo[mat_id] != None and int(evo[mat_id]) != 0:
                mat_unit = {}
                if int(evo[EVO_JP_MAT_TYPES[idx]]) == 1:
                    mat_unit = units.get(evo[mat_id], {'name': evo[mat_id], 'id': evo[mat_id], 'type': 'unit'})
                elif int(evo[EVO_JP_MAT_TYPES[idx]]) == 2:
                    mat_unit = items.get(evo[mat_id], {'name': evo[mat_id], 'id': evo[mat_id], 'type': 'item'})
                else:
                    mat_unit = {'name': evo[mat_id], 'id': evo[mat_id], 'type': 'unk'}
                data['mats'].append({'name': mat_unit['name'], 'id': mat_unit['id'], 'type': mat_unit['type']})
            idx += 1
    return data


if __name__ == '__main__':
    subdirectory = 'data/decoded_dat/'
    dict_file = 'data/dictionary_raw.txt'
    if len(sys.argv) > 1:
        subdirectory = sys.argv[1]
    if len(sys.argv) > 2:
        dict_file = sys.argv[2]
    isJp = False
    if 'jp' in sys.argv:
        isJp = True
    with open(max(glob.iglob(subdirectory + 'Ver*_2r9cNSdt*'), key=os.path.getctime)) as f:
        with open(max(glob.iglob(dict_file), key=os.path.getctime)) as f2:
            with open(max(glob.iglob(subdirectory + 'Ver*_Ef6oG0mz*'), key=os.path.getctime)) as f3:
                with open(max(glob.iglob(subdirectory + 'Ver*_83JWTCGy*'), key=os.path.getctime)) as f4:
                    units = json.load(f)
                    dictionary = dict([line.split('^')[:2] for line in f2.readlines() if len(line.split('^')) >= 2])
                    evo_js = json.load(f3)
                    items_js = json.load(f4)
    
                    units_data = {}
                    for unit in units:
                        unit_data = parse_unit(unit, dictionary, isJp)
                        units_data[unit_data['id']] = unit_data

                    items_data = {}
                    for item in items_js:
                        item_data = parse_item(item, dictionary, isJp)
                        items_data[item_data['id']] = item_data
    
                    evos_data = dict()
                    for evo in evo_js:
                        evo_data = parse_evo(evo, units_data, items_data, dictionary)
                        evos_data[evo_data['unit_id']] = evo_data
                        evo_data.pop('unit_id')

    
                    if 'jp' in subdirectory:
                        print json.dumps(evos_data, indent=4, sort_keys=True, ensure_ascii=False).encode('utf8')
                    else:
                        print json.dumps(evos_data, indent=4, sort_keys=True).encode('utf8')