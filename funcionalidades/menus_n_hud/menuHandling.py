import pygame
import json
import copy
from random import randint, choices

def menuControl(myTurn, events, state, weaponry, bl_length, menu_list, options, selected_id, main_player, enemies_list_serialized, level, isLastWeaponShopLevel, isLastShopLevel, save_path, running):
    
    shop_items = options[2]

    for event in events:
        if event.type == pygame.QUIT:
                running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                    if(menu_list["Pause"]):
                        menu_list["Pause"] = False
                    else: menu_list["Pause"] = True
                    selected_id = 0
            
            elif myTurn or any(menu_list):
                if state == "menu" and myTurn:
                    if event.key == pygame.K_LSHIFT: state = "attack"
                    elif event.key == pygame.K_LCTRL: state = "items"
                    elif event.key == pygame.K_a and getattr(main_player.weapon, "magic_dmg", 0) is not 0: state = "attack"
                elif event.key == pygame.K_b:
                    state = "menu"

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
                                        item_names = [item.name for item in main_player.items]
                                        with open(save_path, "w") as w:
                                            json.dump({
                                                "level": level,
                                                "player_hp": main_player.hp,
                                                "player_mp": main_player.mp,
                                                "items": item_names,
                                                "weapon": {
                                                    "name": main_player.weapon.name,
                                                    "m_damage": main_player.weapon.m_damage,
                                                    "magic_dmg": getattr(main_player.weapon, "magic_dmg", 0)
                                                },
                                                "armor": {
                                                    "name": main_player.armor.name,
                                                    "dmg_red": main_player.armor.dmg_red
                                                },
                                                "enemies": enemies_list_serialized
                                            }, w, indent=4)
                                        running = False
                                        
                    case {"Weapons": True}:
                        match event.key:
                            case pygame.K_UP | pygame.K_w:
                                selected_id = (selected_id - 1) % len(options[1])
                            case pygame.K_DOWN | pygame.K_s:
                                selected_id = (selected_id + 1) % len(options[1])
                            case pygame.K_RETURN | pygame.K_KP_ENTER:
                                if selected_id == 0:  # "Yes"
                                    x = randint(0, bl_length-1)   
                                    main_player.equip_armament(weaponry[x])

                                menu_list["Weapons"] = False
                                isLastWeaponShopLevel = True
                                selected_id = 0
                    
                    case {"Shop": True}:
                        match event.key:
                            case pygame.K_UP | pygame.K_w:
                                selected_id = (selected_id - 1) % len(options[2])
                            case pygame.K_DOWN | pygame.K_s:
                                selected_id = (selected_id + 1) % len(options[2])
                            case pygame.K_RETURN | pygame.K_KP_ENTER:
                                main_player.equip_armament(shop_items[selected_id][0])
                                main_player.gold_remove(shop_items[selected_id][1])
                                menu_list["Shop"] = False
                                isLastShopLevel = True
                                selected_id = 0
                    
    return selected_id, running, isLastWeaponShopLevel, isLastShopLevel, state
                

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


def drawShopMenu(display, items, random_items, selected_idx_s):
    overlay = pygame.Surface(display[0].get_size(), pygame.SRCALPHA)
    display[0].fill("black")
    overlay.fill((0, 0, 0, 160))
    display[0].blit(overlay, (0, 0))

    bg_color = (30, 144, 255)      # color del rectángulo
    padding = 10                   # pixeles alrededor del texto
    border_radius = 8              # redondeo opcional

    center_x = (display[0].get_width() // 2) - 20
    center_y = (display[0].get_height() // 2) - 20

    merchant_img = pygame.image.load("assets/shopkeeper.png").convert_alpha()
    merchant_img = pygame.transform.scale(merchant_img, (display[0].get_width(), display[0].get_height()))

    merchant_rect = merchant_img.get_rect(center=(center_x, center_y))
    display[0].blit(merchant_img, merchant_rect)
    
    if not random_items: 
        random_items = choices(items, k=5)
        items_chosen = True

    for i, opt in enumerate(random_items):
        # opt[0] es el item, opt[1] es el precio
        color_text = (255, 255, 100) if i == selected_idx_s else (255, 255, 255)
        color_bg = (50, 50, 50) if i == selected_idx_s else (30, 30, 30)

        # Renderiza el texto
        opt_surf = display[1].render(opt[0].name + " - $" + str(opt[1]), True, color_text)
        width, height = display[1].size(opt[0].name)
        
        # Rectángulo de fondo con padding
        padding = 10
        bg_rect = pygame.Rect(0, 0,
                            opt_surf.get_width() + padding*2,
                            opt_surf.get_height() + padding*2)
        
        # Posición del rectángulo
        match i:
            case 0:
                bg_rect.center = (center_x - 320, center_y + 180)
            case 1: 
                bg_rect.center = (center_x - 30, center_y + 180)
            case 2:
                bg_rect.center = (center_x + 300, center_y + 180)
            case 3:
                bg_rect.center = (center_x - 180, center_y + 250)
            case 4:
                bg_rect.center = (center_x + 120, center_y + 250)


                
        
        # Dibuja el rectángulo de fondo
        pygame.draw.rect(display[0], color_bg, bg_rect, border_radius=8)
        
        # Dibuja el texto centrado dentro del rect
        text_pos = (bg_rect.x + padding, bg_rect.y + padding) 
        display[0].blit(opt_surf, text_pos)

    return random_items
