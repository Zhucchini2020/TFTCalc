from PIL import Image, ImageDraw
import csv
import pandas as pd
import numpy as np

# Note: the following code is for possible function checkers
# invert_op = getattr(self, "invert_op", None)
#   if callable(invert_op):
#       someList.append(self)

# standardized list of methods for all champion classes
# get_spell_shield
# get_spell_heal
# get_spell_cc_dur
# get_spell_mr_cut
# get_spell_armor_cut
# get_spell_num_targets
# get_spell_ad_percent
# get_spell_as_boost
# get_spell_dmg_amp
# get_spell_area
# get_dmg_reduc
# get_dmg_reduc_dur
# get_ss_ad
# get_ss_arm
# get_ss_


class Champion:
    
    def __init__(self, dictEntry):
        self.cost = dictEntry["cost"]
        self.name = dictEntry["name"]
        stats = dictEntry["stats"]
        self.armor = stats["armor"]
        self.mr = stats["magicResist"]
        self.range = stats["range"]
        self.critChance = stats["critChance"]
        self.critMult = stats["critMultiplier"]
        self.ad = stats["damage"]
        self.hp = stats["hp"]
        self.initMana = stats["initialMana"]
        self.mana = stats["mana"]
        self.atkspd = stats["attackSpeed"]
        ability = dictEntry["ability"]
        self.abName = ability["name"]
        self.abDesc = ability["desc"]
        self.abVars = {}
        for variable in ability["variables"]:
            vals = variable["value"]
            if vals != None:
                self.abVars[variable["name"]] = [vals[1],vals[2],vals[3]]
        self.traits = dictEntry["traits"]

    def get_hp(self, starLevel):
        return self.hp * (1.8 ** (starLevel - 1))
    
    def get_ad_hp(self, starLevel):
        return self.get_hp(starLevel) * (100 + self.armor) / 100 
    
    def get_ap_hp(self, starLevel):
        return self.get_hp(starLevel) * (100 + self.mr) / 100 

    def get_avg_ad(self, starLevel):
        return self.ad * pow(1.5, starLevel - 1) * (1-self.critChance + self.critChance * self.critMult)

    def get_auto_dps(self, starLevel):
        return self.atkspd * self.get_avg_ad(starLevel)
    
    def get_first_cast_time(self):
        return -(self.mana - self.initMana) // (10*self.atkspd)

    def get_full_cast_time(self):
        return -self.mana // (10*self.atkspd)

    def get_spell_damage(self, starLevel):
        return 0 * pow(1.5, starLevel-1)
    
    def get_early_spell_dps(self, starLevel):
        return self.get_spell_damage(starLevel) / self.get_first_cast_time()
    
    def get_full_spell_dps(self, starLevel):
        return self.get_spell_damage(starLevel) / self.get_full_cast_time()

def simplifyChampDict(champsDict):
    simpleChampsDict = {}
    for champ in champsDict:
        simpleChampsDict[champ] = Champion(champsDict[champ])
    return simpleChampsDict

def generateExcelCards(simpChampDict):
    writer = pd.ExcelWriter('tftAbilityCards.xlsx',engine='xlsxwriter')   
    workbook=writer.book
    for cost in [1,2,3,4,5]:
        # Excel worksheet blurb
        sheetName = str(cost) + "-cost information"
        worksheet=workbook.add_worksheet(sheetName)
        writer.sheets[sheetName] = worksheet
        # Actually setting up the rankings / list
        champAbilityList = []
        for champ in simpChampDict:
            champion = simpChampDict[champ]
            if champion.cost == cost:
                abilityString = ""
                for abilityVar in champion.abVars:
                    values = champion.abVars[abilityVar]
                    abilityString += f"{abilityVar}: {str(values[0])}, {str(values[1])}, {str(values[2])}; "
                champAbilityList.append([champ, champion.abDesc, abilityString])
        numChamps = len(champAbilityList)
        # Setting up the individual rankings for each type of HP
        sorted_hp = np.zeros((numChamps, 3), dtype = object)
        for i in range(numChamps):
            champAbEntry = champAbilityList[i]
            sorted_hp[i] = np.array(champAbEntry, dtype = object)
        champ_df = pd.DataFrame(sorted_hp, columns = ['Champion', 'Ability Description', 'Ability Variables'])
        champ_df.to_excel(writer,sheet_name=sheetName,startrow=0 , startcol=0)
    writer.save()

def generateTraitCards(traitList):
    writer = pd.ExcelWriter('tftTraitCards.xlsx',engine='xlsxwriter')   
    workbook=writer.book
    # Excel worksheet blurb
    sheetName = "trait variables"
    worksheet=workbook.add_worksheet(sheetName)
    writer.sheets[sheetName] = worksheet
    # Actually setting up the rankings / list
    traitCardList = []
    for trait_d in traitList:
        name = trait_d["name"]
        desc = trait_d["desc"]
        minUnitString = "minUnits: "
        temp_variable_dict = {}
        for thresh_d in trait_d["effects"]:
            minUnitString += str(thresh_d["minUnits"])+", "
            var_d = thresh_d["variables"]
            for var_key in var_d:
                if var_key not in temp_variable_dict:
                    temp_variable_dict[var_key] = []
                temp_variable_dict[var_key].append(var_d[var_key])
        minUnitString = minUnitString[:-2]
        varString = ""
        for var in temp_variable_dict:
            varList = temp_variable_dict[var]
            varString += f"{var}: "
            for value in varList:
                varString += f"{str(value)}, "    
            varString = varString[:-2] + ";"
        traitCardList.append([name, desc, minUnitString, varString])
    numChamps = len(traitCardList)
    # Setting up the individual rankings for each type of HP
    sorted_hp = np.zeros((numChamps, 4), dtype = object)
    for i in range(numChamps):
        champAbEntry = traitCardList[i]
        sorted_hp[i] = np.array(champAbEntry, dtype = object)
    champ_df = pd.DataFrame(sorted_hp, columns = ['Trait', 'Description', 'MinUnits','Variables'])
    champ_df.to_excel(writer,sheet_name=sheetName,startrow=0 , startcol=0)      
    writer.save()

def generateItemCards(itemList):
    writer = pd.ExcelWriter('tftItemCards.xlsx',engine='xlsxwriter')   
    workbook=writer.book
    # Excel worksheet blurb
    sheetName = "item variables"
    worksheet=workbook.add_worksheet(sheetName)
    writer.sheets[sheetName] = worksheet
    # Actually setting up the rankings / list
    itemCardList = []
    for item_d in itemList:
        name = item_d["name"]
        desc = item_d["desc"]
        temp_variable_dict = {}
        varString = ""
        for var in item_d["effects"]:
            varString += f"{var}: " + str(item_d["effects"][var]) + "; "
        varString = varString[:-2]
        itemCardList.append([name, desc, varString])
    numChamps = len(itemCardList)
    # Setting up the individual rankings for each type of HP
    sorted_hp = np.zeros((numChamps, 3), dtype = object)
    for i in range(numChamps):
        champAbEntry = itemCardList[i]
        sorted_hp[i] = np.array(champAbEntry, dtype = object)
    champ_df = pd.DataFrame(sorted_hp, columns = ['Item', 'Description', 'Variables'])
    champ_df.to_excel(writer,sheet_name=sheetName,startrow=0 , startcol=0)      
    writer.save()