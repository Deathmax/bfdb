#!/usr/bin/python

import collections
import glob
import json
import sys
import os
import re
import requests
from to_json import *
from util import *
from leaderskill import parse_leader_skill
from leaderskill import parse_extra_skill
from braveburst import parse_skill

reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')


def search_units(search_id, units_data):
    prog = re.compile(search_id)
    units = []
    for unit_id, unit_data in units_data.items():
        if prog.match(unit_id):
            units.append(unit_data)
    return units

def search_units_by_category(search_id, units_data):
    units = []
    for unit_id, unit_data in units_data.items():
        if str(unit_data['category']) == search_id:
            units.append(unit_data)
    return units


def parse_unit(unit, skills, bbs, leader_skills, ais, extra_skills, unit_types, dictionary, jp=True, debug=False):
    def max_bc_gen(s, data):
        return int(s) * data['damage frames']['hits']

    def _damage_range(s):
        return '~'.join(map(str, damage_range(int(s))))

    def _parse_skill(bb_id, data):
        if bb_id not in skills or bb_id not in bbs:
            return {'error': 'data missing', 'id': bb_id}
        return parse_skill(data, skills[bb_id], bbs[bb_id], dictionary, jp, debug, bb_id)

    def _parse_ubb(bb_id, data):
        data = _parse_skill(bb_id, data)
        if 'levels' in data:
            rtn = []
            rtn.append(data['levels'][0])
            data['levels'] = rtn
        return data

    def parse_ls(ls_id, data):
        if ls_id not in leader_skills:
            return {'error': 'data missing', 'id': ls_id}
        return parse_leader_skill(data, leader_skills[ls_id], dictionary, jp, debug, ls_id)

    def _parse_extra(extra_id, data):
        if extra_skills != {}:
            if extra_id not in extra_skills:
                return {'error': 'data missing', 'id': extra_id}
            return parse_extra_skill(data, extra_skills[extra_id], dictionary, jp, debug, extra_id)
        else:
            return {'error': 'data missing'}

    def get_name(data):
        return {'name': get_unit_name(dictionary, data[UNIT_ID], jp)(data[UNIT_NAME])}

    def get_stats(process_info):
        data = dict()
        max_level = int(process_info[UNIT_MAX_LEVEL]) - 1
        data['_base'] = {
            'hp': int(process_info[UNIT_BASE_HP]),
            'atk': int(process_info[UNIT_BASE_ATK]),
            'def': int(process_info[UNIT_BASE_DEF]),
            'rec': int(process_info[UNIT_BASE_REC])
        }
        data['_lord'] = {
            'hp': int(process_info[UNIT_LORD_HP]),
            'atk': int(process_info[UNIT_LORD_ATK]),
            'def': int(process_info[UNIT_LORD_DEF]),
            'rec': int(process_info[UNIT_LORD_REC])
        }
        data['anima'] = get_specific_stat(process_info, '2')
        data['breaker'] = get_specific_stat(process_info, '3')
        data['guardian'] = get_specific_stat(process_info, '4')
        data['oracle'] = get_specific_stat(process_info, '5')
        return {'stats': data}

    def get_specific_stat(process_info, unit_type):
        max_level = int(process_info[UNIT_MAX_LEVEL]) - 1
        type_data = unit_types[unit_type]
        data = {}
        if type_data[UNITTYPE_HP] != '0,0':
            parts = type_data[UNITTYPE_HP].split(',')
            data['hp min'] = int(process_info[UNIT_LORD_HP]) + max_level*int(parts[0])
            data['hp max'] = int(process_info[UNIT_LORD_HP]) + max_level*int(parts[1])
        else:
            data['hp'] = int(process_info[UNIT_LORD_HP])

        if type_data[UNITTYPE_ATK] != '0,0':
            parts = type_data[UNITTYPE_ATK].split(',')
            data['atk min'] = int(process_info[UNIT_LORD_ATK]) + max_level*int(parts[0])
            data['atk max'] = int(process_info[UNIT_LORD_ATK]) + max_level*int(parts[1])
        else:
            data['atk'] = int(process_info[UNIT_LORD_ATK])

        if type_data[UNITTYPE_DEF] != '0,0':
            parts = type_data[UNITTYPE_DEF].split(',')
            data['def min'] = int(process_info[UNIT_LORD_DEF]) + max_level*int(parts[0])
            data['def max'] = int(process_info[UNIT_LORD_DEF]) + max_level*int(parts[1])
        else:
            data['def'] = int(process_info[UNIT_LORD_DEF])

        if type_data[UNITTYPE_REC] != '0,0':
            parts = type_data[UNITTYPE_REC].split(',')
            data['rec min'] = int(process_info[UNIT_LORD_REC]) + max_level*int(parts[0])
            data['rec max'] = int(process_info[UNIT_LORD_REC]) + max_level*int(parts[1])
        else:
            data['rec'] = int(process_info[UNIT_LORD_REC])

        return data

    def get_overdrive_stat(stats):
        rtn = {}
        parts = stats.split(',')
        if not_zero(parts[0]):
            rtn['atk%'] = int(parts[0])
        if not_zero(parts[1]):
            rtn['def%'] = int(parts[1])
        if not_zero(parts[2]):
            rtn['rec%'] = int(parts[2])
        if not_zero(parts[3]):
            rtn['od cost increase'] = int(parts[3]) 
        return rtn

    def get_move_types(attackType, skillType, speedType):
        rtn = {}
        rtn['attack'] = {'move type': attackType, 'move speed type': speedType, 'move speed': move_speed.get(attackType, {}).get(speedType, '?')}
        rtn['skill'] = {'move type': skillType, 'move speed type': speedType, 'move speed': move_speed.get(skillType, {}).get(speedType, '?')}
        return rtn

    def get_damage_frame(action_frame):
        data = {}
        data['hit dmg% distribution'] = NoIndent(hit_dmg_dist(action_frame))
        data['frame times'] = NoIndent(frame_time_dist(action_frame))
        data['hit dmg% distribution (total)'] = hit_dmg_dist_total(action_frame)
        data['hits'] = hits(action_frame)

        return data

    unit_format = ((get_name),
                   ([UNIT_ATTACK_MOVE_TYPE, UNIT_SKILL_MOVE_TYPE, UNIT_MOVE_SPEED], 'movement', get_move_types),
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
                   (DMG_FRAME, 'damage frames', get_damage_frame),
                   #(DMG_FRAME, 'hit dmg% distribution', hit_dmg_dist),
                   #(DMG_FRAME, 'hit dmg% distribution (total)', hit_dmg_dist_total),
                   #(DROP_CHECK_CNT, 'max bc generated', max_bc_gen),
                   (DROP_CHECK_CNT, 'drop check count', int),
                   (UNIT_LORD_ATK, 'lord damage range', _damage_range),
                   (UNIT_AI_ID, 'ai', ais.get),
                   (UNIT_IMP, 'imp', lambda s: parse_imps(s.split(':'))),
                   (BB_ID, 'bb', _parse_skill, not_zero),
                   (SBB_ID, 'sbb', _parse_skill, not_zero),
                   (UBB_ID, 'ubb', _parse_ubb, not_zero),
                   (LS_ID, 'leader skill', parse_ls, not_zero),
                   (ES_ID, 'extra skill', _parse_extra, not_zero),
                   (UNIT_ID, 'id', int),
                   (UNIT_GUIDE_ID, 'guide_id', int),
                   (UNIT_EXP_PATTERN_ID, 'exp_pattern', int),
                   (UNIT_COST, 'cost', int),
                   (UNIT_GENDER, 'gender', gender.get),
                   (SELL_CAUTION, 'sell caution', caution.get),
                   (UNIT_CATEGORY, 'category', int),
                   (UNIT_GETTING_TYPE, 'getting type', get_type.get),
                   (UNIT_KIND, 'kind', unit_kind.get),
                   (UNIT_OD_STATS, 'overdrive stats', get_overdrive_stat, not_empty),
                   # (UNIT_MOVE_SPEED, 'move speed', move_speed.get)
                   )

    return handle_format(unit_format, unit)


