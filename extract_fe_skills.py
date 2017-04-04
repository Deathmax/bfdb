#!/usr/bin/python

import json
import glob
import sys
import collections
import os
from to_json import *
from util import *
from leaderskill import *
from braveburst import *


reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')


def parse_unit_skill(skill, skills):
    data = {}
    data['category'] = skill[FE_CAT_ID]
    data['skill'] = skills.get(skill[FE_ID], {'error': 'data missing', 'id': skill[FE_ID]})
    data['id'] = skill[FE_ID]
    data['dependency'] = skill[FE_TERM_SKILL]
    data['dependency comment'] = skill[FE_TERM_COMMENT]
    return data


def parse_category(category):
    data = {}
    data['name'] = category[FE_CAT_NAME]
    #TODO: IMPLEMENT AT SOME POINT IN THE FUTURE
    #data['cost'] = {}
    return data


fe_effect = {
    '2': 'bb',
    '3': 'sbb',
    '4': 'ubb'
}


def parse_fe_skill(unit_data, leader_skill, dictionary, jp=True, debug=False, id=None):
    data = dict()

    data['name'] = get_fe_name(dictionary, id, jp)(leader_skill[FE_NAME])
    if id != None:
      data['id'] = id
    data['desc'] = get_fe_desc(dictionary, id, jp)(leader_skill[DESC])
    data['effects'] = []
    # workaround for EU, EU is missing the series key
    data['series'] = leader_skill.get(FE_SERIES, '')
    data['level'] = int(leader_skill[FE_LEVEL])
    data['bp'] = int(leader_skill[FE_NEED_BP])

    for effect_type, process_type, process_info in zip(
            leader_skill[FE_EFFECT_TYPE].split('@'),
            leader_skill[PROCESS_TYPE].split('@'),
            leader_skill[LS_PROCESS].split('@')):

        if effect_type == '1':
            try:
              process_data = parse_ls_process(process_type, process_info)
            except:
              process_data = {'error occured during parsing': str(sys.exc_info()[0]),
                              'passive id': process_type,
                              'passive param': process_info}
            if debug:
                process_data['_debug id'] = process_type
                process_data['_debug params'] = process_info
    
            data['effects'].append({'passive': process_data})
        elif effect_type == '2' or effect_type == '3' or effect_type == '4':
            process_data = {}
            try:
                process_data = parse_skill_level_process(process_type,
                                                         process_info)
            except Exception, err:
                process_data = {'error occured during parsing': str(sys.exc_info()[0]),
                                'process ids': process_types,
                                'process params': process_infos}
    
            if debug:
                process_data['_debug id'] = process_type
                process_data['_debug params'] = process_info
    
            data['effects'].append({'add to ' + fe_effect[effect_type]:process_data})
        elif effect_type == '5':
            try:
              process_data = parse_ls_process(process_type, process_info)
            except:
              process_data = {'error occured during parsing': str(sys.exc_info()[0]),
                              'passive id': process_type,
                              'passive param': process_info}
            if debug:
                process_data['_debug id'] = process_type
                process_data['_debug params'] = process_info
    
            data['effects'].append({'add to passive': process_data})
        else:
            data['effects'].append({'error': 'unknown effect', 'effect': effect_type, 'ids': leader_skill[PROCESS_TYPE], 'params': leader_skill[LS_PROCESS]})

    return data

if __name__ == '__main__':
    _dir = 'data/decoded_dat/'
    dict_file = 'data/dictionary_raw.txt'
    if len(sys.argv) > 1:
        _dir = sys.argv[1]
    if len(sys.argv) > 2:
        dict_file = sys.argv[2]

    files = {
        'dict': dict_file,
        'fe skill':     _dir + 'Ver*_2h9r3yEY*',
        'unit fe skill':_dir + 'Ver*_8gu2U4Mh*',
        'unit fe cat':  _dir + 'Ver*_nd18wpsy*',
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

    if 'jp' in sys.argv:
        jsons['dict'] = {}

    def key_by_id(lst, id_str):
        return {obj[id_str]: obj for obj in lst}

    fe_skills = key_by_id(jsons['fe skill'], FE_ID)

    fe_skills_data = {}
    for fe in fe_skills:
        ls_data = parse_fe_skill(None, fe_skills[fe], jsons['dict'], 'jp' in sys.argv, id=fe)
        fe_skills_data[fe] = ls_data

    unit_fe_skills = {}
    for unit_skill in jsons['unit fe skill']:
        if unit_skill[UNIT_ID] in unit_fe_skills:
            unit_fe_skills[unit_skill[UNIT_ID]]['skills'].append(parse_unit_skill(unit_skill, fe_skills_data))
        else:
            unit_fe_skills[unit_skill[UNIT_ID]] = {'skills': [], 'category': {}}
            unit_fe_skills[unit_skill[UNIT_ID]]['skills'].append(parse_unit_skill(unit_skill, fe_skills_data))

    for category in jsons['unit fe cat']:
        unit_fe_skills[category[UNIT_ID]]['category'][category[FE_CAT_ID]] = parse_category(category)

    dump_data = unit_fe_skills
    if 'jp' in sys.argv:
        print json.dumps(dump_data, 
        				 sort_keys=True, 
                         indent=4, 
                         cls=IndentlessEncoder, 
                         ensure_ascii=False).encode('utf8').replace('"[', '[').replace(']"', ']')
    else:
        print json.dumps(dump_data, 
        				 sort_keys=True, 
                         indent=4, 
                         cls=IndentlessEncoder).replace('"[', '[').replace(']"', ']')