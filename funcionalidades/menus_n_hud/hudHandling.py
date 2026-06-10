import pygame
from random import randint
from funcionalidades.Utility.information import addHover

counter = 1

hp_bar_state = {}   # afuera, por ejemplo en tu archivo de HUD

def drawStatEffs(char, display, last_pmember):
    statuses_imgs = []
    statuses_tags = []
    seen_tags = set()

    # --- cargar imágenes y tags ---
    if char.stat_effs:
        for stat in char.stat_effs:
            for tag in stat.tags:
                if tag in seen_tags:
                    continue

                try:
                    img = pygame.image.load(f"assets/statuses/{tag}.png")
                except FileNotFoundError:
                    print(f"[WARN] Falta asset para tag: {tag}")
                    continue

                statuses_imgs.append(img)
                statuses_tags.append(tag)
                seen_tags.add(tag)

    COLS = 4
    ICON_SIZE = 32
    X_SPACING = 30
    Y_SPACING = 30

    mouse_pos = pygame.mouse.get_pos()

    hovered_tag = None
    hovered_pos = None

    for i, img in enumerate(statuses_imgs):
        u = len(statuses_imgs) - 1

        img = pygame.transform.scale(img, (ICON_SIZE, ICON_SIZE))

        col = i % COLS
        row = i // COLS

        img_rect = img.get_rect(
            center=(
                last_pmember - 18 - (X_SPACING * col),
                17 + (Y_SPACING * row)
            )
        )

        # --- TUS RECTÁNGULOS (sin tocar) ---
        if u == 0:
            pygame.draw.rect(
                display[0], (200,200,255), img_rect, 2,
                border_radius=10,
                border_bottom_right_radius=0,
                border_top_left_radius=0
            )
        elif i == 0:
            pygame.draw.rect(
                display[0], (200,200,255), img_rect, 2,
                border_top_right_radius=10
            )
        else:
            pygame.draw.rect(display[0], (200,200,255), img_rect, 2)

        display[0].blit(img, img_rect)

        # --- detectar hover (NO dibujar tooltip acá) ---
        if img_rect.collidepoint(mouse_pos):
            hovered_tag = statuses_tags[i]
            hovered_pos = mouse_pos

    # ==========================
    # TOOLTIP AL FINAL (Z-INDEX)
    # ==========================
    if hovered_tag:
        tooltip = display[1][1].render(hovered_tag, True, (255,255,255))
        pad = 6

        tooltip_rect = tooltip.get_rect(
            topleft=(hovered_pos[0] + 10, hovered_pos[1] + 10)
        )

        bg_rect = tooltip_rect.inflate(pad * 2, pad * 2)

        pygame.draw.rect(display[0], (20,20,30), bg_rect, border_radius=6)
        pygame.draw.rect(display[0], (200,200,255), bg_rect, 1, border_radius=6)
        display[0].blit(tooltip, tooltip_rect)

def drawAdvStats(char, display, width, height, length, i, partyTurn, myTurn):

    y = 130

    # Fondo
    pygame.draw.rect(display[0], (50,50,50), (length, y, width, height), border_radius=10)
    pygame.draw.rect(display[0], (200,200,255), (length, y, width, height), 2, border_radius=10)

    # Highlight
    if i == partyTurn and myTurn:
        glow = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(glow, (255, 255, 0, 120), (0, 0, width, height), width=4, border_radius=10)
        pygame.draw.rect(glow, (255, 255, 0, 80), (2, 2, width-4, height-4), width=2, border_radius=8)
        display[0].blit(glow, (length, y))

    # ====================================================
    #   LISTA DE STATS: 10 BASE + DMG RED AL FINAL
    # ====================================================
    stat_names = ["vit", "mnd", "int", "str", "lck", "chr", "awe", "agi", "end", "dex", "def"]
    stat_values = list(char.statBlock) + [char.dmgRed()]

    label_font = display[1][2]
    value_font = display[1][2]

    # Columnas como antes
    col1_x = length + 20
    col2_x = length + width//2 +10

    spacing = 15
    start_y = y + 10

    for idx, name in enumerate(stat_names):
        value = stat_values[idx]

        # Primeras 6 en columna 1 (vit–gre + dmg red)
        if idx < 6:  
            x_label = col1_x
            x_value = col1_x + 70
            y_line = start_y + idx * spacing
        else:
            # Las restantes en columna derecha
            x_label = col2_x
            x_value = col2_x + 70
            y_line = start_y + (idx - 6) * spacing

        lbl = label_font.render(name.upper() + ":", True, (255, 255, 255))
        val = value_font.render(str(value), True, (200, 200, 255))

        display[0].blit(lbl, (x_label, y_line))
        display[0].blit(val, (x_value, y_line))


