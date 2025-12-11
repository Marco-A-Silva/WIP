import pygame
import json
import copy
from random import randint, choices
from vault.events import Event
from funcionalidades.combat_n_entities.characters import Player

def menuControl(myTurn, events, randEvent: Event, eventContext, state, weaponry, bl_length, menu_list,
                options, selected_id, main_player: Player, advParty, enemies_list_serialized, level, 
                isLastWeaponShopLevel, isLastShopLevel, save_path, running, rects, targetArrow, maxTarget):
    
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
                if (event.key == pygame.K_LEFT or event.key == pygame.K_UP) and targetArrow != 0: targetArrow -= 1
                if (event.key == pygame.K_RIGHT or event.key == pygame.K_DOWN) and targetArrow < maxTarget: targetArrow += 1

                if state == "menu" and myTurn and not any(menu_list.values()):
                    if event.key == pygame.K_LSHIFT: state = "attack"
                    elif event.key == pygame.K_LCTRL: state = "items"
                    elif event.key == pygame.K_a and getattr(main_player.weapon, "magic_dmg", 0) != 0: state = "attack"
                    elif event.key == pygame.K_s: state = "skills"
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
                                        advParty_serialized = []

                                        for player in advParty:
                                            advParty_serialized.append({
                                                "player_name": player.name,
                                                "player_hp": player._hp,
                                                "player_max_hp": player.max_hp,
                                                "player_mp": player.mp,
                                                "player_max_mp": player.max_mp,
                                                "player_sta": player.sta,
                                                "player_max_sta": player.max_sta,
                                                "player_statBlock": player.statBlock,
                                                "weapon": {
                                                    "name": player.weapon.name,
                                                    "melee_dmg": player.weapon.melee_dmg,
                                                    "magic_dmg": getattr(player.weapon, "magic_dmg", 0),
                                                    "skills": list(player.weapon.skills.keys())
                                                },
                                                "armor": {
                                                    "name": player.armor.name,
                                                    "dmg_red": player.armor.dmg_red
                                                },
                                                "items": [item.name for item in player.items]
                                            })

                                        with open(save_path, "w") as w:
                                            json.dump({
                                                "level": level,
                                                "advParty": advParty_serialized,
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
                                    main_player.equip_armament(weaponry[x], True)
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
                                if main_player.gd - shop_items[selected_id][1] > 0:
                                    
                                    main_player.equip_armament(shop_items[selected_id][0])
                                    main_player.gold_remove(shop_items[selected_id][1])
                                    menu_list["Shop"] = False
                                    isLastShopLevel = True
                                    selected_id = 0
                            case pygame.K_p:
                                menu_list["Shop"] = False
                                isLastShopLevel = True
                                selected_id = 0

                    case {"randEvent": True}:
                        match event.key:
                            case pygame.K_UP | pygame.K_w:
                                selected_id = (selected_id - 1) % len(options[3])
                            case pygame.K_DOWN | pygame.K_s:
                                selected_id = (selected_id + 1) % len(options[3])
                            case pygame.K_RETURN | pygame.K_KP_ENTER:

                                if selected_id == 0:
                                    randEvent.answer = 0 
                                if selected_id == 1:
                                    randEvent.answer = 1
                                randEvent.resolveEvent(eventContext)        
                                menu_list["randEvent"] = False
                                selected_id = 0

        elif  event.type == pygame.MOUSEBUTTONDOWN:
            match menu_list:
                case {"lvlUp": True}:
                    mouse_pos = pygame.mouse.get_pos()
                    for i, rect in enumerate(rects[0]):
                        if rect.collidepoint(mouse_pos):
                            print("Click izquierdo en:", mouse_pos)
                    
                            if event.button == 1:   # botón izquierdo
                                main_player.statBlock[i] += 1
                                menu_list["lvlUp"] = False
                                main_player.updStats(i)


    return selected_id, running, isLastWeaponShopLevel, isLastShopLevel, state, targetArrow
                

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

    title_surf = display[1][0].render("Menu", True, (200, 255, 255))
    title_rect = title_surf.get_rect(center=(center_x, panel_rect.top + 36))
    display[0].blit(title_surf, title_rect)

    for i, opt in enumerate(menu_options):
        color = (255, 255, 100) if i == selected_idx else (255, 255, 255)
        opt_surf = display[1][0].render(opt, True, color)
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

    menu_surf = display[1][0].render("Take Item?", True, (200, 255, 255))
    menu_rect = menu_surf.get_rect(center=(center_x, panel_rect.top + 36))
    display[0].blit(menu_surf, menu_rect)

    for i, opt in enumerate(options):
        color = (255, 255, 100) if i == selected_idx_w else (255, 255, 255)
        opt_surf = display[1][0].render(opt, True, color)

        opt_rect = opt_surf.get_rect(center=(center_x, panel_rect.top + 100 + i * 60))
        display[0].blit(opt_surf, opt_rect)


def drawShopMenu(display, items, random_items, selected_idx_s):
    item_rects = []  # <-- lista para guardar los rects

    overlay = pygame.Surface(display[0].get_size(), pygame.SRCALPHA)
    display[0].fill("black")
    overlay.fill((0, 0, 0, 160))
    display[0].blit(overlay, (0, 0))

    bg_color = (30, 144, 255)
    padding = 10
    border_radius = 8

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
        color_text = (255, 255, 100) if i == selected_idx_s else (255, 255, 255)
        color_bg = (50, 50, 50) if i == selected_idx_s else (30, 30, 30)

        opt_surf = display[1][0].render(opt[0].name + " - $" + str(opt[1]), True, color_text)

        bg_rect = pygame.Rect(0, 0,
                              opt_surf.get_width() + padding*2,
                              opt_surf.get_height() + padding*2)

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

        pygame.draw.rect(display[0], color_bg, bg_rect, border_radius=8)
        text_pos = (bg_rect.x + padding, bg_rect.y + padding)
        display[0].blit(opt_surf, text_pos)

        item_rects.append(bg_rect)  # <-- guardo cada rect

    return random_items, item_rects  # <-- devuelvo los rects también

def drawLevelUpMenu(display, player, selected_idx):
    overlay = pygame.Surface(display[0].get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    display[0].blit(overlay, (0, 0))

    stats = [
        "Vitality " + str(player.statBlock[0]),
        "Mind " + str(player.statBlock[1]),
        "Inteligence " + str(player.statBlock[2]),
        "Strength " + str(player.statBlock[3]),
        "Luck " + str(player.statBlock[4]),
        "Charisma " + str(player.statBlock[5]),
        "Awareness " + str(player.statBlock[6]),
        "Greed " + str(player.statBlock[7]),
        "Endurance " + str(player.statBlock[8]),
        "Dexterity " + str(player.statBlock[9])
    ]

    # Menú alto y angosto
    menu_w, menu_h = 300, 400
    menu_x = (display[0].get_width() - menu_w) // 2
    menu_y = (display[0].get_height() - menu_h) // 2
    menu_rect = pygame.Rect(menu_x, menu_y, menu_w, menu_h)
    pygame.draw.rect(display[0], (50, 50, 60), menu_rect, border_radius=14)

    rects = []

    rows = 5
    cols = 2
    padding_x = 20
    padding_y = 20

    font = pygame.font.SysFont(None, 32)

    idx = 0
    for r in range(rows):
        for c in range(cols):
            # Posición aproximada de la celda
            cell_w = (menu_w - padding_x * (cols + 1)) // cols
            cell_h = 55
            cell_x = menu_x + padding_x + c * (cell_w + padding_x)
            cell_y = menu_y + padding_y + r * (cell_h + padding_y)

            # Render del texto
            text = font.render(stats[idx], True, (230, 230, 240))
            text_rect = text.get_rect(center=(cell_x + cell_w//2, cell_y + cell_h//2))
            display[0].blit(text, text_rect)

            # La hitbox será exactamente el tamaño del texto
            hitbox = text.get_rect(topleft=text_rect.topleft)
            rects.append(hitbox)
            idx += 1

    return rects
