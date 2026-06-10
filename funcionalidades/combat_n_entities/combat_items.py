from .protocols import Equipable
from funcionalidades.Utility.combat_utils import Hook

STATS = {"vit": 0, "mnd": 1, "int": 2, "str": 3, "lck": 4, "chr": 5, "awe": 6, "agi": 7,"end":8,"dex":9}

class Weapon:
    def __init__(self, name: str, dmg: int, weight=1.0, skills = None, passives = None, owner = None, type: list = ["melee"], twoHand = False, stats = None):
        self.name = name
        self.type = type
        self.owner = owner
        self.dmg = dmg 
        self.base_dmg = dmg
        self.skills = skills or {}
        self.passives = passives or []
        """Format for passives : [(on_equip,eff),(on_hit,a)]"""
        self.weight = weight
        self.twoHand = twoHand
        self.scaling = stats or {"str": 0.4}
        self._registered_hooks = []
        
    def setOwner(self, owner):
        self.owner = owner

    def unEquip(self,ctx):
        self._run_local("on_unequip",ctx)
        self._remove_hooks()
        self.owner = None

    def equip(self, isMod):
        if self.owner: 
            for passive in self.passives:
                if passive[0] in ["on_equip", "on_unequip", "on_hit"]:
                    self._registered_hooks.append((passive[0], Hook(*passive)))
                else:
                    self.owner.hooks.add(passive[0], Hook(*passive, origin=self))

            slot = "primary" if self.twoHand or "secondary" not in self.type else "secondary"

            ctx = {
                "target": self.owner
            }

            if self.owner.weapon[slot]:
                self.owner.weapon[slot].unEquip(ctx)

            self.owner.weapon[slot] = self
            self.owner.weapon[slot]._run_local("on_equip", ctx)

            self.dmg = self.calc_damage(self.base_dmg)

    def useSkill(self, index, target):
        self.skills[index](self,target)
        
    def attack(self, target, ignore: int = 0, cost = 8):
        self.owner.sta -= cost
        dmg = self.calc_damage(self.base_dmg)
        ctx = {
            "attacker": self.owner,
            "target": target,
            "damage": dmg,
            "weapon": self,
        }
        self.owner.hooks.run("on_attack", ctx)
        target.take_damage(dmg, ignore)


    def _softcap(self, stat, cap=40):
        return stat / (stat + cap)

    def calc_damage(self,dmg):
        mult = 1.0

        for stat, scale in self.scaling.items():
            val = self.owner.statBlock[STATS[stat]]
            mult += self._softcap(val) * scale

        return int(dmg * mult)

    def _remove_hooks(self):
        if not self.owner:
            return
        self.owner.hooks.remove(self)
        self._registered_hooks.clear()

    def _run_local(self, hook_name, ctx):
        for name, hook in self._registered_hooks:
            if name == hook_name:
                hook.run(ctx)

class MagicWeapon(Weapon):
    def __init__(self, name, dmg, mgc, weight=1.0, mana_cost=20, skills = None, passives = None, type: list = ["magic"], twoHand = False, stats = None):
        super().__init__(name, dmg, weight=weight,skills=skills, passives=passives, type=type, twoHand=twoHand, stats=stats or {"int": 0.4})
        self.mgc = mgc
        self.base_mgc = mgc
        self.mana_cost = mana_cost

    def equip(self,isMod):
        super().equip(isMod)        
        self.mgc = self.calc_damage(self.base_mgc)

    def attack(self, target, ignore: int = 0):
        if self.owner.mp >= self.mana_cost:
            self.owner.mp -= self.mana_cost
            dmg = self.calc_damage(self.base_mgc)
            target.take_damage(dmg, ignore)

class RangedWeapon(Weapon):
    def __init__(self, name, dmg, ammo: int = 1, ammoReq: int = 1, weight: float = 1.0, skills = None, passives = None, type: list = ["ranged"], twoHand = False, stats = None):
        super().__init__(name, dmg, weight=weight,skills=skills, passives=passives, twoHand=twoHand, stats=stats or {"dex": 0.4})
        self.ammo = ammo
        self.ammoReq = ammoReq
        self.type = type

    def attack(self, target, ignore: int = 0):
        cost = 4*self.weight
        if self.ammo >= self.ammoReq and self.owner.sta >= cost:
            self.ammo -= self.ammoReq
            super().attack(target, ignore, cost)

class SecondaryWeapon(Weapon):
    def __init__(self, name, dmg_red, dmg, weight: float = 1.0, skills = None, passives = None, type: list = ["secondary"],twoHand = False, stats = None):
        super().__init__(name, dmg, weight=weight,skills=skills, passives=passives, type=type, twoHand=twoHand, stats=stats or {"vit": 0.4})
        self.base_red = dmg_red
        self.dmg_red = dmg_red

    def equip(self,isMod):
        super().equip(isMod)
        self.dmg_red = self.calc_damage(self.base_red)


class Item:
    def __init__(self, name, function , uses):
        self.name = name
        self.owner = None
        self.function = function
        self.uses = uses

    def setOwner(self, owner):
        self.owner = owner

    def equip(self, isMod):
        for i in self.owner.items:
            if i.name == self.name:
                i.uses += self.uses
                return
          
        self.owner.items.append(self)

class Armor:
    def __init__(self, name, dmg_red, type: str = "chest", owner = None, skills = None):
        self.name = name
        self.type = type
        self.dmg_red = dmg_red
        self.owner = owner
        self.skills = skills or {}

    def setOwner(self, owner):
        self.owner = owner

    def equip(self, isMod):
        if self.owner: self.owner.armor[self.type] = self