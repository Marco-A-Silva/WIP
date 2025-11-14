import pygame, json, random, os, sys
from vault import blacksmith, bl_length, shopItems, enemies, bosses, enemySkills
from funcionalidades import Player, Enemy, Weapon, MagicWeapon
from funcionalidades import eventHandling, drawPauseMenu, drawWeaponMenu, drawShopMenu, menuControl, drawScreen, pickNewEnemies


def passTurn(partyTurns):
    partyTurns += 1
    if partyTurns >= len(advParty):
        return 0, False  # reinicia turno y termina la ronda
    return partyTurns, True


pygame.init()
display_info = pygame.display.Info()
screen = pygame.display.set_mode((display_info.current_w - 100, display_info.current_h - 50))
colore = (255, 0, 255)
font = pygame.font.SysFont("Arial", 30)
display = [screen, font, colore]

clock = pygame.time.Clock()
running = True
myTurn = True

shiftPressed = False
aPressed = False
ctrlPressed = False

enemyCount = 0
enemyList = []
enemyList_serialized = None
enemyList_IsSerialized = False
isBossLevel = False
isLastBossLevel = False

advParty = []
partyTurn = 0
playerTurn = None

menuIsOpen = False
menuList = {"Pause" : False, "Weapons" : False, "Shop" : False}
selected_id = 0

enemy_turn_start = None

if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

save_path = os.path.join(base_path, "SaveState.json")

with open(save_path, "r") as f:
    data = json.load(f)
    has_weapon = data.get("weapon",{})
    weapon_eq = None
    if has_weapon and has_weapon.get("magic_dmg") is not None:
        weapon_eq = MagicWeapon(data["weapon"]["name"], data["weapon"]["m_damage"], data["weapon"]["magic_dmg"])
    elif has_weapon: weapon_eq = Weapon(data["weapon"]["name"], data["weapon"]["m_damage"])
    main_player = Player(data["player_hp"], data["player_mp"], weapon=weapon_eq)
    if data.get("items"): 
        items = [item[0] for item in shopItems if item[0].name in data.get("items")]
        for item in items: 
            main_player.equip_armament(item)
    level = data["level"]
    if data.get("enemies",[]):
        enemyList = [Enemy(e["name"], e["hp"], skills = {name: enemySkills[name] for name in e["skills"] if name in enemySkills}) for e in data["enemies"]]

advParty.append(main_player)

last_weapon_menu_level = data["level"]
last_shop_menu_level = data["level"]
lastMenuOpen = {"Shop": True, "Weapons": True}
isLastWeaponShopLevel = True
isLastShopLevel = True
isFirstLevelLoaded = True

item_selection = None
state = "menu"

hud_states = {
    "EnemyTurn": ["Enemy Turn..."],
    "party": ["[" + str(i) + "]" + char.name for i,char in enumerate(advParty)],
    "menu": ["[Shift] Attack", "[A] Magic Attack", "[Ctrl] Use Item"],
    "items": [item.name + " - " + str(item.uses) for item in main_player.items] if main_player.items else ["[Empty] - No items"],
    "attack": [" [" + str(index+1) + "] - " + enemy.name for index, enemy in enumerate(enemyList)]
}

