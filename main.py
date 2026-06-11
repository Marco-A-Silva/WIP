import pygame, json, random, os, sys, time
from pytmx.util_pygame import load_pygame
from funcionalidades import combatState

from funcionalidades import combatState, combatManager, combatRenderer
from funcionalidades import gameManager, gameRenderer, gameState

#Import drawing functions
from funcionalidades import drawPauseMenu, drawShopMenu, drawScreen, drawChestMenu, drawRandomEvent, drawLayout, drawLevelUpMenu, drawEventMenu, drawExtraMenu, drawHub, drawNotifications

#Import control functions
from funcionalidades import menuControl, gameStateChange, shopControl, eventControl, extraControl, treasureControl, loadNewRoom, addRoom, removeRoom

#Import blueprints
from vault import blacksmith, bl_length, shopItems, enemies, bosses, enemySkills, magicSkills, meleeSkills, itemPools, staticEvents, shopSmith

#Import generator functions
from vault import generateItemPool
from funcionalidades import getRandEvent, getCollisions, initializeFloorLayout, addNotification, pickNewEnemies
from funcionalidades.Utility.saving_loading import create_initial_save, load_game_state

#Import important classes
from funcionalidades import Player, Enemy, Weapon, MagicWeapon, RangedWeapon, SecondaryWeapon, Armor, Item, EnemyAi, Attack, UseSkill
 
def passTurn(partyTurns, Party):
    partyTurns += 1
    if partyTurns >= len(Party):
        return 0, False  # reinicia turno y termina la ronda
    return partyTurns, True

def toggleDict(menu, key):
    menu[key] = not menu[key]


#Initialization of screen, save path, lib and important utils
pygame.init()
display_info = pygame.display.Info()

VIRTUAL_W = 20 * 32 # 640
VIRTUAL_H = 15 * 32  # 480

hub_surface = pygame.Surface((VIRTUAL_W, VIRTUAL_H))
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.NOFRAME)

colore = (255, 0, 255)
fonts = [pygame.font.SysFont("Arial", 30),pygame.font.SysFont("Arial", 20),pygame.font.SysFont("Arial", 15)]
display = [screen, fonts, colore]
clock = pygame.time.Clock()

# Ruta segura para guardar el archivo de estado
home = os.path.expanduser("~")
app_dir = os.path.join(home, ".mi_juego")
os.makedirs(app_dir, exist_ok=True)  # crea la carpeta si no existe
save_path = os.path.join(app_dir, "SaveState.json")

#-----------------------------------------------------------------------------------------------------------

#Initialization of hud related elements
actionStates = {
    "": "",
    "Attack":"[Shift] Attack",
    "Magicly Attack": "[A] Magic Attack",
    "Choose Skill": "[S] Skills",
    "Choose Item": "[Ctrl] Inventory"
}
menuStates = ["Menu","[Shift] Attack", "[S] Skills", "[A] Magic Attack", "[Ctrl] Inventory", "[R] Rest"]
hudOptions = {
    "noMagic": ["You have", "no magic power,", "and thus cant do a", "magic attack..."],
    "EnemyTurn": ["Enemy Turn..."],
    "party": "",
    "items": "",
    "targetSel": ""
}

room = 0
maxRoom = 10
floor = 1
visual_level = room

all_rects = [None, None]

eventList = {"pause" : False, "chest" : False, "shop" : False, "event": False, "extra": False, "randEvent": False, "bossLevel": False, "lvlUp": False}
selected_id = 0
lastEvent = {"lvldUp": False, "bossLevel": False, "randEvent": False}
notifications = []
randEvent = None

#-----------------------------------------------------------------------------------------------------------

#Initialization of floor related elements

floorLayout = initializeFloorLayout(floor)
activeFloor = ""
floorLoaded = False

extraOptions = [["sleep","guard","eat"],["delve in the intricacies of magic","leave"],["train","leave"]]
shopPool = None
chestPool = None
staticEvent = None
item_selection = ""

#-----------------------------------------------------------------------------------------------------------

#Initialization of player character related elements

player = None
advParty = []
partyTurn = 0