def drawAdvParty(char, display, i, last_pmember, length, partyTurn, myTurn, tabPressed):

    width_px, height_px = display[1][0].size(char.name + "  ")
    last_pmember = max(240, width_px + 20)
    pygame.draw.rect(display[0], (50,50,50), (length, 0, length + 240, 130), border_radius=10)
    pygame.draw.rect(display[0], (200,200,255), (length, 0, length + 240, 130), 2, border_radius=10)
    drawStatEffs(char,display,last_pmember)
    print(length, last_pmember)

    if tabPressed:
        drawAdvStats(char,display,last_pmember, 105, length, i, partyTurn, myTurn)

    draw_bar(display[0],25+length,77,190, 2, char.sta, char.max_sta, hp_bar_state, f"STA_{i}", (50, 200, 110) if char.sta > min(getattr(char.weapon["secondary"], "weight", 100)*8, char.weapon["primary"].weight*8) else (255, 20, 110), (0, 0, 0))
    draw_bar(display[0],20+length,80,200, 15, char._hp, char.max_hp, hp_bar_state, f"HP_{i}", (50, 200, 50), (255, 255, 255))
    draw_bar(display[0],20+length,100,200, 15, char.mp, char.max_mp, hp_bar_state, f"MP_{i}", (50, 50, 200), (255, 255, 255))
    draw_bar(display[0],20+length,119,200, 6, char.xp, char.xp2level, hp_bar_state, f"XP_{i}", (178, 213, 255), (255,255,255) if char.xp < char.xp2level*0.1 else (20, 20, 20))

    texto = display[1][0].render(char.name + " ", True, (255, 255, 255))
    display[0].blit(texto, (20+length, 20))

    texto = display[1][1].render(str(char.gd) + "g", True, (255, 255, 255))
    display[0].blit(texto, (20+length, 50))

    if i == partyTurn and myTurn:
        glow = pygame.Surface((last_pmember, 130), pygame.SRCALPHA)
        pygame.draw.rect(glow, (255, 255, 0, 120), (0, 0, last_pmember, 130), width=4, border_radius=10)
        pygame.draw.rect(glow, (255, 255, 0, 80), (2, 2, last_pmember-4, 130-4), width=2, border_radius=8)
        display[0].blit(glow, (length, 0))

    length += last_pmember
    return last_pmember, length, tabPressed

def draw_round_rect_scaled(surface, color, rect, radius):
    x, y, w, h = rect

    # Escala para suavidad (entre 2x y 4x)
    scale = 3
    surf = pygame.Surface((w * scale, h * scale), pygame.SRCALPHA)

    pygame.draw.rect(surf,color,(0, 0, w * scale, h * scale),border_radius=radius * scale)

    # Escalar abajo con suavizado
    smooth = pygame.transform.smoothscale(surf, (w, h))
    surface.blit(smooth, (x, y))

def draw_bar(surface, x, y, width, height, current, max_, state_dict, key, color, textColor):
    if key not in state_dict:
        state_dict[key] = float(current)

    speed = 0.15
    state_dict[key] += (current - state_dict[key]) * speed
    shown = state_dict[key]

    ratio = max(0, min(1, shown / max_))
    current_width = int(width * ratio)

    radius = height // 2

    # Fondo
    draw_round_rect_scaled(surface, (40, 40, 40), (x, y, width, height), radius)

    # Barra
    if current_width > 0:
        draw_round_rect_scaled(surface, color, (x, y, current_width, height), radius)

    # Texto
    font_size = max(8, int(height * 0.75))
    font = pygame.font.SysFont("Arial", font_size)
    text = str(key)[0:-2]

    if textColor != (0,0,0):
        label = font.render(text+": "+str(int(current))+"/"+str(int(max_)), True, textColor)
        padding = int(height * 0.2)
        text_x = x + padding
        text_y = y + (height - label.get_height()) // 2

        surface.blit(label, (text_x, text_y))

