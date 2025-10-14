from funcionalidades.combat_n_entities.combat_items import MagicWeapon, Weapon, Item, Armor

fists = Weapon("Fists", 50)
tunic = Armor("Tunic", 0.1)

class Player:

    def __init__(self, hp: int, mp: int, gd: int = 0, weapon: Weapon = None, armor: Armor = None):
        self.hp = hp
        self.mp = mp
        self.gd = gd
        self.items = []
        self.weapon = weapon
        if self.weapon is None:
            self.equip_weapon(fists)
        self.armor = armor
        if self.armor is None:
            self.equip_armor(tunic)

    def equip_weapon(self, weapon: Weapon):
        weapon.setOwner(self)
        self.weapon = weapon

    def equip_armor(self, armor: Armor):
        self.armor = armor

    def unequip_weapon(self):
        if not self.weapon:
            return
        else:
            self.weapon = None

    def unequip_armor(self):
        if not self.armor:
            return
        else:
            self.armor = None

    def addItem(self, item : Item):
        self.items.append(item)

    def take_damage(self, amount):
        self.hp -= amount
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
    def __init__(self, name: str, hp: int, reward: int = 10):
        self.hp = hp
        self.name = name
        self.reward = reward

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0