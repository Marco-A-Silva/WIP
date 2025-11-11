from funcionalidades import Item, OverTimeEffects, modifyAttrs

shopItems = [[Item("Health Potion",lambda self: modifyAttrs(self.owner, {"hp": lambda x: x+10}),2),15],
              [Item("Mana Potion", lambda self: modifyAttrs(self.owner, {"mp": lambda x: x+10}),2),15],
              [Item("Invigorating Potion", lambda self: self.owner.addStatusEffect(OverTimeEffects(self.owner,2,effects={"hp": (0.2, 1)})), 2), 30],
              [Item("Ether Flask", lambda self: (modifyAttrs(self.owner, {"mp": lambda x: x+self.owner.mp}),
                                                 self.owner.addStatusEffect(OverTimeEffects(self.owner.weapon,2,effects={"magic_dmg": (round(self.owner.weapon.magic_dmg*-0.4), 1)}))),2),5],
              [Item("Rejuvenation Brew", lambda self: self.owner.addStatusEffect(OverTimeEffects(self.owner, 3, effects={"hp": (100,2)})), 1),5],
              [Item("Berserker’s Tonic", lambda self: None, 2),5]
            ]