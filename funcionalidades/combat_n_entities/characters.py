from funcionalidades.combat_n_entities.combat_items import MagicWeapon, Weapon, Item, Armor
from .protocols import Equipable

fists = Weapon("Fists", 50)
tunic = Armor("Tunic", 0.02)

class Player:

    def __init__(self, hp: int, mp: int, gd: int = 0, weapon: Weapon = None, armor: Armor = None, stat_effs = []):
        self.hp = hp
        self.mp = mp
        self.gd = gd
        self.items = []
        self.stat_effs = stat_effs
        self.weapon = weapon
        if self.weapon is None:
            self.equip_armament(fists)
        self.armor = armor
        if self.armor is None:
            self.equip_armament(tunic)

    def addStatusEffect(self, status):
        self.stat_effs.append(status)

    def equip_armament(self, armament: Equipable):
        armament.setOwner(self)
        armament.equip()

    def addItem(self, item : Item):
        self.items.append(item)

    def useItem(self,index):
        self.items[index].function()
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


class Mage(Player):
    def __init__(self, hp: int, mp: int, weapon: Weapon = None):
        super().__init__(hp, mp, weapon)
        

class Enemy:
    def __init__(self, name: str, hp: int, dmg: int = 5, dmg_red: int = 0, reward: int = 10, skills = None, stat_effs = []):
        self.hp = hp
        self.base_hp = hp
        self.dmg = dmg
        self.dmg_red = dmg_red
        self.name = name
        self.reward = reward
        self.skills = skills
        self.stat_effs = stat_effs

    def addStatusEffect(self, status):
        self.stat_effs.append(status)

    def attack(self, target, ignore):
        target.take_damage(self.dmg, ignore)

    def take_damage(self, amount, ignore):
        if not ignore:
            self.hp -= round(amount * (1 - self.dmg_red))
        else: self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    # Reserved for swarm-like enemies
    def call_reinforcements(self, amount: int, enemy_list):
        goblin_count = sum(1 for enemy in enemy_list if enemy.name == "Goblin")
        if(goblin_count <= 3):
            index = next((i for i, e in enumerate(enemy_list) if e.name == "Goblin"), -1)
            if index == -1:
                return  # no hay Goblin

            for i in range(amount):
                reinforcement = Enemy(self.name, self.base_hp - 50, self.dmg, self.dmg_red, skills=self.skills)
                enemy_list.insert(index + 1 + i, reinforcement)
        else:
            self.dmg += 5