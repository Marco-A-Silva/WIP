from funcionalidades.combat_n_entities.combat_items import  Weapon, Armor
from .protocols import Equipable

fists = Weapon("Fists", 50)
tunic = Armor("Tunic", 0.02)

class Player:

    def __init__(self, hp: int, mp: int, gd: int = 0, weapon: Weapon | None = None, armor: Armor | None = None, stat_effs: list | None = None, name = "Hero"):
        self.name = name
        self._hp = hp
        self.mp = mp
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
            self.hp -= round(amount* (1 - self.armor.dmg_red))
        else: self.hp -= amount
        if self.hp < 0:
            self.hp = 0
 
    def gold_reward(self, amount):
        self.gd += amount

    def gold_remove(self, amount):
        self.gd -= amount


class Enemy:
    def __init__(self, name: str, hp: int, dmg: int = 5, dmg_red: int = 0, reward: int = 10, skills: dict | None = None, stat_effs: list | None = None, tameable: bool = False):
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
            self.hp -= round(amount * (1 - self.dmg_red))
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