from funcionalidades import Enemy, OverTimeEffects, modifyAttrs

enemySkills = {
    "Regen": lambda self, **kwargs: self.addStatusEffect(OverTimeEffects(self,2,effects={"hp": (self.hp*0.4, 0), "dmg_red": (0.05,1)})),
    "Harden": lambda self, **kwargs: self.addStatusEffect(OverTimeEffects(self,2,effects={"dmg_red": (0.3,1), "dmg": (-5,-1)})),
    "Call Reinforcements": lambda self, **kwargs: self.call_reinforcements(kwargs["enemyList"]),
    "Humiliation": lambda self, **kwargs: self.addStatusEffect(OverTimeEffects(self,2,effects={"dmg_red": (0.02, 1)})),
    "Shroud": lambda self, **kwargs: self.addStatusEffect(OverTimeEffects(self,1,effects={"dmg_red": (1,True),"hp": (20,0)})),     
    "Intangable Attack": lambda self, **kwargs: self.attack(kwargs["main_player"], True),
    "Berserk": lambda self, **kwargs: self.addStatusEffect(OverTimeEffects(self,2,effects={"dmg_red": (0.2, 1), "dmg": (20, 0)})),
    "Taunt": lambda self, **kwargs: (kwargs["main_player"].addStatusEffect(OverTimeEffects(kwargs["main_player"].armor,3,effects={"defense": (-0.4, 1)})), 
                            kwargs["main_player"].addStatusEffect(OverTimeEffects(kwargs["main_player"].weapon,2,effects={"melee_dmg": (10, 1), "magic_dmg": (-20, 1)}))),
    "Sea's Call": lambda self, **kwargs: kwargs["main_player"].addStatusEffect(OverTimeEffects(kwargs["main_player"].weapon,3,effects={"melee_dmg"  if kwargs["main_player"].weapon.melee_dmg > kwargs["main_player"].weapon.magic_dmg else "magic_dmg": 
                                                                                                                                    (-kwargs["main_player"].weapon.melee_dmg*0.25 if kwargs["main_player"].weapon.melee_dmg > kwargs["main_player"].weapon.magic_dmg else -kwargs["main_player"].weapon.magic_dmg*0.25 ,1)})),
    "Overclocked Strike": lambda self, **kwargs: (self.addStatusEffect(OverTimeEffects(self,2,effects={"dmg_red": (-0.05,1)})), 
                                        modifyAttrs(kwargs["main_player"], {"hp": lambda x: x-15})),
    "Toxic Spores": lambda self, **kwargs: kwargs["main_player"].addStatusEffect(OverTimeEffects(kwargs["main_player"],3,effects={"hp": (-5, 2)})),
    "Cinder Swipe": lambda self, **kwargs: kwargs["main_player"].addStatusEffect(OverTimeEffects(kwargs["main_player"],3,effects={"hp": (-5, 2)})),
    "Smoke Screen": lambda self, **kwargs: self.addStatusEffect(OverTimeEffects(self,2,effects={"dmg_red": (0.4, 1)})),
    "Leech Life": lambda self, **kwargs: (modifyAttrs(self, {"hp": lambda x: x+10}), 
                                modifyAttrs(kwargs["main_player"], {"hp": lambda x: x-10})),
    "Reverse Cursed Technique": lambda self, **kwargs: (self.addStatusEffect(OverTimeEffects(kwargs["main_player"],2,effects={"hp": (-kwargs["main_player"].weapon.melee_dmg,0)},),1), 
                                                        self.addStatusEffect(OverTimeEffects(self,2,effects={"hp": (0.4,5)}),1)),
    "Ashen Return": lambda self, **kwargs: self.addStatusEffect(OverTimeEffects(self,2,effects={"hp": (self.base_hp*0.5,3)},treshold=0),1)
}

