import sys
from utils.util import *
from parsers.common.passives import parse_ls_process
from parsers.common.skills import parse_skill_level_process


def parse_unit_skill(skill, skills):
    data = {}
    data['category'] = skill[FE_CAT_ID]
    data['skill'] = skills.get(
        skill[FE_ID], {'error': 'data missing', 'id': skill[FE_ID]})
    data['id'] = skill[FE_ID]
    data['dependency'] = skill[FE_TERM_SKILL]
    data['dependency comment'] = skill[FE_TERM_COMMENT]
    return data


def parse_category(category):
    data = {}
    data['name'] = category[FE_CAT_NAME]
    # TODO: IMPLEMENT AT SOME POINT IN THE FUTURE
    #data['cost'] = {}
    return data


fe_effect = {
    '2': 'bb',
    '3': 'sbb',
    '4': 'ubb'
}


def parse_fe_skill(leader_skill, dictionary, jp=True, debug=False, id=None):
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
                                'process ids': process_type,
                                'process params': process_info}

            if debug:
                process_data['_debug id'] = process_type
                process_data['_debug params'] = process_info

            data['effects'].append(
                {'add to ' + fe_effect[effect_type]: process_data})
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
            data['effects'].append({'error': 'unknown effect', 'effect': effect_type,
                                    'ids': leader_skill[PROCESS_TYPE], 'params': leader_skill[LS_PROCESS]})

    return data
