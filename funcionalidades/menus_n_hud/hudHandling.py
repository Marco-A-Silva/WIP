import pygame
from random import randint

hp_bar_state = {}   # afuera, por ejemplo en tu archivo de HUD

def drawAdvStats(char, display, width, height, length, i, partyTurn, myTurn):

    y = 130

    pygame.draw.rect(display[0], (50,50,50), (length, y, width, height), border_radius=10)
    pygame.draw.rect(display[0], (200,200,255), (length, y, width, height), 2, border_radius=10)

    if i == partyTurn and myTurn:
        tooltip_x = length
        tooltip_y = y        # o tu valor actual
        tooltip_w = width
        tooltip_h = height

        glow = pygame.Surface((tooltip_w, tooltip_h), pygame.SRCALPHA)
        pygame.draw.rect(glow, (255, 255, 0, 120),(0, 0, tooltip_w, tooltip_h),width=4, border_radius=10)
        pygame.draw.rect(glow, (255, 255, 0, 80),(2, 2, tooltip_w - 4, tooltip_h - 4),width=2, border_radius=8)
        display[0].blit(glow, (tooltip_x, tooltip_y))

    # texto izquierda
    txt_label = display[1][1].render("Dmg Red:", True, (255, 255, 255))
    display[0].blit(txt_label, (length + 20, y + 5))

    # texto derecha (alineado al borde)
    txt_value = display[1][1].render(str(char.armor.dmg_red), True, (255, 50, 50))
    txt_w, txt_h = txt_value.get_size()

    right_x = length + width - txt_w - 20 

    display[0].blit(txt_value, (right_x, y + 5))


def drawAdvParty(char, display, i, last_pmember, length, partyTurn, myTurn, tabPressed):

    width_px, height_px = display[1][0].size(char.name + "  ")
    last_pmember = max(240, width_px + 20)
    pygame.draw.rect(display[0], (50,50,50), (length, 0, last_pmember, 130), border_radius=10)
    pygame.draw.rect(display[0], (200,200,255), (length, 0, last_pmember, 130), 2, border_radius=10)

    if tabPressed:
        drawAdvStats(char,display,last_pmember, 80, length, i, partyTurn, myTurn)

    draw_bar(display[0],20+length,80,200, 15, char._hp, char.max_hp, hp_bar_state, "HP_"+str(i), (50, 200, 50), (255, 255, 255))
    draw_bar(display[0],20+length,100,200, 15, char.mp, char.max_mp, hp_bar_state, "MP_"+str(i), (50, 50, 200), (255, 255, 255))
    draw_bar(display[0],20+length,119,200, 6, char.xp, char.xp2level, hp_bar_state, "XP_"+str(i), (178, 213, 255), (255,255,255) if char.xp < char.xp2level*0.1 else (20, 20, 20))


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
        display[0].blit(texto, (900,300 +120*i))
    texto = display[1][0].render("- " + char.weapon.name + " " + str(int(char.weapon.melee_dmg)) + " " + str(int(getattr(char.weapon, "magic_dmg", 0))), True, (255,255,255))
    display[0].blit(texto, (900,340 +35*i))
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
    text = str(key)[0:2]
    label = font.render(text+": "+str(int(current))+"/"+str(int(max_)), True, textColor)
    padding = int(height * 0.2)
    text_x = x + padding
    text_y = y + (height - label.get_height()) // 2

    surface.blit(label, (text_x, text_y))



def drawScreen(display, hud_states, state, my_turn, advParty, level, isLastWeaponShopLevel, enemies_list, enemies_list_is_serialized, partyTurn, tabPressed):
    enemies_list_serialized = None
    
    display[0].fill("black")

    texto = display[1][0].render("Level: " + str(level) + " : " + str(isLastWeaponShopLevel), True, (255, 255, 255))   
    display[0].blit(texto, (900, 120))

    last_pmember = None
    length = 0
    for i, char in enumerate(advParty): 
        last_pmember, length, tabPressed = drawAdvParty(char, display, i, last_pmember, length, partyTurn, my_turn, tabPressed)

    pygame.draw.rect(display[0], (50,50,50), (20, display[0].get_height() - 150, display[0].get_width() - 40, 130), border_radius= 10)
    pygame.draw.rect(display[0], (200,200,255), (20, display[0].get_height() - 150, display[0].get_width() - 40, 130), 2, border_radius= 10)

    x_offset = display[0].get_width() - 1230
    for line in hud_states[state]:
        text_surface = display[1][0].render(line, True, (255, 255, 255))
        display[0].blit(text_surface, (x_offset, display[0].get_height() - 130))
        width, height = display[1][0].size(line)
        x_offset += width + 20

    for i, en in enumerate(enemies_list):
        texto2 = display[1][0].render(en.name + " Enemy hp: " + str(int(en.hp)) + " " + str(en.dmg) + " " + str(en.dmg_red), True, display[2])
        display[0].blit(texto2, (150, 300 + i * 40))
        enemies_list_serialized = [{"name": e.name, "hp": e.hp, "skills": list(e.skills.keys())} for e in enemies_list]
        enemies_list_is_serialized = True

    return enemies_list_serialized, enemies_list_is_serialized, tabPressed