from utils.util import *

# TODO: Possibly find some way of sharing the data parsed from the AI step with the unit step
# but not critical, as AI takes ~4 seconds on an i5 6500 anyways

def merge_action_data(ai_list):
    ai_datas = {}
    for ai_data in ai_list:
        if ai_data[AI_ID] in ai_datas:
            parsed_data = parse_ai_action(ai_data)
            parsed_data.pop('name')
            ai_datas[ai_data[AI_ID]]['actions'].append(parsed_data)
        else:
            ai_datas[ai_data[AI_ID]] = {'actions': []}
            parsed_data = parse_ai_action(ai_data)
            ai_datas[ai_data[AI_ID]]['name'] = parsed_data['name']
            parsed_data.pop('name')
            ai_datas[ai_data[AI_ID]]['actions'].append(parsed_data)
    return ai_datas


def parse_ai_for_unit(ai):
    ai_format = ((AI_ID, 'id', str),
                 (AI_CHANCE, 'chance%', float),
                 (AI_TARGET_CONDITIONS, 'target conditions', str),
                 (AI_ACTION_PARAMS, 'action', lambda s: s.split('@')[0]),
                 (AI_TARGET_TYPE, 'target type', target_type_names.get))

    return handle_format(ai_format, ai)


def parse_ai_action(ai):
    def parse_condtions(ai_data):
        data = {}
        data['party conditions/set parameters'] = []
        data['conditions/set parameters'] = []

        ai_terms = ai[AI_TERM].split('#')
        # partyact
        partsList = ai_terms[0].split('@')
        for parts in partsList:
            targetParts = parts.split(':')
            if len(targetParts) == 1:
                continue
            targetId = targetParts[0]
            if targetId == '0':
                continue
            targetParam = targetParts[1]
            termId = targetParts[2]
            termParam = targetParts[3]
            data['party conditions/set parameters'].append(
                {'type': termId, 'parameters': termParam, 'target type': targetId, 'target param': targetParam})

        # act
        partsList = ai_terms[1].split('@')
        for parts in partsList:
            targetParts = parts.split(':')
            if len(targetParts) == 1:
                continue
            termId = targetParts[0]
            if termId == 'non':
                continue
            termParam = targetParts[1]
            data['conditions/set parameters'].append(
                {'type': termId, 'parameters': termParam})

        return data

    def parse_action(ai_data):
        parts = ai_data.split('@')
        if len(parts) >= 2:
            return {'type': parts[0], 'parameters': parts[1]}
        else:
            return {}

    ai_format = ((AI_CHANCE, 'percent', float),
                 (AI_TARGET_CONDITIONS, 'target conditions', str),
                 (AI_TARGET_TYPE, 'target type', int),
                 (AI_PRIORITY, 'priority', str),
                 (AI_NAME, 'name', str),
                 (AI_ACTION_PARAMS, 'action', parse_action),
                 (parse_condtions))

    return handle_format(ai_format, ai)
