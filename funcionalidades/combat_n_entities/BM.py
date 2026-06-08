from .entities import Enemy

class BattleManager:
    
    def __init__(self, party, enemies, notiFunc=None):
        self.party = party
        self.enemies = enemies
        self.notify = add_notiFunc

    def _update(self):
        self.enemies[:] = [e for e in self.enemies if e.hp > 0]
        self.party[:] = [p for p in self.party if p.hp > 0]
        
        if not self.party:
            return "GAME_OVER"
        if not self.enemies:
            return "VICTORY"
            
        return "CONTINUE"

    def melee(self, caster, weapon, target, ignore=False):
        weapon.attack(target, ignore)
        if self.notify:
            self.notify(f"{caster.name} attacked {target.name}!", 1.5)
        return self._update()
    
    def cast(self, caster, weapon, spell, target = None):
        side = "enemies" if target in self.enemies else "party"

        if self.notify:
                self.notify(f"¡{caster.name} castea {spell.name}!", 1.5)

        targets = []
        match spell.effects:
            case {"aoe": True}:
                targets = [x for x in getattr(self, side) if x.hp > 0]
            case {"chain": c} if c > 0:
                targets.append(target)
                otros = [x for x in getattr(self, side) if x != target and x.hp > 0]
                targets.extend(otros[:c])
            case _:
                targets.append(target)

        for tar in targets:
            finalDmg = caster.statBlock[2]*1.5 + spell.effect.get("baseDmg", 0) + spell.effects.get("bonusDmg",0)
            

        return self._update()