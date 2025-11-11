import pygame
from random import randint

def drawScreen(display, hud_states, state, my_turn, main_player, level, isLastWeaponShopLevel, enemies_list, enemies_list_is_serialized):
    enemies_list_serialized = None

    display[0].fill("black")
    texto = display[1].render("Player hp: " + str(main_player.hp) + " " + str(main_player.mp) + " dmg_red: " + str(main_player.armor.dmg_red) + " gold: " + str(main_player.gd), True, (255, 255, 255))
    display[0].blit(texto, (150, 120))
    texto = display[1].render("Level: " + str(level) + " : " + str(isLastWeaponShopLevel), True, (255, 255, 255))
    display[0].blit(texto, (700, 120))
    texto = display[1].render("Equipped Weapon:", True, (255,0,0))
    display[0].blit(texto, (700,300))
    texto = display[1].render(main_player.weapon.name + " " + str(main_player.weapon.m_damage) + " " + str(getattr(main_player.weapon, "magic_dmg", 0)), True, (255,255,255))
    display[0].blit(texto, (700,340))

    if my_turn:
        display[0].blit(display[1].render("Mi Turno", True, (255, 255, 255)), (10, 10))
    else:
        display[0].blit(display[1].render("Turno Enemigo", True, (255, 255, 255)), (10, 10))

    pygame.draw.rect(display[0], (50,50,50), (20, display[0].get_height() - 150, display[0].get_width() - 40, 130), border_radius= 10)
    pygame.draw.rect(display[0], (200,200,255), (20, display[0].get_height() - 150, display[0].get_width() - 40, 130), 2, border_radius= 10)

    x_offset = display[0].get_width() - 1230
    for line in hud_states[state]:
        text_surface = display[1].render(line, True, (255, 255, 255))
        display[0].blit(text_surface, (x_offset, display[0].get_height() - 130))
        width, height = display[1].size(line)
        x_offset += width + 20

    for i, en in enumerate(enemies_list):
        texto2 = display[1].render("Enemy name: " + en.name + " Enemy hp: " + str(en.hp) + " " + str(en.dmg_red), True, display[2])
        display[0].blit(texto2, (150, 160 + i * 40))
        enemies_list_serialized = [{"name": e.name, "hp": e.hp, "skills": list(e.skills.keys())} for e in enemies_list]
        enemies_list_is_serialized = True

    return enemies_list_serialized, enemies_list_is_serialized