classSelected = 0
races = ["Eudrýan","Arcanthian","Thanoran","Ünds","Apexian","Brumed","Thanoran","Thalûnd","Skŷnder","Ferravan","Vitalean","Noctyrrn"]

player_img = pygame.Surface((32, 48), pygame.SRCALPHA)
player_img.fill((220, 40, 40))  # rojo

player_rect = player_img.get_rect()
player_rect.midbottom = (200, 200)  # coordenadas de MUNDO

cam_x = player_rect.centerx - screen.get_width() // 2
cam_y = player_rect.centery - screen.get_height() // 2

weaponUsed = None

#-----------------------------------------------------------------------------------------------------------

#Initialization of hub related elements

world = "Unden"
tmx_data = None
collision_layer = None
collision_rects = None

#-----------------------------------------------------------------------------------------------------------

#Initialization of Game Loop related elements

transition_alpha = 0
transition_speed = 10   # más alto = más rápido

startSelected = 0

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

pending_levels = 0

menuState = "menu"
appState = "start" #start/hub
gameState = "chooseAction"

action = ""
actionArgs = {}
playerAction = None
playerTargets = ""
playerUsables = ""

mouse_hidden = False
input_lock = False 

myTurn = True
enemy_turn_start = None
running = True
instance = gameState(display, advParty)
#-----------------------------------------------------------------------------------------------------------

