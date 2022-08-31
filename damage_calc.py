from email.mime import base
from enum import auto
import numpy as np

def target_dummy_DPS(c_dict, c_name, c_star, c_vip = 0, d_HP = 1000, d_Armor = 0, d_MR = 0):
    '''
    Calculates the number of seconds needed for a champion with given star count to kill
    a target dummy. The dummy by default has 1000 HP, 0 Armor, and 0 MR. 

    Inputs:
        c_dict: champion dictionary 
        c_name: champion name
        c_star: champion star level (one of {1,2,3})
        c_vip: champion VIP boolean (default 0)
        d_HP: dummy HP (default 1000)
        d_Armor: dummy Armor (default 0)
        d_MR: dummy MR (default 0)
    Output:
        num_seconds: number of seconds needed to kill dummy
    
    '''
    c_stats_dict = c_dict[c_name]["stats"]
    curr_HP = d_HP
    
    
    # Auto attack related portions
    auto_count = 0
    base_dmg = c_stats_dict["damage"]
    crit_adj_dmg = (c_stats_dict["critChance"] * c_stats_dict["critMultiplier"] + 1-c_stats_dict["critChance"]) * base_dmg
    dmg_per_auto = pow(1.8,c_star - 1) * crit_adj_dmg * 100 / (100 + d_Armor)
    
    # Ability/spell related portions 
    spell_count = 0
    curr_Mana = c_stats_dict["initialMana"]
    spell_vars = c_dict[c_name]["ability"]["variables"]
    spell_dmg = 0
    spell_dur = 0
    as_modifier = 1
    # ad_mult also serves as an indicator on if a spell is magic or physical damage
    ad_mult = 0 
    num_proj = 0
    for var in spell_vars:
        # Variety of damage names in the scraped file, so I'll compile outliers and the champions
        # MagicDamage - Miss Fortune, Illaoi, Sejuani
        # BonusDamage - Jihn (?), Ezreal, Vex, Quinn, Brand   
        if var["name"] in ["Damage", "MagicDamage"]:
            spell_dmg = var["value"][c_star]
        # Duration counters for certain spells
        # BellyDuration - Tahm Kench
        # Duration - Malzahar, Renata Glasc
        # BleedDuration - Talon
        if var["name"] in ["BellyDuration", "Duration", "BleedDuration"]:
            if c_name in ["Tahm Kench", "Malzahar", "Renata Glasc", "Talon"]:
                spell_dur = var["value"][c_star]
        # Attack speed steroids
        # ASBoost - Ezreal
        # BonusAttackSpeed - Sivir
        # ASPercent - Jarvan IV, Jayce (Ranged) (added)
        # BonusAS - Ekko 
        if var["name"] in ["ASBoost", "BonusAttackSpeed","ASPercent", "BonusAS"]:
            as_modifier += var["value"][c_star]
        # Attack Damage spells
        # ADPercent - Ashe, GP, Gnar, Kha'zix, Rek'sai
        # PercentADDamage - Irelia
        # SpinDamage - Tryndamere
        # PercentAD - Ezreal, Senna, Zeri, Mechanical Bear
        # PercentAttackDamage - Jhin, Twitch
        # PercentDamage - Sivir
        if var["name"] in ["ADPercent","PercentADDamage","SpinDamage","PercentAD","PercentAttackDamage","PercentDamage"]:
            ad_mult = var["value"][c_star]
        # Multiple missile spells
        # NumMissiles - Kai'sa
        # NumShots - Lucian
        if var["name"] in ["NumMissiles", "NumShots"]:
            num_proj = var["value"][c_star]
    while (curr_HP > 0):
        curr_HP -= dmg_per_auto
        curr_Mana += 10
        auto_count += 1
        if curr_Mana >= c_stats_dict["mana"]:
            spell_count += 1
            curr_HP -= spell_dmg
            curr_Mana = 0
    return auto_count / c_stats_dict["attackSpeed"]