from funcionalidades import Enemy, OverTimeEffects, modifyAttrs

enemySkills = {"Goblin Gang": lambda self, **kwargs: self.call_reinforcements(kwargs["enemyList"]), 
            "Humiliation": lambda self, **kwargs: self.addStatusEffect(OverTimeEffects(self,2,effects={"dmg_red": (0.02, 1)})),
            "Shroud": lambda self, **kwargs: self.addStatusEffect(OverTimeEffects(self,1,effects={"dmg_red": (1,True),"hp": (20,0)})),     
            "Intangable Attack": lambda self, **kwargs: self.attack(kwargs["main_player"], True),
            "Berserk": lambda self, **kwargs: self.addStatusEffect(OverTimeEffects(self,2,effects={"dmg_red": (0.2, 1), "dmg": (20, 0)})),
            "Taunt": lambda self, **kwargs: (kwargs["main_player"].addStatusEffect(OverTimeEffects(kwargs["main_player"].armor,3,effects={"defense": (-0.4, 1)})), 
                                    kwargs["main_player"].addStatusEffect(OverTimeEffects(kwargs["main_player"].weapon,2,effects={"m_damage": (10, 1), "magic_dmg": (-20, 1)}))),
            "Leech Life": lambda self, **kwargs: (modifyAttrs(self, {"hp": lambda x: x+10}), 
                                        modifyAttrs(kwargs["main_player"], {"hp": lambda x: x-10})),
            "Sea's Call": lambda self, **kwargs: kwargs["main_player"].addStatusEffect(OverTimeEffects(kwargs["main_player"],3,effects={"m_damage"  if kwargs["main_player"].weapon.m_damage > kwargs["main_player"].weapon.magic_dmg else "magic_dmg": (200,1)})),
            "Overclocked Strike": lambda self, **kwargs: (modifyAttrs(OverTimeEffects(self,2,effects={"dmg_red": (-0.4,1)})), 
                                                modifyAttrs(kwargs["main_player"], {"hp": lambda x: x-10})),
            "Toxic Spores": lambda self, **kwargs: kwargs["main_player"].addStatusEffect(OverTimeEffects(kwargs["main_player"],3,effects={"hp": (-5, 2)})),
            "Cinder Swipe": lambda self, **kwargs: kwargs["main_player"].addStatusEffect(OverTimeEffects(kwargs["main_player"],3,effects={"hp": (-5, 2)})),
            "Smoke Screen": lambda self, **kwargs: self.addStatusEffect(OverTimeEffects(self,2,effects={"dmg_red": (0.4, 1)})),
            "Reverse Cursed Technique": lambda self, **kwargs: (self.addStatusEffect(OverTimeEffects(kwargs["main_player"],2,effects={"hp": (-kwargs["main_player"].weapon.m_damage,0)},),1), 
                                                            self.addStatusEffect(OverTimeEffects(self,2,effects={"hp": (0.4,5)}),1))
            }

enemies = [Enemy("Goblin", 100, skills= {"Goblin Gang": enemySkills["Goblin Gang"],"Humiliation": enemySkills["Humiliation"]}),
           Enemy("Wraith", 50, skills={"Shroud": enemySkills["Shroud"], "Intangable Attack": enemySkills["Intangable Attack"]}), 
           Enemy("Orc", 150, skills={"Berserk": enemySkills["Berserk"], "Taunt": enemySkills["Taunt"]}),
           Enemy("Hollow Siren", 125, skills={"Sea's Call": enemySkills["Sea's Call"]}),
           Enemy("Guilded Automaton", 200, skills={"Overclocked Strike": enemySkills["Overclocked Strike"]}),
           Enemy("Fungal Titan", 225, skills={"Toxic Spores": enemySkills["Toxic Spores"]}),
           Enemy("Ashling Stalker",100,skills={"Cinder Swipe": enemySkills["Cinder Swipe"], "Smoke Screen": enemySkills["Smoke Screen"]})
           ]

bosses = [Enemy("High Orc", 300, skills={"Berkerk": enemySkills["Berserk"], "Taunt": enemySkills["Taunt"]}, reward= 90),
          Enemy("Vampire Lord", 250, skills={"Leech Life": enemySkills["Leech Life"], "Shroud": enemySkills["Shroud"]}, reward=140),
          Enemy("High Oracle of the Abyss, En’Thar", 250, skills={"Reversed Cursed Technique": enemySkills["Reverse Cursed Technique"]},reward=200)
          ]