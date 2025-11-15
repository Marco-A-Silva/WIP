from funcionalidades import Item, OverTimeEffects, modifyAttrs
import random

shopItems = [[Item("Health Vial",lambda self: modifyAttrs(self.owner, {"hp": lambda x: x+10}),2),15],
              [Item("Aether Essence", lambda self: modifyAttrs(self.owner, {"mp": lambda x: x+10}),2),15],
              [Item("Invigorating Tonic", lambda self: self.owner.addStatusEffect(OverTimeEffects(self.owner,2,effects={"hp": (0.2, 1)})), 2), 30],
              [Item("Ether Draught", lambda self: (modifyAttrs(self.owner, {"mp": lambda x: x+self.owner.mp}),
                                                 self.owner.addStatusEffect(OverTimeEffects(self.owner.weapon,2,effects={"magic_dmg": (round(self.owner.weapon.magic_dmg*-0.4), 1)}))),2),5],
              [Item("Rejuvenation Nectar", lambda self: self.owner.addStatusEffect(OverTimeEffects(self.owner, 3, effects={"hp": (50,2)})), 1),5],
              [Item("Berserker Serum", lambda self: (self.owner.addStatusEffect(OverTimeEffects(self.owner.armor, 2, effects={"dmg_red": (-0.4,1)}),
                                                       self.owner.addStatusEffect(OverTimeEffects(self.owner.weapon, 2, effects={"m_damage": (100,1)})))), 2),5],
              [Item("Stonegolem Essence", lambda self: self.owner.addStatusEffect(OverTimeEffects(self.owner.armor, 3, effects={"dmg_red": (0.6,1)})),2),5],
              [Item("Seraphic Nectar", lambda self: self.owner.addStatusEffect(OverTimeEffects(self.owner,2,effects={"hp": (25,3)},treshold=0),1),1),5],
              [Item("Null Serum", lambda self: (self.owner.addStatusEffect(OverTimeEffects(self.owner,2,effects={"hp": (60,4)}),1), 
                                                self.owner.addStatusEffect(OverTimeEffects(self.owner.weapon,2,effects={"magic_dmg": (100,1)}))),2), 5],
              [Item("Elixir of Duality", lambda self: self.owner.addStatusEffect(OverTimeEffects(self.owner.weapon, 2, effects={ "m_damage" if random.randint(0,1) == 0 else "magic_dmg": (50,1)})), 2), 5]
            ]