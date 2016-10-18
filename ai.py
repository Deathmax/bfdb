import json
import glob
import sys
import os


ai_js = []
_dir = 'data/decoded_dat/'
if len(sys.argv) > 1:
    _dir = sys.argv[1]

with open(max(glob.iglob(_dir + '*XkBhe70R*'), key=os.path.getctime)) as f:#open('data/jp/decoded_dat/Ver63_XkBhe70R.dat.json') as f:#
	ai_js = json.load(f)

ai_datas = dict()

for ai_data in ai_js:
	if ai_data['4eEVw5hL'] in ai_datas:
		ai_datas[ai_data['4eEVw5hL']].append(ai_data)
	else:
		ai_datas[ai_data['4eEVw5hL']] = []
		ai_datas[ai_data['4eEVw5hL']].append(ai_data)

dump_data = dict()

for ai_id, ai_action_data in ai_datas.items():
	data = dict()
	data['actions'] = []
	for action in ai_action_data:
		ai_data = dict()
		ai_data['target conditions'] = action['VBj9u0ot']
		ai_data['target type'] = int(action['4xctV8gF'])
		ai_data['percent'] = float(action['ug9xV4Fz'])
		ai_data['party conditions/set parameters'] = []
		ai_data['conditions/set parameters'] = []
		ai_terms = action['q7Nit8JW'].split('#')
		#partyact
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
			ai_data['party conditions/set parameters'].append({'type': termId, 'parameters': termParam, 'target type': targetId, 'target param': targetParam})
		#act
		partsList = ai_terms[1].split('@')
		for parts in partsList:
			targetParts = parts.split(':')
			if len(targetParts) == 1:
				continue
			termId = targetParts[0]
			if termId == 'non':
				continue
			termParam = targetParts[1]
			ai_data['conditions/set parameters'].append({'type': termId, 'parameters': termParam})
		#ai_terms = action['q7Nit8JW'].split('#')[1]
		#ai_conditions = ai_terms.split('@')
		#for ai_condition in ai_conditions:
		#	if ai_condition.split(':')[0] == 'non' or ai_condition.split(':')[0] == '':
		#		continue
		#	ai_data['conditions/set parameters'].append({'type': ai_condition.split(':')[0], 'parameters': ai_condition.split(':')[1]})
		ai_data['action'] = {'type': action['Hhgi79M1'].split('@')[0], 'parameters': action['Hhgi79M1'].split('@')[1]}
		ai_data['priority'] = action['yu18xScw']
		data['actions'].append(ai_data)
		data['name'] = action['L8PCsu0K']
	dump_data[ai_id] = data

print json.dumps(dump_data, indent=4, ensure_ascii=False, sort_keys=True).encode('utf8')