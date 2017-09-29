import sys
from utils.util import *


def parse_stat_buff(a, b, c, d):
    data = dict()
    stat_type = int(a) - 1
    if stat_type == 0 or stat_type == 3:
        data['atk% buff ' + get_status_change_id(d, 0, b)] = int(b)
    if stat_type == 1 or stat_type == 3:
        data['def% buff ' + get_status_change_id(d, 1, b)] = int(b)
    if stat_type == 2 or stat_type == 3:
        data['rec% buff ' + get_status_change_id(d, 2, b)] = int(b)
    data['proc chance%'] = float(c)
    return data


def get_cured_ailments(info):
    rtn = []
    for a in info:
        if (not_zero(a)):
            rtn.append(ailments.get(a, a).rstrip('%'))
    return {'ailments cured': rtn}


def get_ailment_buff(a, b):
    return ailments.get(a, a) + ' buff'


def get_status_change_id(element, index, value):
    val = int(value)
    ele = int(element)
    ind = int(index)
    rtn = '('
    if (val > 0):
        if (ele > 0):
            rtn += str(ind + 13)
        else:
            rtn += str(2 * ind + 1)
    else:
        if (ele > 0):
            rtn += str(ind + 17)
        else:
            rtn += str(2 * (ind + 1))
    return rtn + ')'


def get_bb_atk_proportional_to_hp(data):
    rtn = {}
    rtn['bb added atk% based on hp'] = int(data[1]) - int(data[0])
    add_type = int(data[2])
    rtn['bb added atk% proportional to hp'] = (
        'lost' if add_type == 1 else 'remaining')
    return rtn


def get_bool(st):
    return st != "1"


