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

def draw_bar(surface, x, y, width, height, current, max_, state_dict, key, color):
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

class Renderer:
    def __init__(self, display):
        self.display = display 
        """colore = (255, 0, 255)
        fonts = [pygame.font.SysFont("Arial", 30),pygame.font.SysFont("Arial", 20),pygame.font.SysFont("Arial", 15)]
        display = [screen, fonts, colore]"""

    def render():
        pass

    def _wrap(self, text, font, max_width):
        lines, line = [], ""
        for word in text.split():
            test = f"{line} {word}".strip()
            if font.size(test)[0] <= max_width:
                line = test
            else:
                if line:
                    lines.append(line)
                line = word
        lines.append(line)
        return lines

    def draw_member(self, number, char, x, y , width, height, name_width):
        #Portrait
        surface = self.display[0]
        pygame.draw.rect(self.display[0], (50,50,50), (x, y, width, height), border_radius=10)

        #Status Bars
        draw_bar(surface, x+9 ,y + 50,width - 18 , 8, char._hp, char.max_hp, hp_bar_state, f"HP_{number}", (50, 200, 50))
        draw_bar(surface, x+9 ,y + 60 ,width - 18 , 8, char.mp, char.max_mp, hp_bar_state, f"MP_{number}", (50, 50, 200))
        draw_bar(surface, x+5 , y+79, width-9, 2, char.xp, char.xp2level, hp_bar_state, f"XP_{number}", (178, 213, 255))

        pygame.draw.rect(self.display[0], (200,200,255), (x, y, width, height), 2, border_radius=10)

        texto = self.display[1][0].render(char.name + " ", True, (255, 255, 255))
        self.display[0].blit(texto, (x+10, y + (height-50)/3))

        texto = self.display[1][1].render("Lv "+(str(char.level))+" ", True, (0, 150, 255))
        self.display[0].blit(texto, (x+name_width, y + (height-50)/1.7))

        texto = self.display[1][1].render(str(char.gd) + "g", True, (255, 255, 0))
        self.display[0].blit(texto, (width - texto.width - 10, y + (height-50)/1.8))

class gameRenderer(Renderer):

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


class combatRenderer(Renderer):

    def render(self, party, enemies, sub_state, selected_index, party_turn, my_turn, current_action, menu_options, active_effs):
        self.display[0].fill("black")
        self.advParty_hud_length = 0

        self.draw_party(party, party_turn, my_turn, selected_index, current_action, menu_options, sub_state)
        self.draw_enemies(enemies, sub_state, selected_index, current_action)

        for effect in active_effs:
            effect.draw(self.display[0])

    def draw_actions(self, char, x, y , width, height, selected_index, menu_options):
  
        pygame.draw.rect(self.display[0], (50,50,50), (x, y - height + 10, width, height), border_radius=10)
        pygame.draw.rect(self.display[0], (200,200,255), (x, y - height + 10, width, height), 2, border_radius=10)

        colors = {1: (255,255,255), 0: (100,100,100)}

        for i, opt in enumerate(menu_options):
            texto = self.display[1][0].render(f"{opt['name']} ", True, (255,255,0) if selected_index == i and opt.get("active", True) == True else colors[opt.get("active", True)])
            self.display[0].blit(texto, (x +10, y - height + 20 + i * 35))

    def draw_party(self, party, party_turn, my_turn, selected_index, current_action, menu_options, sub_state):
        max_height = self.display[0].get_height()
        
        for i, char in enumerate(party):
            width_name, height_name = self.display[1][0].size(char.name + "  ")
            hud_y = max_height - (height_name + 50)
            last_pmember = max(240, width_name + 20)

            if i == party_turn and sub_state != "TARGET":
                height_total = (len(menu_options) - 1) * 35 + height_name + 30
                self.draw_actions(char, self.advParty_hud_length, hud_y, last_pmember, height_total, selected_index, menu_options)

            self.draw_member(i, char, self.advParty_hud_length, hud_y, last_pmember, height_name + 50, width_name)
            if i == party_turn and (current_action["target_team"] if current_action else "None") == "party":
                pygame.draw.rect(self.display[0], (255, 255, 0, 80), (self.advParty_hud_length, hud_y, last_pmember, height_name + 50), width=2, border_radius=8)
                

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

        if i == party_turn and my_turn:
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
    
    def draw_enemies(self, enemies, sub_state, selected_index, current_action):
        for i, en in enumerate([e for e in enemies if e.hp > 0]):
            texto = f"{en.name} Enemy hp: {int(en.hp)} {en.dmg} {en.dmg_red}"
            
            if sub_state == "TARGET" and i == selected_index and current_action["target_team"] == "enemies":
                color_texto = (255, 255, 100)
            else:
                color_texto = self.display[2]

            texto_surface = self.display[1][0].render(texto, True, color_texto)
            self.display[0].blit(texto_surface, (150, 300 + i * 40))

        
