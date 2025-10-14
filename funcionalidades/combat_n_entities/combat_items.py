
class Weapon:
    def __init__(self, name: str, m_damage: int, owner = None):
        self.name = name
        self.m_damage = m_damage
        self.owner = owner

    def setOwner(self, owner):
        self.owner = owner

    def melee_attack(self, target):
        target.take_damage(self.m_damage)

class MagicWeapon(Weapon):
    def __init__(self, name, m_damage, magic_dmg):
        super().__init__(name, m_damage)
        self.magic_dmg = magic_dmg

    def cast_spell(self, target):
        target.take_damage(self.magic_dmg)
        self.owner.mp -= 10


class Item:
    def __init__(self, name, uses):
        self.name = name
        self.uses = uses

# Defense is a % reduction of damage taken
class Armor:
    def __init__(self, name, defense):
        self.name = name
        self.defense = defense