import pygame
from random import randint
from funcionalidades import Player as player, Enemy as enemy
from funcionalidades import Item as item, Weapon as weapon, MagicWeapon as magic_weapon
import json

pygame.init()
screen = pygame.display.set_mode((1000, 1000))
clock = pygame.time.Clock()
running = True

enemies_list = []

with open("SaveState.json", "r") as f:
    data = json.load(f)
    has_weapon = data.get("weapon",{})
    weapon_eq = None
    if has_weapon and has_weapon.get("magic_dmg") is not None:
        weapon_eq = magic_weapon(data["weapon"]["name"], data["weapon"]["m_damage"], data["weapon"]["magic_dmg"])
    elif has_weapon: weapon_eq = weapon(data["weapon"]["name"], data["weapon"]["m_damage"])
    main_player = player(data["player_hp"], data["player_mp"],weapon_eq)
    level = data["level"]
    if data.get("enemies",{}):
        enemies_list = [enemy(e["name"], e["hp"]) for e in data["enemies"]]


font = pygame.font.SysFont("Arial", 30)
MyTurn = True
menu_title = font.render("Menu", True, (255, 255, 255))

weaponry = [weapon("Sword", 30), magic_weapon("Staff", 8, 30), weapon("Axe", 50)]
enemy_count = 0
enemies = [enemy("Goblin", 100), enemy("Wraith", 50), enemy("Orc", 150)]
bosses = []

menu_open = False
w_menu_open = False
menu_options = ["Continue", "Quit to Desktop"]
yes_no = ["Yes", "No"]
selected_idx = 0
selected_idx_w = 0
last_w_menu_level = data["level"]
colore = (255, 0, 255)

while running:
    screen.fill("black")
    texto = font.render("Player hp: " + str(main_player.hp) + " mp: " + str(main_player.mp), True, (255, 255, 255))
    screen.blit(texto, (150, 120))

    if not enemies_list:
        enemy_count = randint(0, 3)
        enemies_list = [enemies[i] for i in range(enemy_count)]

    for i, en in enumerate(enemies_list):
        texto2 = font.render("Enemy name: " + en.name + " Enemy hp: " + str(en.hp), True, colore)
        screen.blit(texto2, (150, 160 + i * 40))
        enemies_list_serialized = [{"name": e.name, "hp": e.hp} for e in enemies_list]

    # Safely get events;
    try:
        events = pygame.event.get()
    except Exception:
        # Ensure internal event queue is updated so input still works
        pygame.event.pump()
        events = []

    # Menu Handling
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Toggle menu with ESC
            if event.key == pygame.K_ESCAPE:
                menu_open = not menu_open
                if menu_open:
                    selected_idx = 0
            elif menu_open:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected_idx = (selected_idx - 1) % len(menu_options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected_idx = (selected_idx + 1) % len(menu_options)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and menu_open:
                    if selected_idx == 0:  # "Continue"
                        menu_open = False
                    elif selected_idx == 1:  # Quit to Desktop
                        with open("SaveState.json", "w") as w:
                            json.dump({
                                "player_hp": main_player.hp,
                                "player_mp": main_player.mp,
                                "level": level,
                                "weapon": {
                                    "name": main_player.weapon.name,
                                    "m_damage": main_player.weapon.m_damage,
                                    "magic_dmg": getattr(main_player.weapon, "magic_dmg", 0)
                                },
                                "armor": {
                                    "name": main_player.armor.name,
                                    "defense": main_player.armor.defense
                                },
                                "enemies": enemies_list_serialized
                            }, w, indent=4)
                        running = False
            elif w_menu_open:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected_idx_w = (selected_idx_w - 1) % len(yes_no)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected_idx_w = (selected_idx_w + 1) % len(yes_no)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and w_menu_open:
                    if selected_idx_w == 0:  # "Yes"
                        x = randint(0, 2)
                        main_player.equip_weapon(weaponry[x])
                        w_menu_open = False
                    elif selected_idx_w == 1:  # "No"
                        w_menu_open = False

    # Game input only when menu is not open
    if not (menu_open or w_menu_open):
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
                
            elif keys[pygame.K_a] and getattr(main_player.weapon, "magic_dmg", None) is not None:
                if main_player.mp >= 10:
                    main_player.weapon.cast_spell(enemies_list[0])
                    MyTurn = False
        elif not MyTurn and keys[pygame.K_s]:
            main_player.take_damage(1)
            MyTurn = True

        # Game in general
        if MyTurn:
            screen.blit(font.render("Mi Turno", True, (255, 255, 255)), (10, 10))
        else:
            screen.blit(font.render("Turno Enemigo", True, (255, 255, 255)), (10, 10))

        if any(e.hp <= 0 for e in enemies_list):
            level += 1
            for i in enemies_list:
                i.hp += level * 10
        
        if(level % 3 == 0 and level != 0 and (last_w_menu_level != level)):
            w_menu_open = True
            last_w_menu_level = level

    # Draw menu overlay if open
    if w_menu_open:
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        center_x = (screen.get_width() // 2) - 20
        center_y = (screen.get_height() // 2) - 20


        panel_w, panel_h = 420, 240
        panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
        panel_rect.center = (center_x, center_y - 20)

        pygame.draw.rect(screen, (30, 30, 30), panel_rect, border_radius=8)
        pygame.draw.rect(screen, (200, 200, 200), panel_rect, width=2, border_radius=8)

        menu_surf = font.render("Take Item?", True, (200, 255, 255))
        menu_rect = menu_surf.get_rect(center=(center_x, panel_rect.top + 36))
        screen.blit(menu_surf, menu_rect)

        for i, opt in enumerate(yes_no):
            color = (255, 255, 100) if i == selected_idx_w else (255, 255, 255)
            opt_surf = font.render(opt, True, color)

            opt_rect = opt_surf.get_rect(center=(center_x, panel_rect.top + 100 + i * 60))
            screen.blit(opt_surf, opt_rect)

    # Draw menu overlay if open
    if menu_open:
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        center_x = (screen.get_width() // 2) - 20
        center_y = (screen.get_height() // 2) - 20


        panel_w, panel_h = 420, 240
        panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
        panel_rect.center = (center_x, center_y - 20)

        pygame.draw.rect(screen, (30, 30, 30), panel_rect, border_radius=8)
        pygame.draw.rect(screen, (200, 200, 200), panel_rect, width=2, border_radius=8)

        title_surf = font.render("Menu", True, (200, 255, 255))
        title_rect = title_surf.get_rect(center=(center_x, panel_rect.top + 36))
        screen.blit(title_surf, title_rect)

        for i, opt in enumerate(menu_options):
            color = (255, 255, 100) if i == selected_idx else (255, 255, 255)
            opt_surf = font.render(opt, True, color)
            opt_rect = opt_surf.get_rect(center=(center_x, panel_rect.top + 100 + i * 60))
            screen.blit(opt_surf, opt_rect)

    pygame.display.flip()
    clock.tick(30)

    if main_player.hp == 0:
        print("El juego ha terminado: el jugador perdió.")
        running = False