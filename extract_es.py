#!/usr/bin/python

import json
import glob
import sys
import collections
import os
from to_json import *
from util import *
from leaderskill import parse_leader_skill
from leaderskill import parse_extra_skill
from braveburst import parse_skill

reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')


if __name__ == '__main__':
    _dir = 'data/decoded_dat/'
    dict_file = 'data/dictionary_raw.txt'
    if len(sys.argv) > 1:
        _dir = sys.argv[1]
    if len(sys.argv) > 2:
        dict_file = sys.argv[2]

    files = {
        'dict': dict_file,
        'extra skill':  _dir + 'Ver*_kP4pTJ7n*',
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

    if 'extra skill' in jsons:
        extra_skills = key_by_id(jsons['extra skill'], ES_ID)
    else:
        sys.exit()

    #skills_data = {}
    #for skill in skills:
    #    skill_data = parse_skill(None, skills[skill], bbs[skill], jsons['dict'])
    #    skills_data[skill] = skill_data

    #leader_skills_data = {}
    #for ls in leader_skills:
    #	ls_data = parse_leader_skill(None, leader_skills[ls], jsons['dict'])
    #	leader_skills_data[ls] = ls_data

    extra_skills_data = {}
    for es in extra_skills:
        es_data = parse_extra_skill(None, extra_skills[es], jsons['dict'], 'jp' in sys.argv)
        extra_skills_data[es] = es_data

    #dump_data = {'bbs': skills_data, 'leader skills': leader_skills_data}

    dump_data = extra_skills_data

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