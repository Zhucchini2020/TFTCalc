import argparse
import os
import numpy as np
import json
import requests
import copy
from damage_calc import target_dummy_DPS


def parse_args():
    """ Perform command-line argument parsing. """

    parser = argparse.ArgumentParser(
        description="TFT Calculations!")
    parser.add_argument(
        '--damage_calc',
        action='store_true',
        help='Use for damage calculations (unimplemented)'
    )
    parser.add_argument(
        '--reimport_files',
        action='store_true',
        help='Indicates whether information files are scraped'
    )

    return parser.parse_args()



def main():
    args = parse_args()
    if args.reimport_files:
        url = 'https://raw.communitydragon.org/latest/cdragon/tft/en_us.json'
        r = requests.get(url, allow_redirects=True)
        open('current_TFT.json','wb').write(r.content)
        print("Re-imported files!")
    info_file = open('current_TFT.json')
    data = json.load(info_file)
    raw_champions_dict = data["setData"][3]["champions"]
    champions_dict = {}
    for champion in raw_champions_dict:
        champions_dict[champion["name"]] = champion
    
    print("Complete")


if __name__ == '__main__':
    main()
