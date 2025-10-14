import pygame
import json
from random import randint

def menuControl(events, weaponry, menu_list, options, selected_id, shop_items, main_player, enemies_list_serialized, level, isLastWeaponShopLevel, isLastShopLevel, running):
    for event in events:
        if event.type == pygame.QUIT:
                running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                    if(menu_list["Pause"]):
                        menu_list["Pause"] = False
                    else: menu_list["Pause"] = True
                    selected_id = 0
            
            else:
                match menu_list:
                    case {"Pause": True}:
                            match event.key:
                                case pygame.K_UP | pygame.K_w:
                                    selected_id = (selected_id - 1) % len(options[0])
                                    
                                case pygame.K_DOWN | pygame.K_s:
                                    selected_id = (selected_id + 1) % len(options[0])

                                case pygame.K_RETURN | pygame.K_KP_ENTER:
                                    if selected_id == 0:  # "Continue"
                                        menu_list["Pause"] = False
                                        selected_id = 0
                                    elif selected_id == 1:  # Quit to Desktop
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
                                        
                    case {"Weapon Shop": True}:
                        match event.key:
                            case pygame.K_UP | pygame.K_w:
                                selected_id = (selected_id - 1) % len(options[1])
                            case pygame.K_DOWN | pygame.K_s:
                                selected_id = (selected_id + 1) % len(options[1])
                            case pygame.K_RETURN | pygame.K_KP_ENTER:
                                if selected_id == 0:  # "Yes"
                                    x = randint(0, 2)
                                    main_player.equip_weapon(weaponry[x])

                                menu_list["Weapon Shop"] = False
                                isLastWeaponShopLevel = True
                                selected_id = 0
                    
                    case {"Shop": True}:
                        match event.key:
                            case pygame.K_UP | pygame.K_w:
                                selected_id = (selected_id - 1) % len(options[2])
                            case pygame.K_DOWN | pygame.K_s:
                                selected_id = (selected_id + 1) % len(options[2])
                            case pygame.K_RETURN | pygame.K_KP_ENTER:
                                main_player.addItem(shop_items[selected_id][0])
                                main_player.gold_remove(shop_items[selected_id][1])
                                menu_list["Shop"] = False
                                isLastShopLevel = True
                                selected_id = 0
                    
    return selected_id, running, isLastWeaponShopLevel, isLastShopLevel
                

def drawPauseMenu(display, menu_options, selected_idx):
    overlay = pygame.Surface(display[0].get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    display[0].blit(overlay, (0, 0))

    center_x = (display[0].get_width() // 2) - 20
    center_y = (display[0].get_height() // 2) - 20


    panel_w, panel_h = 420, 240
    panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
    panel_rect.center = (center_x, center_y - 20)

    pygame.draw.rect(display[0], (30, 30, 30), panel_rect, border_radius=8)
    pygame.draw.rect(display[0], (200, 200, 200), panel_rect, width=2, border_radius=8)

    title_surf = display[1].render("Menu", True, (200, 255, 255))
    title_rect = title_surf.get_rect(center=(center_x, panel_rect.top + 36))
    display[0].blit(title_surf, title_rect)

    for i, opt in enumerate(menu_options):
        color = (255, 255, 100) if i == selected_idx else (255, 255, 255)
        opt_surf = display[1].render(opt, True, color)
        opt_rect = opt_surf.get_rect(center=(center_x, panel_rect.top + 100 + i * 60))
        display[0].blit(opt_surf, opt_rect)


def drawWeaponMenu(display, options, selected_idx_w):
    overlay = pygame.Surface(display[0].get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    display[0].blit(overlay, (0, 0))

    center_x = (display[0].get_width() // 2) - 20
    center_y = (display[0].get_height() // 2) - 20


    panel_w, panel_h = 420, 240
    panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
    panel_rect.center = (center_x, center_y - 20)

    pygame.draw.rect(display[0], (30, 30, 30), panel_rect, border_radius=8)
    pygame.draw.rect(display[0], (200, 200, 200), panel_rect, width=2, border_radius=8)

    menu_surf = display[1].render("Take Item?", True, (200, 255, 255))
    menu_rect = menu_surf.get_rect(center=(center_x, panel_rect.top + 36))
    display[0].blit(menu_surf, menu_rect)

    for i, opt in enumerate(options):
        color = (255, 255, 100) if i == selected_idx_w else (255, 255, 255)
        opt_surf = display[1].render(opt, True, color)

        opt_rect = opt_surf.get_rect(center=(center_x, panel_rect.top + 100 + i * 60))
        display[0].blit(opt_surf, opt_rect)


def drawShopMenu(display, items, selected_idx_s):
    overlay = pygame.Surface(display[0].get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    display[0].blit(overlay, (0, 0))

    center_x = (display[0].get_width() // 2) - 20
    center_y = (display[0].get_height() // 2) - 20


    panel_w, panel_h = 420, 240
    panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
    panel_rect.center = (center_x, center_y - 20)

    pygame.draw.rect(display[0], (30, 30, 30), panel_rect, border_radius=8)
    pygame.draw.rect(display[0], (200, 200, 200), panel_rect, width=2, border_radius=8)

    menu_surf = display[1].render("Shop", True, (200, 255, 255))
    menu_rect = menu_surf.get_rect(center=(center_x, panel_rect.top + 36))
    display[0].blit(menu_surf, menu_rect)

    for i, opt in enumerate(items): 
        color = (255, 255, 100) if i == selected_idx_s else (255, 255, 255)
        opt_surf = display[1].render(opt[0].name + " - $" + str(opt[1]), True, color)

        opt_rect = opt_surf.get_rect(center=(center_x, panel_rect.top + 100 + i * 60))
        display[0].blit(opt_surf, opt_rect)
