import pygame, json, copy, random
from vault.events import Event
from funcionalidades.combat_n_entities.entities import Player
from funcionalidades.Utility.information import addHover

def shopControl(events, selected_id, player, shopIsOpen, shopItems, running):

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
                match event.key:
                    case pygame.K_UP | pygame.K_w:
                        selected_id = (selected_id - 1) % len(shopItems)
                    case pygame.K_DOWN | pygame.K_s:
                        selected_id = (selected_id + 1) % len(shopItems)
                    case pygame.K_RETURN | pygame.K_KP_ENTER:
                        if player.gd - shopItems[selected_id][1] > 0:
                            player.equip_armament(copy.deepcopy(shopItems[selected_id][0]),False)
                            player.gold_remove(shopItems[selected_id][1])
                            shopIsOpen = False 
                            selected_id = 0
                    case pygame.K_p:
                        shopIsOpen = False
                        selected_id = 0

    return selected_id, shopIsOpen, running

def eventControl(events, selected_id, player, eventIsOpen, staticEvent, context, running):
    
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
                match event.key:
                        case pygame.K_UP | pygame.K_w:
                            selected_id = (selected_id - 1) % len(staticEvent.actions)
                        case pygame.K_DOWN | pygame.K_s:
                            selected_id = (selected_id + 1) % len(staticEvent.actions)
                        case pygame.K_RETURN | pygame.K_KP_ENTER:
                            staticEvent.answer = selected_id
                            staticEvent.resolveEvent(context)
                            eventIsOpen = False
                            selected_id = 0
                        case pygame.K_p:
                            eventIsOpen = False
                            selected_id = 0
    
    return selected_id, eventIsOpen, running

def treasureControl(events, selected_id, player, chestWillOpen, chest_pool, running):

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
                match event.key:
                        case pygame.K_UP | pygame.K_w:
                            selected_id = (selected_id - 1) % len(chest_pool)
                        case pygame.K_DOWN | pygame.K_s:
                            selected_id = (selected_id + 1) % len(chest_pool)
                        case pygame.K_RETURN | pygame.K_KP_ENTER:
                            player.equip_armament(chest_pool[selected_id],False)
                            chest_pool.pop(selected_id)
                            if not chest_pool:
                                chestWillOpen = False
                                selected_id = 0
                        case pygame.K_p:
                            chest_pool.clear()
                            chestWillOpen = False
                            selected_id = 0
    
    return selected_id, chestWillOpen, running

def extraControl(extra, player, selected_id, events, options, extraIsOpen, running):

    for event in events:
        if event.type == pygame.QUIT:
                running = False
        elif event.type == pygame.KEYDOWN:
            match extra:
                case "rest site":
                    match event.key:
                        case pygame.K_UP | pygame.K_w:
                            selected_id = (selected_id - 1) % len(options[0])
                        case pygame.K_DOWN | pygame.K_s:
                            selected_id = (selected_id + 1) % len(options[0])
                        case pygame.K_RETURN | pygame.K_KP_ENTER:
                            match selected_id:
                                case 0: #Sleep
                                    player.statBlock[8] += 1 #Endurance
                                    player.max_sta = player.sta
                                case 1: #Guard
                                    player.statBlock[6] += 1 #Awareness
                                    player.statBlock[9] += 1 #Dexterity
                                case 2: #Eat
                                    player._hp += player.max_hp * 0.10

                            extraIsOpen = False 
                            selected_id = 0
                        case pygame.K_p:
                            extraIsOpen = False
                            selected_id = 0
                case "school of magic":
                    match event.key:
                        case pygame.K_UP | pygame.K_w:
                            selected_id = (selected_id - 1) % len(options[1])
                        case pygame.K_DOWN | pygame.K_s:
                            selected_id = (selected_id + 1) % len(options[1])
                        case pygame.K_RETURN | pygame.K_KP_ENTER:
                            if selected_id == 0:
                                #learn
                                pass
                            else:
                                pass

                            extraIsOpen = False 
                            selected_id = 0
                        case pygame.K_p:
                            extraIsOpen = False
                            selected_id = 0
                case "dojo":
                    match event.key:
                        case pygame.K_UP | pygame.K_w:
                            selected_id = (selected_id - 1) % len(options[2])
                        case pygame.K_DOWN | pygame.K_s:
                            selected_id = (selected_id + 1) % len(options[2])
                        case pygame.K_RETURN | pygame.K_KP_ENTER:
                            if selected_id == 0:
                                #learn
                                pass
                            else:
                                pass
                            extraIsOpen = False 
                            selected_id = 0
                        case pygame.K_p:
                            extraIsOpen = False
                            selected_id = 0

    return running, extraIsOpen, selected_id

