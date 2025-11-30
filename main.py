import pygame, json, random, os, sys, copy
from vault import blacksmith, bl_length, shopItems, enemies, bosses, enemySkills
from funcionalidades import Player, Enemy, Weapon, MagicWeapon, Armor
from funcionalidades import (eventHandling, drawPauseMenu, drawWeaponMenu, drawShopMenu, menuControl, drawScreen, 
                            drawLevelUpMenu, pickNewEnemies, drawRandomEvent, getRandEvent)


def passTurn(partyTurns):
    partyTurns += 1
    if partyTurns >= len(advParty):
        return 0, False  # reinicia turno y termina la ronda
    return partyTurns, True


pygame.init()
display_info = pygame.display.Info()
screen = pygame.display.set_mode((display_info.current_w - 100, display_info.current_h - 50))
colore = (255, 0, 255)
fonts = [pygame.font.SysFont("Arial", 30),pygame.font.SysFont("Arial", 20),pygame.font.SysFont("Arial", 15)]
display = [screen, fonts, colore]

clock = pygame.time.Clock()
running = True
myTurn = True

shiftPressed = False
aPressed = False
ctrlPressed = False
tabPressed = False

enemyCount = 0
enemyList = []
enemyList_serialized = None
enemyList_IsSerialized = False

all_rects = [None, None]

advParty = []
partyTurn = 0

enemy_turn_start = None

# Ruta segura para guardar el archivo de estado
home = os.path.expanduser("~")
app_dir = os.path.join(home, ".mi_juego")
os.makedirs(app_dir, exist_ok=True)  # crea la carpeta si no existe
save_path = os.path.join(app_dir, "SaveState.json")

if not os.path.exists(save_path):
    initial_data = {
        "advParty": [
            {
                "player_hp": 500,
                "player_max_hp": 500,
                "player_mp": 100,
                "player_max_mp": 100,
                "weapon": {},
                "armor": {},
                "items": ["Health Vial"]
            }
        ],
        "level": 0,
        "enemies": []
    }
    with open(save_path, "w") as f:
        json.dump(initial_data, f)

with open(save_path, "r") as f:
    data = json.load(f)

    enemyList = []
    if data.get("enemies"):
        enemyList = [
            Enemy(
                e["name"],
                e["hp"],
                skills={name: enemySkills[name] for name in e.get("skills", []) if name in enemySkills}
            )
            for e in data["enemies"]
        ]

    level = data.get("level", 0)

    for p in data.get("advParty", []):
        weapon_data = p.get("weapon", {})
        weapon_eq = None
        if weapon_data:
            if weapon_data.get("magic_dmg", 0) > 0:
                weapon_eq = MagicWeapon(weapon_data["name"],weapon_data["melee_dmg"],weapon_data["magic_dmg"])
            else:
                weapon_eq = Weapon(weapon_data["name"],weapon_data["melee_dmg"])

        armor_data = p.get("armor", {})
        armor_eq = None
        if armor_data:
            armor_eq = Armor(armor_data["name"],armor_data["dmg_red"])

        player_obj = Player(p["player_hp"],p["player_mp"],max_hp=p.get("player_max_hp", 0),max_mp=p.get("player_max_mp", 0),weapon=weapon_eq,armor=armor_eq)

        if p.get("items"):
            player_items = [item_data[0] for item_data in shopItems if item_data[0].name in p["items"]]
            for it in player_items:
                player_obj.equip_armament(it)
        
        advParty.append(player_obj)

def toggleDict(menu, key):
    menu[key] = not menu[key]

eventList = {"Pause" : False, "Weapons" : False, "Shop" : False, "lvlUp": False, "randEvent": False, "bossLevel": False}
selected_id = 0
lastMenuOpen = {"Shop": [level,True], "Weapons": [level,True]}
lastEvent = {"lvldUp": False, "bossLevel": False, "randEvent": False}
randEvent = None

item_selection = None
state = "menu"

player = advParty[0]

hud_states = {
    "noMagic": ["You have no magic power, and thus cant do a magic attack..."],
    "EnemyTurn": ["Enemy Turn..."],
    "party": "",
    "menu": ["[Shift] Attack", "[A] Magic Attack", "[Ctrl] Use Item"],
    "items": "",
    "attack": ""
}

