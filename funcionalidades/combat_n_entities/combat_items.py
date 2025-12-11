from .protocols import Equipable
 
stats = {"vit": 0, "mnd": 1, "int": 2, "str": 3, "lck": 4, "chr": 5, "awe": 6, "gre": 7,"end":8,"dex":9}

def modifyAttrs(target, changes: dict):

    for attr, val in changes.items():
        if attr in stats: attr = stats[attr]
        if type(attr) == int:
            target.statBlock[attr] += val
        else:
            if hasattr(target, attr):
                # Si el valor es callable (función), lo ejecuta con el valor actual
                if callable(val):
                    setattr(target, attr, val(getattr(target, attr)))
                else:
                    setattr(target, attr, val)

class Weapon:
    def __init__(self, name: str, melee_dmg: int, weight=1.0, skills = None, owner = None):
        self.name = name
        self.magic_dmg = 0
        self.owner = owner
        self.melee_dmg = melee_dmg 
        self.skills = skills or {}
        self.weight = weight
        
    def setOwner(self, owner):
        self.owner = owner

    def equip(self, isMod):
        if self.owner: 
            self.owner.weapon = self
            self.melee_dmg += self.owner.statBlock[3]*0.10* self.melee_dmg if isMod else 0

    def useSkill(self, index, target):
        self.skills[index](self,target)
        
    def melee_attack(self, target, ignore):
        cost = 8*self.weight # 8 is the base stamina cost

        if self.owner.sta <= cost:
            return  # o ataque fallido/debilitado

        self.owner.sta -= cost
        target.take_damage(self.melee_dmg, ignore)

class MagicWeapon(Weapon):
    def __init__(self, name, melee_dmg, magic_dmg, weight=1.0, mana_cost=20, skills = None):
        super().__init__(name, melee_dmg, weight=weight,skills=skills)
        self.magic_dmg = magic_dmg
        self.mana_cost = mana_cost

    def equip(self,isMod):
        if self.owner: 
            self.owner.weapon = self
            self.magic_dmg += self.owner.statBlock[2]*0.10* self.magic_dmg if isMod else 0

    def cast_spell(self, target, ignore: bool = False):
        target.take_damage(self.magic_dmg, ignore)
        self.owner.mp -= self.mana_cost


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

    def equip(self, isMod):
        for i in self.owner.items:
            if i.name == self.name:
                i.uses += self.uses
                return
          
        self.owner.items.append(self.copy())

# Defense is a % reduction of damage taken
class Armor:
    def __init__(self, name, dmg_red, owner = None):
        self.name = name
        self.dmg_red = dmg_red
        self.owner = owner

    def setOwner(self, owner):
        self.owner = owner

    def equip(self, isMod):
        if self.owner: self.owner.armor = self

class OverTimeEffects:
    def __init__(self, target, turns, effects, treshold: int = 0):
        """
        effects: diccionario {atributo: diferencia}
        Ejemplo: {"hp": +10, "armor": -5}
        """

        self.treshold = treshold
        self.turns = turns
        self.og_turns = turns
        self.target = target
        self.effects = effects

        # Aplica todos los efectos al crear el objeto
        modifyAttrs(target, {attr: (lambda d=diff: (lambda x: x + d))() for attr, (diff,_) in effects.items() if _ == 0 or _ == 1})
    
    def passTurn(self):
        self.turns -= 1
        self.resolveOTE()

    def resolveOTE(self, trigger: int = False, hp:int = 0, mod: int = 0):
        # Revierte todos los efectos
        for attr, (diff, nature) in self.effects.items():
            match nature:
                case -1: #Delayed Time Effect
                    if self.turns == 0:
                        attr = attr.replace("_fin","")
                        effects = {attr: (diff,1)}
                        self.target.addStatusEffect(OverTimeEffects(self.target, self.og_turns, effects))
                case 0: #One time effect
                    pass
                case 1: #Limited time effect
                    if self.turns == 0: 
                        modifyAttrs(self.target, {attr: (lambda d=diff: (lambda x: x - d))()})
                case 2: #Every turn for X turns
                    modifyAttrs(self.target, {attr: (lambda d=diff: (lambda x: x + d))()})
                case 3: #Triggered effect
                    if trigger:
                        val = getattr(self.target, attr)
                        if val <= self.treshold:
                            modifyAttrs(self.target, {attr: (lambda d=diff: (lambda x: x + d))()})
                case 4: #Prevents increase of a stat
                    if trigger:
                        old = hp      # HP antes del cambio
                        new = mod     # HP después del cambio
                        delta = new - old

                        # Si delta > 0 → se intentó curar → cancelar
                        if delta > 0:
                            setattr(self.target, f"_{attr}", final_value)
                case 5: #Prevents descrease of a stat
                    if trigger:
                        old = hp      # HP antes del cambio
                        new = mod     # HP después del cambio
                        delta = new - old

                        final_value = round(old + delta*diff)

                        # Si delta > 0 → se intentó curar → cancelar
                        if delta < 0:
                            setattr(self.target, f"_{attr}", final_value)
        