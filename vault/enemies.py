from funcionalidades.combat_n_entities.entities import Enemy
from funcionalidades.Utility.combat_utils import OverTimeEffects, modifyAttrs

class EnemySkill:

    def __init__(self, name, type_, effect,tags:str = ""):
        self.name = name
        self.type = type_
        self.effect = effect
        self.tags = tags
    
enemySkills = {
    "Regen": EnemySkill(
        "Regen",
        "heal",
        lambda self, target: target.addStatusEffect(OverTimeEffects(target,2,effects={"hp": (target.hp*0.4, 0), "dmg_red": (0.05,1)},tags=["def_up"])),
        tags=["def_up"]
    ),

    "Harden": EnemySkill(
        "Harden",
        "buff",
        lambda self, target: target.addStatusEffect(OverTimeEffects(target,2,effects={"dmg_red": (0.3,1), "dmg": (-5,-1)},tags=["def_up","dmg_up"])),
        tags=["def_up","dmg_up"]
    ),

    "Call Reinforcements": EnemySkill(
        "Call Reinforcements",
        "special",
        lambda self, target: self.call_reinforcements(),
    ),

    "Humiliation": EnemySkill( 
        "Humiliation",
        "buff",
        lambda self, target: target.addStatusEffect(OverTimeEffects(target,2,effects={"dmg_red": (0.02, 1)},tags=["def_up"])),
        tags=["def_up"]
    ),

    "Shroud": EnemySkill(
        "Shroud",
        "buff",
        lambda self, target: target.addStatusEffect(OverTimeEffects(target,1,effects={"dmg_red": (1,True),"hp": (20,0)},tags=["def_max"])),
        tags=["def_max"]
    ),

    "Intangable Attack": EnemySkill(
        "Intangible Attack",
        "special",
        lambda self, target: self.attack(target, True)
    ),

    "Berserk": EnemySkill(
        "Berserk",
        "buff",
        lambda self, target: target.addStatusEffect(OverTimeEffects(target,2,effects={"dmg_red": (0.2, 1), "dmg": (target.dmg*0.3, 1)},tags=["def_up","dmg_up"])),
        tags=["def_up","dmg_up"]
    ),

    "Taunt": EnemySkill(
        "Taunt",
        "debuff",
        lambda self, target: (
            target.addStatusEffect(OverTimeEffects(target.armor["chest"],3,effects={"dmg_red": (-0.25, 1)},tags=["def_dn"])),
            target.addStatusEffect(OverTimeEffects(target.desiredWeapon("dmg") if target.desiredWeapon("dmg") != None else target.desiredWeapon("mgc"),2,effects={"dmg" if target.desiredWeapon("dmg") != None else "mgc":
                    (-target.desiredWeapon("dmg").dmg*0.25 if target.desiredWeapon("dmg") != None else -target.desiredWeapon("mgc").mgc*0.25, 1)},tags=["dmg_dn" if target.desiredWeapon("dmg") != None else "mgc_dn"]))
        ),
        tags=["def_dn","mgc_dn","dmg_dn"]
    ),

    "Overclocked Strike": EnemySkill(
        "Overclocked Strike",
        "special",
        lambda self, target: (
            self.addStatusEffect(OverTimeEffects(self,3,effects={"dmg_red": (-0.05,1)},tags=["def_dn"])),
            modifyAttrs(target, {"hp": lambda x: x-target.max_hp*0.05})
        ),
        tags=["def_dn"]
    ),

    "Toxic Spores": EnemySkill(
        "Toxic Spores",
        "debuff",
        lambda self, target: target.addStatusEffect(OverTimeEffects(target,3,effects={"hp": (-5, 2)},tags=["dot"])),
        tags=["dot"]
    ),

    "Cinder Swipe": EnemySkill(
        "Cinder Swipe",
        "debuff",
        lambda self, target: target.addStatusEffect(OverTimeEffects(target,3,effects={"hp": (-5, 2)},tags=["dot"])),
        tags=["dot"]
    ),

    "Smoke Screen": EnemySkill(
        "Smoke Screen",
        "buff",
        lambda self, target: target.addStatusEffect(OverTimeEffects(target,2,effects={"dmg_red": (0.4, 1)},tags=["def_up"])),
        tags=["def_up"]
    ),

    "Leech Life": EnemySkill(
        "Leech Life",
        "special",
        lambda self, target: (
            modifyAttrs(self, {"hp": lambda x: x+10}),
            modifyAttrs(target, {"hp": lambda x: x-10})
        )
    ),

    "Reverse Cursed Technique": EnemySkill(
        "Reverse Cursed Technique",
        "special",
        lambda self, target: (
            modifyAttrs(target,{"hp": lambda x: x-target.weapon.dmg*0.05}),
            self.addStatusEffect(OverTimeEffects(self,2,effects={"hp": (0.4,5)},tags=["imm"]),1)
        ),
        tags=["imm"]
    ),

    "Ashen Return": EnemySkill(
        "Ashen Return",
        "heal",
        lambda self, target: target.addStatusEffect(OverTimeEffects(target,3,effects={"hp": (target.base_hp*0.5,3)},tags=["revive"],treshold=0),1),
        tags=["revive"]
    )
}

