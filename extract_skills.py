#!/usr/bin/python

import json
import glob
import sys
import collections
import os
from to_json import *
from util import *
from leaderskill import parse_leader_skill
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
        'skill level':  _dir + 'Ver*_zLIvD5o2*',
        'skill':        _dir + 'Ver*_wkCyV73D*',
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

    skills = key_by_id(jsons['skill'], BB_ID)
    bbs = key_by_id(jsons['skill level'], BB_ID)

    skills_data = {}
    for skill in skills:
        skill_data = parse_skill(None, skills[skill], bbs[skill], jsons['dict'], 'jp' in sys.argv)
        skills_data[skill] = skill_data

    #leader_skills_data = {}
    #for ls in leader_skills:
    #	ls_data = parse_leader_skill(None, leader_skills[ls], jsons['dict'])
    #	leader_skills_data[ls] = ls_data
#
    #dump_data = {'bbs': skills_data, 'leader skills': leader_skills_data}

    dump_data = skills_data

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