class shopRenderer(Renderer):

    def render(self, sub_state, party, selected_index, shop_items, effs):

        self._shopper_selection(self.display[0], party, selected_index, sub_state)
        self._render_items(self.display[0], shop_items, sub_state, selected_index)

        for effect in effs:
            effect.draw(self.display[0])

    def _render_items(self, surface, shop_items, sub_state, selected_index):
        fuente = self.display[1][0]
        ancho = surface.get_width()
        x_nombre = ancho // 4
        x_precio = ancho - ancho // 4
        y = 60

        for i, entry in enumerate(shop_items):
            objeto, precio = entry[0], entry[1]
            seleccionado = sub_state == "BROWSING" and i == selected_index

            nombre = fuente.render(objeto.name, True, (255, 255, 0) if seleccionado else (255, 255, 255))
            costo = fuente.render(f"{precio}g", True, (255, 215, 0))

            surface.blit(nombre, (x_nombre, y))
            surface.blit(costo, (x_precio - costo.get_width(), y))
            y += nombre.get_height() + 8
            

    def _shopper_selection(self, surface, party, selected_index, sub_state): 
        max_height = self.display[0].get_height()
        a = 0

        for i, char in enumerate(party):
            width_name, height_name = self.display[1][0].size(char.name + "  ")
            hud_y = max_height - (height_name + 50)
            last_pmember = max(240, width_name + 20)

            self.draw_member(i, char, a, hud_y, last_pmember, height_name + 50, width_name)
            if i == selected_index and sub_state == "SELECT":
                pygame.draw.rect(self.display[0], (255, 255, 0, 80), (a, hud_y, last_pmember, height_name + 50), width=2, border_radius=8)
                

            a += last_pmember

class chestRenderer(Renderer):
    def __init__(self, display):
        super().__init__(display)
        fondo = pygame.image.load("assets/backgrounds/chest_1.png").convert_alpha()
        self.background = pygame.transform.scale(fondo, display[0].get_size())

    def render(self, sub_state, party, chest_items, selected_index, effs):
        self.display[0].blit(self.background, (0, 0))
        self._render_items(self.display[0], chest_items, sub_state, selected_index)
        self._player_selection(self.display[0], party, selected_index, sub_state)

        for effect in effs:
            effect.draw(self.display[0])

    def _player_selection(self, surface, party, selected_index, sub_state): 
        max_height = self.display[0].get_height()
        a = 0

        for i, char in enumerate(party):
            width_name, height_name = self.display[1][0].size(char.name + "  ")
            hud_y = max_height - (height_name + 50)
            last_pmember = max(240, width_name + 20)

            self.draw_member(i, char, a, hud_y, last_pmember, height_name + 50, width_name)
            if i == selected_index and sub_state == "SELECT":
                pygame.draw.rect(self.display[0], (255, 255, 0, 80), (a, hud_y, last_pmember, height_name + 50), width=2, border_radius=8)
                

            a += last_pmember

    def _render_items(self, surface, chest_items, sub_state, selected_index):
        center_x = surface.get_width() // 2
        center_y = surface.get_height() // 2

        panel_rect = pygame.Rect(0, 0, 420, 100 + len(chest_items) * 50)
        panel_rect.center = (center_x, center_y - 100)

        pygame.draw.rect(surface, (30, 30, 30), panel_rect, border_radius=8)
        pygame.draw.rect(surface, (200, 200, 200), panel_rect, width=2, border_radius=8)

        titulo = self.display[1][0].render("You opened a chest, it had:", True, (200, 255, 255))
        surface.blit(titulo, titulo.get_rect(center=(center_x, panel_rect.top + 36)))

        for i, opt in enumerate(chest_items):
            seleccionado = sub_state == "TAKE" and i == selected_index
            color = (255, 255, 100) if seleccionado else (255, 255, 255)
            opt_surf = self.display[1][0].render(opt.name, True, color)
            surface.blit(opt_surf, opt_surf.get_rect(center=(center_x, panel_rect.top + 90 + i * 50)))