while running:

    maxRoom = len(floorLayout)

    if appState == "hub":
        if not mouse_hidden:
            pygame.mouse.set_visible(False)
            mouse_hidden = True
    else:
        if mouse_hidden:
            pygame.mouse.set_visible(True)
            mouse_hidden = False


    for key in ["shop","chest","event","extra"]:
        eventList[key] = True if key in activeFloor else False

    try:
        events = pygame.event.get()
    except Exception:
        pygame.event.pump()
        events = []

    match appState:

        case "eventTransition":
            overlay = pygame.Surface(screen.get_size())
            overlay.fill((0,0,0))
            overlay.set_alpha(transition_alpha)
            screen.blit(overlay, (0,0))
            transition_alpha += transition_speed
            drawNotifications(display)

            if transition_alpha >= 800:
                appState = "game"
                transition_alpha = 0
                visual_level = room

        case "roomTransition":
            overlay = pygame.Surface(screen.get_size())
            overlay.fill((0,0,0))
            overlay.set_alpha(transition_alpha)
            screen.blit(overlay, (0,0))
            transition_alpha += transition_speed

            if transition_alpha >= 255:
                appState = "game"
                transition_alpha = 0
                visual_level = room

        case "transition":
            overlay = pygame.Surface(screen.get_size())
            overlay.fill((0,0,0))
            overlay.set_alpha(transition_alpha)
            screen.blit(overlay, (0,0))
            transition_alpha += transition_speed

            if transition_alpha >= 255:
                partida_party, enemyList, room, activeFloor, visual_level = load_game_state(save_path, floorLayout)
                advParty[:] = partida_party
                player = advParty[0]
                appState = "game"
                transition_alpha = 0

        case "hubTransition":
            overlay = pygame.Surface(screen.get_size())
            overlay.fill((0,0,0))
            overlay.set_alpha(transition_alpha)
            screen.blit(overlay, (0,0))
            transition_alpha += transition_speed

            if transition_alpha >= 255:
                partida_party, enemyList, room, activeFloor, visual_level = load_game_state(save_path, floorLayout)
                advParty[:] = partida_party
                player = advParty[0]
                appState = "hub"
                transition_alpha = 0

        case "classSelect":
            screen.fill((10,10,15))
            title = fonts[0].render("Choose Your Class", True, (240,240,255))
            screen.blit(title, title.get_rect(center=(640, 200)))

            for i, c in enumerate(races):
                y = 320 + i*60
                if i == classSelected:
                    pygame.draw.rect(screen, (200,200,255), pygame.Rect(500, y-20, 280, 40), 2)
                t = fonts[1].render(c, True, (255,255,255))
                screen.blit(t, t.get_rect(center=(640, y)))

            for e in events:
                if e.type == pygame.KEYDOWN:
                    if e.key in (pygame.K_w, pygame.K_UP):
                        classSelected = (classSelected - 1) % len(races)
                    if e.key in (pygame.K_s, pygame.K_DOWN):
                        classSelected = (classSelected + 1) % len(races)
                    if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        create_initial_save(races[classSelected], save_path)
                        transition_alpha = 0
                        appState = "hubTransition"

        case "quit":
            running = False

        case "start":
            screen.fill((10,10,15))
            center_x = (display[0].get_width() // 2)
            center_y = (display[0].get_height() // 2) 

            opts = ["Start Game", "Quit"]
            for i, o in enumerate(opts):
                y = center_y - 50 + i*60
                if i == startSelected:
                    pygame.draw.rect(screen, (200,200,255), pygame.Rect(center_x - 117, y-20, 240, 40), 2)
                t = fonts[1].render(o, True, (255,255,255))
                screen.blit(t, t.get_rect(center=(center_x, y)))

            for e in events:
                if e.type == pygame.KEYDOWN:
                    if e.key in (pygame.K_w, pygame.K_UP):
                        startSelected = (startSelected - 1) % 2
                    if e.key in (pygame.K_s, pygame.K_DOWN):
                        startSelected = (startSelected + 1) % 2
                    if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if startSelected == 0:
                            appState = "hubTransition" if os.path.exists(save_path) else "classSelect"
                        else:
                            appState = "quit"

        case "hub":

            for e in events:
                if e.type == pygame.QUIT:
                    running = False

            if not tmx_data:
                tmx_data = load_pygame(f"assets/maps/{world.split('_')[0]}/{world}.tmx")
                collision_layer = tmx_data.get_layer_by_name("collision")
                collision_rects = getCollisions(collision_layer)

                object_layer = tmx_data.get_layer_by_name("Object Layer 1")
                dungeon_doors = []

                for obj in object_layer:
                    if obj.properties.get("style") == "door":
                        rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                        dungeon_doors.append((rect, obj.properties.get("target")))


            appState, world = drawHub(screen, hub_surface, player_rect, player_img,tmx_data, collision_rects, dungeon_doors, appState, world)

        case "game": 

            match activeFloor:
                case _ if activeFloor.startswith("extra_"):
                    
                    extra_floor = activeFloor[6:]

                    running, eventList["extra"], selected_id = extraControl(extra_floor, player, selected_id, events, extraOptions, eventList["extra"], running)

                    if eventList["extra"]:
                        drawExtraMenu(extra_floor, display, player, selected_id, extraOptions)
                    else: floorLayout, floor, room, activeFloor, appState, notifications = loadNewRoom(floor, maxRoom,room,floorLayout,"roomTransition")
                
                case "event":

                    if not staticEvent and eventList["event"]:
                        staticEvent = random.choice(staticEvents)

                    context = {
                        "player": player,
                        "addRoom": lambda key: addRoom(floorLayout, key, room),
                        "removeRoom": lambda key, i: removeRoom(floorLayout,key, i),
                        "addNotification": lambda key, duration: addNotification(key, duration)
                    }
    
                    selected_id, eventList["event"], running = eventControl(events, selected_id, player, eventList["event"], staticEvent, context, running)
                    drawNotifications(display)
                    if eventList["event"]:
                        drawEventMenu(display, staticEvent, selected_id)
                    else: 
                        floorLayout, floor, room, activeFloor, appState, notifications = loadNewRoom(floor, maxRoom,room,floorLayout,"roomTransition")
                        staticEvent = None

                case "chest":
                    
                    if not chestPool and eventList["chest"]: 
                        chestPool = generateItemPool(itemPools)

                    selected_id, eventList["chest"], running = treasureControl(events, selected_id, player, eventList["chest"], chestPool, running)

                    if eventList["chest"]:
                        drawChestMenu(display, itemPools, chestPool, selected_id)
                    else: 
                        floorLayout, floor, room, activeFloor, appState, notifications = loadNewRoom(floor, maxRoom,room,floorLayout,"roomTransition")
                        chestPool = None

                case "shop":
                    
                    if not shopPool and eventList["shop"]: 
                        shopPool = generateItemPool(shopItems) + generateItemPool(shopSmith)

                    selected_id, eventList["shop"], running = shopControl(events, selected_id, player, eventList["shop"], shopPool, running)

                    if eventList["shop"]:
                        all_rects[1] = drawShopMenu(display, shopItems, shopPool, selected_id)
                    else: 
                        floorLayout, floor, room, activeFloor, appState, notifications = loadNewRoom(floor, maxRoom, room,floorLayout,"roomTransition")
                        shopPool = None
                
                case "fight" | "elite":

                    if not floorLoaded:
                        instance = combatState(display, advParty, enemyList, myTurn, room, floor, activeFloor, pending_levels, addNotification)
                        floorLoaded = True

                    for e in events:
                        if e.type == pygame.QUIT:
                            running = False
                        resultado_combate = instance.handle_event(e) 

                    instance.update()
                    instance.render()
                    drawLayout(display, visual_level, floorLayout, room, floor)
                    drawNotifications(display)

                    if not instance.ongoing:
                        if instance.result == "VICTORY":
                            floorLayout, floor, room, activeFloor, appState, notifications = loadNewRoom(floor, maxRoom, room, floorLayout, "roomTransition")
                            myTurn = True
                            floorLoaded = False
                            enemyList = []
                        else: running = False 

                    """if not enemyList and pending_levels == 0:
                        enemyList = pickNewEnemies(random.randint(1,3),enemyList,enemies,bosses,room)
                        if activeFloor == "elite":
                            boss_count = random.choices([1, 2], weights=[90, 10], k=1)[0]
                            bosses_picked = random.choices(bosses, k=boss_count)
                            enemyList = bosses_picked + enemyList

                    partyLenght = len(advParty)
                    hudOptions["menu"] = [""]
                    hudOptions["targetSel"] = ([f"{index+1} - {obj.name}" for index, obj in enumerate(playerTargets)] if playerTargets else [""])
                    hudOptions["usableSel"] = ([f"{index+1} - {obj.name +" "+ str(obj.uses) if hasattr(obj, 'name') else str(obj)}" for index, obj in enumerate(playerUsables)] if playerUsables else ["[Empty] - Nothing Here"])

                    menuOptions = [["Continue", "Quit to Desktop"],["Yes", "No"], item_selection]

                    drawScreenArgs = [display, action, hudOptions, actionStates, menuStates, menuState, myTurn, advParty, floor, room, enemyList, enemyList_IsSerialized, partyTurn, tabPressed]
                    enemyList_serialized, enemyList_IsSerialized, tabPressed = drawScreen(*drawScreenArgs)

                    drawNotifications(display)

                    eventContext = {
                        "player": player,
                        "enemyList": enemyList,
                        "toggleMenu": lambda key: toggleDict(eventList, key),
                        "addRoom": lambda key: addRoom(floorLayout, key, room),
                        "addNotification": lambda key, duration: addNotification(key, duration)
                    }

                    # Menu Control
                    menuControlArgs = [myTurn, events, randEvent, eventContext, menuState, blacksmith, bl_length, eventList, menuOptions, 
                                        selected_id, player, advParty, enemyList_serialized, room,save_path, running, all_rects, 
                                        pending_levels, appState]
                    selected_id, running, menuState, pending_levels = menuControl(*menuControlArgs)

                    # Game input only when menu is not open
                    if not any(eventList.values()): 

                        keys = pygame.key.get_pressed()
                        
                        any_num_pressed = False
                        max_idx_check = 9 # O el máximo que uses
                        for i in range(1, max_idx_check + 1):
                            if keys[getattr(pygame, f"K_{i}")]:
                                any_num_pressed = True
                                break

                        if input_lock:
                            if any_num_pressed:
                                any_num_pressed = False 
                            else:
                                input_lock = False

                        inputs = {
                            "shift": [keys[pygame.K_LSHIFT], shiftPressed], 
                            "a": [keys[pygame.K_a], aPressed], 
                            "s": [keys[pygame.K_s], sPressed], 
                            "r": [keys[pygame.K_r], rPressed], 
                            "ctrl": [keys[pygame.K_LCTRL], ctrlPressed],
                            "tab": [keys[pygame.K_TAB], tabPressed]
                        }

                        # 2. Teclas de DISPARO (Números) - Lógica cambiada a EVENTOS
                        max_index = max(len(enemyList), len(player.items), partyLenght, len(getattr(player.weapon["primary"],"skills", "")),len(getattr(player.weapon["secondary"],"skills", "")))
                        for i in range(1, max_index+1):
                            key_attr = getattr(pygame, f"K_{i}")
                            # AQUÍ ESTÁ EL TRUCO: Solo asignamos True si NO hay bloqueo (input_lock es False)
                            if input_lock:
                                inputs[str(i)] = False
                            else:
                                inputs[str(i)] = keys[key_attr]

                        if myTurn:

                            player = advParty[partyTurn]  # jugador actual
                            #randEvent, eventList, lastEvent = getRandEvent(eventList,lastEvent,randEvent,player)
                            
                            match gameState:

                                case "chooseAction":
                                    menuState = "menu"
                                    match inputs:
                                        case {"shift": [active, pressed]} if pressed or active:
                                            playerTargets,gameState,action,inputs,input_lock= gameStateChange(
                                                inputs,"selectTarget",enemyList,"Attack"
                                            )
                                            playerAction = player.weapon["primary"].attack
                                            actionArgs = {"target": enemyList}

                                        case {"s": [active, pressed]} if pressed or active:
                                            playerUsables,gameState,action,inputs,input_lock= gameStateChange(
                                                inputs,"selectUsable",player.weapon["primary"].skills | getattr(player.weapon["secondary"], "skills",{}),"Choose Skill"
                                            )
                                            actionArgs = {"self": player,"target": enemyList}

                                        case {"a": [active, pressed]} if pressed or active:
                                            if player.weapon["primary"].type == "magic" and player.mp >= 10:
                                                playerTargets,gameState,action,inputs,input_lock= gameStateChange(
                                                    inputs,"selectTarget",enemyList,"Magicly Attack"
                                                )
                                                playerAction = player.weapon["primary"].attack

                                            else:
                                                menuState = "noMagic"

                                        case {"ctrl": [active, pressed]} if pressed or active:

                                            playerUsables, gameState, action, inputs, input_lock = gameStateChange(
                                                inputs, "selectUsable", player.items, "Choose Item"
                                            )
                                            actionArgs = {"target": advParty}


                                        case {"tab": [active, pressed]} if pressed or active:
                                            if active:
                                                tabPressed = True
                                            else:
                                                tabPressed = False

                                        case {"r": [active, pressed]} if pressed or active:
                                            if getattr(player.weapon, "mgc", 0) <= 0:
                                                player.sta += round(player.max_sta*0.5)
                                            else: 
                                                player.mp += round(player.max_mp*0.02)
                                            partyTurn, myTurn = passTurn(partyTurn, advParty)
                                
                                case "selectTarget":
                                    menuState = "targetSel"
                                    enemy_keys = {str(i+1): inputs.get(str(i+1), False) for i in range(len(playerTargets))}
                                    for key, pressed in enemy_keys.items():
                                        if pressed:
                                            enemy_idx = int(key) - 1
                                            playerTargets = playerTargets[enemy_idx]
                                            actionArgs["target"] = playerTargets
                                            if type(playerAction) == Item:
                                                playerAction = playerAction.useItem
                                            playerAction(**actionArgs)
                                            partyTurn, myTurn = passTurn(partyTurn, advParty)
                                            menuState = "menu"
                                            shiftPressed = False
                                            playerTargets,gameState,action,inputs,input_lock= gameStateChange(inputs,"chooseAction",None,"")
                                            break

                                    if keys[pygame.K_b]:
                                        playerTargets,gameState,action,inputs,input_lock= gameStateChange(inputs,"chooseAction",None,"") 
                                
                                case "selectUsable":
                                    menuState = "usableSel"
                                    usable_keys = {str(i+1): inputs.get(str(i+1), False) for i in range(len(playerUsables))}

                                    for key, pressed in usable_keys.items():
                                        if pressed:

                                            ikey = int(key) - 1

                                            # Caso especial: items
                                            if type(playerUsables) == type(player.weapon["primary"].skills):
                                                if list(playerUsables.keys())[ikey] in player.weapon["primary"].skills.keys():
                                                    ikey = list(player.weapon["primary"].skills.keys())[ikey]
                                                    actionArgs["weaponUsed"] = "primary"
                                                else:
                                                    ikey = list(player.weapon["secondary"].skills.keys())[ikey-1]
                                                    actionArgs["weaponUsed"] = "secondary"

                                            playerAction = playerUsables[ikey]

                                            if partyLenght == 1 and type(playerAction) == Item:
                                                player.useItem(ikey)
                                                partyTurn, myTurn = passTurn(partyTurn, advParty)
                                                playerTargets,gameState,action,inputs,input_lock= gameStateChange(inputs,"chooseAction",None,"") 
                                                menuState = "menu"
                                                break
                                            
                                            playerTargets, gameState, action, inputs, input_lock = gameStateChange(
                                                inputs,
                                                "selectTarget",
                                                actionArgs["target"],
                                                f"Use{action[6:]}"
                                            )
                                            menuState = "menu"
                                            break

                                    if keys[pygame.K_b]:
                                        playerTargets,gameState,action,inputs,input_lock= gameStateChange(inputs,"chooseAction",None,"") 

                            if advParty[partyTurn] != player or not myTurn:
                                for e in enemyList:
                                    for effect in e.stat_effs:
                                        effect.passTurn()
                                        e.stat_effs = [s for s in e.stat_effs if s.turns != 0]
                            
                        elif not myTurn:
                            
                            for key in lastEvent.keys(): lastEvent[key] = False
                            menuState = "EnemyTurn"
                            
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

                                    if enemy._hp <= 0:
                                        continue

                                    # Crear IA solo si no existe
                                    if not hasattr(enemy, "ai") or enemy.ai is None:
                                        enemy.ai = EnemyAi(
                                            [UseSkill(skill) for skill in enemy.skills] + [Attack()],
                                            enemy.personality if hasattr(enemy, "personality") else None
                                        )

                                    allies = [e for e in enemyList if e is not enemy and e._hp > 0]
                                    adversaries = advParty

                                    result = enemy.ai.act(enemy, allies, adversaries)

                                    if result:
                                        action_name = f"used {result["action"].name} on" if hasattr(result["action"], "name") else "attacked"
                                        target_name = result["target"].name

                                        addNotification(f"{enemy.name} {action_name} {target_name} {result["action"].tags}",2)

                                print("-----------------------------")
                                myTurn = True
                                menuState = "menu"
                                enemy_turn_start = None  # reiniciamos el temporizador
                                
                                for player in advParty:
                                    if player._hp <= 0:
                                        player.hooks.run("on_death",{"player":player})
                        
                        if enemyList:
                            for enemy in enemyList:  
                                if enemy.hp <= 0:
                                    if enemy.tameable:
                                        tame_chance = random.randint(0,5)
                                        if tame_chance == 5: advParty.append(Player(enemy.base_hp,0, name=enemy.name))
                                    enemyList = [e for e in enemyList if e.hp > 0]
                                    player.gold_reward(enemy.reward)
                                    pending_levels += player.gainXP(enemy.reward)
                                    if pending_levels > 0:
                                        eventList["lvlUp"] = True
                                    lastEvent["lvldUp"] = eventList["lvlUp"]
                                    break   

                        if not enemyList and pending_levels == 0:
                            floorLayout, floor, room, activeFloor, appState, notifications = loadNewRoom(floor, maxRoom, room, floorLayout, "roomTransition")
                            myTurn = True

                    else:

                        match eventList:
                            case {"pause": True}:
                                drawPauseMenu(display, hudOptions[0], selected_id)
                            case {"shop": True}:
                                all_rects[1] = drawShopMenu(display, shopItems, item_selection, selected_id)
                            case {"lvlUp": True}:  
                                all_rects[0] = drawLevelUpMenu(display, player, selected_id, pending_levels)
                            case {"randEvent": True}:  
                                drawRandomEvent(display, randEvent, selected_id)

                    advParty = [p for p in advParty if p._hp > 0]

            if appState == "game":
                drawLayout(display, visual_level, floorLayout, room, floor)

            if advParty == []:
                print("El juego ha terminado: el jugador perdió.")

                running = False"""

    pygame.display.flip()
    clock.tick(120)