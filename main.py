#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import argparse
import traceback
import parsers
from timeit import default_timer as timer
from loader.jsonloader import JsonLoader
from utils.config import Config
from utils.util import *

# Force python to use utf-8, this is apparently bad
# but we need it else we fail to properly load dat files
# see: http://stackoverflow.com/questions/3828723/
reload(sys)
sys.setdefaultencoding("utf-8")


def main():
    # Process command line args
    parser = argparse.ArgumentParser(
        description='Process Brave Frontier data files.')
    parser.add_argument('--config', dest='config_path', metavar="CONFIG",
                        default=Config.DEFAULT_CONFIG_PATH,
                        help='path to config file')

    args = parser.parse_args()

    # Load the config file
    config = Config(args.config_path)

    files = {
        # dict file
        'dict':         {'filename': config.dictionary_path},

        # Legacy .dat files
        'ai':           {'filename': config.directory_dat + 'Ver*_XkBhe70R*'},
        'evo':          {'filename': config.directory_dat + 'Ver*_Ef6oG0mz*'},
        'extra skill':  {'filename': config.directory_dat + 'Ver*_kP4pTJ7n*', 'idkey': ES_ID},
        'fe skill':     {'filename': config.directory_dat + 'Ver*_2h9r3yEY*', 'idkey': FE_ID},
        'items':        {'filename': config.directory_dat + 'Ver*_83JWTCGy*'},
        'leader skill': {'filename': config.directory_dat + 'Ver*_4dE8UKcw*', 'idkey': LS_ID},
        'skill level':  {'filename': config.directory_dat + 'Ver*_zLIvD5o2*', 'idkey': BB_ID},
        'skill':        {'filename': config.directory_dat + 'Ver*_wkCyV73D*', 'idkey': BB_ID},
        'unit fe cat':  {'filename': config.directory_dat + 'Ver*_nd18wpsy*'},
        'unit fe skill': {'filename': config.directory_dat + 'Ver*_8gu2U4Mh*'},
        'unit type':    {'filename': config.directory_dat + 'Ver*_J4heGZ2U*', 'idkey': UNITTYPE_ID},
        'unit':         {'filename': config.directory_dat + 'Ver*_2r9cNSdt*'},

        # Proper .json files
        'area':         {'filename': config.directory_json + 'M_AREA_MST.json'},
        'dungeon':      {'filename': config.directory_json + 'M_DUNGEON_MST.json'},
        'land':         {'filename': config.directory_json + 'M_LAND_MST.json'},
        'mission':      {'filename': config.directory_json + 'F_MISSION_MST.json'},
        'recipe_f':     {'filename': config.directory_json + 'F_RECIPE_MST.json', 'idkey': RECIPE_ITEM_ID},
        'recipe_m':     {'filename': config.directory_json + 'M_RECIPE_MST.json', 'idkey': RECIPE_ITEM_ID},
        # 'town facility': {'filename': config.directory_json + 'M_TOWN_FACILITY_LV_MST.json'},

        # Animation data
        'cgs':          {'filename': config.directory_dat + 'animationpreprocess.json'}
    }

    start = timer()
    # Load all the json files
    jsons = {name: loader.json for name,
             loader in JsonLoader.loadjsonfiles(**files).iteritems()}
    end = timer()
    print "File loading took {}s".format(end - start)

    # Add foreign config into the data dict
    jsons['isForeign'] = config.foreign

    # Run all the parsers specified in the config
    # Warning, some parsers may have dependencies on others (such as unit -> skills)
    # so ordering is important!
    for parser_name in config.parsers:
        try:
            if parser_name not in parsers.PARSER_DICT:
                print "Warning, " + parser_name + " was not found"
                continue
            start = timer()
            data_parser = parsers.PARSER_DICT[parser_name](**jsons)
            data_parser_name = data_parser.__class__.__name__
            print "Running {}".format(data_parser_name)
            data_parser.run()
            # Store parsed data for when we want to use it for other parsers
            jsons[data_parser_name] = data_parser.get_parsed_data()
            data_parser.save(config.output_path)
            end = timer()
            print "{} took {}s to run".format(data_parser_name, end - start)
        except Exception as e:
            print "{} failed to parse.".format(parser_name)
            traceback.print_exc()


if __name__ == "__main__":
    main()
