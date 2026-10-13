import random, copy
from vault.enemies import enemies, bosses
from vault.items import shopItems, itemPools
from vault.gear import blacksmith
from vault.events import events
from funcionalidades.core.AI import EnemyAi, Attack, UseSkill
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

    @property
    def progress(self):
        return (self.floor - 1) + self.room / self.max_rooms

    def _init_floor_layout(self, floor):
        layout = random.choices(MAIN_ROOMS,k=ROOMS_PER_FLOOR,weights=MAIN_ODDS)

        for i,room in enumerate(layout):
            if room == "extra":
                layout[i] = "extra_" + random.choices(EXTRA_ROOMS, k=1, weights=EXTRA_ODDS)[0]

        if floor % 10 == 0:
            layout.append("elite")
        else: layout.append("shop")

        layout.insert(1,"shop")
        
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
        self.turn = 0
        self.enemies = enemiess if enemiess != [] else self._generate_enemies(random.randint(1,3), enemies, bosses, room, floor, active_floor)
        self.order = self.party + self.enemies
        self.notify = notiFunc
        self.visual_trigger = visualCallback

        if self.order[self.turn].hp <= 0:
            self.next_turn()
   
    @property
    def my_turn(self):
        return self.order[self.turn] in self.party

    def _generate_enemies(self, count, enemiess, bosses, level, floor, activeFloor):
        enemyList = [copy.deepcopy(enemy) for enemy in random.choices(enemiess, k=count)]
        for i, enemy in enumerate(enemyList):
            enemy.hp = enemy.base_hp + (level * floor)/2

        if activeFloor == "elite":
            boss_count = random.choices([1, 2], weights=[90, 10], k=1)[0]
            bosses_picked = [copy.deepcopy(b) for b in random.choices(bosses, k=boss_count)]
            enemyList.extend(bosses_picked)

        return enemyList

    def next_turn(self):
        status = self._update()
        
        if status != "CONTINUE":
            return status

        while True:
            self.turn = (self.turn + 1) % len(self.order)
            if self.order[self.turn].hp > 0:
                return "CONTINUE"

    def enemy_turn(self):
        if self.my_turn:
            return "CONTINUE"

        status = self._update()
        if status != "CONTINUE":
            return status

        enemy = self.order[self.turn]
        if not hasattr(enemy, "ai") or enemy.ai is None:
            enemy.ai = EnemyAi(
                [UseSkill(skill) for skill in enemy.skills] + [Attack()],
                enemy.personality if hasattr(enemy, "personality") else None
            )

        allies = [e for e in self.enemies if e is not enemy and e.hp > 0]
        targets = [p for p in self.party if p.hp > 0]

        action, target = enemy.ai.choose_action(enemy, allies, targets)

        if action and target:
            hp_antes = target.hp
            action.execute(enemy, allies, targets, target)
            danio_real = hp_antes - target.hp

            if self.notify:
                accion = f"used {action.name} on" if hasattr(action, "name") else "attacked"
                self.notify(f"{enemy.name} {accion} {target.name}!", 1.5)

            if self.visual_trigger and danio_real > 0:
                self.visual_trigger(target, int(danio_real))

        return self.next_turn()

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

        if self.visual_trigger and danio_real > 0:
            self.visual_trigger(target, int(danio_real))

        if target.hp <= 0:
            caster.gold_reward(target.reward)
            caster.gainXP(target.reward)

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
            finalDmg = caster.statBlock[2] + spell.effect.get("baseDmg", 0) + spell.effects.get("bonusDmg",0)
            
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

    def usar_item(self, caster, target, item_index):
        item = caster.items[item_index]
        
        item.function(item)
        
        item.uses -= 1
        if item.uses <= 0:
            del caster.items[item_index]

        if self.notify:
            self.notify(f"¡{caster.name} usó {item.name}!", 1.5)

        status = self._update()
        if status == "CONTINUE" and caster in self.party:
            self.next_turn()

        return status


class shopManager:

    def __init__(self, party, visualCallback = None):
        self.party = party
        self._generate_item_pool(shopItems)
        self.visual_trigger = visualCallback
        self.active_shopper = None
    
    def set_active_shopper(self, index):
        if 0 <= index < len(self.party):
            self.active_shopper = self.party[index]
            return True
        return False

    def _generate_item_pool(self, possible_items):

        options = list(range(2, 11))
        weights = [5, 10, 30, 40, 30, 10, 5, 2, 1]
        amount = random.choices(options, k=1, weights=weights)[0]

        item_pool = []
        for i in range(amount):
            rarity = random.choices([0, 1, 2, 3], k=1, weights=[50, 25, 10, 5])[0]
            item_pool.append(random.choice(possible_items[rarity]))

            if random.randint(1, 20) == 20:
                item_pool.append(random.choice(possible_items[rarity]))

        self.shop_items = item_pool

    def process_purchase(self, item):
        if not self.active_shopper:
            return None

        if self.active_shopper.gd >= item[1]: 
            self.active_shopper.gold_remove(item[1])
            self.active_shopper.equip_armament(copy.deepcopy(item[0]), False)
            self.shop_items.remove(item)
            if self.visual_trigger:
                self.visual_trigger(self.active_shopper, item[1])
            return -item[1]

        if self.visual_trigger:
            self.visual_trigger(self.active_shopper, "not enough gold")
        return None

class chestManager:

    def __init__(self, party, visualCallback = None):
        self.party = party
        self.items = self._generateItemPool(itemPools)
        self.visual_trigger = visualCallback
        self.active_shopper = None

    def _generateItemPool(self, possibleItems):

        itemPool = []

        amount = random.choices([1,2,3,4],k=1,weights=[40,40,15,5])[0]
        for i in range(amount):
            rarity = random.choices([0,1,2,3],k=1,weights=[500, 25, 10, 5])[0]

            itemPool.append(random.choice(possibleItems[rarity]))

            if random.randint(1,20) == 20:
                itemPool.append(random.choice(possibleItems[rarity]))

        return itemPool

    def set_active_player(self, index):
        if 0 <= index < len(self.party):
            self.active_shopper = self.party[index]
            return True
        return False

    def open_chest(self, member, item):
        self.items.remove(item)
        member.equip_armament(copy.deepcopy(item), False)
        if self.visual_trigger:
            self.visual_trigger(member, item.name)


class eventManager:
    def __init__(self, party, progress, room, addRoom):
        self.party = party
        self.event = self.gen_event()
        self.active_player = None
        self.progress = progress
        self.addRoom = addRoom
        self.nroom = room + 1

    def set_active_player(self, index):
        if 0 <= index < len(self.party):
            self.active_player = self.party[index]
            return True
        return False

    def run_event(self, selected_index):
        context = {"player": self.active_player, "nroom":self.nroom, "addRoom": self.addRoom}
        action = list(self.event.actions.keys())[selected_index]
        self.event.resolve(action, context)
        self.event = None

    def gen_event(self):
        return random.choice(events)