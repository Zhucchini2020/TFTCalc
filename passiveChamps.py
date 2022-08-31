from cardGenerator import Champion

class passiveChampion(Champion):
    def get_10s_dmg(self, starLevel):
        return 10 // (1/self.atkspd) * self.get_avg_ad(starLevel)
    def get_15s_dmg(self, starLevel):
        return 15 // (1/self.atkspd) * self.get_avg_ad(starLevel)
    def get_20s_dmg(self, starLevel):
        return 20 // (1/self.atkspd) * self.get_avg_ad(starLevel)

class bard(passiveChampion):
    def get_spell_cc_dur(self, starLevel):
        return self.abVars["StasisDuration"][starLevel-1]
    def get_spell_dmg_amp(self, starLevel):
        return self.abVars["DamageAmpRatio"][starLevel-1]
    def get_spell_area(self):
        return 19

class braum(passiveChampion):
    def get_dmg_reduc(self, starLevel):
        return self.abVars["ShieldDR"][starLevel-1]
    def get_dmg_reduc_dur(self, starLevel):
        return self.abVars["ShieldDuration"][starLevel-1]

class leona(passiveChampion):
    def get_flat_dmg_reduc(self, starLevel):
        return self.abVars["FlatDamageReduction"][starLevel-1]
    def get_flat_dmg_reduc_dur(self, starLevel):
        return self.abVars["Duration"][starLevel-1]

class lulu(passiveChampion):
    def get_num_targets(self, starLevel):
        return self.abVars["NumTargets"][starLevel-1]
    def get_atk_spd_buff(self, starLevel):
        return self.abVars["AttackSpeedPercent"][starLevel-1]
    def get_atk_spd_buff_dur(self, starLevel):
        return self.abVars["AllyBuffDuration"][starLevel-1]
    def get_poly_dur(self, starLevel):
        return self.abVars["PolymorphDuration"][starLevel-1]
    def get_poly_dmg_buff(self, starLevel):
        return self.abVars["DamageAmp"][starLevel-1]

class skarner(passiveChampion):
    def get_shield(self, starLevel):
        return self.abVars["ShieldAmount"][starLevel-1]
    def get_spell_dur(self, starLevel):
        return self.abVars["Duration"][starLevel-1]
    def get_atk_spd_buff(self, starLevel):
        return self.abVars["AttackSpeed"][starLevel-1]
