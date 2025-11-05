import pygame, json, random, os, sys
from funcionalidades import Player, Enemy, Item, Weapon, MagicWeapon, Armor, OverTimeEffects 
from funcionalidades import eventHandling, drawPauseMenu, drawWeaponMenu, drawShopMenu, menuControl, drawScreen, modifyAttrs, pickNewEnemies

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

blacksmith = [Weapon("Sword", 500), MagicWeapon("Staff", 500, 30), Weapon("Axe", 500), Armor("Chestplate",0.05)]

enemySkills = {"Goblin Gang": lambda self: self.call_reinforcements(2,enemyList), 
              "Humiliation": lambda self: self.addStatusEffect(OverTimeEffects(self,2,effects={"dmg_red": (0.02, True)})),
              "Shroud": lambda self: self.addStatusEffect(OverTimeEffects(self,1,effects={"dmg_red": (1,True),"hp": (20,False)})),     
              "Intangable Attack": lambda self: self.attack(main_player, True),
              "Berserk": lambda self: self.addStatusEffect(OverTimeEffects(self,2,effects={"dmg_red": (0.2, True), "dmg": (20, True)})),
              "Taunt": lambda self: (main_player.addStatusEffect(OverTimeEffects(main_player.armor,3,effects={"defense": (-0.4, True)})), 
                                    main_player.addStatusEffect(OverTimeEffects(main_player.weapon,2,effects={"m_damage": (10, True), "magic_dmg": (-20, True)}))),
              "Leech Life": lambda self: (modifyAttrs(self, {"hp": lambda x: x+10}), modifyAttrs(main_player, {"hp": lambda x: x-10}))
              }

enemyCount = 0
enemies = [Enemy("Goblin", 100, skills= {"Goblin Gang": enemySkills["Goblin Gang"],"Humiliation": enemySkills["Humiliation"]}),
           Enemy("Wraith", 50, skills={"Shroud": enemySkills["Shroud"], "Intangable Attack": enemySkills["Intangable Attack"]}), 
           Enemy("Orc", 150, skills={"Berserk": enemySkills["Berserk"], "Taunt": enemySkills["Taunt"]})
           ]

enemyList = []
enemyList_serialized = None
enemyList_IsSerialized = False
isBossLevel = False
isLastBossLevel = False
bosses = [Enemy("High Orc", 300, skills={"Berkerk": enemySkills["Berserk"], "Taunt": enemySkills["Taunt"]}),
          Enemy("Vampire Lord", 250, skills={"Leech Life": enemySkills["Leech Life"], "Shroud": enemySkills["Shroud"]}),
          ]

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
    level = data["level"]
    if data.get("enemies",[]):
        enemyList = [Enemy(e["name"], e["hp"], skills = {name: enemySkills[name] for name in e["skills"] if name in enemySkills}) for e in data["enemies"]]

last_weapon_menu_level = data["level"]
last_shop_menu_level = data["level"]
lastMenuOpen = {"Shop": True, "Weapons": True}
isLastWeaponShopLevel = True
isLastShopLevel = True
isFirstLevelLoaded = True

shopItems = [[Item("Health Potion",lambda: modifyAttrs(main_player, {"hp": lambda x: x+10}),2),15],
              [Item("Mana Potion", lambda: modifyAttrs(main_player, {"mp": lambda x: x+10}),2),15],
              [Item("Invigorating Potion", lambda: main_player.addStatusEffect(OverTimeEffects(main_player.armor,2,effects={"dmg_red": (0.2, True)})), 2), 30],
              [Item("Nothing Potion", lambda: None, 2),5],
              [Item("Nothing Potion", lambda: None, 2),5]
              ]

menuOptions = [["Continue", "Quit to Desktop"],["Yes", "No"], shopItems]
state = "menu"

