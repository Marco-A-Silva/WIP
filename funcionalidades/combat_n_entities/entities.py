from funcionalidades.combat_n_entities.combat_items import  Weapon, Armor, Hook
from .protocols import Equipable
from funcionalidades.Utility.combat_utils import Hooks
import random

FISTS = Weapon("Fists", 50)
TUNIC = Armor("Tunic", 0.01, "chest")

class StatBlock(list):

    def __init__(self, player, iterable = ()):
        super().__init__(iterable)
        self.player = player

    def __setitem__(self, index, value):
        if self[index] != value:
            diff = value - self[index]
            super().__setitem__(index,value)
            self.onChange(index,diff)

    def onChange(self, index, diff):
        match index:
            case 0:  # Vitality → Max HP
                inc = 10 * diff
                self.player.max_hp += inc
                self.player._hp += inc

            case 1:  # Mind → Max MP
                inc = 8 * diff
                self.player.max_mp += inc
                self.player.mp += inc
            
            case 2:
                for key,weapon in self.player.weapon.items():
                    if weapon is not None and "int" in weapon.scaling.keys():
                        if "magic" in weapon.type:
                            weapon.mgc = weapon.calc_damage(weapon.base_mgc)
                        else:
                            weapon.dmg = weapon.calc_damage(weapon.base_dmg)

            case 3:
                for key,weapon in self.player.weapon.items():
                    if weapon is not None and "str" in weapon.scaling.keys():
                        if "magic" in weapon.type:
                            weapon.mgc = weapon.calc_damage(weapon.base_dmg)
                        else:
                            weapon.dmg = weapon.calc_damage(weapon.base_dmg)



            case 8:  # Endurance → Max STA
                inc = 8 * diff
                self.player.max_sta += inc
                self.player.sta += inc

class Entity():

    def __init__(self, applyMods, hp: float, mp:int = 100, sta:int = 60, max_sta:int = 60, max_hp:int = 0, max_mp:int = 0, weapons: {} | None = None, armor: {} | None = None, stat_effs: list | None = None, statBlock: list = [], name = "Entity"):
        self.name = name
        self.statBlock = StatBlock(self,statBlock) if statBlock else StatBlock(self,[random.randint(0,11) for i in range(10)])
        """Vitality/Mind/Inteligence/Strength/Luck/Charisma/Awareness/Agility/Endurance/Dexterity"""
        self._hp = hp + 20*self.statBlock[0] if applyMods else hp
        self.max_hp = max(self._hp,max_hp)
        self.mp = mp + 20*self.statBlock[1] if applyMods else mp
        self.max_mp = max(self.mp,max_mp)
        self.sta = sta
        self.max_sta = max(max_sta,sta)
        self.gd = gd
        self.stat_effs = stat_effs or []
        self.tags = []
        self.hooks = Hooks()
        self.armor = {"head": None, "chest": None, "legs": None, "feet": None}
        self.weapon = {"primary": None, "secondary": None}
        if weapons is None or all(weapon is None for weapon in weapons.values()):
            self.equip_armament(FISTS,applyMods)
        else:
            self.weapon = weapons
        if armor is None or all(piece is None for piece in armor.values()):
            self.equip_armament(TUNIC, applyMods)
        else:
            for key, piece in armor.items():
                if piece:
                    self.equip_armament(piece,applyMods)
        self.items = []

