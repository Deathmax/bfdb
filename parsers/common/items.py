from utils.util import *
from parsers.common.skills import parse_skill_level_process
from parsers.common.passives import parse_ls_process


def parse_item_remove_status_ailments(process_info):
    effect = dict()
    for status in process_info:
        if int(status) != 0 and int(status) < 7:
            effect['remove ' + ailments[status].rstrip('%')] = True
    return effect


item_process_format = {
    '1': ((0, 'item atk%', int, not_zero),
          (1, 'item flat atk', int, not_zero),
          (2, 'item crit%', int, not_zero),
          (3, 'item bc%', int, not_zero),
          (4, 'item hc%', int, not_zero),
          (5, 'item dmg%', int, not_zero)),

    '10': (parse_item_remove_status_ailments,),
}


def parse_item_process(process_type, process_info, debug=False):
    if process_type in item_process_format:
        return handle_format(item_process_format[process_type],
                             process_info.split(','))
    return parse_skill_level_process(process_type, process_info, debug)


def parse_item_effect(item, data, debug=False):
    effects = dict()
    effects['effect'] = []
    for process_type, process_info in zip(item[PROCESS_TYPE].split('@'),
                                          item[ITEM_PROCESS].split('@')):
        effects['effect'].append(parse_item_process(
            process_type, process_info, debug))
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
            data['effect'] = parse_sphere_effect(
                item_data, data, dictionary, debug)
        elif item_type == '4':
            data['type'] = 'evomat'
        elif item_type == '5':
            data['type'] = 'summoner_consumable'
            data['max equipped'] = int(item[ITEM_MAX_EQUIPPED])
            data['effect'] = parse_item_effect(item_data, data, debug)
        elif item_type == '6':
            data['type'] = 'ls_sphere'
            data['effect'] = parse_sphere_effect(
                item_data, data, dictionary, debug)
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
