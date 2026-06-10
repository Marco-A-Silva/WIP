from funcionalidades.combat_n_entities.entities import Enemy

class combatManager:
    
    def __init__(self, party, enemies, notiFunc=None, visualCallback = None):
        self.party = party
        self.enemies = enemies
        self.notify = notiFunc
        self.trigger_visual = visualCallback

    def _update(self):
        self.enemies[:] = [e for e in self.enemies if e.hp > 0]
        self.party[:] = [p for p in self.party if p.hp > 0]
        
        if not self.party:
            return "GAME_OVER"
        if not self.enemies:
            return "VICTORY"
            
        return "CONTINUE"

    def melee(self, caster, weapon, target, ignore=0):

        hp_antes = target.hp
        weapon.attack(target, ignore)
        danio_real = hp_antes - target.hp

        if self.notify:
            self.notify(f"{caster.name} attacked {target.name}!", 1.5)

        if self.trigger_visual and danio_real > 0:
            self.trigger_visual(target, int(danio_real))

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
            
        if spell.effects.get("poison", False):
            return
        
        if spell.effects.get("stun", True):
            return
        
        if spell.effects.get("lifesteal", False):
            return

        return self._update()