enemies = [
    # Eudrýs (Steampunk)
    Enemy("Guilded Automaton", 200, dmg=25, skills=[
        enemySkills["Overclocked Strike"]
    ], reward=25),
    Enemy("Scrap Wyvern", 140, dmg=25, skills=[

    ]),

    Enemy("Slime", 50, dmg=10, skills=[
        enemySkills["Call Reinforcements"],
        enemySkills["Regen"],
        enemySkills["Harden"]
    ], tameable=True, reward=10),

    Enemy("Goblin", 100, dmg=15, skills=[
        enemySkills["Call Reinforcements"],
        enemySkills["Humiliation"]
    ], reward=15),

    Enemy("Wraith", 50, dmg=12, skills=[
        enemySkills["Shroud"],
        enemySkills["Intangable Attack"]
    ], reward=12),

    Enemy("Orc", 150, dmg=20, skills=[
        enemySkills["Berserk"],
        enemySkills["Taunt"]
    ], reward=20),

    Enemy("Hollow Siren", 125, dmg=18, skills=[
        
    ], reward=18),

    Enemy("Fungal Titan", 225, dmg=30, skills=[
        enemySkills["Toxic Spores"]
    ], reward=28),

    Enemy("Ashling Stalker", 100, dmg=15, skills=[
        enemySkills["Cinder Swipe"],
        enemySkills["Smoke Screen"]
    ], reward=15),

    Enemy("Fire Imp", 80, dmg=12, skills=[
        enemySkills["Cinder Swipe"],
        enemySkills["Berserk"]
    ], reward=14),

    Enemy("Stone Golem", 250, dmg=25, skills=[
        enemySkills["Harden"],
        enemySkills["Taunt"]
    ], reward=25),

    Enemy("Spectral Knight", 180, dmg=18, skills=[
        enemySkills["Shroud"],
        enemySkills["Overclocked Strike"]
    ], reward=22),

    Enemy("Blight Horror", 160, dmg=22, skills=[
        enemySkills["Toxic Spores"],
        enemySkills["Berserk"],
        enemySkills["Call Reinforcements"]
    ], reward=20),

    Enemy("Forest Treant", 210, dmg=24, skills=[
        enemySkills["Taunt"],
        enemySkills["Harden"]
    ], reward=26),
]


bosses = [
    Enemy("High Orc", 300, dmg=25, skills=[
        enemySkills["Berserk"],
        enemySkills["Taunt"]
    ], reward=90),

    Enemy("Vampire Lord", 250, dmg=22, skills=[
        enemySkills["Leech Life"],
        enemySkills["Shroud"]
    ], reward=140),

    Enemy("High Oracle of the Abyss, En’Thar", 250, dmg=24, skills=[
        enemySkills["Reverse Cursed Technique"]
    ], reward=200),

    Enemy("Ancient Fire Dragon", 400, dmg=35, skills=[
        enemySkills["Cinder Swipe"],
        enemySkills["Berserk"],
        enemySkills["Smoke Screen"]
    ], reward=300),

    Enemy("Void Warden", 350, dmg=30, skills=[
        enemySkills["Reverse Cursed Technique"],
        enemySkills["Shroud"],
        enemySkills["Intangable Attack"]
    ], reward=280),

    Enemy("Titanic Fungal Behemoth", 450, dmg=40, skills=[
        enemySkills["Toxic Spores"],
        enemySkills["Harden"],
        enemySkills["Overclocked Strike"]
    ], reward=350),

    Enemy("Storm Leviathan", 380, dmg=32, skills=[
        enemySkills["Berserk"],
        enemySkills["Overclocked Strike"]
    ], reward=320),

    Enemy("Shadow Reaper", 360, dmg=30, skills=[
        enemySkills["Shroud"],
        enemySkills["Intangable Attack"],
        enemySkills["Leech Life"]
    ], reward=300),

    Enemy("Molten Titan", 420, dmg=38, skills=[
        enemySkills["Cinder Swipe"],
        enemySkills["Smoke Screen"],
        enemySkills["Berserk"]
    ], reward=340),

    Enemy("Celestial Phoenix", 400, dmg=35, skills=[
        enemySkills["Cinder Swipe"],
        enemySkills["Reverse Cursed Technique"]
    ], reward=360),
]