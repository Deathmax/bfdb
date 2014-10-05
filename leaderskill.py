from util import *


def parse_elements_buffed(process_info):
    buffs = dict()

    if process_info[0] != '0':
        buffs['elements buffed'] = buffs.get('elements buffed', []) + [
            elements[process_info[0]]]
    if process_info[1] != '0':
        buffs['elements buffed'] = buffs.get('elements buffed', []) + [
            elements[process_info[1]]]

    return buffs


def crit_elem_weakness(x):
    return float(x)*100


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

genders = {'0': 'genderless', '1': 'male', '2': 'female'}

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

    '4': ((0, 'poison resist%', int, not_zero),
          (1, 'weaken resist%', int, not_zero),
          (2, 'sick resist%', int, not_zero),
          (3, 'injury resist%', int, not_zero),
          (4, 'curse resist%', int, not_zero),
          (5, 'paralysis resist%', int, not_zero)),

    '5': (([0, 1], lambda el: '%s resist%%' % elements[el], second_int),),

    '9': ((0, 'bc fill per turn', bb_gauge),),

    '10': ((0, 'hc effectiveness%', int),),

    '11': ((0, 'atk% buff', int, not_zero),
           (1, 'def% buff', int, not_zero),
           (2, 'rec% buff', int, not_zero),
           (3, 'crit% buff', int, not_zero),
           ([5, 4], lambda s: 'hp %s %% buff requirement' %
            ('above' if int(s) == 1 else 'below'), second_int, not_zero)),

    '13': ((0, 'bc fill on enemy defeat low', bb_gauge),
           (1, 'bc fill on enemy defeat high', bb_gauge),
           (2, 'bc fill on enemy defeat%', int)),

    '14': ((0, 'dmg reduction%', int),
           (1, 'dmg reduction chance%', int)),

    '17': ((0, 'hp drain% low', int),
           (1, 'hp drain% high', int),
           (2, 'hp drain chance%', int)),

    '19': ((0, 'bc production%', int, not_zero),
           (1, 'hc production%', int, not_zero),
           (2, 'item production%', int, not_zero),
           (3, 'zel production%', int, not_zero),
           (4, 'karma production%', int, not_zero)),

    '20': (([0, 1], ailments.get, second_int, not_zero),
           ([2, 3], ailments.get, second_int, not_zero),
           ([4, 5], ailments.get, second_int, not_zero),
           ([6, 7], ailments.get, second_int, not_zero)),

    '21': ((0, 'first x turns atk%', int, not_zero),
           (1, 'first x turns def%', int, not_zero),
           (2, 'first x turns rec% GUESSED', int, not_zero),
           (3, 'first x turns crit% GUESSED', int, not_zero),
           (4, 'first x turns', int)),

    '23': ((0, 'battle end bc fill low', bb_gauge),
           (1, 'battle end bc fill high', bb_gauge)),

    '25': ((0, 'bc fill when attacked low', bb_gauge),
           (1, 'bc fill when attacked high', bb_gauge),
           (2, 'bc fill when attacked%', int)),

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
           (3, 'item drop% for spark GUESSED', int, not_zero),
           (4, 'zel drop% for spark', int, not_zero),
           (5, 'karma drop% for spark', int, not_zero)),

    '32': ((0, 'bb gauge fill rate%', int),),

    '34': ((0, 'dmg% for crits', crit_elem_weakness),),

    '35': ((0, 'bc fill when attacking low', bb_gauge),
           (1, 'bc fill when attacking high', bb_gauge),
           (2, 'bc fill when attacking%', int)),

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
           (6, 'dmg% for elemental weakness', crit_elem_weakness)),

    '10000': ((4, 'taunt turns', int),),

    '10001': ((4, 'stealth turns', int),),
}


def parse_ls_process(process_type, process_info):
    if process_type in ls_process_format:
        return handle_format(ls_process_format[process_type],
                             process_info.split(','))
    return {'unknown passive id': process_type,
            'unknown passive params': process_info}


def parse_leader_skill(unit_data, leader_skill, dictionary):
    data = dict()

    data['name'] = dictionary.get(leader_skill[LS_NAME], leader_skill[LS_NAME])
    data['desc'] = dictionary.get(leader_skill[DESC], leader_skill[DESC])
    data['effects'] = []

    for process_type, process_info in zip(
            leader_skill[PROCESS_TYPE].split('@'),
            leader_skill[LS_PROCESS].split('@')):
        process_data = parse_ls_process(process_type, process_info)
        if 'elements buffed' in process_data and 'elements buffed' in data:
            data['elements buffed'] += process_data.pop('elements buffed')

        data['effects'].append(process_data)
        #data.update(process_data)

    return data
