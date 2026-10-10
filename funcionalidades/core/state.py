import pygame, random, copy, os
from .ui import HBox, VBox, UIPanel, SItemSlot
from .view import gameRenderer, combatRenderer, shopRenderer
from .manager import gameManager, combatManager, shopManager
from .visuals import floatingText, animation
from funcionalidades.Utility.information import addNotification
from funcionalidades.Utility.saving_loading import load_game_state

ENEMY_TURN_DELAY = 1000  # ms entre cada accion enemiga

"STATE = LOGICA PURA"
"MANAGER = ORCHESTRADOR (MANEJA LAS COSAS -ej- crear enemyList o itemPool, compras, ataques, aka lo que pasa en el estado digamos)"
"RENDERER = LO QUE SE VE EN LA PANTALLA"


class State:
    def __init__(self, display):
        self.display = display
        self.is_done = False
        self.active_effs = []

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def render(self):
        pass

    def _floating_text(self, x, y, cantidad, font, color=(255, 50, 50)):
        nuevo_texto = floatingText(str(cantidad), x, y, font, color=color)
        self.active_effs.append(nuevo_texto)

    def gen_floating_text():
        pass


class menuState(State):
    def __init__(self, display, options, columnas, quit):
        super().__init__(display)
        self.options = options
        self.selected_index = 0
        self.columnas = max(1, columnas)
        self.quit = quit

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key in [pygame.K_UP, pygame.K_w]:
            self.selected_index = max(0, self.selected_index - 1)
        elif event.key in [pygame.K_DOWN, pygame.K_s]:
            self.selected_index = min (len(self.options) - 1, self.selected_index + 1)

    def render(self):
        screen = self.display[0]
        fuente_opciones = self.display[1][1]

        ancho_pantalla = screen.get_width()
        alto_pantalla = screen.get_height()

        overlay = pygame.Surface((ancho_pantalla, alto_pantalla), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        screen.blit(overlay, (0, 0))

        ancho_opcion = 220
        alto_opcion = 40
        espaciado = 25

        total_height = len(self.options) * (alto_opcion + espaciado) - espaciado
        start_y = (alto_pantalla - total_height) // 2

        centro_x = ancho_pantalla // 2

        for i, opcion in enumerate(self.options):
            centro_y = start_y + i * (alto_opcion + espaciado)
            es_seleccionado = (i == self.selected_index)
            self._dibujar_opcion(screen, fuente_opciones, opcion, centro_x, centro_y, es_seleccionado, ancho_opcion)
    
    def _dibujar_opcion(self, screen, fuente, texto, x, y, es_seleccionado, ancho_opcion):
        rect_alto = 40
        rect_selector = pygame.Rect(x - ancho_opcion // 2, y - 8, ancho_opcion, rect_alto)
        color_texto = (150, 150, 160)

        if es_seleccionado:
            pygame.draw.rect(screen, (60,60,60, 150), rect_selector, border_radius=6)
        else:
            pygame.draw.rect(screen, (30, 30, 35), rect_selector, border_radius=6)

        texto_surface = fuente.render(texto, True, color_texto)
        texto_rect = texto_surface.get_rect(center=(x, y + 12))
        screen.blit(texto_surface, texto_rect)


class gameState(State):
    def __init__(self, display, save_path, room = 0, floor = 1, floor_layout = None):
        super().__init__(display)
        self.sub_state = None
        self.menu = None
        self.vfx = [] # <- solo para animaciones y notificaciones
        self.is_transitioning = False

        if os.path.exists(save_path):
            datos = load_game_state(save_path) 
            
            self.adv_party = datos["party"]
            self.enemies = datos["enemies"]
            self.room = datos["room"]
            self.floor = 1
            self.floor_layout = None
        else:
            self.room = 0
            self.floor = 1
            self.floor_layout = None
            self.adv_party = []
            self.enemies = []

        self.manager = gameManager(room, floor, floor_layout)
        self.renderer = gameRenderer(self.display)

        self.update_state(self.manager.active_floor)


    def handle_event(self, event):

        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_ESCAPE:
                if self.menu: self.menu = None
                else: self.menu = pauseState(self.display, save= self.save, quit=self.exitMenu)
                return

            if event.key == pygame.K_F5:
                self.guardar_progreso()
                return
            
        if self.sub_state and not self.menu and not self.is_transitioning:
            self.sub_state.handle_event(event)  
        elif self.menu: self.menu.handle_event(event)

    def update(self):
        if self.menu is not None:
            self.menu.update()
            if self.menu.is_done:
                self.menu = None
            return

        #for vfx in self.vfx:
        #    vfx.update()
        #self.vfx = [e for e in self.vfx if not e.is_done]

        if self.is_transitioning:
        #    transicion = next((v for v in self.vfx if isinstance(v, animation)), None)
        #    if transicion and transicion.In:
                self.load_new_room()
                self.is_transitioning = False

        if self.sub_state is not None and not self.is_transitioning:
            self.sub_state.update()

            if self.sub_state.is_done:
                if hasattr(self.sub_state, 'result') and self.sub_state.result == "GAME_OVER":
                    self.is_done = True
                    return

                self.sub_state = None
                self.enemies = []
                self.is_transitioning = True
                self.vfx.append(animation(velocity=2))

    def update_state(self, tipo_sala):
        match tipo_sala:
            case "fight" | "elite":
                self.sub_state = combatState(self.display, self.adv_party, self.enemies, True, self.manager.room, self.manager.floor, self.manager.active_floor, addNotification) 
            case "chest":
                self.sub_state = chestState(self.display)
            case "shop":
                self.sub_state = shopState(self.display, self.adv_party)
            case "event":
                self.sub_state = eventState(self.display)
            case _ if self.manager.active_floor.startswith("extra_"):
                self.sub_state = extraState(self.display)


    def load_new_room(self):
        self.manager.load_new_room()
        tipo_sala = self.manager.active_floor
        self.update_state(tipo_sala)

    def exitMenu(self):
        self.menu = None

    def save(self):
        pass


    def render(self):
        self.display[0].fill((10,10,15))
        
        if self.sub_state is not None:
            self.sub_state.render()

        self.renderer.render(
            self.manager.floor_layout,
            self.manager.room,
            self.manager.floor
        )  

        for vfx in self.vfx:
            vfx.render(self.display[0])

        if self.menu is not None:
            self.menu.render()


class combatState(State):
    def __init__(self, display, party, enemies, my_turn, room, floor, activeFloor, addNotification):
        super().__init__(display)
        self.selected_index = 0

        self.manager = combatManager(party, enemies, my_turn, room, floor, activeFloor, addNotification, self.gen_floating_text)
        self.renderer = combatRenderer(self.display)

        self.enemy_turn_start = None

        self.sub_state = "MENU"
        self.current_action = None
        self.menu_options = []  

        self.menu_opt_update()

    def menu_opt_update(self):
        if not self.manager.my_turn:
            return
        
        self.menu_options = []
        personaje_actual = self.manager.order[self.manager.turn] 
        special_toggle = hasattr(personaje_actual, 'skills') and personaje_actual.skills

        if self.sub_state == "MENU":
            
            self.menu_options.append({
                "name": "Attack",
                "nstate": "ATTACK",
                "active": True,
                "target_team": "enemies"
            })

            self.menu_options.append({
                "name": "Special",
                "nstate": "SPECIAL",
                "active" : special_toggle,
                "target_team": "enemies"
            })

            self.menu_options.append({
                "name": "Inventory",
                "active": True,
                "nstate": "INVENTORY",
                "target_team": "self"
            })

        elif self.sub_state == "ATTACK":
            for weapon in personaje_actual.weapon.values():
                if weapon is None:
                    continue
                self.menu_options.append({
                    "name": weapon.name,
                    "nstate": "TARGET",
                    "execute": lambda target, w=weapon: self.manager.melee(personaje_actual, w, target),
                    "target_team": "enemies"
                })


        elif self.sub_state == "SPECIAL":
            for nombre_skill in personaje_actual.skills.keys():
                self.menu_options.append({
                    "name": nombre_skill,
                    "nstate": "TARGET",
                    "execute": lambda target, sk=nombre_skill: personaje_actual.skills[sk](personaje_actual, target, "primary"),
                    "target_team": "enemies"
                })

        elif self.sub_state == "INVENTORY":
            for i, item in enumerate(personaje_actual.items):
                self.menu_options.append({
                    "name": item.name + " - " + str(item.uses),
                    "nstate": "TARGET",
                    "execute": lambda target, idx=i: self.manager.usar_item(personaje_actual, target, idx),
                    "target_team": "party"
                })

        if not self.menu_options:
            self.menu_options.append({
                "name": "Nothing Here...",
                "nstate": "MENU",
                "active": False
            })


    def handle_event(self, event):
        if self.is_done or not self.manager.my_turn:
            return

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_UP:

            if self.sub_state == "MENU" and self.selected_index + -1 < len(self.menu_options) and not self.menu_options[self.selected_index - 1]["active"]:
                self.selected_index = (self.selected_index - 1) % len(self.menu_options)

            self.selected_index = max(0, self.selected_index - 1)
        elif event.key == pygame.K_DOWN:

            if self.sub_state == "MENU" and self.selected_index + 1 < len(self.menu_options) and not self.menu_options[self.selected_index + 1]["active"]:
                self.selected_index = (self.selected_index + 1) % len(self.menu_options)

            limite = len(self.get_valid_targets()) if self.sub_state == "TARGET" else len(self.menu_options)
            self.selected_index = min(limite - 1, self.selected_index + 1)
        
        elif event.key == pygame.K_b:
            self.sub_state = "MENU"
            self.current_action = None
            self.selected_index = 0
            self.menu_opt_update()

        elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
            if self.sub_state in ["MENU", "SPECIAL", "ATTACK", "INVENTORY"]:
                opcion = self.menu_options[self.selected_index]
                
                if opcion["nstate"] == "SPECIAL":
                    self.current_action = opcion
                    self.sub_state = "SPECIAL"
                    self.selected_index = 0
                    self.menu_opt_update()
                    
                elif opcion["nstate"] == "ATTACK":
                    self.current_action = opcion
                    self.sub_state = "ATTACK"
                    self.selected_index = 0 
                    self.menu_opt_update()
                
                elif opcion["nstate"] == "INVENTORY":
                    self.current_action = opcion
                    self.sub_state = "INVENTORY"
                    self.selected_index = 0 
                    self.menu_opt_update()

                elif opcion["nstate"] == "TARGET":
                    self.current_action = opcion
                    self.sub_state = "TARGET"
                    self.selected_index = 0 
                    self.menu_opt_update()

            elif self.sub_state == "TARGET":
                living_targets = self.get_valid_targets()
                enemigo_objetivo = living_targets[self.selected_index]
                result = self.current_action["execute"](enemigo_objetivo)
                self.combat_flow(result)

    def get_valid_targets(self):
        team_list = getattr(self.manager, self.current_action.get("target_team", "enemies"))
        return [e for e in team_list if e.hp > 0]


    def combat_flow(self, result):
        if result != "CONTINUE":
            self.result = result
            self.is_done = True
            return

        self.sub_state = "MENU"
        self.selected_index = 0
        self.current_action = None
        
        self.menu_opt_update()


    def render(self):
        self.renderer.render(
            party=self.manager.party,
            enemies=self.manager.enemies,
            sub_state=self.sub_state,
            selected_index=self.selected_index,
            party_turn=self.manager.turn,
            my_turn=self.manager.my_turn,
            current_action=self.current_action,
            menu_options=self.menu_options,
            active_effs=self.active_effs
        )


    def update(self):
        for efecto in self.active_effs:
            efecto.update()

        self.active_effs = [e for e in self.active_effs if e.alpha > 0]

        if self.is_done:
            return

        if not self.manager.my_turn:
            ahora = pygame.time.get_ticks()
            if self.enemy_turn_start is None:
                self.enemy_turn_start = ahora
            elif ahora - self.enemy_turn_start >= ENEMY_TURN_DELAY:
                self.enemy_turn_start = None
                self.combat_flow(self.manager.enemy_turn())

    def gen_floating_text(self, target, dmg):
        x, y = 0, 0

        if target in self.manager.enemies:
            indice = self.manager.enemies.index(target)
            x = 350  
            y = 300 + indice * 40 - 20 
        elif target in self.manager.party:
            indice = self.manager.party.index(target)
            x = 110 + (indice * 240) 
            y = self.display[0].get_height() - 150

        self._floating_text(x, y, str(dmg), self.display[1][0])


class shopState(State):
    def __init__(self, display, adv_party):
        super().__init__(display)
        self.selected_index = 0
        self.turn = 0

        self.sub_state = "SELECT_SHOPPER"

        self.manager = shopManager(adv_party, self.gen_floating_text)
        self.renderer = shopRenderer(self.display)

        self.ui_root = UIPanel(0, 0, display[0].get_width(), display[0].get_height())

    #---------------------------------------------------------------------------------------------------------------------------
    #Item List
        self.item_list = HBox(10, 600, display[0].get_width(), spacing=15, wrap=True, align="center")
        self.ui_root.add_child(self.item_list)

        for item in self.manager.shop_items:
            slot = SItemSlot(display[1][0].render(str(item[0].name), True, (255, 255, 255)).width + 20, 40, item[0].name, None)
            slot.data = lambda s=slot, i=item: self.buy_item(s, i) 
            self.item_list.add_child(slot)

        self.item_list.recalculate_layout()
    #---------------------------------------------------------------------------------------------------------------------------
    #Player List

    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = max(0, self.selected_index - 1)
            elif event.key == pygame.K_DOWN:
                limite = len(self.manager.party) if self.sub_state == "SELECT_SHOPPER" else len(self.manager.shop_items)
                self.selected_index = min(limite - 1, self.selected_index + 1)
            
            elif event.key == pygame.K_BACKSPACE:
                if self.sub_state == "BROWSING":
                    self.sub_state = "SELECT_SHOPPER"
                    self.selected_index = 0

            elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:

                if self.sub_state == "BROWSING":
                    self.item_list.children[self.selected_index].execute()
                elif self.sub_state == "SELECT_SHOPPER":
                    self.manager.set_active_shopper(self.selected_index)
                    self.sub_state = "BROWSING"
                    self.selected_index = 0
            elif event.key == pygame.K_p:
                self.is_done = True

    def buy_item(self, slot, item):
        cost = self.manager.process_purchase(item)
        if cost:
            self.gen_floating_text(slot, cost)
        else: 
            self.gen_floating_text(slot, "not enough money")


    def render(self):
        self.renderer.render(
            self.sub_state, 
            self.manager.party, 
            self.selected_index,
            self.ui_root, 
            self.active_effs
        )


    def gen_floating_text(self, slot, gold):
        texto_str = str(gold)

        fuente = self.display[1][0] 
        ancho_texto = fuente.size(texto_str)[0]

        x_ajustada = slot.global_rect.centerx - (ancho_texto // 2)
        y_ajustada = slot.global_rect.top - 20

        self._floating_text(x_ajustada, y_ajustada, texto_str, self.display[1][0], color=(255, 215, 0))

    def update(self):
        if self.sub_state == "BROWSING":
            self.ui_root.update()
        else:
            for slot in self.item_list.children:
                slot.is_selected = False

        for efecto in self.active_effs:
            efecto.update()

        self.active_effs = [e for e in self.active_effs if e.alpha > 0]


class eventState(State):
    def __init__(self, display):
        super().__init__(display)
        self.selected_index = 0


class chestState(State):
    def __init__(self, display):
        super().__init__(display)
        self.selected_index = 0


class extraState(State):
    def __init__(self, display):
        super().__init__(display)
        self.selected_index = 0


class hubState(State):
    def __init__(self, display):
        super().__init__(display)


class pauseState(menuState):
    def __init__(self, display, columns = 1, save = callable, quit = callable):
        super().__init__(display, ["Continuar", "Guardar", "Salir al Menú"], columns, quit)
        self.save = save

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN: 
                if self.selected_index == 0:
                    self.quit()
                elif self.selected_index == 1:
                    self.save()


class lvlUpState(menuState):
    def __init__(self, display, char, quit):
        options = [
            "Vitality " + str(char.statBlock[0]),
            "Mind " + str(char.statBlock[1]),
            "Inteligence " + str(char.statBlock[2]),
            "Strength " + str(char.statBlock[3]),
            "Luck " + str(char.statBlock[4]),
            "Charisma " + str(char.statBlock[5]),
            "Awareness " + str(char.statBlock[6]),
            "Agility " + str(char.statBlock[7]),
            "Endurance " + str(char.statBlock[8]),
            "Dexterity " + str(char.statBlock[9])
        ]
        super().__init__(display, options, 2, quit)