class Player:

    def __init__(self, applyMods, hp: float, mp:int = 100, sta:int = 60, max_sta:int = 60, max_hp:int = 0, max_mp:int = 0, level: int = 0, xp: int = 0, gd: int = 0, weapons: {} | None = None, armor: {} | None = None, stat_effs: list | None = None, statBlock: list = [], name = "Hero"):
        self.name = name
        self.level = level
        self.xp2level = self._calc_xp2level()
        self.xp = xp
        self.statBlock = StatBlock(self,statBlock) if statBlock else StatBlock(self,[random.randint(0,11) for i in range(10)])
        """Vitality/Mind/Inteligence/Strength/Luck/Charisma/Awareness/Agility/Endurance/Dexterity"""
        self._hp = hp + 20*self.statBlock[0] if applyMods else hp
        self.max_hp = max(self._hp,max_hp)
        self.mp = mp + 20*self.statBlock[1] if applyMods else mp
        self.max_mp = max(self.mp,max_mp)
        self.sta = sta
        self.max_sta = max(max_sta,sta)
        self.gd = gd
        self.stat_effs = stat_effs or []
        self.tags = []
        self.hooks = Hooks()
        self.armor = {"head": None, "chest": None, "legs": None, "feet": None}
        self.weapon = {"primary": None, "secondary": None}
        if weapons is None or all(weapon is None for weapon in weapons.values()):
            self.equip_armament(FISTS,applyMods)
        else:
            self.weapon = weapons
        if armor is None or all(piece is None for piece in armor.values()):
            self.equip_armament(TUNIC, applyMods)
        else:
            for key, piece in armor.items():
                if piece:
                    self.equip_armament(piece,applyMods)
        self.items = []

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        old = self._hp
        self._hp = max(0, value)

       # if "hp" in self.hooks:
        #    for hook in self.hooks["hp"]:
          #      hook.resolveOTE(True, old, self._hp)
    
    def _calc_xp2level(self):
        base = 50
        factor = 1.35
        return int(base * (factor ** self.level))

    def gainXP(self, amount):
        levels_gained = 0
        self.xp += amount

        while self.xp >= self.xp2level:
            self.xp -= self.xp2level
            self.level += 1
            levels_gained += 1
            self.xp2level = self._calc_xp2level()

        return levels_gained

    def addStatusEffect(self, status, style: int = 0):
        if style == 0:
            self.stat_effs.append(status)
        else:
            type, effect = status
            self.hooks.add(type, effect)

    def equip_armament(self, armament: Equipable, isMod):
        armament.setOwner(self)
        armament.equip(isMod)

    def useItem(self,index):
        self.items[index].function(self.items[index])
        self.items[index].uses -= 1
        if(self.items[index].uses == 0):
            del self.items[index]

    def take_damage(self, amount, ignore):
        self.hp -= amount * (1 - (self.dmgRed() * (1 - ignore)))
        if self.hp < 0:
            self.hp = 0
 
    def gold_reward(self, amount):
        self.gd += amount

    def gold_remove(self, amount):
        self.gd -= amount

    def hasStatus(self, tags):

        for tag in tags:
            for effect in self.stat_effs:
                if tag in effect.tags:
                    return True

        return False

    def dmgRed(self):
        return getattr(self.weapon["primary"],"dmg_red",0) + getattr(self.weapon["secondary"],"dmg_red",0) + sum(piece.dmg_red for piece in self.armor.values() if piece is not None)
            
    def desiredWeapon(self, attr):
        if getattr(self.weapon["primary"],attr,0) != 0:
            return self.weapon["primary"]
        elif getattr(self.weapon["secondary"],attr,0) != 0:
            return self.weapon["secondary"]
        else:
            return None

class Enemy:
    def __init__(self, name: str, hp: float, dmg: int = 5, dmg_red: int = 0, reward: int = 10, skills: dict | None = None, stat_effs: list | None = None, tameable: bool = False):
        self._hp = hp
        self.max_hp = hp
        self.base_hp = hp
        self.dmg = dmg
        self.dmg_red = dmg_red
        self.name = name
        self.reward = reward
        self.skills = skills or {}
        self.stat_effs = stat_effs or []
        self.hooks = {}
        self.tags = []
        self.tameable = tameable

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        old = self._hp
        self._hp = max(0, value)

        if "hp" in self.hooks:
            for hook in self.hooks["hp"]:
                hook.resolveOTE(True, old, self._hp)



    def addStatusEffect(self, status, style: int = 0):
        if style == 0:
            self.stat_effs.append(status)
        else:
            for attr, (diff, nature) in status.effects.items():
                if attr not in self.hooks:
                    self.hooks[attr] = []
                self.hooks[attr].append(status)

    def attack(self, target, ignore):
        target.take_damage(self.dmg, ignore)

    def take_damage(self, amount, ignore):
        if not ignore:
            self.hp -= amount * (1 - self.dmg_red)
        else: self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    # Reserved for swarm-like enemies
    def call_reinforcements(self):
        diff = 3
        return

    def hasStatus(self, tags):

        for tag in tags:
            for effect in self.stat_effs:
                if tag in effect.tags:
                    return True

        return False