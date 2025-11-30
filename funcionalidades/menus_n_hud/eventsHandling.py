import pygame, random, copy
from vault.events import badEvents,neutralEvents,goodEvents


def eventHandling(display, level, my_turn, lastMenuOpened, lastEvent, menu_list): 
    isBossLevel = False
    lastMenuOpened["Weapons"][1] = (lastMenuOpened["Weapons"][0] == level)
    lastMenuOpened["Shop"][1] = (lastMenuOpened["Shop"][0] == level)

    if not menu_list["Weapons"] and level % 5 == 0 and level % 10 != 0 and not lastMenuOpened["Weapons"][1]:
        menu_list["Weapons"] = True
        lastMenuOpened["Weapons"][0] = level
        
    if not menu_list["Shop"] and level % 5 == 0 and level % 2 == 0 and not lastMenuOpened["Shop"][1]:
        menu_list["Shop"] = True
        lastMenuOpened["Shop"][0] = level

    if level % 10 == 0 and level % 2 == 0:
        isBossLevel = True

    return menu_list, lastMenuOpened, isBossLevel

def drawRandomEvent(display, event, selected_idx):
    overlay = pygame.Surface(display[0].get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    display[0].blit(overlay, (0, 0))
    
    center_x = (display[0].get_width() // 2) - 20
    center_y = (display[0].get_height() // 2) - 20

    panel_w, panel_h = 500, 340
    panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
    panel_rect.center = (center_x, center_y - 20)

    pygame.draw.rect(display[0], (30, 30, 30), panel_rect, border_radius=8)
    pygame.draw.rect(display[0], (200, 200, 200), panel_rect, width=2, border_radius=8)

    font = display[1][0]  # fuente grande

    # Helper: wrap text to width
    def wrap(text, font, max_width):
        words = text.split(" ")
        lines = []
        curr = ""

        for w in words:
            test = curr + w + " "
            if font.size(test)[0] <= max_width:
                curr = test
            else:
                lines.append(curr)
                curr = w + " "
        if curr:
            lines.append(curr)
        return lines

    # DESCRIPTION FIRST
    wrapped = wrap(event.description, font, panel_w - 40)

    y = panel_rect.top + 35
    for line in wrapped:
        surf = font.render(line.strip(), True, (200, 255, 255))
        rect = surf.get_rect(center=(center_x, y))
        display[0].blit(surf, rect)
        y += font.get_height() + 4

    # ACTION BELOW DESCRIPTION
    action_surf = font.render(event.choice, True, (255, 255, 255))
    action_rect = action_surf.get_rect(center=(center_x, y + 10))
    display[0].blit(action_surf, action_rect)

    # OPTIONS
    opt_y = action_rect.bottom + 30
    for i, opt in enumerate(event.actions):
        color = (255, 255, 100) if i == selected_idx else (255, 255, 255)
        opt_surf = font.render(opt, True, color)
        opt_rect = opt_surf.get_rect(center=(center_x, opt_y + i * 60))
        display[0].blit(opt_surf, opt_rect)



def pickNewEnemies(count, enemyList, enemies, bosses, level, isBossLevel):

    enemyList = [copy.deepcopy(enemy) for enemy in random.choices(enemies, k=count)]
    for i, enemy in enumerate(enemyList):
        enemy.hp = enemy.base_hp + level    

    if isBossLevel:
        enemyList.insert(0, copy.deepcopy(random.choice(bosses)))

    return enemyList

def getRandEvent(eventList, lastEvent, event_choice, player):
    
    if not lastEvent["randEvent"]:

        event_chance = random.randint(1,20)
        print(event_chance , eventList["randEvent"])
        if event_chance <= 5 + ((player.statBlock[4] // 2) - 4):

            event_type = random.choice([badEvents,neutralEvents,goodEvents])
            event_choice = event_type[random.randint(0,len(event_type)-1)]
            relevant_stats = [(player.statBlock[sta] // 2) - 5 for sta in event_choice.stat]
            roll = random.randint(1,20)
            for i in relevant_stats: 
                roll += i
            event_choice.roll = roll
            eventList["randEvent"] = True
        lastEvent["randEvent"] = True
    
    return event_choice, eventList, lastEvent