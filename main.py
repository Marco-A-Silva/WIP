import pygame, json, random, os, sys, copy, time
from vault import blacksmith, bl_length, shopItems, enemies, bosses, enemySkills, magicSkills, meleeSkills
from funcionalidades import Player, Enemy, Weapon, MagicWeapon, Armor
from funcionalidades import (eventHandling, drawPauseMenu, drawWeaponMenu, drawShopMenu, menuControl, drawScreen, 
                            drawLevelUpMenu, pickNewEnemies, drawRandomEvent, getRandEvent)


def passTurn(partyTurns):
    partyTurns += 1
    if partyTurns >= len(advParty):
        return 0, False  # reinicia turno y termina la ronda
    return partyTurns, True

def drawNotification(display, notification, y_offset=0):
    if time.time() > notification["expires"]:
        return

    font = display[1][1]
    rendered = font.render(notification["text"], True, (255, 255, 255))
    text_rect = rendered.get_rect(center=(display[0].get_width() // 2, 50 + y_offset))

    padding_x = 15
    padding_y = 8
    box_rect = pygame.Rect(
        text_rect.x - padding_x,
        text_rect.y - padding_y,
        text_rect.width + padding_x*2,
        text_rect.height + padding_y*2
    )

    pygame.draw.rect(display[0], (50,50,50), box_rect, border_radius=10)
    pygame.draw.rect(display[0], (200,200,255), box_rect, 2, border_radius=10)
    display[0].blit(rendered, text_rect)

def addNotification(text, duration=2):
    notifications.append({"text": text, "expires": time.time() + duration})


pygame.init()
display_info = pygame.display.Info()
screen = pygame.display.set_mode((display_info.current_w - 100, display_info.current_h - 50))
colore = (255, 0, 255)
fonts = [pygame.font.SysFont("Arial", 30),pygame.font.SysFont("Arial", 20),pygame.font.SysFont("Arial", 15)]
display = [screen, fonts, colore]

clock = pygame.time.Clock()
running = False
myTurn = True

isFirstRun = False

shiftPressed = False
aPressed = False
rPressed = False
sPressed = False
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
    isFirstRun = True
    initial_data = {
        "level": 0,
        "advParty": [
            {
                "player_hp": 500,
                "player_max_hp": 500,
                "player_mp": 100,
                "player_max_mp": 100,
                "player_sta": 60,
                "player_max_sta":60,
                "player_statBlock": [10 for i in range(10)],
                "weapon": {},
                "armor": {},
                "items": ["Health Vial"]
            }
        ],
        "enemies": []
    }
    with open(save_path, "w") as f:
        json.dump(initial_data, f, indent=4)

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
                weapon_eq.skills = {key: magicSkills[key] for key in weapon_data["skills"]}
            else:
                weapon_eq = Weapon(weapon_data["name"],weapon_data["melee_dmg"])
                weapon_eq.skills = {key: meleeSkills[key] for key in weapon_data["skills"]}

        armor_data = p.get("armor", {})
        armor_eq = None
        if armor_data:
            armor_eq = Armor(armor_data["name"],armor_data["dmg_red"])

        player_obj = Player(isFirstRun,p["player_hp"],p["player_mp"],p["player_sta"], max_sta=p.get("player_max_sta",0),max_hp=p.get("player_max_hp", 0),max_mp=p.get("player_max_mp", 0),weapon=weapon_eq,armor=armor_eq,statBlock=p["player_statBlock"])

        if p.get("items"):
            player_items = [item_data[0] for item_data in shopItems if item_data[0].name in p["items"]]
            for it in player_items:
                player_obj.equip_armament(it, False)
        
        advParty.append(player_obj)

def toggleDict(menu, key):
    menu[key] = not menu[key]

eventList = {"Pause" : False, "Weapons" : False, "Shop" : False, "lvlUp": False, "randEvent": False, "bossLevel": False}
selected_id = 0
lastMenuOpen = {"Shop": [level,True], "Weapons": [level,True]}
lastEvent = {"lvldUp": False, "bossLevel": False, "randEvent": False}
notifications = []
randEvent = None

item_selection = None

hudState = "menu"

gameState = "chooseAction"

player = advParty[0]

hud_states = {
    "noMagic": ["You have", "no magic power,", "and thus cant do a", "magic attack..."],
    "EnemyTurn": ["Enemy Turn..."],
    "party": "",
    "items": "",
    "attack": ""
}

targetArrow = 0


while running:

    partyLenght = len(advParty)

    hud_states["menu"] = ["Menu","[Shift] Attack", "[S] Skills", "[A] Magic Attack", "[Ctrl] Use Item", "[R] Rest"]
    hud_states["party"] = [f"[{i+1}] {char.name}" for i, char in enumerate(advParty)]
    hud_states["attack"] = ["Attack"] + [f"{index+1} - {enemy.name}" for index, enemy in enumerate(enemyList)]
    hud_states["skills"] = ["Skills"] + ([f"{i+1} - {key}" for i, key in enumerate(player.weapon.skills.keys())] if player.weapon.skills else ["[Empty] - No skills"])


    menuOptions = [["Continue", "Quit to Desktop"],["Yes", "No"], item_selection, randEvent.actions if randEvent else ""]

    # Events Handling
    eventHandlingArgs = [display, level, myTurn, lastMenuOpen, lastEvent, eventList]
    eventList, lastMenuOpen, lastEvent["bossLevel"] = eventHandling(*eventHandlingArgs)

    # Hud Setup
    drawScreenArgs = [display, hud_states, hudState, myTurn, advParty, level, lastMenuOpen["Weapons"], enemyList, enemyList_IsSerialized, partyTurn, tabPressed, targetArrow]
    enemyList_serialized, enemyList_IsSerialized, tabPressed = drawScreen(*drawScreenArgs)

    y_offset = 0
    for n in notifications:
        drawNotification(display, n, y_offset)
        y_offset += 50  # o lo que quieras

    notifications = [n for n in notifications if time.time() <= n["expires"]]


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
        "addBoss": lambda count: [enemyList.insert(0, copy.deepcopy(e)) for e in reversed(random.choices(bosses, k=count))],
        "addNotification": lambda key: addNotification(key, 2)
    }

    # Menu Control
    menuControlArgs = [myTurn, events, randEvent, eventContext, hudState, blacksmith, bl_length, eventList, menuOptions, 
                        selected_id, player, advParty, enemyList_serialized, level, lastMenuOpen["Weapons"], lastMenuOpen["Shop"], 
                        save_path, running, all_rects, targetArrow, len(enemyList)-1]
    selected_id, running, lastMenuOpen["Weapons"][1], lastMenuOpen["Shop"][1], hudState, targetArrow = menuControl(*menuControlArgs)

    # Game input only when menu is not open
    if not any(eventList.values()): 

        keys = pygame.key.get_pressed()
        inputs = {
            "shift": [keys[pygame.K_LSHIFT], shiftPressed], # "nombre": [isActive, wasPressed]
            "a": [keys[pygame.K_a], aPressed], 
            "s": [keys[pygame.K_s], sPressed], 
            "r": [keys[pygame.K_r], rPressed], 
            "ctrl": [keys[pygame.K_LCTRL], ctrlPressed],
            "tab": [keys[pygame.K_TAB], tabPressed]
        }

        # Registrar teclas necesarias según contexto
        max_index = max(len(enemyList), len(player.items), partyLenght)
        for i in range(1, max_index+1):
            key_attr = getattr(pygame, f"K_{i}")
            inputs[str(i)] = keys[key_attr]
            

        if myTurn:
            player = advParty[partyTurn]  # jugador actual
            randEvent, eventList, lastEvent = getRandEvent(eventList,lastEvent,randEvent,player)

            hud_states["items"] = ["Items"] + [f"[{i+1}] {item.name} - {item.uses}" for i,item in enumerate(player.items)] if player.items else ["[Empty] - No items"]
            
            match inputs:
                case {"shift": [active, pressed]} if pressed or active:

                    enemy_keys = {str(i+1): inputs.get(str(i+1), False) for i in range(len(enemyList))}
                    for key, pressed in enemy_keys.items():
                        if pressed:
                            enemy_idx = int(key) - 1
                            player.weapon.melee_attack(enemyList[enemy_idx], False)
                            partyTurn, myTurn = passTurn(partyTurn)
                            hudState = "menu"
                            shiftPressed = False
                            break
                    if keys[pygame.K_b]:
                        shiftPressed = False
                    if active:
                        shiftPressed = True
                
                case {"s": [active, pressed]} if pressed or active:

                    skill_keys = {str(i+1): inputs.get(str(i+1), False) for i in range(len(player.weapon.skills))}
                    for key, pressed in skill_keys.items():
                        if pressed:
                            skill_idx = int(key) - 1
                            key = list(player.weapon.skills.keys())[skill_idx]
                            player.weapon.skills[key](player,enemyList[targetArrow])
                            hudState = "menu"
                            sPressed = False
                            break
                    if keys[pygame.K_b]:
                        sPressed = False
                    if active:
                        sPressed = True

                case {"a": [active, pressed]} if pressed or active:

                    if getattr(player.weapon, "magic_dmg", 0) > 0 and player.mp >= 10:
                        enemy_keys = {str(i+1): inputs.get(str(i+1), False) for i in range(len(enemyList))}
                        for key, pressed in enemy_keys.items():
                            if pressed:
                                enemy_idx = int(key) - 1
                                player.weapon.cast_spell(enemyList[enemy_idx])
                                partyTurn, myTurn = passTurn(partyTurn)
                                hudState = "menu"
                                break
                        if keys[pygame.K_b]:
                            aPressed = False
                        if active:
                            aPressed = True
                    else:
                        hudState = "noMagic"

                case {"ctrl": [active, pressed]} if pressed or active:
                    
                    item_keys = {str(i+1): inputs.get(str(i+1), False) for i in range(len(player.items))}
                    for key, pressed in item_keys.items():
                        if pressed:
                            key_id = int(key) - 1
                            player.useItem(key_id) 
                            ctrlPressed = False
                            partyTurn, myTurn = passTurn(partyTurn)
                            hudState = "menu"
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
                
                case {"r": [active, pressed]} if pressed or active:
                    
                    if keys[pygame.K_b]:
                        tabPressed = False
                    player.sta += round(player.max_sta*0.15)
                    partyTurn, myTurn = passTurn(partyTurn)
                    hudState = "menu"

            if advParty[partyTurn] != player or not myTurn:
                for e in enemyList:
                    for effect in e.stat_effs:
                        effect.passTurn()
                        e.stat_effs = [s for s in e.stat_effs if s.turns != 0]

            
        elif not myTurn:
            
            targetArrow = 0
            for key in lastEvent.keys(): lastEvent[key] = False
            hudState = "EnemyTurn"

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
                            addNotification(f"{enemy.name} uses {skill_name}!",2)
                            print(f"{enemy.name} uses {skill_name}!")
                    else:
                        enemy.attack(target, False)    
                        addNotification(f"{enemy.name} attacks, dealing {enemy.dmg}dmg!",2)
                        print(f"{enemy.name} attacks! {enemy.dmg} {target.armor.dmg_red} {enemy.dmg*target.armor.dmg_red}")

                    for attr, ote_list in enemy.hooks.items():
                        for ote in ote_list: ote.passTurn()
                        enemy.hooks = {attr: [ote for ote in ote_list if ote.turns != 0]for attr, ote_list in enemy.hooks.items()}

                print("-----------------------------")
                myTurn = True
                hudState = "menu"
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
                    eventList["lvlUp"] = player.gainXP(enemy.reward, eventList["lvlUp"])
                    lastEvent["lvldUp"] = eventList["lvlUp"]
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
                all_rects[0] = drawLevelUpMenu(display, player, selected_id)
            case {"randEvent": True}:  
                drawRandomEvent(display, randEvent, selected_id)

    pygame.display.flip()
    clock.tick(120)

    advParty = [p for p in advParty if p._hp > 0]

    if advParty == []:
        print("El juego ha terminado: el jugador perdió.")

        if os.path.exists(save_path):
            os.remove(save_path)

        running = False