def drawScreen(display, action, stateOptions, actionStates, states, state, my_turn, advParty, floor, level,
               enemies_list, enemies_list_is_serialized, partyTurn, tabPressed):

    enemies_list_serialized = None
    
    display[0].fill("black")

    last_pmember = None
    length = 0
    for i, char in enumerate(advParty): 
        last_pmember, length, tabPressed = drawAdvParty(char, display, i, last_pmember, length, partyTurn, my_turn, tabPressed)

    drawPlayerHud(display,states, state, stateOptions, action, actionStates)
    
    for i, char in enumerate(advParty):
        x = display[0].get_width() - 600
        y = 300 + i * 40

        if char.weapon["primary"] != None:
            texto = "Primary weapon: "
            texto2 = display[1][0].render(texto,True, display[2])
            a = texto2.get_width()
            display[0].blit(texto2, (x, y))

            
            texto = char.weapon["primary"].name 
            texto2 = display[1][0].render(texto,True, (255,255,255))
            text_rect = texto2.get_rect(topleft=(x+a, y))
            match char.weapon["primary"].type:
                case ["melee"] | ["melee", _]:
                    addHover(display,text_rect,"top",f"{str(int(char.weapon["primary"].dmg))} dmg",f"- scales with: {[key for key in char.weapon["primary"].scaling.keys()]}")
                case ["magic"] | ["magic", _]:
                    addHover(display,text_rect,"top",f"{str(int(char.weapon["primary"].mgc))} mgc",f"- scales with: {[key for key in char.weapon["primary"].scaling.keys()]}")
                case ["secondary"] | ["secondary", _]:
                    addHover(display,text_rect,"top",f"{str(int(char.weapon["primary"].dmg))} dmg",f"{str(int(char.weapon["primary"].dmg_red))} dmg_red",f"- scales with: {[key for key in char.weapon["primary"].scaling.keys()]}")
                case ["ranged"] | ["ranged", _]:
                    addHover(display,text_rect,"top",f"{str(int(char.weapon["primary"].dmg))} dmg",f"{str(int(char.weapon["primary"].ammo))} ammo",f"- scales with: {[key for key in char.weapon["primary"].scaling.keys()]}")
            display[0].blit(texto2, (x + a, y))

        if char.weapon["secondary"] != None:
            texto = "Secondary weapon: "
            texto2 = display[1][0].render(texto,True, display[2])
            text_rect = texto2.get_rect()
            a = texto2.get_width()
            display[0].blit(texto2, (x, y+50))

            texto = char.weapon["secondary"].name
            texto2 = display[1][0].render(texto,True, (255,255,255))
            text_rect = texto2.get_rect(topleft=(x+a, y+50))
            match char.weapon["secondary"].type:
                case ["melee"] | ["melee", _]:
                    addHover(display,text_rect,"top",f"{str(int(char.weapon["secondary"].dmg))} dmg",f"- scales with: {[key for key in char.weapon["secondary"].scaling.keys()]}",f"- scales with: {[key for key in char.weapon["secondary"].scaling.values()]}")
                case ["magic"] | ["magic", _]:
                    addHover(display,text_rect,"top",f"{str(int(char.weapon["secondary"].mgc))} mgc",f"- scales with: {[key for key in char.weapon["secondary"].scaling.keys()]}",f"- scales with: {[key for key in char.weapon["secondary"].scaling.values()]}")
                case ["secondary"] | ["secondary", _]:
                    addHover(display,text_rect,"top",f"{str(int(char.weapon["secondary"].dmg))} dmg",f"{str(char.weapon["secondary"].dmg_red)} dmg_red",f"- scales with: {[key for key in char.weapon["secondary"].scaling.keys()]}",f"- scales with: {[key for key in char.weapon["secondary"].scaling.values()]}")
                case ["ranged"] | ["ranged", _]:
                    addHover(display,text_rect,"top",f"{str(int(char.weapon["secondary"].dmg))} dmg",f"{str(int(char.weapon["secondary"].ammo))} ammo",f"- scales with: {[key for key in char.weapon["secondary"].scaling.keys()]}",f"- scales with: {[key for key in char.weapon["secondary"].scaling.values()]}")
                    
            display[0].blit(texto2, (x + a, y+50))


    # === Enemigos ===
    for i, en in enumerate(enemies_list):
        texto = en.name + " Enemy hp: " + str(int(en.hp)) + " " + str(en.dmg) + " " + str(en.dmg_red)

        texto2 = display[1][0].render(
            texto,
            True, display[2]
        )
        
        display[0].blit(texto2, (150, 300 + i * 40))
        enemies_list_serialized = [
            {"name": e.name, "hp": e.hp, "skills": [skill.name for skill in e.skills]} for e in enemies_list
        ]
        enemies_list_is_serialized = True

    return enemies_list_serialized, enemies_list_is_serialized, tabPressed

