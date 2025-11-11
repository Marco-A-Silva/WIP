from .protocols import Equipable
 

def modifyAttrs(target, changes: dict):
    
    for attr, val in changes.items():
        if hasattr(target, attr):
            # Si el valor es callable (función), lo ejecuta con el valor actual
            if callable(val):
                setattr(target, attr, val(getattr(target, attr)))
            else:
                setattr(target, attr, val)

class Weapon:
    def __init__(self, name: str, m_damage: int, owner = None):
        self.name = name
        self.m_damage = m_damage
        self.owner = owner

    def setOwner(self, owner):
        self.owner = owner

    def equip(self):
        if self.owner: self.owner.weapon = self

    def melee_attack(self, target,ignore):
        target.take_damage(self.m_damage, ignore)

class MagicWeapon(Weapon):
    def __init__(self, name, m_damage, magic_dmg):
        super().__init__(name, m_damage)
        self.magic_dmg = magic_dmg

    def cast_spell(self, target):
        target.take_damage(self.magic_dmg)
        self.owner.mp -= 10


class Item:
    def __init__(self, name, function , uses):
        self.name = name
        self.owner = None
        self.function = function
        self.uses = uses

    def setOwner(self, owner):
        self.owner = owner

    def copy(self):
        item = Item(self.name, self.function, self.uses)
        item.setOwner(self.owner)
        self.owner = None
        return item

    def equip(self):
        self.owner.items.append(self.copy())

# Defense is a % reduction of damage taken
class Armor:
    def __init__(self, name, dmg_red, owner = None):
        self.name = name
        self.dmg_red = dmg_red
        self.owner = owner

    def setOwner(self, owner):
        self.owner = owner

    def equip(self):
        if self.owner: self.owner.armor = self

class OverTimeEffects:
    def __init__(self, target, turns, effects):
        """
        effects: diccionario {atributo: diferencia}
        Ejemplo: {"hp": +10, "armor": -5}
        """
        self.turns = turns
        self.target = target
        self.effects = effects
        self.first = True

        # Aplica todos los efectos al crear el objeto
        modifyAttrs(target, {attr: (lambda d=diff: (lambda x: x + d))() for attr, (diff,_) in effects.items()})

    def resolveOTE(self):
        # Revierte todos los efectos
        for attr, (diff, nature) in self.effects.items():
            match nature:
                case 0: #One time effect
                    pass
                case 1: #Limited time effect
                    if self.turns == 0: 
                        modifyAttrs(self.target, {attr: (lambda d=diff: (lambda x: x - d))()})
                case 2: #Every turn for X turns
                    if not self.first:
                        modifyAttrs(self.target, {attr: (lambda d=diff: (lambda x: x + d))()})
                    
                    self.first = False
            
    def passTurn(self):
        self.turns -= 1
        self.resolveOTE()
        