while running:

    partyLenght = len(advParty)

    hud_states["party"] = ["[" + str(i) + "]" + char.name for i,char in enumerate(advParty)]
    hud_states["attack"] = [" [" + str(index+1) + "] - " + enemy.name for index, enemy in enumerate(enemyList)]

    menuOptions = [["Continue", "Quit to Desktop"],["Yes", "No"], item_selection]
    
    # Hud Setup
    drawScreenArgs = [display, hud_states, state, myTurn, advParty, level, isLastWeaponShopLevel, enemyList, enemyList_IsSerialized]
    enemyList_serialized, enemyList_IsSerialized = drawScreen(*drawScreenArgs)

    # Safely get events;
    try:
        events = pygame.event.get()
    except Exception:
        # Ensure internal event queue is updated so input still works
        pygame.event.pump()
        events = []

    # Menu Control
    menuControlArgs = [myTurn, events, state, blacksmith, bl_length, menuList, menuOptions, selected_id, main_player, enemyList_serialized, level, isLastWeaponShopLevel, isLastShopLevel, save_path, running]
    selected_id, running, isLastWeaponShopLevel, isLastShopLevel, state = menuControl(*menuControlArgs)

    # Game input only when menu is not open
    if not menuIsOpen: 

        keys = pygame.key.get_pressed()
        inputs = {"shift": [keys[pygame.K_LSHIFT], shiftPressed], # "nombre": [isActive, wasPressed]
                  "a": [keys[pygame.K_a], aPressed], 
                  "ctrl": [keys[pygame.K_LCTRL], ctrlPressed]}
        for i, enemey in enumerate(enemyList, start=1): 
            key_attr = getattr(pygame, f"K_{i}") 
            inputs[str(i)] = keys[key_attr]

        if myTurn and partyTurn < len(advParty):
            player = advParty[partyTurn]  # jugador actual

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
                    if getattr(player.weapon, "magic_dmg", 0) != 0 and player.mp >= 10:
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


            if not myTurn:
                state = "menu"
                for e in enemyList:
                    for effect in e.stat_effs:
                        effect.passTurn()
            
        elif not myTurn:
            state = "EnemyTurn"

            if enemy_turn_start is None:
                enemy_turn_start = pygame.time.get_ticks()  # registramos cuándo empezó el turno enemigo

            # Si pasaron 1 segundo (1000 ms)
            if pygame.time.get_ticks() - enemy_turn_start > 1000:

                print(main_player.stat_effs)
                for effect in main_player.stat_effs:  
                    effect.passTurn()
                    print(effect.turns)
                    main_player.stat_effs = [e for e in main_player.stat_effs if e.turns > 0]
                
                for enemy in enemyList:
                    outcome = random.randint(0,3)
                    if outcome == 3:
                        skill_names = list(enemy.skills.keys())
                        if skill_names != []: 
                            skill_name = random.choice(skill_names)
                            context = {
                                "self": enemy,
                                "main_player": main_player,
                                "enemyList": enemyList
                            }
                            enemy.skills[skill_name](**context)
                            print(f"{enemy.name} uses {skill_name}!")
                    else:
                        enemy.attack(main_player, False)    
                        print(f"{enemy.name} attacks! {enemy.dmg} {main_player.armor.dmg_red} {enemy.dmg*main_player.armor.dmg_red}")
                    
                print("-----------------------------")
                myTurn = True
                state = "menu"
                enemy_turn_start = None  # reiniciamos el temporizador

        
        if enemyList:
            for enemy in enemyList:  
                if enemy.hp <= 0:
                    tame_chance = random.randint(0,5)
                    if enemy.tameable and  tame_chance == 5: advParty.append(Player(enemy.base_hp,0, name=enemy.name))
                    enemyList.remove(enemy)
                    main_player.gold_reward(enemy.reward)
                    
                    break   
        else:
            level += 1
            enemyList = pickNewEnemies(random.randint(0,3),enemyList, enemies, bosses, level, isBossLevel, isLastBossLevel)
            for enemy in enemyList: enemy.hp = enemy.base_hp + level
            isLastWeaponShopLevel = last_weapon_menu_level == level
            isLastShopLevel = last_shop_menu_level == level
            isFirstLevelLoaded = False 
        
        
    else:
        match menuList:
            case {"Pause": True}:
                drawPauseMenu(display, menuOptions[0], selected_id)
            case {"Weapons": True}:
                drawWeaponMenu(display, menuOptions[1], selected_id)
            case {"Shop": True}:
                item_selection = drawShopMenu(display, shopItems, item_selection, selected_id)

    # EventHandling 
    eventHandlingArgs = [display, level, myTurn, isLastWeaponShopLevel, isLastShopLevel, isLastBossLevel, menuList]
    menuList, last_weapon_menu_level, last_shop_menu_level, menuIsOpen, isBossLevel, isLastBossLevel = eventHandling(*eventHandlingArgs)

    pygame.display.flip()
    clock.tick(120)

    if main_player.hp == 0:
        print("El juego ha terminado: el jugador perdió.")
        running = False