def menuControl(myTurn, events, randEvent: Event, eventContext, state, weaponry, bl_length, menu_list,
                options, selected_id, main_player: Player, advParty, enemies_list_serialized, room, 
                save_path, running, rects, pending_levels, appState):
    
    shop_items = options[2]

    for event in events:
        if event.type == pygame.QUIT:
                running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                    if(menu_list["pause"]):
                        menu_list["pause"] = False
                    else: menu_list["pause"] = True
                    selected_id = 0
            
            elif myTurn or any(menu_list):

                if state == "menu" and myTurn and not any(menu_list.values()) and appState == "game":
                    if event.key == pygame.K_LSHIFT: state = "attack"
                    elif event.key == pygame.K_LCTRL: state = "items"
                    elif event.key == pygame.K_a and getattr(main_player.weapon, "mgc", 0) != 0: state = "attack"
                    elif event.key == pygame.K_s: state = "skills"
                elif event.key == pygame.K_b:
                    state = "menu"

                match menu_list:
                    case {"pause": True}:
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

                                            armor_serialized = []
                                            pos = [armor.type for armor in player.armor.values() if armor is not None]
                                            for key in pos:
                                                armor_serialized.append({
                                                    "name": player.armor[key].name,
                                                    "type": player.armor[key].type,
                                                    "dmg_red": player.armor[key].dmg_red
                                                }) 

                                            weapons_serialized = []
                                            names = ["primary", "secondary"]
                                            for key in player.weapon.keys():
                                                if player.weapon[key] is not None:
                                                    match player.weapon[key].type:
                                                        case "melee":
                                                            weapons_serialized.append({
                                                                "name": player.weapon[key].name,
                                                                "type": "melee",
                                                                "dmg": player.weapon[key].base_dmg,
                                                                "weight": player.weapon[key].weight,
                                                                "skills": list(player.weapon[key].skills.keys())
                                                            })

                                                        case "magic":
                                                            weapons_serialized.append({
                                                                "name": player.weapon[key].name,
                                                                "type": "magic",
                                                                "dmg": player.weapon[key].dmg,
                                                                "mgc": player.weapon[key].base_mgc,
                                                                "weight": player.weapon[key].weight,
                                                                "mana_cost": player.weapon[key].mana_cost,
                                                                "skills": list(player.weapon[key].skills.keys())
                                                            })

                                                        case "ranged":         
                                                            weapons_serialized.append({
                                                                "name": player.weapon[key].name,
                                                                "type": "ranged",
                                                                "dmg": player.weapon[key].base_dmg,
                                                                "weight": player.weapon[key].weight,
                                                                "ammo": player.weapon[key].ammo,
                                                                "ammoReq": player.weapon[key].ammoReq,
                                                                "skills": list(player.weapon[key].skills.keys())
                                                            })
  
                                                        case "secondary":
                                                            weapons_serialized.append({
                                                                "name": player.weapon[key].name,
                                                                "type": "secondary",
                                                                "dmg": player.weapon[key].base_dmg,
                                                                "weight": player.weapon[key].weight,
                                                                "dmg_red": player.weapon[key].base_red,
                                                                "stat": player.weapon[key].stat,
                                                                "skills": list(player.weapon[key].skills.keys())
                                                            })

                                            advParty_serialized.append({
                                                "player_name": player.name,
                                                "player_hp": player._hp,
                                                "player_max_hp": player.max_hp,
                                                "player_mp": player.mp,
                                                "player_max_mp": player.max_mp,
                                                "player_sta": player.sta,
                                                "player_max_sta": player.max_sta,
                                                "player_statBlock": player.statBlock,
                                                "weapon": {names[i]: weapons_serialized[i] for i,idk in enumerate(weapons_serialized)},
                                                "armor": {pos[i]: armor_serialized[i] for i,idk in enumerate(armor_serialized)},
                                                "items": [item.name for item in player.items]
                                            })

                                        with open(save_path, "w") as w:
                                            json.dump({
                                                "room": room,
                                                "load": False,
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
                                selected_id = 0
                    
                    case {"Shop": True}:
                        match event.key:
                            case pygame.K_UP | pygame.K_w:
                                selected_id = (selected_id - 1) % len(options[2])
                            case pygame.K_DOWN | pygame.K_s:
                                selected_id = (selected_id + 1) % len(options[2])
                            case pygame.K_RETURN | pygame.K_KP_ENTER:
                                if main_player.gd - shop_items[selected_id][1] > 0:
                                    
                                    main_player.equip_armament(shop_items[selected_id][0],False)
                                    main_player.gold_remove(shop_items[selected_id][1])
                                    menu_list["Shop"] = False 
                                    selected_id = 0
                            case pygame.K_p:
                                menu_list["Shop"] = False
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

        elif event.type == pygame.MOUSEBUTTONDOWN:
            match menu_list:
                case {"lvlUp": True}:
                    mouse_pos = pygame.mouse.get_pos()

                    for i, rect in enumerate(rects[0]):
                        if rect.collidepoint(mouse_pos) and event.button == 1:

                            main_player.statBlock[i] += 1
                            pending_levels -= 1

                            if pending_levels > 0:
                                menu_list["lvlUp"] = True
                            else:
                                menu_list["lvlUp"] = False

    return selected_id, running, state, pending_levels

def drawChestMenu(display, item_pools, chest_pool, selected_idx):
    overlay = pygame.Surface(display[0].get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    display[0].blit(overlay, (0, 0))

    center_x = (display[0].get_width() // 2)
    center_y = (display[0].get_height() // 2) 

    chest_img = pygame.image.load("assets/backgrounds/chest_1.png").convert_alpha()
    chest_img = pygame.transform.scale(chest_img, (display[0].get_width(), display[0].get_height()))
    chest_rect = chest_img.get_rect(center=(center_x, center_y))
    display[0].blit(chest_img, chest_rect)

    panel_w, panel_h = 420, 240
    panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
    panel_rect.center = (center_x, center_y - 100)

    pygame.draw.rect(display[0], (30, 30, 30), panel_rect, border_radius=8)
    pygame.draw.rect(display[0], (200, 200, 200), panel_rect, width=2, border_radius=8)

    menu_surf = display[1][0].render("You opened a chest, it had:", True, (200, 255, 255))
    menu_rect = menu_surf.get_rect(center=(center_x, panel_rect.top + 36))
    display[0].blit(menu_surf, menu_rect)

    for i, opt in enumerate(chest_pool):
        color = (255, 255, 100) if i == selected_idx else (255, 255, 255)
        opt_surf = display[1][0].render(opt.name, True, color)

        opt_rect = opt_surf.get_rect(center=(center_x, panel_rect.top + 100 + i * 60))
        display[0].blit(opt_surf, opt_rect)

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

def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "

    if current_line:
        lines.append(current_line)

    return lines

def drawEventMenu(display, event, selected_idx):
    overlay = pygame.Surface(display[0].get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    display[0].blit(overlay, (0, 0))

    center_x = display[0].get_width() // 2
    center_y = display[0].get_height() // 2

    panel_w, panel_h = 420, 240
    panel_rect = pygame.Rect(0, 0, display[0].get_width(), display[0].get_height())
    panel_rect.center = (center_x, center_y)

    pygame.draw.rect(display[0], (30, 30, 30), panel_rect, border_radius=8)
    pygame.draw.rect(display[0], (200, 200, 200), panel_rect, width=2, border_radius=8)

    font = display[1][0]
    max_text_width = panel_w

    lines = wrap_text(event.description, font, max_text_width)

    line_height = font.get_height()
    desc_height = len(lines) * (line_height + 4)
    actions_height = len(event.actions) * 60
    total_height = desc_height + 30 + actions_height

    start_y = panel_rect.centery - total_height // 2

    y_offset = start_y
    for line in lines:
        surf = font.render(line, True, (200, 255, 255))
        rect = surf.get_rect(centerx=center_x + 250, y=y_offset)
        display[0].blit(surf, rect)
        y_offset += surf.get_height() + 4

    actions_start_y = y_offset + 30

    for i, opt in enumerate(event.actions):
        color = (255, 255, 100) if i == selected_idx else (255, 255, 255)
        opt_surf = font.render(opt, True, color)
        opt_rect = opt_surf.get_rect(
            center=(center_x + 250, actions_start_y + i * 60)
        )
        display[0].blit(opt_surf, opt_rect)

def drawShopMenu(display, random_items, selected_idx_s):
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

    for i, opt in enumerate(random_items):
        color_text = (255, 255, 100) if i == selected_idx_s else (255, 255, 255)
        color_bg = (50, 50, 50) if i == selected_idx_s else (30, 30, 30)

        opt_surf = display[1][0].render(opt[0].name, True, color_text)

        bg_rect = pygame.Rect(0, 0,
                              opt_surf.get_width() + padding*2,
                              opt_surf.get_height() + padding*2)

        spacing = 70
        bg_rect.center = (center_x,  500 + i * spacing)


        pygame.draw.rect(display[0], color_bg, bg_rect, border_radius=8)
        text_pos = (bg_rect.x + padding, bg_rect.y + padding)
        display[0].blit(opt_surf, text_pos)
        if getattr(opt[0],"uses",-1) != -1:
            addHover(display,bg_rect,"top",f"uses: {opt[0].uses}", f" - ${str(opt[1])}")
        else:
            match opt[0].type[0]:
                case "melee":
                    addHover(display,bg_rect,"top",f"dmg: {opt[0].dmg}", f" - ${str(opt[1])}",f"- scales with: {[key for key in opt[0].scaling.keys()]}")                
                case "magic":
                    addHover(display,bg_rect,"top",f"mgc: {opt[0].mgc}", f" - ${str(opt[1])}",f"- scales with: {[key for key in opt[0].scaling.keys()]}")                
                case "ranged":
                    addHover(display,bg_rect,"top",f"dmg: {opt[0].dmg}",f" - ammo: {opt[0].ammo}", f" - ${str(opt[1])}",f"- scales with: {[key for key in opt[0].scaling.keys()]}")                
                case "melee":
                    addHover(display,bg_rect,"top",f"dmg: {opt[0].dmg}",f" - dmg_res: {opt[0].dmg_res}", f" - ${str(opt[1])}",f"- scales with: {[key for key in opy[0].scaling.keys()]}")

        item_rects.append(bg_rect)  # <-- guardo cada rect

    return random_items, item_rects  # <-- devuelvo los rects también

def drawLevelUpMenu(display, player, selected_idx, pending_levels):

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
        "Agility " + str(player.statBlock[7]),
        "Endurance " + str(player.statBlock[8]),
        "Dexterity " + str(player.statBlock[9])
    ]

    menu_w, menu_h = 300, 400
    menu_x = (display[0].get_width() - menu_w) // 2
    menu_y = (display[0].get_height() - menu_h) // 2
    menu_rect = pygame.Rect(menu_x, menu_y, menu_w, menu_h)
    pygame.draw.rect(display[0], (50, 50, 60), menu_rect, border_radius=14)

    font = pygame.font.SysFont(None, 32)
    small_font = pygame.font.SysFont(None, 26)

    # 🔹 TEXTO DE LEVELS PENDIENTES
    lvl_text = f"Levels to assign: {pending_levels}"
    lvl_surf = small_font.render(lvl_text, True, (200, 200, 220))
    lvl_rect = lvl_surf.get_rect(
        center=(menu_rect.centerx, menu_rect.top - 18)
    )
    display[0].blit(lvl_surf, lvl_rect)

    rects = []

    rows = 5
    cols = 2
    padding_x = 20
    padding_y = 20

    idx = 0
    for r in range(rows):
        for c in range(cols):
            cell_w = (menu_w - padding_x * (cols + 1)) // cols
            cell_h = 55
            cell_x = menu_x + padding_x + c * (cell_w + padding_x)
            cell_y = menu_y + padding_y + r * (cell_h + padding_y)

            text = font.render(stats[idx], True, (230, 230, 240))
            text_rect = text.get_rect(center=(cell_x + cell_w // 2, cell_y + cell_h // 2))
            display[0].blit(text, text_rect)
            texto = ""
            match index:
                case 0:
                    texto = "+10 HP"
                case 1:
                    texto = "+8 MP"
                case 8:
                    texto = "+8 STA"
                case _:
                    texto = stats[idx]
                    
            addHover(display,text_rect,"bot",texto)

            hitbox = text.get_rect(topleft=text_rect.topleft)
            rects.append(hitbox)

            idx += 1

    return rects

def drawExtraMenu(extra, display, player, selected_id, extraOpts):

    center_x = (display[0].get_width() // 2)
    center_y = (display[0].get_height() // 2) 

    panel_w, panel_h = 420, 240
    panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
    panel_rect.center = (center_x, center_y - 100)

    pygame.draw.rect(display[0], (30, 30, 30), panel_rect, border_radius=8)
    pygame.draw.rect(display[0], (200, 200, 200), panel_rect, width=2, border_radius=8)

    match extra:
        case "rest site":
            extra_img = pygame.image.load("assets/backgrounds/rest site.png").convert_alpha()
            extra_img = pygame.transform.scale(extra_img, (display[0].get_width(), display[0].get_height()))
            extra_rect = extra_img.get_rect(center=(center_x, center_y))
            display[0].blit(extra_img, extra_rect)

            for i, opt in enumerate(extraOpts[0]):
                color = (255, 255, 100) if i == selected_id else (255, 255, 255)
                opt_surf = display[1][0].render(opt, True, color)

                opt_rect = opt_surf.get_rect(center=(center_x, panel_rect.top + 100 + i * 60))
                display[0].blit(opt_surf, opt_rect)

        case "dojo":
            extra_img = pygame.image.load("assets/shopkeeper.png").convert_alpha()
            extra_img = pygame.transform.scale(extra_img, (display[0].get_width(), display[0].get_height()))
            extra_rect = extra_img.get_rect(center=(center_x, center_y))
            display[0].blit(extra_img, extra_rect)

            for i, opt in enumerate(extraOpts[1]):
                color = (255, 255, 100) if i == selected_id else (255, 255, 255)
                opt_surf = display[1][0].render(opt, True, color)

                opt_rect = opt_surf.get_rect(center=(center_x, panel_rect.top + 100 + i * 60))
                display[0].blit(opt_surf, opt_rect)

        case "school of magic":
            extra_img = pygame.image.load("assets/shopkeeper.png").convert_alpha()
            extra_img = pygame.transform.scale(extra_img, (display[0].get_width(), display[0].get_height()))
            extra_rect = extra_img.get_rect(center=(center_x, center_y))
            display[0].blit(extra_img, extra_rect)

            for i, opt in enumerate(extraOpts[2]):
                color = (255, 255, 100) if i == selected_id else (255, 255, 255)
                opt_surf = display[1][0].render(opt, True, color)

                opt_rect = opt_surf.get_rect(center=(center_x, panel_rect.top + 100 + i * 60))
                display[0].blit(opt_surf, opt_rect)

