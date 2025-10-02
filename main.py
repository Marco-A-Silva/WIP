import pygame
from funcionalidades import Player as player, Enemy as enemy
from funcionalidades import Item as item, Weapon as weapon, MagicWeapon as magic_weapon
import json

pygame.init()
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()
running = True

with open("SaveState.json", "r") as f:
    data = json.load(f)
    equipped_weapon = magic_weapon(data["weapon"]["name"], data["weapon"]["m_damage"], data["weapon"]["magic_dmg"])
    main_player = player(data["player_hp"], data["player_mp"], equipped_weapon)
    enemy1 = enemy(data["enemy_hp"])
    level = data["level"]
    

font = pygame.font.SysFont("Arial", 30)
MyTurn = True
menu_title = font.render("Menu", True, (255, 255, 255))

menu_open = False
menu_options = ["Continue", "Quit to Desktop"]
selected_idx = 0

while running:
    screen.fill("black")
    texto = font.render("Player hp: " + str(main_player.hp) + " mp: " + str(main_player.mp), True, (255, 255, 255))
    texto2 = font.render("Enemy hp: " + str(enemy1.hp), True, (255, 255, 255))
    screen.blit(texto, (150, 120))
    screen.blit(texto2, (150, 160))

    # Safely get events;
    try:
        events = pygame.event.get()
    except Exception:
        # Ensure internal event queue is updated so input still works
        pygame.event.pump()
        events = []

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
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if selected_idx == 0:  # "Continue"
                        menu_open = False
                    elif selected_idx == 1:  # Quit to Desktop
                        with open("SaveState.json", "w") as w:
                            json.dump({
                                "player_hp": main_player.hp,
                                "player_mp": main_player.mp,
                                "enemy_hp": enemy1.hp,
                                "level": level,
                                "weapon": {
                                    "name": equipped_weapon.name,
                                    "m_damage": equipped_weapon.m_damage,
                                    "magic_dmg": getattr(equipped_weapon, "magic_dmg", 0)
                                }
                            }, w, indent=4)
                        running = False

    # Game input only when menu is not open
    if not menu_open:
        keys = pygame.key.get_pressed()

        # Turn-based logic
        if MyTurn:
            if keys[pygame.K_w]:
                main_player.weapon.melee_attack(main_player, enemy1)
                MyTurn = False
            elif keys[pygame.K_a] and getattr(main_player.weapon, "magic_dmg", None) is not None:
                if main_player.mp >= 10:
                    main_player.weapon.cast_spell(main_player, enemy1)
                    MyTurn = False
        elif not MyTurn and keys[pygame.K_s]:
            main_player.take_damage(1)
            MyTurn = True

        # Game in general
        if MyTurn:
            screen.blit(font.render("Mi Turno", True, (255, 255, 255)), (10, 10))
        else:
            screen.blit(font.render("Turno Enemigo", True, (255, 255, 255)), (10, 10))

        if enemy1.hp == 0:
            level += 1
            enemy1.hp = 100 + level * 10


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