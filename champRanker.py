import pandas as pd
import numpy as np

class champInst:
    def __init__(self, champion, starLevel, items):
        self.champ = champion
        self.starLevel = starLevel
        self.items = items
    
    def get_hp(self):
        return self.champ.get_hp(self.starLevel)

    def get_ad_hp(self):
        return self.champ.get_ad_hp(self.starLevel)

    def get_ap_hp(self):
        return self.champ.get_ap_hp(self.starLevel)
    
    def get_avg_ad(self):
        return self.champ.get_avg_ad(self.starLevel)

def createHPRanking(simpChampDict):
    writer = pd.ExcelWriter('tftHpRankings.xlsx',engine='xlsxwriter')   
    workbook=writer.book
    for cost in [1,2,3,4,5]:
        # Excel worksheet blurb
        sheetName = str(cost) + "-cost HP Rankings"
        worksheet=workbook.add_worksheet(sheetName)
        writer.sheets[sheetName] = worksheet
        # Actually setting up the rankings / list
        champHpList = []
        for champ in simpChampDict:
            champion = simpChampDict[champ]
            if simpChampDict[champ].cost == cost:
                champHpList.append([champ, champion.get_hp(1), champion.get_ad_hp(1), champion.get_ap_hp(1)])
        numChamps = len(champHpList)
        # Setting up the individual rankings for each type of HP
        sorted_hp = np.zeros((numChamps, 4), dtype=object)
        sorted_ad_hp = np.zeros((numChamps, 4), dtype=object)
        sorted_ap_hp = np.zeros((numChamps, 4), dtype=object)
        for i in range(numChamps):
            champHpEntry = champHpList[i]
            name = champHpEntry[0]
            hp = champHpEntry[1]
            ad_hp = champHpEntry[2]
            ap_hp = champHpEntry[3]
            sorted_hp[i] = np.array([name, hp, hp*1.8, hp*(1.8**2)], dtype=object)
            sorted_ad_hp[i] = np.array([name, ad_hp, ad_hp*1.8, ad_hp*(1.8**2)], dtype=object)
            sorted_ap_hp[i] = np.array([name, ap_hp, ap_hp*1.8, ap_hp*(1.8**2)], dtype=object)
        sorted_hp = sorted_hp[sorted_hp[:, 1].argsort()[::-1]]
        sorted_ad_hp = sorted_ad_hp[sorted_ad_hp[:, 1].argsort()[::-1]]
        sorted_ap_hp = sorted_ap_hp[sorted_ap_hp[:, 1].argsort()[::-1]]
        sorted_hp_df = pd.DataFrame(sorted_hp, columns = ['Champion', 'HP (*)', 'HP (**)', 'HP (***)'])
        sorted_ad_hp_df = pd.DataFrame(sorted_ad_hp, columns = ['Champion', 'AD HP (*)', 'AD HP (**)', 'AD HP (***)'])
        sorted_ap_hp_df = pd.DataFrame(sorted_ap_hp, columns = ['Champion', 'AP HP (*)', 'AP HP (**)', 'AP HP (***)'])
        sorted_hp_df.to_excel(writer,sheet_name=sheetName,startrow=0 , startcol=0)
        sorted_ad_hp_df.to_excel(writer,sheet_name=sheetName,startrow=0 , startcol=6)
        sorted_ap_hp_df.to_excel(writer,sheet_name=sheetName,startrow=0 , startcol=12)
    writer.save()






    

