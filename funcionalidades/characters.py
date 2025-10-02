from funcionalidades.combat_items import MagicWeapon, Weapon, Item, Armor

class Player:
    def __init__(self, hp, mp, weapon: Weapon):
        self.hp = hp
        self.mp = mp
        self.weapon = None
        if weapon is not None:
            self.equip_weapon(weapon)

    def equip_weapon(self, weapon):
        self.weapon = weapon


    def unequip_weapon(self):
        if not self.weapon:
            return
        else:
            self.weapon = None

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

class Mage(Player):
    def __init__(self, hp, mp):
        super().__init__(hp, mp)



class Enemy:
    def __init__(self,hp):
        self.hp = hp

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0