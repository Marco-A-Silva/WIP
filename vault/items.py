from funcionalidades.combat_n_entities.combat_items import Item
from funcionalidades.Utility.combat_utils import OverTimeEffects, modifyAttrs
import random

def generateItemPool(possibleItems):

    itemPool = []

    amount = random.choices([1,2,3,4],k=1,weights=[40,40,15,5])[0]
    for i in range(amount):
        rarity = random.choices([0,1,2,3],k=1,weights=[500, 25, 10, 5])[0]

        itemPool.append(random.choice(possibleItems[rarity]))

        if random.randint(1,20) == 20:
            itemPool.append(random.choice(possibleItems[rarity]))

    return itemPool


shopItems = [
    [#common
        [Item("Health Vial",lambda self: modifyAttrs(self.owner, {"hp": lambda x: x+self.owner.max_hp * 0.15}),2),15],
        [Item("Aether Essence", lambda self: modifyAttrs(self.owner, {"mp": lambda x: x+self.owner.max_mp * 0.15}),2),15],
    ],
    [#uncommon
        [Item("Invigorating Tonic", lambda self: self.owner.addStatusEffect(OverTimeEffects(self.owner.armor,2,effects={"dmg_red": (0.25, 1)})), 2), 30],
        [Item("Stonegolem Essence", lambda self: self.owner.addStatusEffect(OverTimeEffects(self.owner.armor, 3, effects={"dmg_red": (0.45,1)})),2),5],
    ],
    [#rare
        [Item("Ether Draught", lambda self: (modifyAttrs(self.owner, {"mp": lambda x: x+self.owner.max_mp}),
                                            self.owner.addStatusEffect(OverTimeEffects(self.owner.weapon,2,effects={"magic_dmg": (round(self.owner.weapon.magic_dmg*-0.4), 1)}))),2),5],
        [Item("Berserker Serum", lambda self: (self.owner.addStatusEffect(OverTimeEffects(self.owner.armor, 2, effects={"dmg_red": (-0.4,1)}),
                                                self.owner.addStatusEffect(OverTimeEffects(self.owner.weapon, 2, effects={"melee_dmg": (100,1)})))), 2),5],
    ],
    [#legendary
        [Item("Rejuvenation Nectar", lambda self: self.owner.addStatusEffect(OverTimeEffects(self.owner, 3, effects={"hp": (self.owner.max_hp*0.15,2)})), 1),5],
        [Item("Seraphic Nectar", lambda self: self.owner.addStatusEffect(OverTimeEffects(self.owner,2,effects={"hp": (25,3)},treshold=0),1),1),5],
        [Item("Null Serum", lambda self: (self.owner.addStatusEffect(("on_death",lambda ctx: modifyAttrs(ctx["player"],{"hp": lambda x: x + 30})),1), 
                                            self.owner.addStatusEffect(OverTimeEffects(self.owner.weapon,2,effects={"magic_dmg": (getattr(self.owner.weapon,"magic_dmg",100),1)}))),2), 5],
        [Item("Elixir of Duality", lambda self: self.owner.addStatusEffect(OverTimeEffects(self.owner.weapon, 2, effects={ "melee_dmg" if random.randint(0,1) == 0 else "magic_dmg": (50,1)})), 2), 5]
    ]
]

itemPools = [
    [#common
        Item("Bag'o gold",lambda self: modifyAttrs(self.owner, {"gd": lambda x: x+random.randint(1,15)}),1),
        Item("Sack of potatos", lambda self: modifyAttrs(self.owner, {"hp": lambda x: x + 50}),5),
        Item("Drop of Aether", lambda self: modifyAttrs(self.owner, {"mp": lambda x: x+10}),1),
    ],
    [#uncommon
        Item("uncommon Bag'o gold",lambda self: modifyAttrs(self.owner, {"gd": lambda x: x+random.randint(15,30)}),1),
        Item("Health Vial",lambda self: modifyAttrs(self.owner, {"hp": lambda x: x+self.owner.max_hp * 0.15}),2),
        Item("Aether Essence", lambda self: modifyAttrs(self.owner, {"mp": lambda x: x+self.owner.max_mp * 0.15}),2),
    ],
    [#rare
        Item("rare Bag'o gold",lambda self: modifyAttrs(self.owner, {"gd": lambda x: x+random.randint(30,45)}),1),
        Item("Invigorating Tonic", lambda self: self.owner.addStatusEffect(OverTimeEffects(self.owner.armor,2,effects={"dmg_red": (0.25, 1)})),2),
        Item("Ether Draught", lambda self: (modifyAttrs(self.owner, {"mp": lambda x: x+self.owner.max_mp}),
                                            self.owner.addStatusEffect(OverTimeEffects(self.owner.weapon,2,effects={"magic_dmg": (round(self.owner.weapon.magic_dmg*-0.4), 1)}))),2)
    ],
    [#legendary
        Item("LEGENDARY Bag'o gold",lambda self: modifyAttrs(self.owner, {"gd": lambda x: x+random.randint(50,70)}),1),
        Item("Rejuvenation Nectar", lambda self: self.owner.addStatusEffect(OverTimeEffects(self.owner, 3, effects={"hp": (self.owner.max_hp*0.15,2)})), 2),
        Item("Null Serum", lambda self: (self.owner.addStatusEffect(OverTimeEffects(self.owner,5,effects={"hp": (60,4)}),1), 
                                        self.owner.addStatusEffect(OverTimeEffects(self.owner.weapon,2,effects={"magic_dmg": (getattr(self.owner.weapon,"magic_dmg",100),1)}))),2)
    ]
]