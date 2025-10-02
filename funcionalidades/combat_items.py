
class Weapon:
    def __init__(self, name, m_damage):
        self.name = name
        self.m_damage = m_damage

    def melee_attack(self, attacker, target):
        target.take_damage(self.m_damage)

class MagicWeapon(Weapon):
    def __init__(self, name, m_damage, magic_dmg):
        super().__init__(name, m_damage)
        self.magic_dmg = magic_dmg

    def cast_spell(self, caster, target):
        target.take_damage(self.magic_dmg)
        caster.mp -= 10 


class Item:
    def __init__(self, name, uses):
        self.name = name
        self.uses = uses

class Armor:
    def __init__(self, name, defense):
        self.name = name
        self.defense = defense