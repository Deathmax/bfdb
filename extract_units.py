#!/usr/bin/python

import collections
import glob
import json
import sys
from to_json import *
from util import *
from leaderskill import parse_leader_skill
from braveburst import parse_skill


def parse_unit(unit, skills, bbs, leader_skills, ais, dictionary):
    def max_bc_gen(s, data):
        return int(s) * data['hits']

    def _damage_range(s):
        return '~'.join(map(str, damage_range(int(s))))

    def _parse_skill(bb_id, data):
        return parse_skill(data, skills[bb_id], bbs[bb_id], dictionary)

    def parse_ls(ls_id, data):
        return parse_leader_skill(data, leader_skills[ls_id], dictionary)

    def get_stats(process_info):
        data = dict()
        max_level = int(process_info[UNIT_MAX_LEVEL]) - 1
        data['base'] = {
            'hp': int(process_info[UNIT_BASE_HP]),
            'atk': int(process_info[UNIT_BASE_ATK]),
            'def': int(process_info[UNIT_BASE_DEF]),
            'rec': int(process_info[UNIT_BASE_REC])
        }
        data['lord'] = {
            'hp': int(process_info[UNIT_LORD_HP]),
            'atk': int(process_info[UNIT_LORD_ATK]),
            'def': int(process_info[UNIT_LORD_DEF]),
            'rec': int(process_info[UNIT_LORD_REC])
        }
        data['anima'] = {
            'hp min': int(process_info[UNIT_LORD_HP]) + max_level*5,
            'hp max': int(process_info[UNIT_LORD_HP]) + max_level*10,
            'rec min': int(process_info[UNIT_LORD_REC]) - max_level*3,
            'rec max': int(process_info[UNIT_LORD_REC]) - max_level*1,
            'atk': int(process_info[UNIT_BASE_ATK]),
            'def': int(process_info[UNIT_BASE_DEF]),
        }
        data['breaker'] = {
            'atk min': int(process_info[UNIT_LORD_ATK]) + max_level*1,
            'atk max': int(process_info[UNIT_LORD_ATK]) + max_level*3,
            'def min': int(process_info[UNIT_LORD_DEF]) - max_level*3,
            'def max': int(process_info[UNIT_LORD_DEF]) - max_level*1,
            'hp': int(process_info[UNIT_BASE_HP]),
            'rec': int(process_info[UNIT_BASE_REC])
        }
        data['guardian'] = {
            'atk min': int(process_info[UNIT_LORD_ATK]) - max_level*3,
            'atk max': int(process_info[UNIT_LORD_ATK]) - max_level*1,
            'def min': int(process_info[UNIT_LORD_DEF]) + max_level*1,
            'hp': int(process_info[UNIT_BASE_HP]),
            'rec': int(process_info[UNIT_BASE_REC]),
            'def max': int(process_info[UNIT_LORD_DEF]) + max_level*3,
        }
        data['oracle'] = {
            'hp min': int(process_info[UNIT_LORD_HP]) - max_level*4,
            'hp max': int(process_info[UNIT_LORD_HP]) - max_level*2,
            'rec min': int(process_info[UNIT_LORD_REC]) + max_level*2,
            'rec max': int(process_info[UNIT_LORD_REC]) + max_level*4,
            'atk': int(process_info[UNIT_BASE_ATK]),
            'def': int(process_info[UNIT_BASE_DEF]),
        }
        return {'stats': data}

    unit_format = ((UNIT_NAME, 'name', get_dict_str(dictionary)),
                   (UNIT_ELEMENT, 'element', elements.get),
                   (UNIT_RARITY, 'rarity', int),
                   #(UNIT_BASE_HP, 'base hp', int),
                   #(UNIT_LORD_HP, 'lord hp', int),
                   #(UNIT_BASE_ATK, 'base atk', int),
                   #(UNIT_LORD_ATK, 'lord atk', int),
                   #(UNIT_BASE_DEF, 'base def', int),
                   #(UNIT_LORD_DEF, 'lord def', int),
                   #(UNIT_BASE_REC, 'base rec', int),
                   #(UNIT_LORD_REC, 'lord rec', int),
                   (get_stats),
                   (DMG_FRAME, 'hits', hits),
                   (DMG_FRAME, 'hit dmg% distribution', hit_dmg_dist),
                   (DMG_FRAME, 'hit dmg% distribution (total)', hit_dmg_dist_total),
                   (DROP_CHECK_CNT, 'max bc generated', max_bc_gen),
                   (UNIT_LORD_ATK, 'lord damage range', _damage_range),
                   (UNIT_AI_ID, 'ai', ais.get),
                   (UNIT_IMP, 'imp', lambda s: parse_imps(s.split(':'))),
                   (BB_ID, 'bb', _parse_skill, not_zero),
                   (SBB_ID, 'sbb', _parse_skill, not_zero),
                   (LS_ID, 'leader skill', parse_ls, not_zero),
                   (UNIT_ID, 'id', int),
                   (UNIT_GUIDE_ID, 'guide_id', int),
                   (UNIT_EXP_PATTERN_ID, 'exp_pattern', int))

    return handle_format(unit_format, unit)


