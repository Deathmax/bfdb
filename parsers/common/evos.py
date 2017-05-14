from utils.util import *


def parse_unit(unit, dictionary, jp=True):
    data = dict()

    data['name'] = get_unit_name(
        dictionary, unit[UNIT_ID], jp)(unit[UNIT_NAME])
    data['rarity'] = int(unit[UNIT_RARITY])
    data['id'] = unit[UNIT_ID]
    data['guide_id'] = int(unit[UNIT_GUIDE_ID])
    data['exp_pattern'] = int(unit[UNIT_EXP_PATTERN_ID])
    data['type'] = 'unit'

    return data


def parse_item(unit, dictionary, jp=True):
    data = dict()

    # dictionary.get(unit['c7Z6xDB2'], unit['c7Z6xDB2'])
    data['name'] = get_item_name(
        dictionary, unit['kixHbe54'], unit['c7Z6xDB2'], jp)
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
                   'id': int(evo[EVO_UNIT_ID])}
    data['amount'] = int(evo[EVO_AMOUNT])
    data['mats'] = []
    idx = 0
    if EVO_MAT_IDS[0] in evo:
        for mat_id in EVO_MAT_IDS:
            if evo[mat_id] != None and int(evo[mat_id]) != 0:
                mat_unit = units.get(
                    evo[mat_id], {'name': evo[mat_id], 'id': evo[mat_id]})
                data['mats'].append(
                    {'name': mat_unit['name'], 'id': mat_unit['id']})
    else:
        for mat_id in EVO_JP_MAT_IDS:
            if mat_id in evo and evo[mat_id] != None and int(evo[mat_id]) != 0:
                mat_unit = {}
                if int(evo[EVO_JP_MAT_TYPES[idx]]) == 1:
                    mat_unit = units.get(
                        evo[mat_id], {'name': evo[mat_id], 'id': evo[mat_id], 'type': 'unit'})
                elif int(evo[EVO_JP_MAT_TYPES[idx]]) == 2:
                    mat_unit = items.get(
                        evo[mat_id], {'name': evo[mat_id], 'id': evo[mat_id], 'type': 'item'})
                else:
                    mat_unit = {'name': evo[mat_id],
                                'id': evo[mat_id], 'type': 'unk'}
                data['mats'].append(
                    {'name': mat_unit['name'], 'id': mat_unit['id'], 'type': mat_unit['type']})
            idx += 1
    return data
