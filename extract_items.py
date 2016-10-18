#!/usr/bin/python

import json
import glob
import sys
import collections
import os
from util import *
from leaderskill import parse_ls_process
from items import *

def parse_item_effect(item, data, debug=False):
    effects = dict()
    effects['effect'] = []
    for process_type, process_info in zip(item[PROCESS_TYPE].split('@'), 
                                          item[ITEM_PROCESS].split('@')):
        #effects.update(parse_item_process(process_type, process_info))
        effects['effect'].append(parse_item_process(process_type, process_info, debug))
    if item[ITEM_TARGET_TYPE] == '2':
        effects['target_type'] = 'enemy'
    else:
        effects['target_type'] = 'party'
    if item[ITEM_TARGET_AREA] == '1':
        effects['target_area'] = 'single'
    else:
        effects['target_area'] = 'aoe'
    return effects


def parse_sphere_effect(item, data, dictionary, debug=False):
    #effects = dict()
    effects = []
    for process_type, process_info in zip(item[PROCESS_TYPE].split('@'), 
                                          item[ITEM_PROCESS].split('@')):
        #effects.update(parse_ls_process(process_type, process_info))
        effects.append(parse_ls_process(process_type, process_info, debug))
    return effects


def get_recipe(item_id, recipes):
    recipe_data = recipes.get(item_id, None)
    if recipe_data == None:
        return None
    data = dict()
    data['karma'] = recipe_data[RECIPE_KARMA]
    data['materials'] = [
                         {'id': int(mat.split(':')[0]), 'count': int(mat.split(':')[1])} 
                         for mat in recipe_data[RECIPE_MATERIALS].split(',')
                        ]
    return data


def parse_item(item, recipes, dictionary, jp=True, debug=False):
    def get_dict_str(s):
        return dictionary.get(s, s)

    def get_name(data):
        return {'name': get_item_name(dictionary, data[ITEM_ID], data[ITEM_NAME], jp)}

    def get_desc(data):
        return {'desc': get_item_desc(dictionary, data[ITEM_ID], data[DESC], jp)}

    def parse_type(item_data):
        data = dict()
        item_type = item_data[ITEM_TYPE]
        if item_type == '0':
            data['type'] = 'other'
        elif item_type == '1':
            data['type'] = 'consumable'
            data['max equipped'] = int(item[ITEM_MAX_EQUIPPED])
            data['effect'] = parse_item_effect(item_data, data, debug)
        elif item_type == '2':
            data['type'] = 'material'
        elif item_type == '3':
            data['type'] = 'sphere'
            data['effect'] = parse_sphere_effect(item_data, data, dictionary, debug)
        elif item_type == '4':
            data['type'] = 'evomat'
        if recipes != None:
            recipe = get_recipe(item_data[ITEM_ID], recipes)
            if recipe != None:
                data['recipe'] = recipe
        return data

    item_format = ((get_name),
                   (get_desc),
                   (ITEM_RARITY, 'rarity', int),
                   (ITEM_SELL_PRICE, 'sell_price', int),
                   (ITEM_MAX_STACK, 'max_stack', int),
                   (ITEM_ID, 'id', int),
                   (ITEM_TYPE, 'type', item_types.get),
                   (ITEM_THUMB, 'thumbnail', str),
                   (ITEM_KIND, 'sphere type', int, not_zero),
                   (ITEM_KIND, 'sphere type text', item_kinds.get, not_zero),
                   (ITEM_RAIDFLG, 'raid', bool_str.get),
                   (parse_type))

    return handle_format(item_format, item)


if __name__ == '__main__':
    _dir = 'data/decoded_dat/'
    dict_file = 'data/dictionary_raw.txt'
    if len(sys.argv) > 1:
        _dir = sys.argv[1]
    if len(sys.argv) > 2:
        dict_file = sys.argv[2]

    files = {
        'dict': dict_file,
        'unit':         _dir + 'Ver*_2r9cNSdt*',
        'skill level':  _dir + 'Ver*_zLIvD5o2*',
        'skill':        _dir + 'Ver*_wkCyV73D*',
        'leader skill': _dir + 'Ver*_4dE8UKcw*',
        'ai':           _dir + 'Ver*_XkBhe70R*',
        'items':        _dir + 'Ver*_83JWTCGy*',
    }

    jsons = {}
    light = False

    if 'light' not in sys.argv:
        if 'legacy' in sys.argv:
            files.update({'recipe': _dir + '7DKCJFK1J7*'})
            files.update({'town': _dir + 'RYCOS1SH7L*'})
        else:
            if os.path.exists(_dir + '../F_RECIPE_MST.json'):
                files.update({'recipe': _dir + '../F_RECIPE_MST.json'})
            else:
                files.update({'recipe': _dir + '../M_RECIPE_MST.json'})
            files.update({'town': _dir + '../M_TOWN_FACILITY_LV_MST.json'})
    else:
        jsons['recipe'] = None
        jsons['town'] = None
        light = True

    for name, filename in files.iteritems():
        try:
            with open(max(glob.iglob(filename), key=os.path.getctime)) as f:
                if f.name.split('.')[-1] == 'txt' or f.name.split('.')[-1] == 'csv':
                    jsons[name] = dict([
                        line.split('^')[:2] for line in f.readlines()  if len(line.split('^')) >= 2
                    ])
                else:
                    jsons[name] = json.load(f)
        except Exception, e:
            pass

    def key_by_id(lst, id_str):
        if lst != None:
            return {obj[id_str]: obj for obj in lst}
        else:
            return None

    skills = key_by_id(jsons['skill'], BB_ID)
    bbs = key_by_id(jsons['skill level'], BB_ID)
    leader_skills = key_by_id(jsons['leader skill'], LS_ID)
    recipes = key_by_id(jsons['recipe'], RECIPE_ITEM_ID)

    items_data = {}
    for item in jsons['items']:
        item_data = parse_item(item, recipes, jsons['dict'], 'jp' in sys.argv, 'debug' in sys.argv)
        #items_data[item_data['name']] = item_data
        #item_data.pop('name')
        items_data[str(item_data['id'])] = item_data

    if 'jp' in sys.argv:
        print json.dumps(items_data, sort_keys=True, indent=4, ensure_ascii=False).encode('utf8')
    else:
        print json.dumps(items_data, sort_keys=True, indent=4)