import sys
from util import *
from braveburst import parse_skill_level_processes


def parse_elements_buffed(process_info):
    buffs = dict()

    if process_info[0] != '0':
        buffs['elements buffed'] = buffs.get('elements buffed', []) + [
            elements[process_info[0]]]
    if process_info[1] != '0':
        buffs['elements buffed'] = buffs.get('elements buffed', []) + [
            elements[process_info[1]]]

    return buffs


def parse_stat_buff_proportion_process(process_info):
    buffs = dict()

    if int(process_info[0]) != 0 or int(process_info[1]) != 0:
        buffs['atk% base buff'] = int(process_info[0])
        buffs['atk% extra buff based on hp'] = int(process_info[1]) - int(process_info[0])
    if int(process_info[2]) != 0 or int(process_info[3]) != 0:
        buffs['def% base buff'] = int(process_info[2])
        buffs['def% extra buff based on hp'] = int(process_info[3]) - int(process_info[2])
    if int(process_info[4]) != 0 or int(process_info[5]) != 0:
        buffs['rec% base buff'] = int(process_info[4])
        buffs['rec% extra buff based on hp'] = int(process_info[5]) - int(process_info[4])
    buffs['buff proportional to hp'] = ('lost' if int(process_info[6]) == 1 else 'remaining')
    return buffs


def parse_damage_buff_on_ailment(process_info):
    rtn = {}

    for ailmentId in process_info[0].split('&'):
      if ailmentId != '0':
        rtn['atk% buff when enemy has ' + ailments.get(ailmentId, ailmentId).rstrip('%')] = True

    rtn['atk% buff when enemy has ailment'] = int(process_info[1])

    return rtn


def get_passive_param(proc_type, params, turns=0):
    rtn = {}
    if proc_type in passivebuff_process_format:
        rtn.update(handle_format(passivebuff_process_format[proc_type], params.split('&')))
    else:
        rtn.update({'unknown buff id': proc_type,
                    'unknown buff params': params})
    rtn['buff turns (' + proc_type + ')'] = turns
    return rtn


def get_bb_passive(proc_id, proc_params, target_type, target_area, start_frame):
    return parse_skill_level_processes(proc_id.split('~'), 
                                       proc_params.replace('&', ',').split('~'), 
                                       start_frame.split('~'),
                                       target_type.split('~'),
                                       target_area.split('~'))


genders = {'0': 'genderless', '1': 'male', '2': 'female'}

passivebuff_process_format = {
    '1': ((0, 'atk% buff (1)', int),),

    '3': ((0, 'def% buff (3)', int),),

    '5': ((0, 'rec% buff (5)', int),),

    '8': ((0, 'gradual heal low', int),
          (1, 'gradual heal high', int),),

    '12': ((0, 'angel idol buff (12)', True),
           (0, 'angel idol recover hp%', int, not_zero),),

    '13': ((0, 'element buffed', elements.get),
           (1, 'atk% buff (13)', int),),

    '14': ((0, 'element buffed', elements.get),
           (1, 'def% buff (14)', int),),

    '36': ((0, 'dmg reduction% buff', int),),

    '37': ((0, 'increase bb gauge gradual buff', bb_gauge),),

    '40': ((0, 'spark dmg% buff', int),),

    '72': ((0, 'bb atk% buff', int, not_zero),
           (1, 'sbb atk% buff', int, not_zero),
           (2, 'ubb atk% buff', int, not_zero),),
} 