class eventRenderer(Renderer):

    def render(self, sub_state, party, event, selected_index, effs):
        self._render_event(self.display[0], event, selected_index, sub_state)
        self._player_selection(self.display[0], party, selected_index, sub_state)

        for effect in effs:
            effect.draw(self.display[0])

    def _render_event(self, surface, event, selected_index, sub_state):
        w, h = surface.get_size()
        body_font, opt_font = self.display[1][1], self.display[1][0]
        hud_h = opt_font.size("A")[1] + 50

        pad, gap, row_h = 30, 24, 46
        panel_w = min(760, int(w * 0.7))
        lines = self._wrap(event.description, body_font, panel_w - pad * 2)
        line_h = body_font.size("A")[1] + 4
        options = list(event.actions.keys())

        panel = pygame.Rect(0, 0, panel_w, pad + len(lines) * line_h + gap + len(options) * row_h + pad)
        panel.center = (w // 2, (h - hud_h) // 2)
        panel.top = max(10, panel.top)

        pygame.draw.rect(surface, (50, 50, 50), panel, border_radius=10)
        pygame.draw.rect(surface, (200, 200, 255), panel, 2, border_radius=10)

        y = panel.top + pad
        for line in lines:
            txt = body_font.render(line, True, (220, 235, 255))
            surface.blit(txt, txt.get_rect(midtop=(panel.centerx, y)))
            y += line_h

        y += gap // 2
        pygame.draw.line(surface, (200, 200, 255), (panel.left + pad, y), (panel.right - pad, y), 1)
        y += gap // 2

        for i, opt in enumerate(options):
            activo = sub_state == "CHOOSE"
            seleccionado = activo and i == selected_index
            row = pygame.Rect(panel.left + pad, y, panel_w - pad * 2, row_h - 6)

            if seleccionado:
                pygame.draw.rect(surface, (90, 90, 40), row, border_radius=8)
                pygame.draw.rect(surface, (255, 255, 100), row, 2, border_radius=8)

            color = (255, 255, 100) if seleccionado else (255, 255, 255) if activo else (140, 140, 140)
            txt = opt_font.render(opt, True, color)
            surface.blit(txt, txt.get_rect(center=row.center))
            y += row_h

    def _player_selection(self, surface, party, selected_index, sub_state): 
        max_height = self.display[0].get_height()
        a = 0

        for i, char in enumerate(party):
            width_name, height_name = self.display[1][0].size(char.name + "  ")
            hud_y = max_height - (height_name + 50)
            last_pmember = max(240, width_name + 20)

            self.draw_member(i, char, a, hud_y, last_pmember, height_name + 50, width_name)
            if i == selected_index and sub_state == "SELECT":
                pygame.draw.rect(self.display[0], (255, 255, 0, 80), (a, hud_y, last_pmember, height_name + 50), width=2, border_radius=8)
                

            a += last_pmember
