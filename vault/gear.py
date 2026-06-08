from funcionalidades.combat_n_entities.combat_items import Item, Weapon, MagicWeapon, Armor, RangedWeapon, SecondaryWeapon
from funcionalidades.Utility.combat_utils import OverTimeEffects, modifyAttrs


meleeSkills = {
    "Focus Slash": lambda self, target, weaponUsed: (target.take_damage(self.weapon[weaponUsed].dmg*1.30, False), modifyAttrs(self, {"sta": lambda x: x-self.weapon["primary"].weight*10})),
    "Shadow Step": lambda self, target, weaponUsed: (target.take_damage(self.weapon[weaponUsed].dmg*2, True), self.addStatusEffect(OverTimeEffects(self.armor["chest"],2,effects={"dmg_red": (0.69,1)})), modifyAttrs(self, {"sta": lambda x: x-self.weapon[weaponUsed].weight*15})),
}

magicSkills = {
    "Fireball": lambda self, target: (target.addStatusEffect(OverTimeEffects(target, 3, effects= {"hp": (-25,2)})), modifyAttrs(self, {"mp": lambda x: x-self.weapon.mana_cost*10}))
}

rangedSkills = {
    "Burst Fire": lambda self, target: (target.take_damage(self.weapon.dmg*3), modifyAttrs(self, {"ammo": lambda x: x-3}))
}

secondarySkills = {
    "Taunt": lambda self, target: (
            target.addStatusEffect(OverTimeEffects(target,3,effects={"dmg_red": (-0.4, 1)})),
            target.addStatusEffect(OverTimeEffects(target,2,effects={"dmg": (20, 1),}))
        ),
}

blacksmith = [
    Weapon("Sword", 50, weight=1.0, skills={"Focus Slash": meleeSkills["Focus Slash"]}),
    Weapon("Axe", 80, weight=1.4, skills={"Focus Slash": meleeSkills["Focus Slash"]}),
    Weapon("Griefreaver", 100, weight=2.0, skills={"Focus Slash": meleeSkills["Focus Slash"]},twoHand=True),
    Weapon("Great Hammer", 350, weight=3.0, skills={"Focus Slash": meleeSkills["Focus Slash"]},twoHand=True),

    MagicWeapon("Staff", 5, 30, mana_cost=10, skills={"Fireball": magicSkills["Fireball"]}),
    MagicWeapon("Grimoire", 10, 70, mana_cost=25, skills={"Fireball": magicSkills["Fireball"]}),
    MagicWeapon("Trident", 40, 100, mana_cost=45, skills={"Fireball": magicSkills["Fireball"]},type=["magic","melee"]),
    MagicWeapon("Staff of ultimate power", 5, 250, mana_cost=60, skills={"Fireball": magicSkills["Fireball"]}),

    RangedWeapon("Beretta 93R", 100, ammo=20, ammoReq=1, weight=0.6, twoHand=True, skills={"Burst Fire": rangedSkills["Burst Fire"]}),
    RangedWeapon("Shortbow", 55, ammo=30, ammoReq=1, weight=2, twoHand=True, skills={"Quick Fire": rangedSkills["Burst Fire"]}),
    RangedWeapon("Throwing Knife", 45, ammo=10, ammoReq=1, weight=0.8, passives=[("on_hit",lambda ctx: ctx[target].addStatusEffect(ctx["target"],OverTimeEffects(ctx["target"],2,effects={"hp": (-15, 2)})))],type=["ranged","secondary"]),
    RangedWeapon("Laser Gun", 200, ammo= 50,ammoReq=10,weight= 0, skills={"Mega Ray": rangedSkills["Burst Fire"]}),

    SecondaryWeapon("Wooden Shield",0.05,10,0.5,skills={"Taunt": secondarySkills["Taunt"]}),
    SecondaryWeapon("Plasma Drone",0.08,15,weight=0,skills={"Taunt": secondarySkills["Taunt"]},stats={"int": 0.1}),
    SecondaryWeapon("Warding Bell",0,0,stats={}),
    SecondaryWeapon("Orb",0.01,0,stats={"int":0.1},passives=[("on_equip", "attr", {"mods": [{"attr": "int", "value": 2}]}),("on_unequip", "attr", {"mods": [{"attr": "int", "value": -2}]})]),
    
    Armor("Leather Helm",0.01,type="head"),
    Armor("Deep Water Bubble",0.05,type="head"), #Head
    Armor("Fedora",0.01,type="head"),
    Armor("Nanoskin(Head)",0.1,type="head"),

    Armor("Leather Chestplate",0.05,type="chest"),
    Armor("Deep Water Suit",0.08,type="chest"), #Chest
    Armor("Mysterious Trench Coat",0.01,type="chest"),
    Armor("Nanoskin(Chest)",0.1,type="chest"),

    Armor("Leather Leggings",0.03,type="legs"),
    Armor("Deep Water Leggings",0.03,type="legs"), #Legs
    Armor("Reinforced Trousers",0.02,type="legs"),
    Armor("Nanoskin(Legs)",0.1,type="legs"),

    Armor("Leather Boots",0.02,type="feet"),
    Armor("Deep Water Boots",0.015,type="feet"), #Feet
    Armor("Military Boots",0.03,type="feet"),
    Armor("Nanoskin(Feet)",0.1,type="feet"),
]

shopSmith = [
    [#common
        [Weapon("Sword", 50, weight=1.0, skills={"Focus Slash": meleeSkills["Focus Slash"]}),10],
        [MagicWeapon("Staff", 5, 30, mana_cost=10, skills={"Fireball": magicSkills["Fireball"]}),8],
        [SecondaryWeapon("Orb",0.01,20,stats={"int":0.1},passives=[("on_equip", "attr", {"mods": [{"attr": "int", "value": 2}]}),("on_unequip", "attr", {"mods": [{"attr": "int", "value": -2}]})]), 8],
    ],
    [#uncommon
        [RangedWeapon("Shortbow", 55, ammo=30, ammoReq=1, weight=2, twoHand=True, skills={"Quick Fire": rangedSkills["Burst Fire"]}),15],
        [RangedWeapon("Throwing Knife", 45, ammo=10, ammoReq=1, weight=0.8, passives=[("on_hit",lambda ctx: ctx[target].addStatusEffect(ctx["target"],OverTimeEffects(ctx["target"],2,effects={"hp": (-15, 2)})))],type=["ranged","secondary"]),24]
    ],
    [#rare
        [MagicWeapon("Grimoire", 10, 70, mana_cost=25, skills={"Fireball": magicSkills["Fireball"]}),30],
        [Weapon("Griefreaver", 100, weight=2.0, skills={"Focus Slash": meleeSkills["Focus Slash"]},twoHand=True),32]
    ],
    [#legendary
        [RangedWeapon("Beretta 93R", 100, ammo=20, ammoReq=1, weight=0.6, twoHand=True, skills={"Burst Fire": rangedSkills["Burst Fire"]}),50],
        [RangedWeapon("Laser Gun", 200, ammo= 50,ammoReq=10,weight= 0, skills={"Mega Ray": rangedSkills["Burst Fire"]}),100],
        [MagicWeapon("Staff of ultimate power", 5, 250, mana_cost=60, skills={"Fireball": magicSkills["Fireball"]}),45]
    ]
]

bl_length = len(blacksmith)