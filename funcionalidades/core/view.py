import pygame
from funcionalidades.Utility.information import addHover

hp_bar_state = {}

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


class gameRenderer:
    def __init__(self, display):
        self.display = display 
        """colore = (255, 0, 255)
        fonts = [pygame.font.SysFont("Arial", 30),pygame.font.SysFont("Arial", 20),pygame.font.SysFont("Arial", 15)]
        display = [screen, fonts, colore]"""

    def render(self, floor_layout, room, floor):
        layout_sprites = []

        ICON_SIZE = 32
        SPACING = 40
        Y = 20

        font = self.display[1][1]
        tooltip_font = self.display[1][2]

        mouse_pos = pygame.mouse.get_pos()

        total = len(floor_layout)
        if total == 0:
            return

        texto = self.display[1][0].render(str(floor) + "-" + str(room + 1), True, (255, 255, 255))   
        self.display[0].blit(texto, (self.display[0].get_width() - texto.get_width() - 6, 8))

        screen_center_x = self.display[0].get_width() // 2
        total_width = (total - 1) * SPACING
        START_X = screen_center_x - total_width // 2

        # --- cargar sprites ---
        for floor in floor_layout:
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
                self.display[0],
                (200, 200, 255) if i == room else (0, 0, 0),
                sprite_rect,
                2,
                border_radius=6
            )

            self.display[0].blit(sprite, sprite_rect)

            # --- tooltip debajo ---
            if hovering:
                text = tooltip_font.render(floor_layout[i][6:] if floor_layout[i].startswith("extra_") else floor_layout[i], True, (255, 255, 255))
                pad = 4

                text_rect = text.get_rect(
                    midtop=(sprite_rect.centerx, sprite_rect.bottom + 6)
                )
                bg_rect = text_rect.inflate(pad * 2, pad * 2)

                pygame.draw.rect(self.display[0], (20, 20, 30), bg_rect, border_radius=6)
                pygame.draw.rect(self.display[0], (200, 200, 255), bg_rect, 1, border_radius=6)
                self.display[0].blit(text, text_rect)

            # --- guion ---
            if i < total - 1:
                dash = font.render("-", True, (200, 200, 255))
                dash_rect = dash.get_rect(center=(x + SPACING // 2, Y))
                self.display[0].blit(dash, dash_rect)


class combatRenderer:
    def __init__(self, display):
        self.display = display 
        """colore = (255, 0, 255)
        fonts = [pygame.font.SysFont("Arial", 30),pygame.font.SysFont("Arial", 20),pygame.font.SysFont("Arial", 15)]
        display = [screen, fonts, colore]"""

    def render(self, party, enemies, sub_state, selected_index, party_turn, my_turn, current_action, menu_options, active_effs):
        self.display[0].fill("black")
        self.advParty_hud_length = 0

        keys = pygame.key.get_pressed()
        tab_pressed = keys[pygame.K_TAB]

        for i, char in enumerate(party): 
            self.draw_party(char, i, tab_pressed, party_turn, my_turn, current_action)

        if party_turn < len(party):
            char_actual = party[party_turn]
            self.draw_weapons_hud(char_actual)

        self.draw_enemies(enemies, sub_state, selected_index, current_action)
        self.draw_hud(selected_index, current_action, sub_state, menu_options)

        for effect in active_effs:
            effect.draw(self.display[0], self.display[1][0])

    def draw_party(self, char, i, tab_pressed, party_turn, my_turn, current_action):
        width_px, height_px = self.display[1][0].size(char.name + "  ")
        last_pmember = max(240, width_px + 20)
        pygame.draw.rect(self.display[0], (50,50,50), (self.advParty_hud_length, 0, last_pmember, 130), border_radius=10)
        pygame.draw.rect(self.display[0], (200,200,255), (self.advParty_hud_length, 0, last_pmember, 130), 2, border_radius=10)
        self.draw_stat_effs(char, last_pmember)

        if tab_pressed:
            self.draw_adv_stats(char,last_pmember, 105, i, party_turn, my_turn)

        draw_bar(self.display[0],25+self.advParty_hud_length,77,190, 2, char.sta, char.max_sta, hp_bar_state, f"STA_{i}", (50, 200, 110) if char.sta > min(getattr(char.weapon["secondary"], "weight", 100)*8, char.weapon["primary"].weight*8) else (255, 20, 110), (0, 0, 0))
        draw_bar(self.display[0],20+self.advParty_hud_length,80,200, 15, char._hp, char.max_hp, hp_bar_state, f"HP_{i}", (50, 200, 50), (255, 255, 255))
        draw_bar(self.display[0],20+self.advParty_hud_length,100,200, 15, char.mp, char.max_mp, hp_bar_state, f"MP_{i}", (50, 50, 200), (255, 255, 255))
        draw_bar(self.display[0],20+self.advParty_hud_length,119,200, 6, char.xp, char.xp2level, hp_bar_state, f"XP_{i}", (178, 213, 255), (255,255,255) if char.xp < char.xp2level*0.1 else (20, 20, 20))

        texto = self.display[1][0].render(char.name + " ", True, (255, 255, 255))
        self.display[0].blit(texto, (20+self.advParty_hud_length, 20))

        texto = self.display[1][1].render(str(char.gd) + "g", True, (255, 255, 255))
        self.display[0].blit(texto, (20+self.advParty_hud_length, 50))

        if i == party_turn & (my_turn or current_action["target_team"] == "party"):
            glow = pygame.Surface((last_pmember, 130), pygame.SRCALPHA)
            pygame.draw.rect(glow, (255, 255, 0, 120), (0, 0, last_pmember, 130), width=4, border_radius=10)
            pygame.draw.rect(glow, (255, 255, 0, 80), (2, 2, last_pmember-4, 130-4), width=2, border_radius=8)
            self.display[0].blit(glow, (self.advParty_hud_length, 0))

        self.advParty_hud_length += last_pmember

    def draw_stat_effs(self, char, last_pmember):
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
                    self.display[0], (200,200,255), img_rect, 2,
                    border_radius=10,
                    border_bottom_right_radius=0,
                    border_top_left_radius=0
                )
            elif i == 0:
                pygame.draw.rect(
                    self.display[0], (200,200,255), img_rect, 2,
                    border_top_right_radius=10
                )
            else:
                pygame.draw.rect(self.display[0], (200,200,255), img_rect, 2)

            self.display[0].blit(img, img_rect)

            # --- detectar hover (NO dibujar tooltip acá) ---
            if img_rect.collidepoint(mouse_pos):
                hovered_tag = statuses_tags[i]
                hovered_pos = mouse_pos

        if hovered_tag:
            tooltip = self.display[1][1].render(hovered_tag, True, (255,255,255))
            pad = 6

            tooltip_rect = tooltip.get_rect(
                topleft=(hovered_pos[0] + 10, hovered_pos[1] + 10)
            )

            bg_rect = tooltip_rect.inflate(pad * 2, pad * 2)

            pygame.draw.rect(self.display[0], (20,20,30), bg_rect, border_radius=6)
            pygame.draw.rect(self.display[0], (200,200,255), bg_rect, 1, border_radius=6)
            self.display[0].blit(tooltip, tooltip_rect)

    def draw_adv_stats(self, char, width, height, i, party_turn, my_turn):

        y = 130
        pygame.draw.rect(self.display[0], (50,50,50), (self.advParty_hud_length, y, width, height), border_radius=10)
        pygame.draw.rect(self.display[0], (200,200,255), (self.advParty_hud_length, y, width, height), 2, border_radius=10)

        if i == party_turn & my_turn:
            glow = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(glow, (255, 255, 0, 120), (0, 0, width, height), width=4, border_radius=10)
            pygame.draw.rect(glow, (255, 255, 0, 80), (2, 2, width-4, height-4), width=2, border_radius=8)
            self.display[0].blit(glow, (self.advParty_hud_length, y))

        stat_names = ["vit", "mnd", "int", "str", "lck", "chr", "awe", "agi", "end", "dex", "def"]
        stat_values = list(char.statBlock) + [char.dmgRed()]

        label_font = self.display[1][2]
        value_font = self.display[1][2]

        col1_x = self.advParty_hud_length + 20
        col2_x = self.advParty_hud_length + width//2 +10

        spacing = 15
        start_y = y + 10

        for idx, name in enumerate(stat_names):
            value = stat_values[idx]

            if idx < 6:  
                x_label = col1_x
                x_value = col1_x + 70
                y_line = start_y + idx * spacing
            else:
                x_label = col2_x
                x_value = col2_x + 70
                y_line = start_y + (idx - 6) * spacing

            lbl = label_font.render(name.upper() + ":", True, (255, 255, 255))
            val = value_font.render(str(value), True, (200, 200, 255))

            self.display[0].blit(lbl, (x_label, y_line))
            self.display[0].blit(val, (x_value, y_line))

    def draw_weapons_hud(self, char):
        x = self.display[0].get_width() - 600
        for idx, slot in enumerate(["primary", "secondary"]):
            y = 300 + 40 + (idx * 50)
            weapon = char.weapon[slot]
            
            if weapon is not None:
                lbl_texto = f"{slot.capitalize()} weapon: "
                lbl_surface = self.display[1][0].render(lbl_texto, True, self.display[2])
                a = lbl_surface.get_width()
                self.display[0].blit(lbl_surface, (x, y))

                val_surface = self.display[1][0].render(weapon.name, True, (255, 255, 255))
                text_rect = val_surface.get_rect(topleft=(x + a, y))
                
                match weapon.type:
                    case ["melee"] | ["melee", _]:
                        addHover(self.display, text_rect, "top", f"{int(weapon.dmg)} dmg", f"- scales with: {list(weapon.scaling.keys())}")
                    case ["magic"] | ["magic", _]:
                        addHover(self.display, text_rect, "top", f"{int(weapon.mgc)} mgc", f"- scales with: {list(weapon.scaling.keys())}")
                    case ["secondary"] | ["secondary", _]:
                        addHover(self.display, text_rect, "top", f"{int(weapon.dmg)} dmg", f"{int(weapon.dmg_red)} dmg_red", f"- scales with: {list(weapon.scaling.keys())}")
                    case ["ranged"] | ["ranged", _]:
                        addHover(self.display, text_rect, "top", f"{int(weapon.dmg)} dmg", f"{int(weapon.ammo)} ammo", f"- scales with: {list(weapon.scaling.keys())}")
                
                self.display[0].blit(val_surface, (x + a, y))
    
    def draw_enemies(self, enemies, sub_state, selected_index, current_action):
        for i, en in enumerate(enemies):
            texto = f"{en.name} Enemy hp: {int(en.hp)} {en.dmg} {en.dmg_red}"
            
            if sub_state == "SELECT_TARGET" and i == selected_index and current_action["target_team"] == "enemies":
                color_texto = (255, 255, 100)
            else:
                color_texto = self.display[2]

            texto_surface = self.display[1][0].render(texto, True, color_texto)
            self.display[0].blit(texto_surface, (150, 300 + i * 40))
    
    def draw_hud(self, selected_index, current_action, sub_state, menu_options):
        font = self.display[1][0]
        hud_y = self.display[0].get_height() - 300 
        
        if sub_state == "SELECT_ACTION":
            y_offset = hud_y + 10
            for i, opcion in enumerate(menu_options):
                es_seleccionado = (i == selected_index)
                color_rect = (100, 100, 100) if es_seleccionado else (50, 50, 50)
                
                text_surface = font.render(opcion["name"], True, (255, 255, 255))
                rect = text_surface.get_rect(topleft=(10, y_offset))

                pygame.draw.rect(self.display[0], color_rect, rect.inflate(5, 5), border_radius=8)
                self.display[0].blit(text_surface, rect)
                y_offset += font.get_height() + 10

        elif sub_state == "SELECT_TARGET":
            accion_fijada = f"{current_action["name"]}"
            txt_surface = font.render(accion_fijada, True, (150, 150, 150))
            self.display[0].blit(txt_surface, (10, hud_y + 10))
            
            ayuda_surface = font.render("Select a target...", True, (150, 150, 150))
            self.display[0].blit(ayuda_surface, (10, hud_y + 50))


class shopRenderer:
    def __init__(self, display, shop_items):
        self.display = display 
        self.shop_items = shop_items
        self.item_rects = []

        """colore = (255, 0, 255)
        fonts = [pygame.font.SysFont("Arial", 30),pygame.font.SysFont("Arial", 20),pygame.font.SysFont("Arial", 15)]
        display = [screen, fonts, colore]"""

    def render(self, party, shop_items, selected_index):
        pass