def drawLayout(display, level, floorLayout, room, floor):

    layout_sprites = []

    ICON_SIZE = 32
    SPACING = 40
    Y = 20

    font = display[1][1]
    tooltip_font = display[1][2]

    mouse_pos = pygame.mouse.get_pos()

    total = len(floorLayout)
    if total == 0:
        return

    texto = display[1][0].render(str(floor) + "-" + str(room), True, (255, 255, 255))   
    display[0].blit(texto, (display[0].get_width() - texto.get_width() - 6, 8))

    screen_center_x = display[0].get_width() // 2
    total_width = (total - 1) * SPACING
    START_X = screen_center_x - total_width // 2

    # --- cargar sprites ---
    for floor in floorLayout:
        if floor.startswith("extra_"):
            floor = floor[6:]

        try:
            sprite = pygame.image.load(f"assets/tiles/{floor}.png").convert_alpha()
        except FileNotFoundError:
            print(f"[WARN] Falta tile: {floor}")
            continue

        sprite = pygame.transform.scale(sprite, (ICON_SIZE, ICON_SIZE))
        layout_sprites.append(sprite)

    # --- dibujar ---
    for i, sprite in enumerate(layout_sprites):
        x = START_X + SPACING * i
        sprite_rect = sprite.get_rect(center=(x, Y))
        hovering = sprite_rect.collidepoint(mouse_pos)

        pygame.draw.rect(
            display[0],
            (200, 200, 255) if i == level - 1 else (0, 0, 0),
            sprite_rect,
            2,
            border_radius=6
        )

        display[0].blit(sprite, sprite_rect)

        # --- tooltip debajo ---
        if hovering:
            text = tooltip_font.render(floorLayout[i][6:] if floorLayout[i].startswith("extra_") else floorLayout[i], True, (255, 255, 255))
            pad = 4

            text_rect = text.get_rect(
                midtop=(sprite_rect.centerx, sprite_rect.bottom + 6)
            )
            bg_rect = text_rect.inflate(pad * 2, pad * 2)

            pygame.draw.rect(display[0], (20, 20, 30), bg_rect, border_radius=6)
            pygame.draw.rect(display[0], (200, 200, 255), bg_rect, 1, border_radius=6)
            display[0].blit(text, text_rect)

        # --- guion ---
        if i < total - 1:
            dash = font.render("-", True, (200, 200, 255))
            dash_rect = dash.get_rect(center=(x + SPACING // 2, Y))
            display[0].blit(dash, dash_rect)

def drawPlayerHud(display,states, state, stateOptions, action, actionStates):
    # === HUD dinámico ===
    minHudW = 300
    padding = 40

    font = display[1][0]
    max_text_w = 0

    hud_w = max(minHudW, max_text_w + padding)
    padding = 10

    hud_x = 0
    hud_h = 300
    hud_y = display[0].get_height() - hud_h 

    y_offset = hud_y + 10
    for line in states:
        text_surface = font.render(line, True, (255, 255, 255))
        rect = text_surface.get_rect(topleft=(hud_x + 10, y_offset))

        pygame.draw.rect(display[0], ((100,100,100) if line == actionStates[action] else (50,50,50)), rect.inflate(5, 5), border_radius=8)
        display[0].blit(text_surface, rect)
        _, h = font.size(line)
        y_offset += h + 10

        if y_offset > hud_y + hud_h - 20:
            break
    
    y_offset = hud_y + 50
    #pygame.draw.rect(display[0],(100,50,50), (hud_w - 40, y_offset - 50, display[0].get_width() - hud_w + 40, display[0].get_height() - y_offset + 50))

    for line in stateOptions[state]:
        if state != "menu":
            text_surface = font.render(line, True, (255, 255, 255))
            rect = text_surface.get_rect(topleft=(hud_w + 10, y_offset))

            pygame.draw.rect(display[0], ((200,200,200) if states == "targetSel" else (50,50,50)), rect.inflate(5, 5), border_radius=8)
            display[0].blit(text_surface, rect)
            _, h = font.size(line)
            y_offset += h + 10

            if y_offset > hud_y + hud_h - 20:
                break