while running:
    
    partyLenght = len(advParty)

    hud_states["party"] = ["[" + str(i) + "]" + char.name for i,char in enumerate(advParty)]
    hud_states["attack"] = [" [" + str(index+1) + "] - " + enemy.name for index, enemy in enumerate(enemyList)]

    menuOptions = [["Continue", "Quit to Desktop"],["Yes", "No"], item_selection]

    # Events Handling
    eventHandlingArgs = [display, level, myTurn, lastMenuOpen, lastEvent, eventList]
    eventList, lastMenuOpen, lastEvent["bossLevel"] = eventHandling(*eventHandlingArgs)

    # Hud Setup
    drawScreenArgs = [display, hud_states, state, myTurn, advParty, level, lastMenuOpen["Weapons"], enemyList, enemyList_IsSerialized, partyTurn, tabPressed]
    enemyList_serialized, enemyList_IsSerialized, tabPressed = drawScreen(*drawScreenArgs)

    # Safely get events;
    try:
        events = pygame.event.get()
    except Exception:
        # Ensure internal event queue is updated so input still works
        pygame.event.pump()
        events = []

    eventContext = {
        "player": player,
        "enemyList": enemyList,
        "toggleMenu": lambda key: toggleDict(eventList, key),
        "toggleEvent": lambda count: enemyList.insert(0,copy.deepcopy(random.choices(bosses, k=count))) if count != 0 else None
    }

    # Menu Control
    menuControlArgs = [myTurn, events, randEvent, eventContext, state, blacksmith, bl_length, eventList, menuOptions, selected_id, player, advParty, enemyList_serialized, level, lastMenuOpen["Weapons"], lastMenuOpen["Shop"], save_path, running, all_rects]
    selected_id, running, lastMenuOpen["Weapons"][1], lastMenuOpen["Shop"][1], state = menuControl(*menuControlArgs)

    # Game input only when menu is not open
    if not any(eventList.values()): 

        keys = pygame.key.get_pressed()
        inputs = {
            "shift": [keys[pygame.K_LSHIFT], shiftPressed], # "nombre": [isActive, wasPressed]
            "a": [keys[pygame.K_a], aPressed], 
            "ctrl": [keys[pygame.K_LCTRL], ctrlPressed],
            "tab": [keys[pygame.K_TAB], tabPressed]
        }

        # Registrar teclas necesarias según contexto
        max_index = max(len(enemyList), len(player.items))
        for i in range(1, max_index+1):
            key_attr = getattr(pygame, f"K_{i}")
            inputs[str(i)] = keys[key_attr]
            

        if myTurn and partyTurn < len(advParty):
            player = advParty[partyTurn]  # jugador actual
            randEvent, eventList, lastEvent = getRandEvent(eventList,lastEvent,randEvent,player)

            hud_states["items"] = [item.name + " - " + str(item.uses) for item in player.items] if player.items else ["[Empty] - No items"]

            match inputs:
                case {"shift": [active, pressed]} if pressed or active:
                    enemy_keys = {str(i+1): inputs.get(str(i+1), False) for i in range(len(enemyList))}
                    for key, pressed in enemy_keys.items():
                        if pressed:
                            enemy_idx = int(key) - 1
                            player.weapon.melee_attack(enemyList[enemy_idx], False)
                            partyTurn, myTurn = passTurn(partyTurn)
                            state = "menu"
                            shiftPressed = False
                            break
                    if keys[pygame.K_b]:
                        shiftPressed = False
                    if active:
                        shiftPressed = True

                case {"a": [active, pressed]} if pressed or active:
                    if getattr(player.weapon, "magic_dmg", 0) > 0 and player.mp >= 10:
                        enemy_keys = {str(i+1): inputs.get(str(i+1), False) for i in range(len(enemyList))}
                        for key, pressed in enemy_keys.items():
                            if pressed:
                                enemy_idx = int(key) - 1
                                player.weapon.cast_spell(enemyList[enemy_idx])
                                partyTurn, myTurn = passTurn(partyTurn)
                                state = "menu"
                                break
                        if keys[pygame.K_b]:
                            aPressed = False
                        if active:
                            aPressed = True
                    else:
                        state = "noMagic"

                case {"ctrl": [active, pressed]} if pressed or active:
                    item_keys = {str(i+1): inputs.get(str(i+1), False) for i in range(len(player.items))}
                    for key, pressed in item_keys.items():
                        if pressed:
                            key_id = int(key) - 1
                            player.useItem(key_id)
                            ctrlPressed = False
                            partyTurn, myTurn = passTurn(partyTurn)
                            state = "menu"
                            break
                    if keys[pygame.K_b]:
                        ctrlPressed = False
                    if active:
                        ctrlPressed = True
                
                case {"tab": [active, pressed]} if pressed or active:
                    if keys[pygame.K_b]:
                        tabPressed = False
                    if active:
                        tabPressed = True
                    else:
                        tabPressed = False

            if advParty[partyTurn] != player or not myTurn:
                for e in enemyList:
                    for effect in e.stat_effs:
                        effect.passTurn()
                        e.stat_effs = [s for s in e.stat_effs if s.turns != 0]

            
        elif not myTurn:

            for key in lastEvent.keys(): lastEvent[key] = False
            state = "EnemyTurn"

            if enemy_turn_start is None:
                enemy_turn_start = pygame.time.get_ticks()  # registramos cuándo empezó el turno enemigo

            # Si pasaron 1 segundo (1000 ms)
            if pygame.time.get_ticks() - enemy_turn_start > 1000:

                for _player in advParty:
                    for effect in _player.stat_effs:  
                        effect.passTurn()
                        print(effect.turns)
                        _player.stat_effs = [e for e in _player.stat_effs if e.turns > 0]
                
                for enemy in enemyList:
                    target = random.choice(advParty)
                    outcome = random.randint(0,3)
                    if outcome == 3:
                        skill_names = list(enemy.skills.keys())
                        if skill_names != []: 
                            skill_name = random.choice(skill_names)
                            context = {
                                "self": enemy,
                                "main_player": target,
                                "advParty": advParty,
                                "enemyList": enemyList
                            }
                            enemy.skills[skill_name](**context)
                            print(f"{enemy.name} uses {skill_name}!")
                    else:
                        enemy.attack(target, False)    
                        print(f"{enemy.name} attacks! {enemy.dmg} {target.armor.dmg_red} {enemy.dmg*target.armor.dmg_red}")

                    for attr, ote_list in enemy.hooks.items():
                        for ote in ote_list: ote.passTurn()
                        enemy.hooks = {attr: [ote for ote in ote_list if ote.turns != 0]for attr, ote_list in enemy.hooks.items()}

                print("-----------------------------")
                myTurn = True
                state = "menu"
                enemy_turn_start = None  # reiniciamos el temporizador

                
                for player in advParty:
                    for attr, ote_list in player.hooks.items():
                        for ote in ote_list: ote.passTurn()
                        player.hooks = {attr: [ote for ote in ote_list if ote.turns != 0]for attr, ote_list in player.hooks.items()}
        
        if enemyList:
            for enemy in enemyList:  
                if enemy.hp <= 0:
                    if enemy.tameable:
                        tame_chance = random.randint(0,5)
                        if tame_chance == 5: advParty.append(Player(enemy.base_hp,0, name=enemy.name))
                    enemyList = [e for e in enemyList if e.hp > 0]
                    player.gold_reward(enemy.reward)
                    eventList["lvldUp"] = player.gainXP(enemy.reward, eventList["lvldUp"])
                    lastEvent["lvlUp"] = eventList["lvldUp"]
                    break   
        else:
            level += 1
            enemyList = pickNewEnemies(random.randint(1,3), enemyList, enemies, bosses, level, lastEvent["bossLevel"])
            for enemy in enemyList:
                enemy.hp = enemy.base_hp + level
    else:
        match eventList:
            case {"Pause": True}:
                drawPauseMenu(display, menuOptions[0], selected_id)
            case {"Weapons": True}:
                drawWeaponMenu(display, menuOptions[1], selected_id)
            case {"Shop": True}:
                item_selection, all_rects[1] = drawShopMenu(display, shopItems, item_selection, selected_id)
            case {"lvlUp": True}:  
                all_rects[0] = drawLevelUpMenu(display, player, menuOptions[0], selected_id)
            case {"randEvent": True}:  
                drawRandomEvent(display, randEvent, selected_id)

    pygame.display.flip()
    clock.tick(120)

    advParty = [p for p in advParty if p._hp > 0]

    if advParty == []:
        print("El juego ha terminado: el jugador perdió.")
        running = False