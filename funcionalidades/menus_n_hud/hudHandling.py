import pygame
from random import randint

def drawScreen(display, main_player, enemies, level, isLastWeaponShopLevel, enemies_list, enemies_list_is_serialized):
    enemies_list_serialized = None

    display[0].fill("black")
    texto = display[1].render("Player hp: " + str(main_player.hp) + " mp: " + str(main_player.mp) + " gold: " + str(main_player.gd), True, (255, 255, 255))
    display[0].blit(texto, (150, 120))
    texto = display[1].render("Level: " + str(level) + " : " + str(isLastWeaponShopLevel), True, (255, 255, 255))
    display[0].blit(texto, (700, 120))
    texto = display[1].render("Items:", True, (0,255,255))
    display[0].blit(texto, (150,500))
    for i, item in enumerate(main_player.items):
        texto = display[1].render(item.name, True, (255,255,255))
        display[0].blit(texto, (150, 540 + 40*i))

    if not enemies_list:
        enemy_count = randint(0, 3)
        enemies_list = [enemies[i] for i in range(enemy_count)]

    for i, en in enumerate(enemies_list):
        texto2 = display[1].render("Enemy name: " + en.name + " Enemy hp: " + str(en.hp), True, display[2])
        display[0].blit(texto2, (150, 160 + i * 40))
        enemies_list_serialized = [{"name": e.name, "hp": e.hp} for e in enemies_list]
        enemies_list_is_serialized = True

    return enemies_list, enemies_list_serialized,enemies_list_is_serialized