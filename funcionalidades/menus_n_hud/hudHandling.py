import pygame
from random import randint

counter = 1

hp_bar_state = {}   # afuera, por ejemplo en tu archivo de HUD

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
    stat_names = ["vit", "mnd", "int", "str", "lck", "chr", "awe", "gre", "end", "dex", "def"]
    stat_values = list(char.statBlock) + [char.armor.dmg_red]

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
    pygame.draw.rect(display[0], (50,50,50), (length, 0, last_pmember, 130), border_radius=10)
    pygame.draw.rect(display[0], (200,200,255), (length, 0, last_pmember, 130), 2, border_radius=10)

    if tabPressed:
        drawAdvStats(char,display,last_pmember, 105, length, i, partyTurn, myTurn)

    draw_bar(display[0],25+length,77,190, 2, char.sta, char.max_sta, hp_bar_state, f"STA_{i}", (50, 200, 110) if char.sta > char.weapon.weight*8 else (255, 20, 110), (0, 0, 0))
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

    if i == 0: 
        texto = display[1][0].render("Equipped Weapon:", True, (255,0,0))
        display[0].blit(texto, (850,300 +120*i))
    texto = display[1][0].render("- " + char.weapon.name + " " + str(int(char.weapon.melee_dmg)) + " " + str(int(getattr(char.weapon, "magic_dmg", 0))), True, (255,255,255))
    display[0].blit(texto, (850,340 +35*i))
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



def drawScreen(display, hud_states, state, my_turn, advParty, level, isLastWeaponShopLevel,
               enemies_list, enemies_list_is_serialized, partyTurn, tabPressed, targetArrow):

    global counter
    counter = (counter + 1) % 80

    enemies_list_serialized = None
    
    display[0].fill("black")

    texto = display[1][0].render("Level: " + str(level) + " : " + str(isLastWeaponShopLevel), True, (255, 255, 255))   
    display[0].blit(texto, (850, 120))

    last_pmember = None
    length = 0
    for i, char in enumerate(advParty): 
        last_pmember, length, tabPressed = drawAdvParty(char, display, i, last_pmember, length, partyTurn, my_turn, tabPressed)

    # === HUD dinámico ===
    minHudW = 300
    padding = 40

    font = display[1][0]
    max_text_w = 0

    for line in hud_states[state]:
        w, _ = font.size(line)
        if w > max_text_w:
            max_text_w = w

    hud_w = max(minHudW, max_text_w + padding)

    hud_x = 0
    hud_h = 250
    hud_y = display[0].get_height() - hud_h 

    pygame.draw.rect(display[0], (50,50,50), (hud_x, hud_y, hud_w, hud_h), border_radius=10)
    pygame.draw.rect(display[0], (200,200,255), (hud_x, hud_y, hud_w, hud_h), 2, border_radius=10)

    y_offset = hud_y + 10
    for line in hud_states[state]:
        text_surface = font.render(line, True, (255, 255, 255))
        display[0].blit(text_surface, (hud_x+10, y_offset))
        _, h = font.size(line)
        y_offset += h + 5

        if y_offset > hud_y + hud_h - 20:
            break

    # === Enemigos ===
    for i, en in enumerate(enemies_list):
        texto = en.name + " Enemy hp: " + str(int(en.hp)) + " " + str(en.dmg) + " " + str(en.dmg_red)
        if i == targetArrow and my_turn and ( (counter // 40) % 2 ) == 0:
            texto += " <---"

        texto2 = display[1][0].render(
            texto,
            True, display[2]
        )
        
        display[0].blit(texto2, (150, 300 + i * 40))
        enemies_list_serialized = [
            {"name": e.name, "hp": e.hp, "skills": list(e.skills.keys())}
            for e in enemies_list
        ]
        enemies_list_is_serialized = True


    return enemies_list_serialized, enemies_list_is_serialized, tabPressed