skill_level_process_format = {
    '1': ((0, 'bb atk%', int, not_zero),
          (1, 'bb flat atk', int, not_zero),
          (2, 'bb crit%', int, not_zero),
          (3, 'bb bc%', int, not_zero),
          (4, 'bb hc%', int, not_zero),
          (5, 'bb dmg%', int, not_zero),),

    '2': ((0, 'heal low', int),
          (1, 'heal high', int),
          ([2, 3], 'rec added% (from healer)',
           lambda x, y: ((100 + float(x)) * (1 + float(y) / 100)) / 10)),

    '3': ((0, 'gradual heal low', int),
          (1, 'gradual heal high', int),
          (2, 'rec added% (from target)', lambda x: (1 + float(x) / 100) * 10),
          (3, 'gradual heal turns (8)', int)),

    '4': ((0, 'bb bc fill', bb_gauge, not_zero),
          (1, 'bb bc fill%', int, not_zero)),

    '5': ((0, 'element buffed', elements.get),
          ([1, 0], lambda y, x: 'atk% buff ' +
           get_status_change_id(x, 0, y), int, not_zero),
          ([2, 0], lambda y, x: 'def% buff ' +
           get_status_change_id(x, 1, y), int, not_zero),
          ([3, 0], lambda y, x: 'rec% buff ' +
           get_status_change_id(x, 2, y), int, not_zero),
          ([4, 0], lambda y, x: 'crit% buff ' +
           get_status_change_id(x, 3, y), int, not_zero),
          (5, 'buff turns', int)),

    '6': ((0, 'bc drop rate% buff (10)', int, not_zero),
          (1, 'hc drop rate% buff (9)', int, not_zero),
          (2, 'item drop rate% buff (11)', int, not_zero),
          (3, 'drop rate buff turns', int, not_zero)),

    '7': ((0, 'angel idol recover hp%', int, not_zero),
          (0, 'angel idol buff (12)', True)),

    '8': ((0, 'max hp increase', int, not_zero),
          (1, 'max hp% increase', float, not_zero),),

    '9': ((0, 'element buffed', elements.get),  # status change buff, again
          ([1, 2, 3, 0], 'buff #1', parse_stat_buff, not_zero),
          ([4, 5, 6, 0], 'buff #2', parse_stat_buff, not_zero),
          (7, 'buff turns', int)),

    '10': ((0, 'remove all status ailments', True),),

    '11': (([0, 1], ailments.get, second_int, not_zero),
           ([2, 3], ailments.get, second_int, not_zero),
           ([4, 5], ailments.get, second_int, not_zero),
           ([6, 7], ailments.get, second_int, not_zero)),

    '12': ((0, 'revive to hp%', int),),

    '13': ((0, 'random attack', True),
           (0, 'bb atk%', int, not_zero),
           (1, 'bb flat atk', int, not_zero),
           (2, 'bb crit%', int, not_zero),
           (3, 'bb bc%', int, not_zero),
           (4, 'bb hc%', int, not_zero),
           (5, 'hits', int, not_zero)),

    '14': ((0, 'bb atk%', int, not_zero),
           (1, 'bb flat atk', int, not_zero),
           (2, 'bb crit%', int, not_zero),
           (3, 'bb bc%', int, not_zero),
           (4, 'bb hc%', int, not_zero),
           (5, 'bb dmg%', int, not_zero),
           (6, 'hp drain% low', int),
           (7, 'hp drain% high', int)),

    #'15': #another status change buff
    '16': (([0, 1], lambda a: 'mitigate %s attacks (%d)' % (elements.get(a, a), int(a) + 20), second_int),
           (2, 'buff turns', int),),

    '17': ((0, 'resist poison% (30)', float, not_zero),
           (1, 'resist weaken% (31)', float, not_zero),
           (2, 'resist sick% (32)', float, not_zero),
           (3, 'resist injury% (33)', float, not_zero),
           (4, 'resist curse% (34)', float, not_zero),
           (5, 'resist paralysis% (35)', float, not_zero),
           (6, 'resist status ails turns', int),),

    '18': ((0, 'dmg% reduction', int),
           (1, 'dmg% reduction turns (36)', int)),

    '19': ((0, 'increase bb gauge gradual', bb_gauge),
           (1, 'increase bb gauge gradual turns (37)', int)),

    '20': ((0, 'bc fill when attacked low', bb_gauge),
           (1, 'bc fill when attacked high', bb_gauge),
           (2, 'bc fill when attacked%', int),
           (3, 'bc fill when attacked turns (38)', int)),

    '22': ((0, 'defense% ignore', int),
           (1, 'defense% ignore turns (39)', int)),

    '23': ((0, 'spark dmg% buff (40)', int),
           (6, 'buff turns', int)),

    '24': ((0, 'converted attribute', attribute.get),
           (1, 'atk% buff (46)', int, not_zero),
           (2, 'def% buff (47)', int, not_zero),
           (3, 'rec% buff (48)', int, not_zero),
           (4, '% converted turns', int)),

    '26':  ((0, 'hit increase/hit', int),
            (2, 'extra hits dmg%', int, not_zero),
            (7, 'hit increase buff turns (50)', int)),

    '27': ((0, 'hp% damage low', int),
           (1, 'hp% damage high', int),
           (2, 'hp% damage chance%', int),
           (3, 'bb atk%', int, not_zero),
           (4, 'bb flat atk', int, not_zero),
           (5, 'bb crit%', int, not_zero),
           (6, 'bb bc%', int, not_zero),
           (7, 'bb hc%', int, not_zero),
           (8, 'bb dmg%', int, not_zero),),

    '28': ((0, 'fixed damage', int),),

    '29': (([0, 1, 2], 'bb elements',
            lambda x, y, z: map(elements.get, filter(not_zero, [x, y, z]))),
           (3, 'bb atk%', int, not_zero),
           (4, 'bb flat atk', int, not_zero),
           (5, 'bb crit%', int, not_zero),
           (6, 'bb bc%', int, not_zero),
           (7, 'bb hc%', int, not_zero),
           (8, 'bb dmg%', int, not_zero)),

    '30': (([0, 1, 2, 3, 4, 5], 'elements added',
            lambda x, y, z, a, b, c: map(elements.get, filter(not_zero, [x, y, z, a, b, c]))),
           (6, 'elements added turns', int)),

    '31': ((0, 'increase bb gauge', bb_gauge),),

    '32': ((0, 'set attack element attribute', elements.get),),

    '33': ((0, 'clear buff chance%', float),),

    '34': ((0, 'base bb gauge reduction low', bb_gauge),
           (1, 'base bb gauge reduction high', bb_gauge),
           (2, 'bb gauge% reduction low', int),
           (3, 'bb gauge% reduction high', int),
           (4, 'bb gauge reduction chance%', float)),

    # elemental weakness ala 55?

    '36': ((0, 'invalidate LS chance%', int),
           (1, 'invalidate LS turns (60)', int),),

    '38': ((get_cured_ailments),),

    '39': ((0, lambda el: 'mitigate %s attacks' %
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
           (7, 'dmg% mitigation for elemental attacks buff turns', int),),

    '40': (([0, 1], get_ailment_buff, second_int, not_zero),
           ([2, 3], get_ailment_buff, second_int, not_zero),
           ([4, 5], get_ailment_buff, second_int, not_zero),
           ([6, 7], get_ailment_buff, second_int, not_zero),
           (8, 'buff turns', int)),

    '44': ((0, 'dot atk%', int),
           (1, 'dot flat atk', int, not_zero),
           (2, 'dot dmg%', int, not_zero),
           (3, 'dot element affected', get_bool),
           (4, 'dot unit index', int),
           (5, 'dot turns (71)', int),),

    #'42': ((0, 'low%', ),
    #       (1, 'high%',),
    #       (2, 'static'),
    #       ()),

    '43': ((0, 'increase od gauge%', float),),

    '45': ((0, 'bb atk% buff', int, not_zero),
           (1, 'sbb atk% buff', int, not_zero),
           (2, 'ubb atk% buff', int, not_zero),
           (3, 'buff turns (72)', int)),

    '47': ((0, 'bb base atk%', int, not_zero),
           (get_bb_atk_proportional_to_hp),
           (3, 'bb flat atk', int, not_zero),
           (4, 'bb crit%', int, not_zero),
           (5, 'bb bc%', int, not_zero),
           (6, 'bb hc%', int, not_zero),
           (7, 'bb dmg%', int, not_zero)),

    '51': ((0, 'inflict atk% debuff (2)', int, not_zero),
           (1, 'inflict def% debuff (4)', int, not_zero),
           (2, 'inflict rec% debuff (6)', int, not_zero),
           (3, 'inflict atk% debuff chance% (74)', float, not_zero),
           (4, 'inflict def% debuff chance% (75)', float, not_zero),
           (5, 'inflict rec% debuff chance% (76)', float, not_zero),
           (6, 'stat% debuff turns', int, not_zero),
           (7, 'buff turns', int, not_zero)),

    '52': ((0, 'bb gauge fill rate% buff', float, not_zero),
           (1, 'buff turns (77)', int)),

    '53': ((0, 'counter inflict poison% (78)', int, not_zero),
           (1, 'counter inflict weaken% (79)', int, not_zero),
           (2, 'counter inflict sick% (80)', int, not_zero),
           (3, 'counter inflict injury% (81)', int, not_zero),
           (4, 'counter inflict curse% (82)', int, not_zero),
           (5, 'counter inflict paralysis% (83)', int, not_zero),
           (6, 'counter inflict ailment turns', int)),

    '54': ((0, 'crit multiplier%', crit_elem_weakness),
           (1, 'buff turns (84)', int),),

    '55': ((0, lambda el: '%s units do extra elemental weakness dmg' %
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
           (6, 'elemental weakness multiplier%', crit_elem_weakness),
           (7, 'elemental weakness buff turns', int)),

    '56': ((0, 'angel idol recover chance%', int, not_zero),
           (1, 'angel idol recover hp%', int, not_zero),
           (2, 'angel idol buff turns (91)', int, not_zero)),

    '57': ((0, 'base bc drop% resist buff', int, not_zero),
           (1, 'buffed bc drop% resist buff', int, not_zero),
           (4, 'bc drop% resist buff turns (92)', int),),

    '58': ((0, 'spark dmg% received', int),
           (1, 'spark dmg received apply%', int),
           (2, 'spark dmg received debuff turns (94)', int)),

    '61': ((0, 'bb base atk%', int, not_zero),
           (1, 'bb max atk% based on ally bb gauge and clear bb gauges', int, not_zero),
           (2, 'bb flat atk', int, not_zero),
           (3, 'bb crit%', int, not_zero),
           (4, 'bb bc%', int, not_zero),
           (5, 'bb hc%', int, not_zero),
           (6, 'bb dmg%', int, not_zero)),

    '62': ((0, 'elemental barrier element', elements.get),
           (1, 'elemental barrier hp', int),
           (2, 'elemental barrier def', int),
           (3, 'elemental barrier absorb dmg%', int)),

    '64': ((0, 'bb base atk%', int, not_zero),
           (1, 'bb atk% inc per use', int, not_zero),
           (2, 'bb atk% max number of inc', int, not_zero),
           (3, 'bb flat atk', int, not_zero),
           (4, 'bb crit%', int, not_zero),
           (5, 'bb bc%', int, not_zero),
           (6, 'bb hc%', int, not_zero),
           (7, 'bb dmg%', int, not_zero)),

    '65': ((0, 'atk% buff when enemy has ailment', int),
           (1, 'atk% buff turns (110)', int),),

    '66': ((0, 'revive unit hp%', int),
           (1, 'revive unit chance%', float)),

    '67': ((0, 'bc fill on spark low', bb_gauge),
           (1, 'bc fill on spark high', bb_gauge),
           (2, 'bc fill on spark%', int),
           (3, 'bc fill on spark buff turns (111)', int)),

    '68': ((0, 'guard increase mitigation%', int),
           (1, 'guard increase mitigation buff turns (113)', int),),

    '69': ((0, 'bb bc fill on guard', bb_gauge, not_zero),
           (1, 'bb bc fill% on guard', int, not_zero),
           (2, 'bb bc fill on guard buff turns (114)', int)),

    '71': ((0, 'bb fill inc%', int),
           (1, 'bb fill inc buff turns (112)', int)),

    '73': ((0, 'atk down resist% (120)', int),
           (1, 'def down resist% (121)', int),
           (2, 'rec down resist% (122)', int),
           (3, 'stat down immunity buff turns', int),),

    '75': ((0, 'counted element for buff multiplier', elements.get),
           (1, 'atk% buff (1)', int, not_zero),
           (2, 'def% buff (3)', int, not_zero),
           (3, 'rec% buff (5)', int, not_zero),
           (4, 'crit% buff (7)', int, not_zero),
           (5, 'buff turns', int, not_zero)),

    '76': ((0, 'max number of extra actions', int),
           (1, 'chance% for extra action', int),
           (2, 'extra action buff turns (123)', int)),

    '78': ((0, 'self atk% buff', int, not_zero),
           (1, 'self def% buff', int, not_zero),
           (2, 'self rec% buff', int, not_zero),
           (3, 'self crit% buff', int, not_zero),
           (4, 'self stat buff turns', int)),

    '83': ((0, 'spark dmg inc chance%', int),
           (1, 'spark dmg inc% buff', int),
           (2, 'spark dmg inc buff turns (131)', int)),

    '84': ((0, 'od fill rate% buff', int),
           (1, 'od fill rate buff turns (132)', int)),

    '85': ((0, 'hp recover from dmg% low', int),
           (1, 'hp recover from dmg% high', int),
           (2, 'hp recover from dmg chance', int),
           (3, 'hp recover from dmg buff turns (133)', int),),

    '86': ((0, 'hp drain% low', int),
           (1, 'hp drain% high', int),
           (2, 'hp drain chance%', int),
           (3, 'hp drain buff turns (134)', int)),

    '87': ((0, 'spark recover hp low', int),
           (1, 'spark recover hp high', int),
           (2, 'spark recover hp chance%', int),
           (3, 'spark recover hp buff turns (135)', int)),

    '88': ((0, 'spark dmg inc%', int),
           # unknown, unused params from 1-5
           (6, 'spark dmg inc% turns (136)', int)),

    '93': ((0, 'crit dmg base damage resist% (143)', int, not_zero),
           (1, 'crit dmg buffed damage resist% (143)', int, not_zero),
           (2, 'strong base element damage resist% (144)', int, not_zero),
           (3, 'strong buffed element damage resist% (144)', int, not_zero),
           (4, 'spark dmg base resist% (145)', int, not_zero),
           (5, 'spark dmg buffed resist% (145)', int, not_zero),
           (6, 'dmg resist turns', int)),

    '94': ((0, 'aoe atk inc%', int),
           (1, 'chance to aoe', int),
           (6, 'aoe atk turns (142)', int)),

    '132': ((0, 'crit vuln dmg%', int, not_zero),
            (1, 'elemental vuln dmg%', int, not_zero),
            (2, 'crit vuln chance%', float, not_zero),
            (3, 'elemental vuln chance%', float, not_zero),
            (4, 'vuln turns', int, not_zero)),

    '902': ((0, 'atk% buff (100)', int, not_zero),
            (1, 'def% buff (101)', int, not_zero),
            (2, 'rec% buff (102)', int, not_zero),
            (3, 'crit% buff (103)', int, not_zero),
            (4, 'buff timer (seconds)', int)),

    '10000': ((0, 'atk% buff', int, not_zero),
              (1, 'def% buff', int, not_zero),
              (2, 'crit% buff', int, not_zero),
              (3, 'taunt turns (10000)', int)),

    '10001': ((0, 'atk% buff', int, not_zero),
              (1, 'def% buff', int, not_zero),
              (2, 'crit% buff', int, not_zero),
              (3, 'rec% buff', int, not_zero),
              (4, 'stealth turns (10001)', int)),

    '10002': ((0, 'shield def', int, not_zero),
              (1, 'shield hp', int, not_zero),
              (2, 'shield element', elements.get),
              (3, 'shield turns (10002)', int),),

    '11000': ((0, 'bb base atk%', int, not_zero),
              (get_bb_atk_proportional_to_hp),
              (3, 'bb flat atk', int, not_zero),
              (4, 'bb crit%', int, not_zero),
              (5, 'bb bc%', int, not_zero),
              (6, 'bb hc%', int, not_zero),
              (7, 'bb dmg%', int, not_zero)),
}


def parse_skill_level_process(process_type, process_info, debug=False):
    process_data = {}
    if debug:
        process_data['_debug id'] = process_type
        process_data['_debug params'] = process_info
    if process_type in skill_level_process_format:
        process_data.update(handle_format(skill_level_process_format[process_type],
                                          process_info.split(',')))
        process_data['proc id'] = process_type
        return process_data
    return {'unknown proc id': process_type,
            'unknown proc param': process_info}


def parse_skill_level_processes(process_types, process_infos, start_frames, target_types, target_areas, debug=False):
    level_data = []
    index = 0
    for process_type, process_info in zip(process_types, process_infos):
        process_data = {}
        try:
            process_data = parse_skill_level_process(process_type,
                                                     process_info)
        except Exception, err:
            process_data = {'error occured during parsing': str(sys.exc_info()[0]),
                            'process ids': process_types,
                            'process params': process_infos}
        # if 'elements added' in process_data and 'elements added' in level_data:
        #     level_data['elements added'] += process_data.pop('elements added')

        # if 'bb elements' in process_data and 'bb elements' in level_data:
        #     level_data['bb elements'] += process_data.pop('bb elements')

        if start_frames != None:
            try:
                float(start_frames[index])
                process_data['effect delay time(ms)/frame'] = str(
                    round((float(start_frames[index]) / 60) * 1000, 1)) + '/' + start_frames[index]
            except:
                pass
        try:
            process_data['target type'] = target_type_names.get(
                target_types[index], target_types[index])
        except:
            pass
        try:
            process_data['target area'] = target_area_names.get(
                target_areas[index], target_areas[index])
        except:
            pass

        if debug:
            process_data['_debug id'] = process_type
            process_data['_debug params'] = process_info

        level_data.append(process_data)

        index += 1

    return level_data


def parse_skill_levels(skill_data, skill, skill_levels, debug=False):
    start_frames = skill[SKILL_START_FRAME].split('@')
    skill_level_format = (
        (1, 'bc cost', bb_gauge),

        (2, 'effects',
            lambda lvl: parse_skill_level_processes(
                skill[PROCESS_TYPE].split('@'), lvl.split('@'),
                start_frames, skill[ITEM_TARGET_TYPE].split('@'),
                skill[SKILL_TARGET_AREA].split('@'), debug)),

        # ([], 'max bc generated',
        #  lambda data: data['hits'] * int(skill[DROP_CHECK_CNT]),
        #  lambda data: 'hits' in data),

        # ([], 'lord damage range',
        #  lambda data: dmg_str(damage_range_bb(unit_data, skill_data, data)),
        #  lambda data: 'bb atk%' in data)
    )

    datas = [handle_format(skill_level_format, level_info.split(':'))
             for level_info in skill_levels[SKILL_LEVELS_PROCESSES].split('|')]
    # for i in range(0, len(datas)):
    #     if 'hits' in datas[i]['effects'][0]:
    #         datas[i]['max bc generated'] = datas[i]['effects'][0]['hits'] * int(skill[DROP_CHECK_CNT])
    return datas


def parse_skill(skill, skill_levels, dictionary, jp=True, debug=False, id=None):
    atk_process_types = {'1', '14', '27', '29', '47', '61', '64', '75'}

    def get_skill_atk_frame(process_types, action_frames):
        for process_type, action_frame in zip(process_types.split('@'),
                                              action_frames.split('@')):
            if process_type in atk_process_types:
                return action_frame

    def get_damage_frames(process_types, action_frames, start_frames):
        procList = []
        for process_type, action_frame, start_frame in zip(process_types.split('@'),
                                                           action_frames.split(
                                                               '@'),
                                                           start_frames.split('@')):
            data = {}
            data['proc id'] = process_type
            data['hit dmg% distribution'] = NoIndent(
                hit_dmg_dist(action_frame))
            data['frame times'] = NoIndent(frame_time_dist(action_frame))
            data['hit dmg% distribution (total)'] = hit_dmg_dist_total(
                action_frame)
            data['hits'] = hits(action_frame)
            try:
                float(start_frame)
                data['effect delay time(ms)/frame'] = str(
                    round((float(start_frame) / 60) * 1000, 1)) + '/' + start_frame
            except:
                pass
            procList.append(data)

        return procList

    skill_format = ((BB_NAME, 'name', get_skill_name(dictionary, id, jp)),
                    (DESC, 'desc', get_skill_desc(dictionary, id, jp)),

                    ([PROCESS_TYPE, DMG_FRAME, SKILL_START_FRAME], 'damage frames',
                     lambda p, a, s: get_damage_frames(p, a, s)),

                    # ([PROCESS_TYPE, DMG_FRAME], 'hits',
                    #  lambda p, a: hits(get_skill_atk_frame(p, a)),
                    #  lambda p: not set(p.split('@')).isdisjoint(
                    #      atk_process_types)),

                    # ([PROCESS_TYPE, DMG_FRAME], 'hit dmg% distribution',
                    #  lambda p, a: hit_dmg_dist(get_skill_atk_frame(p, a)),
                    #  lambda p, a, data: 'hits' in data),

                    # ([PROCESS_TYPE, DMG_FRAME], 'hit dmg% distribution (total)',
                    #  lambda p, a: hit_dmg_dist_total(get_skill_atk_frame(p, a)),
                    #  lambda p, a, data: 'hits' in data),

                    (DROP_CHECK_CNT, 'drop check count', int),

                    # (DROP_CHECK_CNT, 'max bc generated',
                    #  lambda x, data: data['hits'] * int(x),
                    #  lambda x, data: 'hits' in data),

                    ([], 'levels', lambda data: parse_skill_levels(
                        data, skill, skill_levels, debug)))

    rtn = handle_format(skill_format, skill)
    if id != None:
        rtn['id'] = id
    if 'hit dmg% distribution' in rtn:
        rtn['hit dmg% distribution'] = NoIndent(rtn['hit dmg% distribution'])
    return rtn
