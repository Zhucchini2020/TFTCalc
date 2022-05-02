from email.mime import base
from more_itertools import first
import numpy as np

# Plan to split the damage formula into multiple parts:
# 1. stat scraping
# 2. auto attack portions
# 3. Spell portions
# 

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
    champion_stats_dict = var_calculator(c_dict, c_name, c_star)
    return flat_dmg(champion_stats_dict, d_HP, d_Armor, d_MR)

def var_calculator(c_dict, c_name, c_star):
    '''
    Scrapes the champions dictionary to find the needed damage variables to calculate damage for each champion

    Inputs:
        c_dict: champion dictionary 
        c_name: champion name
        c_star: champion star level (one of {1,2,3})
        
    Output:
        num_seconds: number of seconds needed to kill dummy
    
    '''
    if c_star not in [1,2,3]:
        raise ValueError("champion star-level must be either 1, 2, or 3")
    c_stats_dict = c_dict[c_name]["stats"]
    # Ability/spell related portions 
    init_Mana = c_stats_dict["initialMana"]
    tot_Mana = c_stats_dict["mana"]
    ad = pow(1.8,c_star - 1) * c_stats_dict["damage"]
    attack_spd = c_stats_dict["attackSpeed"]
    spell_vars = c_dict[c_name]["ability"]["variables"]
    critChance = c_stats_dict["critChance"]
    critMultiplier = c_stats_dict["critMultiplier"]
    spell_dmg = None
    spell_dur = None
    as_modifier = None
    num_projs = None
    ad_percent = None
    armor_shred, mr_shred = None, None
    shred_dur = None
    passive_ad = None
    warwick_aa_percent = None
    draven_pen = None
    gnar_hp = None
    jinx_rocket_dmg = None
    jinx_burn_per = None

    for var in spell_vars:
        var_name = var["name"]
        # Variety of damage names in the scraped file, so I'll compile outliers and the champions
        # MagicDamage - Miss Fortune, Illaoi, Sejuani
        # BonusDamage - Jihn (?), Ezreal, Vex, Quinn, Brand   
        if var_name in ["Damage", "MagicDamage"]:
            spell_dmg = var["value"][c_star]
        # Attack Damage Percent Champs
        # ADPercent - Ashe, Gangplank, Gnar, Kha'zix, Rek'sai, Jayce (both)
        # PercentADDamage - Irelia
        # SpinDamage - Tryndamere
        # PercentAD - Zeri, Mechanical Bear, Senna
        # PercentAttackDamage - Twitch, Jhin
        # ADMult - Draven
        elif var_name in ["ADPercent", "PercentADDamage","SpinDamage","PercentAD","PercentAttackDamage","ADMult"]:
            ad_percent = var["value"][c_star]
        # Attack speed steroids
        # ASBoost - Ezreal
        # BonusAttackSpeed - Sivir
        # ASPercent - Jarvan IV, Jayce (Ranged) (added)
        # BonusAS - Ekko 
        # ASBonus - Seraphine
        elif var_name in ["ASBoost", "BonusAttackSpeed","ASPercent", "BonusAS", "ASBonus"]:
                as_modifier = var["value"][c_star]
        # Duration counters for certain spells
        # BellyDuration - Tahm Kench
        # Duration - Malzahar, Renata Glasc
        # BleedDuration - Talon
        elif var_name in ["BellyDuration", "Duration", "BleedDuration"]:
            if c_name in ["Tahm Kench", "Malzahar", "Renata Glasc", "Talon"]:
                spell_dur = var["value"][c_star]
                if c_name == "Malzahar":
                    shred_dur = var["value"][c_star]
        # Projectiles counter
        # NumMissiles - Kai'sa
        # NumShots - Lucian
        elif var_name in ["NumMissiles", "NumShots"]:
            num_projs = var["value"][c_star]
        
        # Armor Damage Percent Champs
        # PercentArmorDamage - Literally just Poppy 
        elif var_name == "PercentArmorDamage":
            spell_dmg = var["value"][c_star] * c_stats_dict["armor"]
        # Armor Shred Champs
        # ArmorReduction - Viktor, Jayce (Melee)
        elif var_name == "ArmorReduction":
            armor_shred = var["value"][c_star]
        # MR Shred Champs
        # MRShred - Malzahar, Jayce (Melee)
        elif var_name == "MRShred":
            mr_shred = var["value"][c_star]
        # For resistance shredding champions
        # ShredDuration - Viktor, Jayce (Melee)
        elif var_name == "ShredDuration":
            shred_dur = var["value"][c_star]
        # Passive Stats
        # ADFromPassive - Jhin
        elif var_name == "ADFromPassive":
            passive_ad = var["value"][c_star]
        # Warwick passive
        # PercentHealth - Warwick
        elif var_name == "PercentHealth":
            warwick_aa_percent = var["value"][c_star]
        # Draven passive
        # PassiveArmorPenPercent - Draven
        elif var_name == "PassiveArmorPenPercent":
            draven_pen = var["value"][c_star]
        # Gnar transformation
        # TransformHealth - Gnar
        elif var_name == "TransformHealth":
            gnar_hp = var["value"][c_star]
        # Jinx post-ultimate damage
        # RocketLauncherPercentAD - Jinx
        elif var_name == "RocketLauncherPercentAD":
            jinx_rocket_dmg = var["value"][c_star]
        # Jinx burn damage
        # PercentBurn - Jinx
        elif var_name == "PercentBurn":
            jinx_burn_per = var["value"][c_star]

    dmg_var_dict = {"ad": ad, "as": attack_spd, "critChance": critChance, "critMultiplier": critMultiplier, 
        "initMana": init_Mana, "totMana": tot_Mana, "spell_dmg": spell_dmg, "spell_dur": spell_dur,
    "as_modifier": as_modifier, "num_projs": num_projs, "ad_percent": ad_percent, "armor_shred": armor_shred,
    "mr_shred": mr_shred, "shred_dur": shred_dur, "passive_ad": passive_ad, "ww_aa_per": warwick_aa_percent, 
    "draven_pen": draven_pen, "transform_health": gnar_hp, "jinx_dmg": jinx_rocket_dmg, "jinx_burn": jinx_burn_per 
    }
    return dmg_var_dict

