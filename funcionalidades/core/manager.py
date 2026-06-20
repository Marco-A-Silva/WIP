import random
from vault.enemies import enemies, bosses
from funcionalidades.combat_n_entities.entities import Enemy

MAIN_ROOMS = ["fight","chest","shop","event","extra"]
MAIN_ODDS = [55,12,6,22,5]
EXTRA_ROOMS = ["dojo","rest site","school of magic"]
EXTRA_ODDS = [1,3,1]

ROOMS_PER_FLOOR = 9

class gameManager:
    def __init__(self, room=0, floor=1, floor_layout=None):
        self.room = room
        self.floor = floor

        if floor_layout is None:
            self._init_floor_layout(self.floor)
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

        layout.insert(1, "shop")
        
        self.max_rooms = len(layout)
        self.floor_layout = layout


    def load_new_room(self):
        self.room += 1
        if self.room >= self.max_rooms:
            self.floor += 1
            self._init_floor_layout(self.floor)
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
    
    def __init__(self, party, enemiess, my_turn, room, floor, active_floor, notiFunc=None, visualCallback = None):
        self.party = party
        self.my_turn = my_turn
        self.party_turn = 0
        self.enemies = enemiess if enemiess != [] else self._generate_enemies(random.randint(1,3), enemies, bosses, room, floor, active_floor)
        self.notify = notiFunc
        self.trigger_visual = visualCallback

    def _generate_enemies(self, count, enemiess, bosses, level, floor, activeFloor):

        enemyList = [copy.deepcopy(enemy) for enemy in random.choices(enemiess, k=count)]
        for i, enemy in enumerate(enemyList):
            enemy.hp = enemy.base_hp + (level * floor)/2

        if activeFloor == "elite":
            boss_count = random.choices([1, 2], weights=[90, 10], k=1)[0]
            bosses_picked = random.choices(bosses, k=boss_count)
            enemyList.extend(bosses_picked)

        return enemyList

    def next_turn(self):
        if not any(p.hp > 0 for p in self.party):
            return

        while True:
            self.party_turn += 1
            if self.party_turn >= len(self.party):
                self.party_turn = 0
            
            if self.party[self.party_turn].hp > 0:
                break

    def _update(self):

        if all(p.hp <= 0 for p in self.party):
            return "GAME_OVER"
        
        if all(e.hp <= 0 for e in self.enemies):
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

        status = self._update()
        
        if status == "CONTINUE" and caster in self.party:
            self.next_turn()

        return status
    
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

        status = self._update()
        
        if status == "CONTINUE" and caster in self.party:
            self.next_turn()

        return status


class shopManager:

    def __init__(self, party, shop_items, visualCallback = None):
        pass