from funcionalidades.combat_n_entities.combat_items import  Weapon, Armor
from .protocols import Equipable
import random

fists = Weapon("Fists", 20)
tunic = Armor("Tunic", 0.01)

class Player:

    def __init__(self, hp: float, mp: int, max_hp:int = 0, max_mp:int = 0, level: int = 0, xp2level: int = 50, xp: int = 0, gd: int = 0, weapon: Weapon | None = None, armor: Armor | None = None, stat_effs: list | None = None, name = "Hero"):
        self.name = name
        self.level = level
        self.xp2level = xp2level
        self.xp = xp
        self.statBlock = [random.randint(0,11) for i in range(8)] 
        """Vitality(hp)/Mind(mp)/Inteligence(magic_dmg)/Strength(melee_dmg)/Luck/Charisma/Awareness/Greed """
        self._hp = hp + 20*self.statBlock[0]
        self.max_hp = self._hp
        self.mp = mp + 20*self.statBlock[1]
        self.max_mp = self.mp or max_mp
        self.gd = gd
        self.stat_effs = stat_effs or []
        self.hooks = {}
        if weapon is None:
            self.equip_armament(fists)
        else:
            self.weapon = weapon
        if armor is None:
            self.equip_armament(tunic)
        else:
            self.armor = armor
        self.items = []

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

    def gainXP(self, amount, lvldUp):
        if self.xp + amount < self.xp2level:
            self.xp += amount
            lvldUp = False
        else:
            amount -= self.xp2level - self.xp
            self.level += 1
            self.xp = amount
            lvldUp = True

        return lvldUp


    def addStatusEffect(self, status, style: int = 0):
        if style == 0:
            self.stat_effs.append(status)
        else:
            for attr, (diff, nature) in status.effects.items():
                if attr not in self.hooks:
                    self.hooks[attr] = []
                self.hooks[attr].append(status)


    def equip_armament(self, armament: Equipable):
        armament.setOwner(self)
        armament.equip()

    def useItem(self,index):
        self.items[index].function(self.items[index])
        self.items[index].uses -= 1
        if(self.items[index].uses == 0):
            del self.items[index]

    def take_damage(self, amount, ignore):
        if not ignore:
            self.hp -= amount* (1 - self.armor.dmg_red)
        else: self.hp -= amount
        if self.hp < 0:
            self.hp = 0
 
    def gold_reward(self, amount):
        self.gd += amount

    def gold_remove(self, amount):
        self.gd -= amount
        
    def updStats(self, index):
        match index:
            case 0:
                self._hp += self.max_hp*0.1
                if self._hp > self.max_hp: self.max_hp = self._hp
            case 1:
                self.mp += self.max_mp*0.1
                if self.mp > self.max_mp: self.max_mp = self.mp
            case 2:
                self.weapon.magic_dmg += self.weapon.magic_dmg*0.01*self.statBlock[2]
            case 3:
                self.weapon.melee_dmg += self.weapon.melee_dmg*0.01*self.statBlock[3]

class Enemy:
    def __init__(self, name: str, hp: float, dmg: int = 5, dmg_red: int = 0, reward: int = 10, skills: dict | None = None, stat_effs: list | None = None, tameable: bool = False):
        self._hp = hp
        self.base_hp = hp
        self.dmg = dmg
        self.dmg_red = dmg_red
        self.name = name
        self.reward = reward
        self.skills = skills or {}
        self.stat_effs = stat_effs or []
        self.hooks = {}
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
    def call_reinforcements(self, enemy_list):
        goblin_count = sum(1 for enemy in enemy_list if enemy.name == self.name)
        diff = 3 - goblin_count
        if(diff > 0):
            index = next((i for i, e in enumerate(enemy_list) if e.name == self.name), -1)
            if index == -1:
                return  # no hay Goblin

            for i in range(diff):
                reinforcement = Enemy(self.name, round(self.base_hp / 2), self.dmg, self.dmg_red, skills=self.skills)
                enemy_list.insert(index + 1 + i, reinforcement)
        else:
            self.dmg += 5