from funcionalidades.combat_items import MagicWeapon, Weapon, Item, Armor

fists = Weapon("Fists", 50)
tunic = Armor("Tunic", 0.1)

class Player:
    

    def __init__(self, hp, mp, weapon: Weapon = None, armor: Armor = None):
        self.hp = hp
        self.mp = mp
        self.weapon = weapon
        if self.weapon is None:
            self.equip_weapon(fists)
        self.armor = armor
        if self.armor is None:
            self.equip_armor(tunic)

    def equip_weapon(self, weapon):
        weapon.setOwner(self)
        self.weapon = weapon
        

    def equip_armor(self, armor):
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

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

class Mage(Player):
    def __init__(self, hp, mp, weapon: Weapon = None):
        super().__init__(hp, mp, weapon)

class Enemy:
    def __init__(self,name,hp):
        self.hp = hp
        self.name = name

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0