def parse_ai(ai):
    ai_format = ((AI_ID, 'id', str),
                 (AI_CHANCE, 'chance%', float),
                 (AI_TARGET, 'target', str),
                 (AI_ACTION_PARAMS, 'action', lambda s: s.split('@')[0]))

    return handle_format(ai_format, ai)

if __name__ == '__main__':
    _dir = 'data/decoded_dat/'
    if len(sys.argv) > 1:
        _dir = sys.argv[1]

    files = {
        'dict': 'data/dictionary_raw.txt',
        'unit':         _dir + 'Ver*_2r9cNSdt*',
        'skill level':  _dir + 'Ver*_zLIvD5o2*',
        'skill':        _dir + 'Ver*_wkCyV73D*',
        'leader skill': _dir + 'Ver*_4dE8UKcw*',
        'ai':           _dir + 'Ver*_XkBhe70R*',
    }

    jsons = {}
    for name, filename in files.iteritems():
        with open(glob.glob(filename)[-1]) as f:
            if f.name.split('.')[-1] == 'txt':
                jsons[name] = dict([
                    line.split('^')[:2] for line in f.readlines()
                ])
            else:
                jsons[name] = json.load(f)

    def key_by_id(lst, id_str):
        return {obj[id_str]: obj for obj in lst}

    skills = key_by_id(jsons['skill'], BB_ID)
    skill_levels = key_by_id(jsons['skill level'], BB_ID)
    leader_skills = key_by_id(jsons['leader skill'], LS_ID)

    ais = collections.defaultdict(list)
    for ai in jsons['ai']:
        ai_data = parse_ai(ai)
        ais[ai_data['id']].append(ai_data)
        ai_data.pop('id')

    units_data = {}
    for unit in jsons['unit']:
        unit_data = parse_unit(unit, skills, skill_levels, leader_skills,
                               ais, jsons['dict'])
        unit_data['hit dmg% distribution'] = NoIndent(unit_data['hit dmg% distribution'])
        if unit_data['name'] in units_data:
          unit_data['name'] += ' (' + str(unit_data['rarity']) + '*)'
        units_data[unit_data['name']] = unit_data
        unit_data.pop('name')

    if 'jp' in sys.argv:
        print json.dumps(units_data, 
                         sort_keys=True, 
                         indent=4, 
                         cls=IndentlessEncoder, 
                         ensure_ascii=False).encode('utf8').replace('"[', '[').replace(']"', ']')
    else:
        print json.dumps(units_data, 
                         sort_keys=True, 
                         indent=4, 
                         cls=IndentlessEncoder).replace('"[', '[').replace(']"', ']')
