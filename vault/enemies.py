from funcionalidades import Enemy, OverTimeEffects 

enemySkills = {"Goblin Gang": lambda self, **kwargs: self.call_reinforcements(kwargs["enemyList"]), 
              "Humiliation": lambda self, **kwargs: self.addStatusEffect(OverTimeEffects(self,2,effects={"dmg_red": (0.02, 1)})),
              "Shroud": lambda self, **kwargs: self.addStatusEffect(OverTimeEffects(self,1,effects={"dmg_red": (1,True),"hp": (20,0)})),     
              "Intangable Attack": lambda self, **kwargs: self.attack(kwargs["main_player"], True),
              "Berserk": lambda self, **kwargs: self.addStatusEffect(OverTimeEffects(self,2,effects={"dmg_red": (0.2, 1), "dmg": (20, 0)})),
              "Taunt": lambda self, **kwargs: (kwargs["main_player"].addStatusEffect(OverTimeEffects(kwargs["main_player"].armor,3,effects={"defense": (-0.4, 1)})), 
                                    kwargs["main_player"].addStatusEffect(OverTimeEffects(kwargs["main_player"].weapon,2,effects={"m_damage": (10, 1), "magic_dmg": (-20, 1)}))),
              "Leech Life": lambda self, **kwargs: (modifyAttrs(self, {"hp": lambda x: x+10}), 
                                        modifyAttrs(kwargs["main_player"], {"hp": lambda x: x-10}))
              }

enemies = [Enemy("Goblin", 100, skills= {"Goblin Gang": enemySkills["Goblin Gang"],"Humiliation": enemySkills["Humiliation"]}),
           Enemy("Wraith", 50, skills={"Shroud": enemySkills["Shroud"], "Intangable Attack": enemySkills["Intangable Attack"]}), 
           Enemy("Orc", 150, skills={"Berserk": enemySkills["Berserk"], "Taunt": enemySkills["Taunt"]}),
           Enemy("Hollow Siren", 125, skills={}),
           Enemy("Guilded Automaton", 200, skills={}),
           Enemy("Fungal Titan", 225, skills={}),
           ]

bosses = [Enemy("High Orc", 300, skills={"Berkerk": enemySkills["Berserk"], "Taunt": enemySkills["Taunt"]}),
          Enemy("Vampire Lord", 250, skills={"Leech Life": enemySkills["Leech Life"], "Shroud": enemySkills["Shroud"]}),
          Enemy("High Oracle of the Abyss, En’Thar", 250, skills={})
          ]