def avg_aa_dmg(baseDamage, critChance, critMult):
    return baseDamage * (1-critChance) + baseDamage*critMult*critChance

def resist_adjust(damage, resistance):
    return 100*damage / (100+resistance)

def ceilDiv(x, y):
    return -1 * (-x // y)

def pacifist_dmg(dmg_var_dict, d_HP, d_Armor, d_MR):
    '''
    Calculates time taken for champions without spell damage
    Champs: Leona, Lulu
    Inputs:
        dmg_var_dict: dictionary of damage variables
        d_HP: dummy HP
        d_Armor: dummy Armor
        d_MR: dummy MR
    Output:
        num_seconds: number of seconds needed to kill dummy
    '''
    auto_dmg = avg_aa_dmg(dmg_var_dict["ad"], dmg_var_dict["critChance"], dmg_var_dict["critMultiplier"])
    auto_true = resist_adjust(auto_dmg, d_Armor)
    num_seconds = ceilDiv(d_HP, auto_true) / dmg_var_dict["as"]
    return num_seconds

def flat_dmg(dmg_var_dict, d_HP, d_Armor, d_MR):
    '''
    Calculates time taken for champions with only flat spell damage
    Champs: Alistar, Ashe, Blitzcrank, Braum, Caitlyn, Camille, Chogath, Corki, Darius, Gangplank,
    Illaoi, Irelia, Kassadin, Kha'zix, Miss Fortune, Nocturne, Orianna, Quinn, Rek'Sai, Sejuani, Senna, 
    Singed, Swain, Syndra, Twitch, Vex, Zac, Ziggs, Zyra 
    Inputs:
        dmg_var_dict: dictionary of damage variables
        d_HP: dummy HP
        d_Armor: dummy Armor
        d_MR: dummy MR
    Output:
        num_seconds: number of seconds needed to kill dummy
    '''
    auto_dmg = avg_aa_dmg(dmg_var_dict["ad"], dmg_var_dict["critChance"], dmg_var_dict["critMultiplier"])
    auto_true = resist_adjust(auto_dmg, d_Armor)
    spell_dmg = dmg_var_dict["spell_dmg"]
    spell_true = 0
    if dmg_var_dict["ad_percent"] == None:
        spell_true = resist_adjust(spell_dmg, d_MR)
    else:
        spell_true = resist_adjust(spell_dmg, d_Armor)
    curr_mana = dmg_var_dict["initMana"]
    tot_mana = dmg_var_dict["totMana"]
    first_rotation_dmg = auto_true * (tot_mana-curr_mana) / 10.0 + spell_true
    first_rotation_time = ceilDiv(tot_mana-curr_mana,10.0) / dmg_var_dict["as"]
    if first_rotation_dmg >= d_HP:
        if d_HP <= auto_true * ceilDiv(tot_mana-curr_mana,10.0):
            num_seconds = ceilDiv(d_HP, auto_true) / dmg_var_dict["as"]
            return num_seconds
        else:
            num_seconds = first_rotation_time
            return num_seconds
    full_rotation_dmg = auto_true * tot_mana-curr_mana / 10.0 + spell_true
    full_rotation_time = tot_mana / 10.0 / dmg_var_dict["as"]
    num_full_rotations = (d_HP - first_rotation_dmg) // full_rotation_dmg 
    final_rotation_HP = d_HP-first_rotation_dmg-full_rotation_time*num_full_rotations
    if final_rotation_HP <= auto_true * ceilDiv(tot_mana,10.0):
        num_seconds = first_rotation_time+full_rotation_time*num_full_rotations+ceilDiv(final_rotation_HP, auto_true) / dmg_var_dict["as"]
        return num_seconds
    elif final_rotation_HP <= 0:
        num_seconds = first_rotation_time+full_rotation_time*num_full_rotations
        return num_seconds
    else:
        num_seconds = first_rotation_time+full_rotation_time*(num_full_rotations+1)
        return num_seconds

def time_dmg(dmg_var_dict, d_HP, d_Armor, d_MR):
    '''
    Calculates time taken for champions with DoT damage
    Champs: Malzahar, Renata Glasc, Talon
    Inputs:
        dmg_var_dict: dictionary of damage variables
        d_HP: dummy HP
        d_Armor: dummy Armor
        d_MR: dummy MR
    Output:
        num_seconds: number of seconds needed to kill dummy
    '''
    auto_dmg = avg_aa_dmg(dmg_var_dict["ad"], dmg_var_dict["critChance"], dmg_var_dict["critMultiplier"])
    auto_true = resist_adjust(auto_dmg, d_Armor)
    spell_dmg = dmg_var_dict["spell_dmg"]
    spell_dur = dmg_var_dict["spell_dur"]
    spell_true = 0
    if dmg_var_dict["ad_percent"] == None:
        spell_true = resist_adjust(spell_dmg, d_MR)
    else:
        spell_true = resist_adjust(spell_dmg, d_Armor)
    curr_mana = dmg_var_dict["initMana"]
    tot_mana = dmg_var_dict["totMana"]
    first_rotation_dmg = auto_true * (tot_mana-curr_mana) / 10.0 + spell_true
    first_rotation_time = ceilDiv(tot_mana-curr_mana,10.0) / dmg_var_dict["as"]
    if first_rotation_dmg >= d_HP:
        if d_HP <= auto_true * ceilDiv(tot_mana-curr_mana,10.0):
            num_seconds = ceilDiv(d_HP, auto_true) / dmg_var_dict["as"]
            return num_seconds
        else:
            num_seconds = first_rotation_time
            return num_seconds
    full_rotation_dmg = auto_true * tot_mana-curr_mana / 10.0 + spell_true
    full_rotation_time = tot_mana / 10.0 / dmg_var_dict["as"]
    num_full_rotations = (d_HP - first_rotation_dmg) // full_rotation_dmg 
    final_rotation_HP = d_HP-first_rotation_dmg-full_rotation_time*num_full_rotations
    if final_rotation_HP <= auto_true * ceilDiv(tot_mana,10.0):
        num_seconds = first_rotation_time+full_rotation_time*num_full_rotations+ceilDiv(final_rotation_HP, auto_true) / dmg_var_dict["as"]
        return num_seconds
    elif final_rotation_HP <= 0:
        num_seconds = first_rotation_time+full_rotation_time*num_full_rotations
        return num_seconds
    else:
        num_seconds = first_rotation_time+full_rotation_time*(num_full_rotations+1)
        return num_seconds        