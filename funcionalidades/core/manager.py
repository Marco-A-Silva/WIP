import random
from funcionalidades.combat_n_entities.entities import Enemy

class gameManager:
    def __init__(self, room=0, floor=1, floor_layout=None):
        self.room = room
        self.floor = floor

        if floor_layout is None:
            self.floor_layout = self._init_floor_layout(self.floor)
        else:
            self.floor_layout = floor_layout
            self.max_rooms = len(self.floor_layout)
            
        self.active_floor = self.floor_layout[self.room]

    def _init_floor_layout(self, floor):
        layout = random.choices(MAIN_ROOMS,k=ROOMS_PER_FLOOR,weights=MAIN_ODDS)

        for i,room in enumerate(layout):
            if room == "extra":
                layout[i] = "extra_" + random.choices(EXTRA_ROOMS, k=1, weights=EXTRA_ODDS)[0]

        if floor % 10 == 0:
            layout.append("elite")
        else: layout.append("shop")
        
        self.max_rooms = len(layout)

    def load_new_room(self):
        self.room += 1
        if self.room >= self.max_rooms:
            self.floor += 1
            self.floor_layout = self._init_floor_layout(self.floor)
            self.room = 0
            
        self.active_floor = self.floor_layout[self.room]

    def add_room(self, key, i):
        self.floor_layout.insert(i, key)
        self.max_rooms += 1

    def rm_room(self, key):
        if key in self.floor_layout:
            self.floor_layout.remove(key)
            self.max_rooms -= 1

    def rm_rooms(self, key):
        self.floor_layout = [r for r in self.floor_layout if r != key]
        self.max_rooms = len(self.floor_layout)

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