while running:

    hud_states = {
        "menu": ["[Shift] Attack", "[A] Magic Attack", "[Ctrl] Use Item"],
        "items": [item.name + " - " + str(item.uses) for item in main_player.items] if main_player.items else ["[Empty] - No items found"],
        "attack": [" " + str(index+1) + " - " + enemy.name for index, enemy in enumerate(enemyList)]
    }
    
    # Hud Setup
    drawScreenArgs = [display, hud_states, state, myTurn, main_player, level, isLastWeaponShopLevel, enemyList, enemyList_IsSerialized]
    enemyList_serialized, enemyList_IsSerialized = drawScreen(*drawScreenArgs)

    # Safely get events;
    try:
        events = pygame.event.get()
    except Exception:
        # Ensure internal event queue is updated so input still works
        pygame.event.pump()
        events = []

    # Menu Control
    menuControlArgs = [myTurn, events, state, blacksmith, menuList, menuOptions, selected_id, main_player, enemyList_serialized, level, isLastWeaponShopLevel, isLastShopLevel, save_path, running]
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

        # Turn-based logic
        if myTurn:
            match inputs:
                case {"shift": [active, pressed]} if pressed or active:
                    
                    enemy_keys = {str(i+1): inputs.get(str(i+1), False) for i in range(len(enemyList))}

                    for key, pressed in enemy_keys.items():
                        if pressed:
                            print([enemy.name for enemy in enemyList])
                            enemy_idx = int(key) - 1
                            print("Before attack HPS:", [e.hp for e in enemyList])
                            main_player.weapon.melee_attack(enemyList[enemy_idx], False)
                            print("After attack HPS: ", [e.hp for e in enemyList])
                            print([enemy.name for enemy in enemyList])
                            myTurn = False
                            shiftPressed = False

                            break
                    
                    if keys[pygame.K_b]:
                        shiftPressed = False
                    
                    if active: 
                        shiftPressed = True

                case {"a": True}:
                    if getattr(main_player.weapon, "magic_dmg", 0) != 0 and main_player.mp >= 10:
                        
                        enemy_keys = {str(i+1): inputs.get(str(i+1), False) for i in range(len(enemyList))}

                        for key, pressed in enemy_keys.items():
                            if pressed:
                                enemy_idx = int(key) - 1
                                main_player.weapon.cast_spell(enemyList[enemy_idx])
                                myTurn = False
                                break

                        if keys[pygame.K_b]:
                            aPressed = False
                        
                        if active: 
                            aPressed = True
                
                case {"ctrl": [active, pressed]} if pressed or active:
                    item_keys = {str(i+1): inputs.get(str(i+1), False) for i in range(len(main_player.items))}
                    for key, pressed in item_keys.items():
                        if pressed:
                            key_id = int(key) - 1
                            main_player.useItem(key_id)
                            myTurn = False
                            ctrlPressed = False
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
            if enemy_turn_start is None:
                enemy_turn_start = pygame.time.get_ticks()  # registramos cuándo empezó el turno enemigo

            # Si pasaron 1 segundo (1000 ms)
            if pygame.time.get_ticks() - enemy_turn_start > 1000:
                for enemy in enemyList:
                    outcome = random.randint(0,3)
                    if outcome == 3:
                        skill_names = list(enemy.skills.keys())
                        skill_name = random.choice(skill_names)
                        enemy.skills[skill_name](enemy)
                        print(f"{enemy.name} uses {skill_name}!")
                    else:
                        enemy.attack(main_player, False)    
                        print(f"{enemy.name} attacks! {enemy.dmg} {main_player.armor.dmg_red} {enemy.dmg - enemy.dmg*main_player.armor.dmg_red} {enemy.dmg*main_player.armor.dmg_red}")
                    
                print("-----------------------------")
                myTurn = True
                enemy_turn_start = None  # reiniciamos el temporizador

                for effect in main_player.stat_effs:
                    effect.passTurn()
        
        if enemyList:
            for enemy in enemyList:  
                if enemy.hp <= 0:
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
                drawShopMenu(display, shopItems, selected_id)

    # EventHandling 
    eventHandlingArgs = [display, level, myTurn, isLastWeaponShopLevel, isLastShopLevel, isLastBossLevel, menuList]
    menuList, last_weapon_menu_level, last_shop_menu_level, menuIsOpen, isBossLevel, isLastBossLevel = eventHandling(*eventHandlingArgs)

    pygame.display.flip()
    clock.tick(120)

    if main_player.hp == 0:
        print("El juego ha terminado: el jugador perdió.")
        running = False