ls_process_format = {
    '1': ((0, 'atk% buff', int, not_zero),
          (1, 'def% buff', int, not_zero),
          (2, 'rec% buff', int, not_zero),
          (3, 'crit% buff', int, not_zero),
          (4, 'hp% buff', int, not_zero)),

    '2': (parse_elements_buffed,
          (2, 'atk% buff', int, not_zero),
          (3, 'def% buff', int, not_zero),
          (4, 'rec% buff', int, not_zero),
          (5, 'crit% buff', int, not_zero),
          (6, 'hp% buff', int, not_zero)),

    '3': ((0, 'unit type buffed', unit_type.get),
          (1, 'atk% buff', int, not_zero),
          (2, 'def% buff', int, not_zero),
          (3, 'rec% buff', int, not_zero),
          (4, 'crit% buff', int, not_zero),
          (5, 'hp% buff', int, not_zero)),

    '4': ((0, 'poison resist%', int, not_zero),
          (1, 'weaken resist%', int, not_zero),
          (2, 'sick resist%', int, not_zero),
          (3, 'injury resist%', int, not_zero),
          (4, 'curse resist%', int, not_zero),
          (5, 'paralysis resist%', int, not_zero)),

    '5': (([0, 1], lambda el: '%s resist%%' % elements[el], second_int),),

    '8': ((0, 'dmg% mitigation', int),),

    '9': ((0, 'bc fill per turn', bb_gauge),),

    '10': ((0, 'hc effectiveness%', int),),

    '11': ((0, 'atk% buff', int, not_zero),
           (1, 'def% buff', int, not_zero),
           (2, 'rec% buff', int, not_zero),
           (3, 'crit% buff', int, not_zero),
           ([5, 4], lambda s: 'hp %s %% buff requirement' %
            ('above' if int(s) == 1 else 'below'), second_int, not_zero)),

    '12': ((0, 'bc drop rate% buff', int, not_zero),
           (1, 'hc drop rate% buff', int, not_zero),
           (2, 'item drop rate% buff', int, not_zero),
           (3, 'zel drop rate% buff', int, not_zero),
           (4, 'karma drop rate% buff', int, not_zero),
           ([6, 5], lambda s: 'hp %s %% buff requirement' %
            ('above' if int(s) == 1 else 'below'), second_int, not_zero)),

    '13': ((0, 'bc fill on enemy defeat low', bb_gauge),
           (1, 'bc fill on enemy defeat high', bb_gauge),
           (2, 'bc fill on enemy defeat%', int)),

    '14': ((0, 'dmg reduction%', int),
           (1, 'dmg reduction chance%', int)),

    '15': ((0, 'hp% recover on enemy defeat low', int),
           (1, 'hp% recover on enemy defeat high', int),
           (3, 'hp% recover on enemy defeat chance%', int)),

    '16': ((0, 'hp% recover on battle win low', int),
           (1, 'hp% recover on battle win high', int),),

    '17': ((0, 'hp drain% low', int),
           (1, 'hp drain% high', int),
           (2, 'hp drain chance%', int)),

    '19': ((0, 'bc drop rate% buff', int, not_zero),
           (1, 'hc drop rate% buff', int, not_zero),
           (2, 'item drop rate% buff', int, not_zero),
           (3, 'zel drop rate% buff', int, not_zero),
           (4, 'karma drop rate% buff', int, not_zero)),

    '20': (([0, 1], ailments.get, second_int, not_zero),
           ([2, 3], ailments.get, second_int, not_zero),
           ([4, 5], ailments.get, second_int, not_zero),
           ([6, 7], ailments.get, second_int, not_zero)),

    '21': ((0, 'first x turns atk% (1)', int, not_zero),
           (1, 'first x turns def% (3)', int, not_zero),
           (2, 'first x turns rec% (5)', int, not_zero),
           (3, 'first x turns crit% (7)', int, not_zero),
           (4, 'first x turns', int)),

    '23': ((0, 'battle end bc fill low', bb_gauge),
           (1, 'battle end bc fill high', bb_gauge)),

    '24': ((0, 'dmg% to hp% when attacked low', int),
           (1, 'dmg% to hp% when attacked high', int),
           (2, 'dmg% to hp% when attacked chance%', int)),

    '25': ((0, 'bc fill when attacked low', bb_gauge),
           (1, 'bc fill when attacked high', bb_gauge),
           (2, 'bc fill when attacked%', int)),

    '26': ((0, 'dmg% reflect low', int),
           (1, 'dmg% reflect high', int),
           (2, 'dmg% reflect chance%', int)),

    '27': ((0, 'target% chance', int),),
    
    '28': ((0, 'target% chance', int),
           ([2, 1], lambda s: 'hp %s %% passive requirement' %
            ('above' if int(s) == 1 else 'below'), second_int, not_zero)),

    '29': ((0, 'ignore def%', int),),

    '30': ((0, 'atk% buff', int, not_zero),
           (1, 'def% buff', int, not_zero),
           (2, 'rec% buff', int, not_zero),
           (3, 'crit% buff', int, not_zero),
           ([5, 4], lambda s: 'bb gauge %s %% buff requirement' %
            ('above' if int(s) == 1 else 'below'), second_int, not_zero)),

    '31': ((0, 'damage% for spark', int, not_zero),
           (1, 'bc drop% for spark', int, not_zero),
           (2, 'hc drop% for spark', int, not_zero),
           (3, 'item drop% for spark', int, not_zero),
           (4, 'zel drop% for spark', int, not_zero),
           (5, 'karma drop% for spark', int, not_zero)),

    '32': ((0, 'bb gauge fill rate%', int),),

    '33': ((0, 'turn heal low', int),
           (1, 'turn heal high', int),
           (2, 'rec% added (turn heal)', lambda x: (1 + float(x) / 100) * 10)),

    '34': ((0, 'crit multiplier%', crit_elem_weakness),),

    '35': ((0, 'bc fill when attacking low', bb_gauge),
           (1, 'bc fill when attacking high', bb_gauge),
           (2, 'bc fill when attacking%', int)),

    '36': ((0, 'additional actions', int),),

    '37': ((0, 'hit increase/hit', int),
           (2, 'extra hits dmg%', int, not_zero)),  

    '40': ((0, 'converted attribute', attribute.get),
           (1, 'atk% buff', int, not_zero),
           (2, 'def% buff', int, not_zero),
           (3, 'rec% buff', int, not_zero)),

    '41': ((0, 'unique elements required', int),
           (1, 'atk% buff', int, not_zero),
           (2, 'def% buff', int, not_zero),
           (3, 'rec% buff', int, not_zero),
           (4, 'crit% buff', int, not_zero),
           (5, 'hp% buff', int, not_zero)),

    '42': ((0, 'gender required', lambda s: genders[s[0]]),
           (1, 'atk% buff', int, not_zero),
           (2, 'def% buff', int, not_zero),
           (3, 'rec% buff', int, not_zero),
           (4, 'crit% buff', int, not_zero),
           (5, 'hp% buff', int, not_zero)),

    '43': ((0, 'take 1 dmg%', int),),

    '44': ((0, 'atk buff', int, not_zero),
          (1, 'def buff', int, not_zero),
          (2, 'rec buff', int, not_zero),
          (3, 'crit buff', int, not_zero),
          (4, 'hp buff', int, not_zero)),

    '45': ((0, 'base crit% resist', int),
           (1, 'buff crit% resist', int)),

    '46': ((parse_stat_buff_proportion_process),),

    '47': ((0, 'bc fill on spark low', bb_gauge),
           (1, 'bc fill on spark high', bb_gauge),
           (2, 'bc fill on spark%', int)),

    '48': ((0, 'reduced bb bc cost%', int),),

    '49': ((0, 'reduced bb bc use% low', int),
           (1, 'reduced bb bc use% high', int),
           (2, 'reduced bb bc use chance%', int),),

    '50': ((0, lambda el: '%s units do extra elemental weakness dmg' %
            elements[el], True, not_zero),
           (1, lambda el: '%s units do extra elemental weakness dmg' %
            elements[el], True, not_zero),
           (2, lambda el: '%s units do extra elemental weakness dmg' %
            elements[el], True, not_zero),
           (3, lambda el: '%s units do extra elemental weakness dmg' %
            elements[el], True, not_zero),
           (4, lambda el: '%s units do extra elemental weakness dmg' %
            elements[el], True, not_zero),
           (5, lambda el: '%s units do extra elemental weakness dmg' %
            elements[el], True, not_zero),
           (6, 'elemental weakness multiplier%', crit_elem_weakness)),

    '51': ((0, 'bc base drop rate resist%', int, not_zero),
           (1, 'bc buffed drop rate resist%', int, not_zero),
           (2, 'hc base drop rate resist%', int, not_zero),
           (3, 'hc buffed drop rate resist%', int, not_zero),),

    #mapping - skipped: not used atm
    '53': ((0, 'crit dmg base damage resist%', int, not_zero),
           (1, 'crit dmg buffed damage resist%', int, not_zero),
           (2, 'strong base element damage resist%', int, not_zero),
           (3, 'strong buffed element damage resist%', int, not_zero),
           (4, 'crit chance base resist%', int, not_zero),
           (5, 'crit chance buffed resist%', int, not_zero),
           (6, 'bc base drop rate resist%', int, not_zero),
           (7, 'bc buffed drop rate resist%', int, not_zero),
           (8, 'hc base drop rate resist%', int, not_zero),
           (9, 'hc buffed drop rate resist%', int, not_zero),),

    '55': (([0, 1, 5], 'buff', get_passive_param),
           #(0, 'buff type', buff_lookup.get),
           #(1, 'TODO: buff params', int),
           #(2, 'TODO: unknown condition', int),
           ([4, 3], lambda s: 'hp %s %% buff activation' %
            ('above' if int(s) == 1 else 'below'), second_int, not_zero),
           #(5, 'buff turns', int),
           ),  #0 - buff id, 1 -

    '58': ((0, 'guard increase mitigation%', int),),

    '59': ((0, 'bb gauge% filled when attacked while guarded', int, not_zero),
           (1, 'bc filled when attacked while guarded', bb_gauge, not_zero),),

    '61': ((0, 'bb gauge% filled on guard', int, not_zero),
           (1, 'bc filled on guard', bb_gauge, not_zero),),

    '62': ((0, lambda el: 'mitigate %s attacks' %
            elements[el], True, not_zero),
           (1, lambda el: 'mitigate %s attacks' %
            elements[el], True, not_zero),
           (2, lambda el: 'mitigate %s attacks' %
            elements[el], True, not_zero),
           (3, lambda el: 'mitigate %s attacks' %
            elements[el], True, not_zero),
           (4, lambda el: 'mitigate %s attacks' %
            elements[el], True, not_zero),
           (5, lambda el: 'mitigate %s attacks' %
            elements[el], True, not_zero),
           (6, 'dmg% mitigation for elemental attacks', float)),

    '63': ((0, lambda el: 'mitigate %s attacks' %
            elements[el], True, not_zero),
           (1, lambda el: 'mitigate %s attacks' %
            elements[el], True, not_zero),
           (2, lambda el: 'mitigate %s attacks' %
            elements[el], True, not_zero),
           (3, lambda el: 'mitigate %s attacks' %
            elements[el], True, not_zero),
           (4, lambda el: 'mitigate %s attacks' %
            elements[el], True, not_zero),
           (5, lambda el: 'mitigate %s attacks' %
            elements[el], True, not_zero),
           (6, 'dmg% mitigation for elemental attacks', int),
           (7, 'dmg% mitigation for elemental attacks buff for first x turns', int),),

    '64': ((0, 'bb atk% buff', int, not_zero),
           (1, 'sbb atk% buff', int, not_zero),
           (2, 'ubb atk% buff', int, not_zero)),

    '65': ((0, 'bc fill on crit min', bb_gauge),
           (1, 'bc fill on crit max', bb_gauge),
           (2, 'bc fill on crit%', float)),

    '66': (([0, 1, 2, 3, 4], 'triggered effect', get_bb_passive),
           (5, 'trigger on bb', True, not_zero),
           (6, 'trigger on sbb', True, not_zero),
           (7, 'trigger on ubb', True, not_zero),),

    '68': ((0, 'item 1 drop% base resist', int, not_zero),
           (1, 'item 1 drop% buff resist', int, not_zero),
           (2, 'item 2 drop% base resist', int, not_zero),
           (3, 'item 2 drop% buff resist', int, not_zero),
           (4, 'zel drop% base resist', int, not_zero),
           (5, 'zel drop% buff resist', int, not_zero),
           (6, 'karma drop% base resist', int, not_zero),
           (7, 'karma drop% buff resist', int, not_zero),),

    '69': ((0, 'angel idol recover hp%', int, not_zero),
           (1, 'angel idol recover counts', int, not_zero),
           (2, 'angel idol recover chance% low', int, not_zero),
           (3, 'angel idol recover chance% high', int, not_zero),
           (4, 'angel idol chance% condition', int)),

    '70': ((0, 'od fill rate%', int),),

    '71': ((0, 'counter inflict poison%', int, not_zero),
           (1, 'counter inflict weaken%', int, not_zero),
           (2, 'counter inflict sick%', int, not_zero),
           (3, 'counter inflict injury%', int, not_zero),
           (4, 'counter inflict curse%', int, not_zero),
           (5, 'counter inflict paralysis%', int, not_zero)),

    '73': ((0, 'poison resist%', int, not_zero),
          (1, 'weaken resist%', int, not_zero),
          (2, 'sick resist%', int, not_zero),
          (3, 'injury resist%', int, not_zero),
          (4, 'curse resist%', int, not_zero),
          (5, 'paralysis resist%', int, not_zero),
          (6, 'atk down resist%', int, not_zero),
          (7, 'def down resist%', int, not_zero),
          (8, 'rec down resist%', int, not_zero),),

    '74': ((parse_damage_buff_on_ailment),),

    '75': ((0, 'spark debuff%', int),
           (1, 'spark debuff chance%', int),
           (2, 'spark debuff turns', int)),

    '77': ((0, 'base spark dmg% resist', int),
           (1, 'buff spark dmg% resist', int)),

#buff_id: 13
#str_param: 1&150
#unk: -1
#judge: 10000
#turns: 1

    '78': (([0, 1, 4], 'buff', get_passive_param),
           #(0, 'buff type', buff_lookup.get),
           #(1, 'TODO: buff params', int),
           #(2, 'TODO: unknown condition', int),
           (3, 'damage threshold buff activation', int),
           #(5, 'buff turns', int),
           ),

    '79': ((0, 'increase bb gauge', bb_gauge),
           (2, 'damage threshold activation', int)),

    '80': (([0, 1, 4], 'buff', get_passive_param),
           #(0, 'buff type', buff_lookup.get),
           #(1, 'TODO: buff params', int),
           #(2, 'TODO: unknown condition', int),
           (3, 'damage dealt threshold buff activation', int),
           #(5, 'buff turns', int),
           ),

    '81': ((0, 'increase bb gauge', bb_gauge),
           (2, 'damage dealt threshold activation', int)),

    '82': (([0, 1, 4], 'buff', get_passive_param),
           #(0, 'buff type', buff_lookup.get),
           #(1, 'TODO: buff params', int),
           #(2, 'TODO: unknown condition', int),
           (3, 'bc receive count buff activation', int),
           #(5, 'buff turns', int),
           ),

    '83': ((0, 'increase bb gauge', bb_gauge),
           (2, 'bc receive count activation', int)),

    '84': (([0, 1, 4], 'buff', get_passive_param),
           #(0, 'buff type', buff_lookup.get),
           #(1, 'TODO: buff params', int),
           #(2, 'TODO: unknown condition', int),
           (3, 'hc receive count buff activation', int),
           #(5, 'buff turns', int),
           ),

    '85': ((0, 'increase bb gauge', bb_gauge),
           (2, 'hc receive count activation', int)),

    '86': (([0, 1, 4], 'buff', get_passive_param),
           #(0, 'buff type', buff_lookup.get),
           #(1, 'TODO: buff params', int),
           #(2, 'TODO: unknown condition', int),
           (3, 'spark count buff activation', int),
           #(5, 'buff turns', int),
           ),

    '87': ((0, 'increase bb gauge', bb_gauge),
           (2, 'spark count activation', int)),

    '88': (([0, 1, 4], 'buff', get_passive_param),
           #(0, 'buff type', buff_lookup.get),
           #(1, 'TODO: buff params', int),
           #(2, 'TODO: unknown condition', int),
           (3, 'on guard activation chance%', int),
           #(5, 'buff turns', int),
           ),

    '89': (([0, 1, 4], 'buff', get_passive_param),
           #(0, 'buff type', buff_lookup.get),
           #(1, 'TODO: buff params', int),
           #(2, 'TODO: unknown condition', int),
           (3, 'on crit activation chance%', int),
           #(5, 'buff turns', int),
           ),

    '90': ((0, 'inflict poison%', int, not_zero),
           (1, 'inflict weaken%', int, not_zero),
           (2, 'inflict sick%', int, not_zero),
           (3, 'inflict injury%', int, not_zero),
           (4, 'inflict curse%', int, not_zero),
           (5, 'inflict paralysis%', int, not_zero)),

    '92': ((0, 'ignore def resist chance%', int),),

    '96': ((0, 'aoe atk inc%', int),
           (1, 'chance to aoe', int)),

    '97': ((0, 'xp gained increase%', int),),

    '101': ((0, 'heal on spark low', int),
            (1, 'heal on spark high', int),
            (2, 'heal on spark%', int)),

    '102': (([0, 1, 2, 3, 4, 5], 'elements added',
             lambda x, y, z, a, b, c: map(elements.get, filter(not_zero, [x, y, z, a, b, c]))),),

    '104': ((0, 'damage% for spark', int, not_zero),
            (1, 'bc drop% for spark', int, not_zero),
            (2, 'hc drop% for spark', int, not_zero),
            (3, 'item drop% for spark', int, not_zero),
            (4, 'zel drop% for spark', int, not_zero),
            (5, 'karma drop% for spark', int, not_zero),
            ([7, 6], lambda s: 'hp %s %% buff requirement' %
            ('above' if int(s) == 1 else 'below'), second_int, not_zero)),

    '105': ((0, 'atk% min buff', int, not_zero),
            (1, 'atk% max buff', int, not_zero),
            (2, 'def% min buff', int, not_zero),
            (3, 'def% max buff', int, not_zero),
            (4, 'rec% min buff', int, not_zero),
            (5, 'rec% max buff', int, not_zero),
            (6, lambda s: '%s from min to max' % ('increase' if int(s) == 1 else 'decrease'), int),
            (7, 'turn count', int)),

    '10000': ((4, 'taunt turns', int),),

    '10001': ((4, 'stealth turns', int),),
}