def parse_ai(ai):
    ai_format = ((AI_ID, 'id', str),
                 (AI_CHANCE, 'chance%', float),
                 (AI_TARGET_CONDITIONS, 'target conditions', str),
                 (AI_ACTION_PARAMS, 'action', lambda s: s.split('@')[0]),
                 (AI_TARGET_TYPE, 'target type', target_type_names.get))

    return handle_format(ai_format, ai)


def download_file(cgs_file):
  cgs_url = cdn_url + '/unit/cgs/' + cgs_file
  try:
        r = requests.get(cgs_url)
        r.raise_for_status()
        return r.text
  except Exception, e:
        return None


def get_animation_data(raw_cgs):
    rtn_data = {}
    for raw_data in raw_cgs.split('|'):
        [cgs_type, cgs_file] = raw_data.split(':')
        if (cgs_type == '4'):
            continue
        if '.sam' in cgs_file:
            rtn_data[animation_type.get(cgs_type, cgs_type)] = {'error': 'unable to parse sam file'}
            continue
        downloaded = download_file(cgs_file)
        if downloaded is None:
            rtn_data[animation_type.get(cgs_type, cgs_type)] = {'error': 'missing data'}
            continue
        cgs_lines = downloaded.split('\n')
        framesum = 0
        for line in cgs_lines:
            params = line.split(',')
            if len(params) < 2:
                break
            delay = int(params[3])
            framesum += delay + 1
        rtn_data[animation_type.get(cgs_type, cgs_type)] = {'total number of frames': framesum}
    return rtn_data


