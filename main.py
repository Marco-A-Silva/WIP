import pygame
from funcionalidades import Player, Enemy, Item, Weapon, MagicWeapon, eventHandling, drawPauseMenu, drawWeaponMenu, drawShopMenu, menuControl,drawScreen
import json

pygame.init()
screen = pygame.display.set_mode((1000, 1000))
colore = (255, 0, 255)
font = pygame.font.SysFont("Arial", 30)
display = [screen, font, colore]

clock = pygame.time.Clock()
running = True
MyTurn = True


with open("SaveState.json", "r") as f:
    data = json.load(f)
    has_weapon = data.get("weapon",{})
    weapon_eq = None
    if has_weapon and has_weapon.get("magic_dmg") is not None:
        weapon_eq = MagicWeapon(data["weapon"]["name"], data["weapon"]["m_damage"], data["weapon"]["magic_dmg"])
    elif has_weapon: weapon_eq = Weapon(data["weapon"]["name"], data["weapon"]["m_damage"])
    main_player = Player(data["player_hp"], data["player_mp"], weapon=weapon_eq)
    level = data["level"]
    if data.get("enemies",{}):
        enemies_list = [Enemy(e["name"], e["hp"]) for e in data["enemies"]]


shop_items = [[Item("Health Potion",3),15],[Item("Mana Potion",3),15]]
weaponry = [Weapon("Sword", 30), MagicWeapon("Staff", 8, 30), Weapon("Axe", 50)]

enemy_count = 0
enemies = [Enemy("Goblin", 100), Enemy("Wraith", 50), Enemy("Orc", 150)]
enemies_list = []
enemies_list_serialized = None
enemies_list_is_serialized = False
bosses = []

menu_is_open = False
menu_list = {"Pause" : False, "Weapon Shop" : False, "Shop" : False}
menu_options = [["Continue", "Quit to Desktop"],["Yes", "No"], shop_items]
selected_id = 0

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
    menuControlArgs = [events, weaponry, menu_list, menu_options, selected_id, shop_items, main_player, enemies_list_serialized, level, isLastWeaponShopLevel, isLastShopLevel, running]
    selected_id, running, isLastWeaponShopLevel, isLastShopLevel = menuControl(*menuControlArgs)

    # Game input only when menu is not open
    if not menu_is_open: 
        keys = pygame.key.get_pressed()

        # Turn-based logic
        if MyTurn:
            if keys[pygame.K_LSHIFT]:
                if keys[pygame.K_1]:
                    main_player.weapon.melee_attack(enemies_list[enemy_count - 1])
                    MyTurn = False
                elif keys[pygame.K_2]:
                    main_player.weapon.melee_attack(enemies_list[0])
                    MyTurn = False
                
            elif keys[pygame.K_a] and getattr(main_player.weapon, "magic_dmg", 0) is not 0:
                if main_player.mp >= 10:
                    main_player.weapon.cast_spell(enemies_list[0])
                    MyTurn = False
        elif not MyTurn and keys[pygame.K_s]:
            main_player.take_damage(1)
            MyTurn = True
        
        for enemy in enemies_list:  
            if enemy.hp <= 0:
                #enemies_list.remove(enemy)
                main_player.gold_reward(enemy.reward)
                enemy.hp += 10
                level += 1
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