def parse_ls_process(process_type, process_info, debug=False):
    process_data = {}
    if debug:
        process_data['_debug id'] = process_type
        process_data['_debug params'] = process_info
    if process_type in ls_process_format:
        process_data.update(handle_format(ls_process_format[process_type],
                             process_info.split(',')))
        process_data['passive id'] = process_type
        return process_data
    return {'unknown passive id': process_type,
            'unknown passive params': process_info}


def parse_leader_skill(unit_data, leader_skill, dictionary, jp=True, debug=False, id=None):
    data = dict()

    data['name'] = get_ls_name(dictionary, id, jp)(leader_skill[LS_NAME])
    if id != None:
      data['id'] = id
    data['desc'] = get_ls_desc(dictionary, id, jp)(leader_skill[DESC])
    data['effects'] = []

    for process_type, process_info in zip(
            leader_skill[PROCESS_TYPE].split('@'),
            leader_skill[LS_PROCESS].split('@')):
        try:
          process_data = parse_ls_process(process_type, process_info)
        except:
          process_data = {'error occured during parsing': str(sys.exc_info()[0]),
                          'passive id': process_type,
                          'passive param': process_info}
        if debug:
            process_data['_debug id'] = process_type
            process_data['_debug params'] = process_info
        if 'elements buffed' in process_data and 'elements buffed' in data:
            data['elements buffed'] += process_data.pop('elements buffed')

        data['effects'].append(process_data)
        #data.update(process_data)

    return data

