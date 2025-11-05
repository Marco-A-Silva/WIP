import pygame, random, copy

def eventHandling(display, level, my_turn, isLastWeaponShopLevel, isLastShopLevel, isLastBossLevel, menu_list):
    last_weapon_menu_level = None
    last_shop_menu_level = None
    isBossLevel = False    
    menu_is_open = any(menu_list.values())

    # Abrir menú solo si no está abierto y no se guardó el nivel

    if not menu_list["Weapons"] and level % 5 == 0 and level % 10 != 0 and not isLastWeaponShopLevel:
        menu_list["Weapons"] = True
        last_weapon_menu_level = level
        
    if not menu_list["Shop"] and level % 5 == 0 and level % 2 == 0 and not isLastShopLevel:
        menu_list["Shop"] = True
        last_shop_menu_level = level

    if level % 20 == 0 and level != 0 and not isLastBossLevel:
        isBossLevel = True

    return {"Pause":menu_list["Pause"], "Weapons": menu_list["Weapons"], "Shop": menu_list["Shop"]}, last_weapon_menu_level, last_shop_menu_level, menu_is_open, isBossLevel, isLastBossLevel

def pickNewEnemies(count, enemyList, enemies, bosses, level, isBossLevel, isLastBossLevel):

    enemyList = [copy.deepcopy(enemy) for enemy in random.choices(enemies, k=count)]
    for i, enemy in enumerate(enemyList):
        enemy.hp = enemy.base_hp + level

    if isBossLevel and not isLastBossLevel:
        enemyList.insert(0,random.choice(bosses))
        isLastBossLevel = True

    return enemyList