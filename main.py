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
        help='Disables intermediate visualizations'
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
    # Adding in Jayce spell information and stats for both forms
    champions_dict["Jayce (Ranged)"] = copy.deepcopy(champions_dict["Jayce"])
    champions_dict["Jayce (Melee)"] = copy.deepcopy(champions_dict["Jayce"])
    # Jayce ranged variables 
    Jayce_r_adstats = {"name": "ADFromPassive", "value": [0.0,45.0,60.0,500.0,0.0,0.0,0.0]}
    Jayce_r_adper = {"name": "ADPercent", "value": [0.0,1.7,1.75,5.0,0.0,0.0,0.0]}
    Jayce_r_asper = {"name": "ASPercent", "value": [0.0,0.2,0.4,10.0,0.0,0.0,0.0]}
    Jayce_r_dur = {"name": "Duration", "value": [0.0,5.0,5.0,5.0,0.0,0.0,0.0]}
    Jayce_r_vars = [Jayce_r_adper, Jayce_r_asper, Jayce_r_dur, Jayce_r_adstats]
    champions_dict["Jayce (Ranged)"]["ability"]["variables"] = Jayce_r_vars
    champions_dict["Jayce (Ranged)"]["stats"]["range"] += 4.0
    champions_dict["Jayce (Ranged)"]["name"] = "Jayce (Ranged)"
    # Jayce melee variables 
    Jayce_m_adper = {"name": "ADPercent", "value": [0.0,1.6,1.7,10.0,0.0,0.0,0.0]}
    Jayce_m_armshred = {"name": "ArmorReduction", "value": [0.0,0.5,0.5,0.7,0.0,0.0,0.0]}
    Jayce_m_mrshred = {"name": "MRShred", "value": [0.0,0.5,0.5,0.7,0.0,0.0,0.0]}
    Jayce_m_shreddur = {"name": "ShredDuration", "value": [0.0,5.0,5.0,5.0,0.0,0.0,0.0]}
    Jayce_m_shielddur = {"name": "ShieldDuration", "value": [0.0,3.0,3.0,3.0,0.0,0.0,0.0]}
    Jayce_m_shield = {"name": "Shield", "value": [0.0,375.0,550.0,3000.0,0.0,0.0,0.0]}
    Jayce_m_vars = [Jayce_m_adper, Jayce_m_armshred, Jayce_m_mrshred, Jayce_m_shreddur, Jayce_m_shielddur, Jayce_m_shield]
    champions_dict["Jayce (Melee)"]["ability"]["variables"] = Jayce_m_vars
    champions_dict["Jayce (Melee)"]["stats"]["armor"] += 40.0
    champions_dict["Jayce (Melee)"]["stats"]["mr"] += 40.0
    champions_dict["Jayce (Melee)"]["name"] = "Jayce (Melee)"
    # Testing zone
    warwick_HP = champions_dict["Warwick"]["stats"]["hp"]
    print(f"Warwick's base health is {warwick_HP}.")
    syndra_base_3 = target_dummy_DPS(champions_dict, "Syndra", 3)
    print(f"Syndra 3 will take {syndra_base_3} seconds to kill a 1000 HP, 0 resistance dummy.")
    syndra_base_2 = target_dummy_DPS(champions_dict, "Syndra", 2)
    print(f"Syndra 2 will take {syndra_base_2} seconds to kill a 1000 HP, 0 resistance dummy.")
    syndra_base_1 = target_dummy_DPS(champions_dict, "Syndra", 1)
    print(f"Syndra 1 will take {syndra_base_1} seconds to kill a 1000 HP, 0 resistance dummy.")
    items_augments_dict = data["items"]



if __name__ == '__main__':
    main()