def parse_fe_skill(unit_data, leader_skill, dictionary, jp=True, debug=False, id=None):
    data = dict()

    data['name'] = get_ls_name(dictionary, id, jp)(leader_skill[FE_NAME])
    if id != None:
      data['id'] = id
    data['desc'] = get_ls_desc(dictionary, id, jp)(leader_skill[DESC])
    data['effects'] = []
    data['series'] = leader_skill[FE_SERIES]
    data['level'] = leader_skill[FE_LEVEL]
    data['bp'] = leader_skill[FE_NEED_BP]

    for process_type, process_info in zip(
            leader_skill[PROCESS_TYPE].split('@'),
            leader_skill[LS_PROCESS].split('@')):
        try:
          process_data = parse_ls_process(process_type, process_info)
        except:
          process_data = {'error occured during parsing': str(sys.exc_info()[0]),
                          'passive id': process_type,
                          'passive param': process_info}
        if debug:
            process_data['_debug id'] = process_type
            process_data['_debug params'] = process_info
        if 'elements buffed' in process_data and 'elements buffed' in data:
            data['elements buffed'] += process_data.pop('elements buffed')

        data['effects'].append(process_data)
        #data.update(process_data)

    return data

def parse_extra_skill(unit_data, leader_skill, dictionary, jp=True, debug=False, id=None):
    data = dict()

    data['name'] = get_es_name(dictionary, id, jp)(leader_skill[ES_NAME])
    if id != None:
      data['id'] = id
    data['desc'] = get_es_desc(dictionary, id, jp)(leader_skill[ES_DESC])
    #data['conditions'] = []
    conditions = []
    data['effects'] = []

    for term in leader_skill[ES_TERM_PARAMS].split('@'):
        multiple_conditions = [term]
        if '#' in term:
            multiple_conditions = term.split('#')[1].split('%')
        multicond = []
        for raw_condition in multiple_conditions:
            splits = raw_condition.split(',')
            condition = {}
            if splits[0] == '0' or splits[0] == '':
                condition['none'] = True
                continue
            if splits[0] == '1' or splits[0] == '3':
                condition['item required'] = splits[1].split(':')
            elif splits[0] == '2' or splits[0] == '4':
                #unit condition.  if ID ends with 0, accept all units the start with the id (for various rarities)
                condition['unit required'] = splits[1]
            elif splits[0] == '5':
                condition['sphere category required'] = item_kinds.get(splits[1], splits[1])
                condition['sphere category required (raw)'] = splits[1]
            else:
                condition['unknown'] = raw_condition
            #data['conditions'].append(condition)
            multicond.append(condition)
            #we only care about the first one for now
        conditions.append(multicond)
        if '#' not in term: #no support for selective/multi conditions, add many to avoid crashing
            conditions.append(multicond)
            conditions.append(multicond)
            conditions.append(multicond)
            conditions.append(multicond)
            conditions.append(multicond)
            conditions.append(multicond)
            conditions.append(multicond)

    idx = 0
    for process_type, process_info in zip(
            leader_skill[PROCESS_TYPE].split('@'),
            leader_skill[LS_PROCESS].split('@')):
        process_type, process_target = process_type.split(',')
        try:
          process_data = parse_ls_process(process_type, process_info)
        except:
          process_data = {'error occured during parsing': str(sys.exc_info()[0]),
                          'passive id': process_type,
                          'passive param': process_info}
        process_data['passive target'] = passive_target.get(process_target, process_target)
        if debug:
            process_data['_debug id'] = process_type
            process_data['_debug params'] = process_info
        if 'elements buffed' in process_data and 'elements buffed' in data:
            data['elements buffed'] += process_data.pop('elements buffed')

        process_data['conditions'] = conditions[idx]
        idx += 1

        data['effects'].append(process_data)
        #data.update(process_data)

    if leader_skill[ES_TARGET] == '2':
        data['target'] = 'party'
    else:
        data['target'] = 'self'

    return data