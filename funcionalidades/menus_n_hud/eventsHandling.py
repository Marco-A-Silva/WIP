import pygame

def eventHandling(display, level, my_turn, isLastWeaponShopLevel, isLastShopLevel, menu_list):
    last_weapon_menu_level = None
    last_shop_menu_level = None
    isBossLevel = False    
    menu_is_open = any(menu_list.values())

    # Mensajes de turno
    if my_turn:
        display[0].blit(display[1].render("Mi Turno", True, (255, 255, 255)), (10, 10))
    else:
        display[0].blit(display[1].render("Turno Enemigo", True, (255, 255, 255)), (10, 10))

    # Abrir menú solo si no está abierto y no se guardó el nivel

    if not menu_list["Weapons"] and level % 5 == 0 and level % 10 != 0 and not isLastWeaponShopLevel:
        menu_list["Weapons"] = True
        last_weapon_menu_level = level
        
    if not menu_list["Shop"] and level % 5 == 0 and level % 2 == 0 and not isLastShopLevel:
        menu_list["Shop"] = True
        last_shop_menu_level = level

    if level % 20 == 0 and level != 0:
        isBossLevel = True

    return menu_list["Weapons"], menu_list["Shop"], last_weapon_menu_level, last_shop_menu_level, menu_is_open, isBossLevel

#def pickNewEnemies(count, enemy_list):

def modify_attrs(obj, changes: dict):

    for attr, val in changes.items():
        if hasattr(obj, attr):
            # Si el valor es callable (función), lo ejecuta con el valor actual
            if callable(val):
                setattr(obj, attr, val(getattr(obj, attr)))
            else:
                setattr(obj, attr, val)