if __name__ == '__main__':
    _dir = 'data/decoded_dat/'
    dict_file = 'data/dictionary_raw.txt'
    cdn_url = 'http://v2.cdn.android.brave.a-lim.jp'
    if len(sys.argv) > 1:
        _dir = sys.argv[1]
    if len(sys.argv) > 2:
        dict_file = sys.argv[2]
    if len(sys.argv) > 3:
        cdn_url = sys.argv[3]

    isJp = 'jp' in sys.argv

    files = {
        'dict': dict_file,
        'unit':         _dir + 'Ver*_2r9cNSdt*',
        'skill level':  _dir + 'Ver*_zLIvD5o2*',
        'skill':        _dir + 'Ver*_wkCyV73D*',
        'leader skill': _dir + 'Ver*_4dE8UKcw*',
        'ai':           _dir + 'Ver*_XkBhe70R*',
        'extra skill':  _dir + 'Ver*_kP4pTJ7n*',
        'unit type':    _dir + 'Ver*_J4heGZ2U*',
        # 'cgs':          _dir + 'Ver*_6rjmY7tV*'
        'cgs':          _dir + 'animationpreprocess.json'
    }

    jsons = {}
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
        return {obj[id_str]: obj for obj in lst}

    skills = key_by_id(jsons['skill'], BB_ID)
    skill_levels = key_by_id(jsons['skill level'], BB_ID)
    leader_skills = key_by_id(jsons['leader skill'], LS_ID)
    extra_skills = {}
    cgs = None
    unit_types = {
        '1': {
            '76IHLVsz': '0,0',
            '2M4mQZgk': '0,0',
            'Sj9zR38K': '0,0',
            '6D3YN9rc': '0,0'
        },
        '2': {
            '76IHLVsz': '5,10',
            '2M4mQZgk': '0,0',
            'Sj9zR38K': '0,0',
            '6D3YN9rc': '-3,-1'
        },
        '3': {
            '76IHLVsz': '0,0',
            '2M4mQZgk': '1,3',
            'Sj9zR38K': '-3,-1',
            '6D3YN9rc': '0,0'
        },
        '4': {
            '76IHLVsz': '0,0',
            '2M4mQZgk': '-3,-1',
            'Sj9zR38K': '1,3',
            '6D3YN9rc': '0,0'
        },
        '5': {
            '76IHLVsz': '-4,-2',
            '2M4mQZgk': '0,0',
            'Sj9zR38K': '0,0',
            '6D3YN9rc': '2,4'
        },
        '6': {
            '76IHLVsz': '10,15',
            '2M4mQZgk': '1,2',
            'Sj9zR38K': '1,2',
            '6D3YN9rc': '1,2'
        },
    }
    if 'extra skill' in jsons:
        extra_skills = key_by_id(jsons['extra skill'], ES_ID)
    if 'unit type' in jsons:
        unit_types = key_by_id(jsons['unit type'], UNITTYPE_ID)
    if 'cgs' in jsons:
        cgs = jsons['cgs']

    ais = collections.defaultdict(list)
    for ai in jsons['ai']:
        ai_data = parse_ai(ai)
        ais[ai_data['id']].append(ai_data)
        ai_data.pop('id')

    units_data = {}
    for unit in jsons['unit']:
        unit_data = parse_unit(unit, skills, skill_levels, leader_skills,
                               ais, extra_skills, unit_types, jsons['dict'], isJp, 'debug' in sys.argv)
        if unit_data['name'] in units_data:
          unit_data['name'] += ' (' + str(unit_data['rarity']) + '*)'
        #units_data[unit_data['name']] = unit_data
        #unit_data.pop('name')
        units_data[str(unit_data['id'])] = unit_data

    #perform some post-processing
    for unit_id, unit_data in units_data.items():
        if 'extra skill' in unit_data:
            if 'effects' in unit_data['extra skill']:
                for effect in unit_data['extra skill']['effects']:
                    for condition in effect['conditions']:
                        if 'unit required' in condition:
                            unit_search_id = condition['unit required']
                            units = search_units_by_category(unit_search_id, units_data)
                            condition['unit required'] = []
                            for unit in units:
                                condition['unit required'].append({'name': unit['name'], 'id': unit['id']})
        if cgs is not None:
            unit_cgs = cgs.get(unit_id, None)
            if unit_cgs is not None:
                unit_data['animations'] = unit_cgs
            else:
                unit_data['animations'] = {'error': 'data missing'}
        else:
            unit_data['animations'] = {'error': 'data missing'}


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