enemies = [ 
    Enemy("Slime", 50, dmg=10, skills={"Divide": enemySkills["Call Reinforcements"], "Regen": enemySkills["Regen"], "Harden": enemySkills["Harden"]}, tameable=True, reward=10),
    Enemy("Goblin", 100, dmg=15, skills={"Goblin Gang": enemySkills["Call Reinforcements"], "Humiliation": enemySkills["Humiliation"]}, reward=15),
    Enemy("Wraith", 50, dmg=12, skills={"Shroud": enemySkills["Shroud"], "Intangable Attack": enemySkills["Intangable Attack"]}, reward=12),
    Enemy("Orc", 150, dmg=20, skills={"Berserk": enemySkills["Berserk"], "Taunt": enemySkills["Taunt"]}, reward=20),
    Enemy("Hollow Siren", 125, dmg=18, skills={"Sea's Call": enemySkills["Sea's Call"]}, reward=18),
    Enemy("Guilded Automaton", 200, dmg=25, skills={"Overclocked Strike": enemySkills["Overclocked Strike"]}, reward=25),
    Enemy("Fungal Titan", 225, dmg=30, skills={"Toxic Spores": enemySkills["Toxic Spores"]}, reward=28),
    Enemy("Ashling Stalker", 100, dmg=15, skills={"Cinder Swipe": enemySkills["Cinder Swipe"], "Smoke Screen": enemySkills["Smoke Screen"]}, reward=15),
    Enemy("Fire Imp", 80, dmg=12, skills={"Cinder Swipe": enemySkills["Cinder Swipe"], "Berserk": enemySkills["Berserk"]}, reward=14),
    Enemy("Stone Golem", 250, dmg=25, skills={"Harden": enemySkills["Harden"], "Taunt": enemySkills["Taunt"]}, reward=25),
    Enemy("Venom Serpent", 120, dmg=15, skills={"Toxic Spores": enemySkills["Toxic Spores"], "Intangable Attack": enemySkills["Intangable Attack"]}, reward=18),
    Enemy("Spectral Knight", 180, dmg=18, skills={"Shroud": enemySkills["Shroud"], "Overclocked Strike": enemySkills["Overclocked Strike"]}, reward=22),
    Enemy("Thunder Drake", 200, dmg=20, skills={"Sea's Call": enemySkills["Sea's Call"], "Berserk": enemySkills["Berserk"]}, reward=24),
    Enemy("Crystal Spider", 90, dmg=14, skills={"Call Minions": enemySkills["Call Reinforcements"], "Harden": enemySkills["Harden"]}, reward=13),
    Enemy("Ice Wraith", 110, dmg=16, skills={"Shroud": enemySkills["Shroud"], "Intangable Attack": enemySkills["Intangable Attack"]}, reward=16),
    Enemy("Blight Horror", 160, dmg=22, skills={"Toxic Spores": enemySkills["Toxic Spores"], "Berserk": enemySkills["Berserk"],"Call Minions": enemySkills["Call Reinforcements"]}, reward=20),
    Enemy("Lava Golem", 230, dmg=28, skills={"Cinder Swipe": enemySkills["Cinder Swipe"], "Harden": enemySkills["Harden"]}, reward=28),
    Enemy("Storm Elemental", 170, dmg=20, skills={"Sea's Call": enemySkills["Sea's Call"], "Overclocked Strike": enemySkills["Overclocked Strike"]}, reward=22),
    Enemy("Necro Lich", 190, dmg=22, skills={"Shroud": enemySkills["Shroud"], "Reverse Cursed Technique": enemySkills["Reverse Cursed Technique"]}, reward=25),
    Enemy("Forest Treant", 210, dmg=24, skills={"Taunt": enemySkills["Taunt"], "Harden": enemySkills["Harden"]}, reward=26),
]

bosses = [
    Enemy("High Orc", 300, dmg=25, skills={"Berserk": enemySkills["Berserk"], "Taunt": enemySkills["Taunt"]}, reward=90),
    Enemy("Vampire Lord", 250, dmg=22, skills={"Leech Life": enemySkills["Leech Life"], "Shroud": enemySkills["Shroud"]}, reward=140),
    Enemy("High Oracle of the Abyss, En’Thar", 250, dmg=24, skills={"Reverse Cursed Technique": enemySkills["Reverse Cursed Technique"]}, reward=200),
    Enemy("Ancient Fire Dragon", 400, dmg=35, skills={"Cinder Swipe": enemySkills["Cinder Swipe"], "Berserk": enemySkills["Berserk"], "Smoke Screen": enemySkills["Smoke Screen"]}, reward=300),
    Enemy("Void Warden", 350, dmg=30, skills={"Reverse Cursed Technique": enemySkills["Reverse Cursed Technique"], "Shroud": enemySkills["Shroud"], "Intangable Attack": enemySkills["Intangable Attack"]}, reward=280),
    Enemy("Titanic Fungal Behemoth", 450, dmg=40, skills={"Toxic Spores": enemySkills["Toxic Spores"], "Harden": enemySkills["Harden"], "Overclocked Strike": enemySkills["Overclocked Strike"]}, reward=350),
    Enemy("Storm Leviathan", 380, dmg=32, skills={"Sea's Call": enemySkills["Sea's Call"], "Berserk": enemySkills["Berserk"], "Overclocked Strike": enemySkills["Overclocked Strike"]}, reward=320),
    Enemy("Shadow Reaper", 360, dmg=30, skills={"Shroud": enemySkills["Shroud"], "Intangable Attack": enemySkills["Intangable Attack"], "Leech Life": enemySkills["Leech Life"]}, reward=300),
    Enemy("Molten Titan", 420, dmg=38, skills={"Cinder Swipe": enemySkills["Cinder Swipe"], "Smoke Screen": enemySkills["Smoke Screen"], "Berserk": enemySkills["Berserk"]}, reward=340),
    Enemy("Celestial Phoenix", 400, dmg=35, skills={"Cinder Swipe": enemySkills["Cinder Swipe"], "Sea's Call": enemySkills["Sea's Call"], "Reverse Cursed Technique": enemySkills["Reverse Cursed Technique"]}, reward=360),
]