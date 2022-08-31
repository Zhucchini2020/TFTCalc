import argparse
import os
import numpy as np
import json
import requests
import copy
from damage_calc import target_dummy_DPS
import shutil
import cardGenerator
import champRanker

def parse_args():
    """ Perform command-line argument parsing. """

    parser = argparse.ArgumentParser(
        description="TFT Calculations!")
    parser.add_argument(
        '--damage_calc',
        action='store_true',
        help='TBI'
    )
    parser.add_argument(
        '--reimport_files',
        action='store_true',
        help='Indicates whether information files are scraped'
    )
    parser.add_argument(
        '--reimport_pbe',
        action='store_true',
        help='Indicates whether pbe files are scraped'
    )
    parser.add_argument(
        '--use_pbe',
        action='store_true',
        help='Indicates whether to use pbe or main files for analysis'
    )
    parser.add_argument(
        '--reimport_splash',
        action='store_true',
        help='Indicates whether champion splash files are scraped'
    )
    parser.add_argument(
        '--hpRanking',
        action='store_true',
        help='Indicates whether to write hp rankings to a file'
    )
    parser.add_argument(
        '--genCards',
        action='store_true',
        help='Indicates whether to write cards into a file'
    )
    parser.add_argument(
        '--genTraits',
        action='store_true',
        help='Indicates whether to write trait cards into a file'
    )
    parser.add_argument(
        '--genItems',
        action='store_true',
        help='Indicates whether to write item cards into a file'
    )

    return parser.parse_args()



def main():
    args = parse_args()
    img_path = "c:/Users/chief/OneDrive/Documents/CS/pics"
    if args.reimport_files:
        url = 'https://raw.communitydragon.org/latest/cdragon/tft/en_us.json'
        r = requests.get(url, allow_redirects=True)
        open('current_TFT.json','wb').write(r.content)
        print("Re-imported files!")
    if args.reimport_pbe:
        url = 'https://raw.communitydragon.org/pbe/cdragon/tft/en_us.json'
        r = requests.get(url, allow_redirects=True)
        open('current_TFT_PBE.json','wb').write(r.content)
        print("Re-imported PBE files!")
    info_file = open('current_TFT.json')
    if args.use_pbe:
        info_file = open('current_TFT_PBE.json')
    data = json.load(info_file)
    raw_champions_dict = data["setData"][6]["champions"]
    champions_dict = {}
    for champion in raw_champions_dict:
        name = champion["name"].lower()
        champions_dict[name] = champion
        # Solely to import splashes
        if args.reimport_splash:
            url = 'https://raw.communitydragon.org/latest/game/assets/ux/tft/championsplashes/tft7_'+name+'_mobile.tft_set7.png'
            response = requests.get(url, stream=True)
            with open(name+'.png', 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
        # Remove non-champions from dictionary
    simpleChampDict = cardGenerator.simplifyChampDict(champions_dict)
    if args.hpRanking:
        champRanker.createHPRanking(simpleChampDict)
    if args.genCards:
        cardGenerator.generateExcelCards(simpleChampDict)
    traits_list = data["setData"][2]["traits"]
    if args.genTraits:
        cardGenerator.generateTraitCards(traits_list)
    itemsList = data["items"]
    if args.genItems:
        cardGenerator.generateItemCards(itemsList)
    print("complete")



if __name__ == '__main__':
    main()
