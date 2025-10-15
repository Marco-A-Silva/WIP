import pygame, json, random, os, sys
from funcionalidades import Player, Enemy, Item, Weapon, MagicWeapon, eventHandling, drawPauseMenu, drawWeaponMenu, drawShopMenu, menuControl, drawScreen, modifyAttrs


pygame.init()
screen = pygame.display.set_mode((1000, 1000))
colore = (255, 0, 255)
font = pygame.font.SysFont("Arial", 30)
display = [screen, font, colore]

clock = pygame.time.Clock()
running = True
MyTurn = True

shop_items = [[Item("Health Potion",lambda: modifyAttrs(main_player, {"hp": lambda x: x+10}),2),15],
              [Item("Mana Potion", lambda: modifyAttrs(main_player, {"mp": lambda x: x+10}),1),15]
              ]

weaponry = [Weapon("Sword", 30), MagicWeapon("Staff", 8, 30), Weapon("Axe", 50)]
all_skills = {"Goblin Gang": lambda self: self.call_reinforcements(2,enemies_list), "Humiliation": lambda self: modifyAttrs(self, {"dmg_red": lambda x: x+0.2})   ,
              "Shroud": lambda self: (modifyAttrs(self, {"dmg_red": 1}), modifyAttrs(self, {"hp" : lambda x: x+20})), "Intangable Attack": lambda self: 10, #ignore armor, to be implementedm
              "Berserk": lambda self: (modifyAttrs(self, {"dmg_red": lambda x: x+0.4}),modifyAttrs(self, {"dmg": lambda x: x+20})),
              "Taunt": lambda self: (modifyAttrs(main_player.armor, {"defense": lambda x: x-0.4}),modifyAttrs(main_player.weapon, {"m_damage": lambda x: x + 10,"magic_dmg": lambda x: x - 20}))
              }

enemy_count = 0
enemies = [Enemy("Goblin", 100, skills= {"Goblin Gang": all_skills["Goblin Gang"],"Humiliation": all_skills["Humiliation"]}),
           Enemy("Wraith", 50, skills={"Shroud": all_skills["Shroud"], "Intangable Attack": all_skills["Intangable Attack"]}), 
           Enemy("Orc", 150, skills={"Berserk": all_skills["Berserk"], "Taunt": all_skills["Taunt"]})
           ]

enemies_list = []
enemies_list_serialized = None
enemies_list_is_serialized = False
bosses = []

menu_is_open = False
menu_list = {"Pause" : False, "Weapon Shop" : False, "Shop" : False}
menu_options = [["Continue", "Quit to Desktop"],["Yes", "No"], shop_items]
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
        enemies_list = [Enemy(e["name"], e["hp"], skills = {name: all_skills[name] for name in e["skills"] if name in all_skills}) for e in data["enemies"]]

last_weapon_menu_level = data["level"]
isLastWeaponShopLevel = True
isLastShopLevel = True


while running:
    
    # Hud Setup
    drawScreenArgs = [display, main_player, enemies, level, isLastWeaponShopLevel, enemies_list, enemies_list_is_serialized]
    enemies_list, enemies_list_serialized, enemies_list_is_serialized = drawScreen(*drawScreenArgs)

    # Safely get events;
    try:
        events = pygame.event.get()
    except Exception:
        # Ensure internal event queue is updated so input still works
        pygame.event.pump()
        events = []

    # Menu Control
    menuControlArgs = [events, weaponry, menu_list, menu_options, selected_id, main_player, enemies_list_serialized, level, isLastWeaponShopLevel, isLastShopLevel, save_path, running]
    selected_id, running, isLastWeaponShopLevel, isLastShopLevel = menuControl(*menuControlArgs)

    # Game input only when menu is not open
    if not menu_is_open: 

        keys = pygame.key.get_pressed()
        inputs = {"shift": keys[pygame.K_LSHIFT],"a": keys[pygame.K_a], "ctrl": keys[pygame.K_LCTRL]}
        for i, enemey in enumerate(enemies_list, start=1):
            key_attr = getattr(pygame, f"K_{i}") 
            inputs[str(i)] = keys[key_attr]

        # Turn-based logic
        if MyTurn:
            match inputs:
                case {"shift": True}:
                   
                    enemy_keys = {str(i+1): inputs.get(str(i+1), False) for i in range(len(enemies_list))}

                    for key, pressed in enemy_keys.items():
                        if pressed:
                            enemy_idx = int(key) - 1
                            main_player.weapon.melee_attack(enemies_list[enemy_idx],False)
                            MyTurn = False
                            break

                case {"a": True}:
                    if getattr(main_player.weapon, "magic_dmg", 0) != 0 and main_player.mp >= 10:
                        
                        enemy_keys = {str(i+1): inputs.get(str(i+1), False) for i in range(len(enemies_list))}

                        for key, pressed in enemy_keys.items():
                            if pressed:
                                enemy_idx = int(key) - 1
                                main_player.weapon.cast_spell(enemies_list[enemy_idx])
                                MyTurn = False
                                break
                
                case {"ctrl": True}:
                    item_keys = {str(i+1): inputs.get(str(i+1), False) for i in range(len(main_player.items))}

                    for key, pressed in item_keys.items():
                        if pressed:
                            key_id = int(key) - 1
                            main_player.useItem(key_id)
                            MyTurn = False
                            break

        elif not MyTurn:
            if enemy_turn_start is None:
                enemy_turn_start = pygame.time.get_ticks()  # registramos cuándo empezó el turno enemigo

            # Si pasaron 1 segundo (1000 ms)
            if pygame.time.get_ticks() - enemy_turn_start > 1000:
                for enemy in enemies_list:
                    outcome = random.randint(0,3)
                    if outcome == 3:
                        skill_names = list(enemy.skills.keys())
                        skill_name = random.choice(skill_names)
                        enemy.skills[skill_name](enemy)
                        print(f"{enemy.name} uses {skill_name}!")
                    else:
                        enemy.attack(main_player, False)
                        print(f"{enemy.name} attacks! {enemy.dmg} {main_player.armor.defense} {enemy.dmg - enemy.dmg*main_player.armor.defense} {enemy.dmg*main_player.armor.defense}")
                    
                print("-----------------------------")
                MyTurn = True
                enemy_turn_start = None  # reiniciamos el temporizador
        
        for enemy in enemies_list:  
            if enemy.hp <= 0:
                #enemies_list.remove(enemy)
                main_player.gold_reward(enemy.reward)
                level += 1
                enemy.hp += enemy.base_hp + level * 5
                isLastWeaponShopLevel = last_weapon_menu_level == level
                isLastShopLevel = last_shop_menu_level == level
                break
    else:
        match menu_list:
            case {"Pause": True}:
                drawPauseMenu(display, menu_options[0], selected_id)
            case {"Weapon Shop": True}:
                drawWeaponMenu(display, menu_options[1], selected_id)
            case {"Shop": True}:
                drawShopMenu(display, shop_items, selected_id)

    # EventHandling 
    eventHandlingArgs = [display, level, MyTurn, isLastWeaponShopLevel, isLastShopLevel, menu_list]
    menu_list["Weapon Shop"], menu_list["Shop"], last_weapon_menu_level, last_shop_menu_level, menu_is_open = eventHandling(*eventHandlingArgs)

    pygame.display.flip()
    clock.tick(30)

    if main_player.hp == 0:
        print("El juego ha terminado: el jugador perdió.")
        running = False