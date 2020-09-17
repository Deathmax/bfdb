#!/usr/bin/python

import re
import collections
from parsers.baseparser import BaseParser
from parsers.common.skills import parse_skill
from parsers.common.passives import parse_extra_skill, parse_leader_skill
from parsers.common.ai import parse_ai_for_unit
from utils.util import *


class UnitParser(BaseParser):
    """Parser for unit data.

    Expects 'ai', 'unit', 'SkillParser', 'LeaderSkillParser', 'ExtraSkillParser'
    and 'dict' in the raw data.

    Optional data include 'unit type' and 'cgs'
    """

    required_data = ['ai', 'unit', 'SkillParser',
                     'LeaderSkillParser', 'ExtraSkillParser', 'dict']

    def __init__(self, **data):
        super(self.__class__, self).__init__(**data)
        self.file_name = "info.json"

    def run(self):
        # Check if we have all the data we need
        if not all(name in self.data for name in self.required_data):
            raise AttributeError("Failed to find all required data")

        is_foreign = self.data['isForeign']

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
        if 'unit type' in self.data:
            unit_types = self.data['unit type']
        if 'cgs' in self.data:
            cgs = self.data['cgs']
        skills = self.data['SkillParser']
        leader_skills = self.data['LeaderSkillParser']
        extra_skills = self.data['ExtraSkillParser']

        ais = collections.defaultdict(list)
        for ai in self.data['ai']:
            ai_data = parse_ai_for_unit(ai)
            ais[ai_data['id']].append(ai_data)
            ai_data.pop('id')

        self.parsed_data = {}
        for unit in self.data['unit']:
            unit_data = parse_unit(unit, skills, leader_skills, ais,
                                   extra_skills, unit_types, self.data['dict'], is_foreign)
            if unit_data['name'] in self.parsed_data:
                unit_data['name'] += ' (' + str(unit_data['rarity']) + '*)'
            self.parsed_data[str(unit_data['id'])] = unit_data

        # perform some post-processing
        for unit_id, unit_data in self.parsed_data.items():
            if 'extra skill' in unit_data:
                if 'effects' in unit_data['extra skill']:
                    for effect in unit_data['extra skill']['effects']:
                        for condition in effect['conditions']:
                            if 'unit required' in condition:
                                unit_search_id = condition['unit required']
                                units = search_units_by_category(
                                    unit_search_id, self.parsed_data)
                                condition['unit required'] = []
                                for unit in units:
                                    condition['unit required'].append(
                                        {'name': unit['name'], 'id': unit['id']})
            if cgs is not None:
                unit_cgs = cgs.get(unit_id, None)
                if unit_cgs is not None:
                    unit_data['animations'] = unit_cgs
                else:
                    unit_data['animations'] = {'error': 'data missing'}
            else:
                unit_data['animations'] = {'error': 'data missing'}


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
        if 'category' not in unit_data:
            continue
        if str(unit_data['category']) == search_id:
            units.append(unit_data)
    return units


def parse_unit(unit, skills, leader_skills, ais, extra_skills, unit_types, dictionary, jp=True, debug=False):
    def max_bc_gen(s, data):
        return int(s) * data['damage frames']['hits']

    def _damage_range(s):
        return '~'.join(map(str, damage_range(int(s))))

    def _parse_skill(bb_id, data):
        if bb_id not in skills:
            return {'error': 'data missing', 'id': bb_id}
        return skills[bb_id]

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
        return leader_skills[ls_id]

    def _parse_extra(extra_id, data):
        if extra_skills != {}:
            if extra_id not in extra_skills:
                return {'error': 'data missing', 'id': extra_id}
            return extra_skills[extra_id]
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
            data['hp min'] = int(process_info[UNIT_LORD_HP]
                                 ) + max_level * int(parts[0])
            data['hp max'] = int(process_info[UNIT_LORD_HP]
                                 ) + max_level * int(parts[1])
        else:
            data['hp'] = int(process_info[UNIT_LORD_HP])

        if type_data[UNITTYPE_ATK] != '0,0':
            parts = type_data[UNITTYPE_ATK].split(',')
            data['atk min'] = int(
                process_info[UNIT_LORD_ATK]) + max_level * int(parts[0])
            data['atk max'] = int(
                process_info[UNIT_LORD_ATK]) + max_level * int(parts[1])
        else:
            data['atk'] = int(process_info[UNIT_LORD_ATK])

        if type_data[UNITTYPE_DEF] != '0,0':
            parts = type_data[UNITTYPE_DEF].split(',')
            data['def min'] = int(
                process_info[UNIT_LORD_DEF]) + max_level * int(parts[0])
            data['def max'] = int(
                process_info[UNIT_LORD_DEF]) + max_level * int(parts[1])
        else:
            data['def'] = int(process_info[UNIT_LORD_DEF])

        if type_data[UNITTYPE_REC] != '0,0':
            parts = type_data[UNITTYPE_REC].split(',')
            data['rec min'] = int(
                process_info[UNIT_LORD_REC]) + max_level * int(parts[0])
            data['rec max'] = int(
                process_info[UNIT_LORD_REC]) + max_level * int(parts[1])
        else:
            data['rec'] = int(process_info[UNIT_LORD_REC])

        return data

    def get_overdrive_stat(stats):
        rtn = {}
        parts = stats.split(',')
        if len(parts) < 4:
            return {'unknown data': stats}
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
        rtn['attack'] = {'move type': attackType, 'move speed type': speedType,
                         'move speed': move_speed.get(attackType, {}).get(speedType, '?')}
        rtn['skill'] = {'move type': skillType, 'move speed type': speedType,
                        'move speed': move_speed.get(skillType, {}).get(speedType, '?')}
        return rtn

    def get_damage_frame(action_frame):
        data = {}
        data['hit dmg% distribution'] = NoIndent(hit_dmg_dist(action_frame))
        data['frame times'] = NoIndent(frame_time_dist(action_frame))
        data['hit dmg% distribution (total)'] = hit_dmg_dist_total(
            action_frame)
        data['hits'] = hits(action_frame)

        return data

    unit_format = ((get_name),
                   ([UNIT_ATTACK_MOVE_TYPE, UNIT_SKILL_MOVE_TYPE,
                     UNIT_MOVE_SPEED], 'movement', get_move_types),
                   (UNIT_ELEMENT, 'element', elements.get),
                   (UNIT_RARITY, 'rarity', int),
                   (get_stats),
                   (DMG_FRAME, 'damage frames', get_damage_frame),
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
                   (UNIT_OD_STATS, 'overdrive stats',
                    get_overdrive_stat, not_empty),)

    return handle_format(unit_format, unit)
