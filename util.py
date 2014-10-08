from to_json import *

UNIT_NAME = 'utP1c0CD'
UNIT_ELEMENT = 'iNy0ZU5M'
UNIT_RARITY = '7ofj5xa1'
UNIT_BASE_HP = 'UZ1Bj7w2'
UNIT_LORD_HP = '3WMz78t6'
UNIT_BASE_ATK = 'i9Tn7kYr'
UNIT_LORD_ATK = 'omuyP54D'
UNIT_BASE_DEF = 'q78KoWsg'
UNIT_LORD_DEF = '32INDST4'
UNIT_BASE_REC = '92ij6UGB'
UNIT_LORD_REC = 'X9P3AN5d'
UNIT_MAX_LEVEL = 'EI1DF8Yt'
UNIT_IMP = 'imQJdg64'
UNIT_ID = 'pn16CNah'
UNIT_GUIDE_ID = 'XuJL4pc5'
UNIT_EXP_PATTERN_ID = '5UvTp7q1'
UNIT_AI_ID = 'i74vGUFa'
DMG_FRAME = '6Aou5M9r'
DROP_CHECK_CNT = 'n9h7p02P'
BB_ID = 'nj9Lw7mV'
SBB_ID = 'iEFZ6H19'
BB_NAME = '0nxpBDz2'
SKILL_LEVELS_PROCESSES = 'Kn51uR4Y'
SKILL_START_FRAME = 'qYCx73y2'
LS_ID = 'oS3kTZ2W'
LS_NAME = 'dJPf9a5v'
LS_PROCESS = '2Smu5Mtq'
PROCESS_TYPE = 'hjAy9St3'
DESC = 'qp37xTDh'
AI_ID = '4eEVw5hL'
AI_CHANCE = 'ug9xV4Fz'
AI_TARGET = 'VBj9u0ot'
AI_ACTION_PARAMS = 'Hhgi79M1'
AI_NAME = 'L8PCsu0K'

REQ_HEADER_TAG = 'F4q6i9xe'
REQ_ID = 'Hhgi79M1'
REQ_BODY_TAG = 'a3vSYuq2'
REQ_BODY = 'Kn51uR4Y'

ITEM_NAME = 'c7Z6xDB2'
ITEM_RARITY = '7ofj5xa1'
ITEM_SELL_PRICE = 'eKtE6k0n'
ITEM_MAX_STACK = 'm9gd5h1u'
ITEM_ID = 'kixHbe54'
ITEM_MAX_EQUIPPED = 't1i2vIbT'
ITEM_PROCESS = '2Smu5Mtq'
ITEM_TARGET_TYPE = 'moWQ30GH'
ITEM_TARGET_AREA = '6E2fGPWT'
ITEM_TYPE = 'h0K7wjeH'

item_types = {
    '0': 'other',
    '1': 'consumable',
    '2': 'material',
    '3': 'sphere'
}

elements = {
    '0': 'all',
    '1': 'fire',
    '2': 'water',
    '3': 'earth',
    '4': 'thunder',
    '5': 'light',
    '6': 'dark'
}

ailments = {
    '1': 'poison%',
    '2': 'weaken%',
    '3': 'sick%',
    '4': 'injury%',
    '5': 'curse%',
    '6': 'paralysis%'
}

attribute = {
    '1': 'attack',
    '2': 'defense',
    '3': 'recovery',
    '4': 'hp'
}


def damage_range(atk):
    return (int((atk * 0.9) + (atk / 32)),
            int(atk + (atk / 25)))


def damage_range_bb(unit, skill, bb_level):
    total_atk = unit['lord atk']
    modifier = bb_level['bb atk%']
    modifier += bb_level.get('atk% buff', 0)

    total_atk = total_atk * (1 + float(modifier) / 100)
    total_atk += bb_level.get('bb flat atk', 0)
    total_atk = total_atk * (1 + float(bb_level.get('bb dmg%', 0))
                             / 100)
    total_atk = total_atk * float(sum(
        skill.get('hit dmg% distribution', [100]))) / 100
    total_atk = int(total_atk)
    return damage_range(total_atk)


def dmg_str(limits):
    return '~'.join(map(str, limits))


def not_zero(a):
    if len(a) == 0:
        return False
    return int(a) != 0


def bb_gauge(a):
    return int(a) / 100


def hits(atk_frames):
    return len(atk_frames.split(','))


def hit_dmg_dist(atk_frames):
    if atk_frames == '0':
        return []
    return [int(hit.split(':')[1]) for hit in atk_frames.split(',')]


def hit_dmg_dist_total(atk_frames):
    if atk_frames == '0':
        return 0
    return sum([int(hit.split(':')[1]) for hit in atk_frames.split(',')])


def parse_imps(args):
    return {'max hp': args[0],
            'max atk': args[1],
            'max def': args[2],
            'max rec': args[3]}


def second_int(_, a):
    return int(a)


def get_dict_str(dictionary):
    return lambda s: dictionary.get(s, s)


def handle_format(fmt, obj):
    import inspect

    data = {}
    for entry in fmt:
        if hasattr(entry, '__call__'):
            data.update(entry(obj))
            continue

        indices = entry[0]
        if not hasattr(indices, '__iter__'):
            indices = [indices]

        key = entry[1]
        value = entry[2]
        if len(entry) > 3:
            predicate = entry[3]
        else:
            predicate = lambda x: True

        skip = False
        for idx in indices:
            skip |= type(idx) == int and idx >= len(obj)
            skip |= type(idx) != int and idx not in obj

        if skip:
            continue

        args = map(obj.__getitem__, indices) + [data]

        def _call(fn, args):
            try:
                num_args = len(inspect.getargspec(fn).args)
            except TypeError:
                num_args = 1
            return fn(*args[:num_args])

        if _call(predicate, args) is not True:
            continue

        if hasattr(key, '__call__'):
            key = _call(key, args)

        if hasattr(value, '__call__'):
            value = _call(value, args)

        data[key] = value

    return data
