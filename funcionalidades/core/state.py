import pygame, random, copy, os
from .ui import HBox, VBox, UIPanel, UISlot
from .view import gameRenderer, combatRenderer, shopRenderer
from .manager import gameManager, combatManager, shopManager
from .visuals import floatingText, animation
from vault.items import shopItems
from vault.gear import blacksmith
from funcionalidades.Utility.information import addNotification
from funcionalidades.Utility.saving_loading import load_game_state


"STATE = LOGICA PURA"
"MANAGER = ORCHESTRADOR (MANEJA LAS COSAS -ej- crear enemyList o itemPool, compras, ataques, aka lo que pasa en el estado digamos)"
"RENDERER = LO QUE SE VE EN LA PANTALLA"


class State:
    def __init__(self, display):
        self.display = display
        self.is_done = False
        

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def render(self):
        pass


class menuState(State):
    def __init__(self, display, options, columnas):
        super().__init__(display)
        self.options = options
        self.selected_index = 0
        self.columnas = max(1, columnas)

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
            print(self.adv_party)
            self.enemies = datos["enemies"]
            self.room = datos["room"]
            self.floor = 1
            self.floor_layout = None
        else:
            self.room = 0
            self.floor = 1
            self.floor_layout = None
            self.adv_party = []

        self.manager = gameManager(room, floor, floor_layout)
        self.renderer = gameRenderer(self.display)

        self.update_state(self.manager.active_floor)


    def handle_event(self, event):

        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_ESCAPE:
                if self.menu: self.menu = None
                else: self.menu = pauseState(self.display)
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

        for vfx in self.vfx:
            vfx.update()
        self.vfx = [e for e in self.vfx if not e.is_done]

        if self.is_transitioning:
            transicion = next((v for v in self.vfx if isinstance(v, animation)), None)
            if transicion and transicion.In:
                self.load_new_room()
                self.is_transitioning = False

        if self.sub_state is not None and not self.is_transitioning:
            self.sub_state.update()

            if self.sub_state.is_done:
                if hasattr(self.sub_state, 'result') and self.sub_state.result == "GAME_OVER":
                    self.is_done = True
                    return

                self.sub_state = None
                self.is_transitioning = True
                self.vfx.append(animation(velocity=2))

    def update_state(self, tipo_sala):
        match tipo_sala:
            case "fight" | "elite":
                self.sub_state = combatState(self.display, self.adv_party, [], True, self.manager.room, self.manager.floor, self.manager.active_floor, addNotification) 
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


    def guardar_progreso(self):
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

        self.manager = combatManager(self.party, self.enemies, my_turn, room, floor, activeFloor, addNotification, self._crear_texto_flotante)
        self.renderer = combatRenderer(self.display)

        self.sub_state = "SELECT_ACTION"
        self.current_action = None
        self.menu_options = []
        self.active_effs = []    

        self.menu_opt_update()

    def menu_opt_update(self):
        if self.party_turn >= len(self.party):
            return
        
        personaje_actual = self.manager.party[self.manager.party_turn]
        self.menu_options = []

        if self.sub_state == "SELECT_ACTION":
 
            arma = personaje_actual.weapon.get("primary") if hasattr(personaje_actual, 'weapon') else None
            if arma:
                self.menu_options.append({
                    "name": f"Attack ({arma.name})",
                    "type": "REQUIRES_TARGET",
                    "execute": lambda target: self.manager.melee(personaje_actual, arma, target),
                    "target_team": "enemies"
                })
            else:
                self.menu_options.append({
                    "name": "Attack (fists)",
                    "type": "REQUIRES_TARGET",
                    "execute": lambda target: self.manager.melee(personaje_actual, None, target),
                    "target_team": "enemies"
                })


            if hasattr(personaje_actual, 'skills') and personaje_actual.skills:
                self.menu_options.append({
                    "name": "Skills",
                    "type": "CHOOSE_SKILL",
                    "execute": None,
                    "target_team": "enemies"
                })

            self.menu_options.append({
                "name": "Items",
                "type": "CHOOSE_ITEM",
                "execute": None,
                "target_team": "enemies"
            })

        elif self.sub_state == "SELECT_SKILL":
            for nombre_skill in personaje_actual.skills.keys():
                self.menu_options.append({
                    "name": nombre_skill,
                    "type": "REQUIRES_TARGET",
                    "execute": lambda target, sk=nombre_skill: personaje_actual.skills[sk](personaje_actual, target, "primary")
                })


    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_UP:
            self.selected_index = max(0, self.selected_index - 1)
        elif event.key == pygame.K_DOWN:
            limite = len(getattr(self.manager, self.current_action.get("target_team", "enemies"))) if self.sub_state == "SELECT_TARGET" else len(self.menu_options)
            self.selected_index = min(limite - 1, self.selected_index + 1)
        
        elif event.key == pygame.K_BACKSPACE:
            if self.sub_state in ["SELECT_SKILL", "SELECT_TARGET"]:
                self.sub_state = "SELECT_ACTION"
                self.selected_index = 0
                self.menu_opt_update()

        elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
            if self.sub_state in ["SELECT_ACTION", "SELECT_SKILL"]:
                opcion = self.menu_options[self.selected_index]
                
                if opcion["type"] == "CHOOSE_SKILL":
                    self.sub_state = "SELECT_SKILL"
                    self.selected_index = 0
                    self.menu_opt_update()
                    
                elif opcion["type"] == "REQUIRES_TARGET":
                    self.current_action = opcion
                    self.sub_state = "SELECT_TARGET"
                    self.selected_index = 0 

            elif self.sub_state == "SELECT_TARGET":
                enemigo_objetivo = self.manager.enemies[self.selected_index]
                result = self.current_action["execute"](enemigo_objetivo)

                self.combat_flow(result)


    def combat_flow(self, result):
        if result != "CONTINUE":
            self.is_done = True
            return

        self.sub_state = "SELECT_ACTION"
        self.selected_index = 0
        self.current_action = None
        
        self.menu_opt_update()


    def render(self):
        self.renderer.render(
            party=self.manager.party,
            enemies=self.manager.enemies,
            sub_state=self.sub_state,
            selected_index=self.selected_index,
            party_turn=self.manager.party_turn,
            my_turn=self.manager.my_turn,
            current_action=self.current_action,
            menu_options=self.menu_options,
            active_effs=self.active_effs
        )


    def _crear_texto_flotante(self, objetivo, cantidad):
        x, y = 0, 0

        if objetivo in self.manager.enemies:
            indice = self.manager.enemies.index(objetivo)
            x = 350  
            y = 300 + indice * 40 - 20 
        elif objetivo in self.manager.party:
            indice = self.manager.party.index(objetivo)
            x = 50 + (indice * 240) 
            y = 20 
            
        nuevo_texto = floatingText(cantidad, x, y, color=(255, 50, 50))
        self.active_effs.append(nuevo_texto)


    def update(self):
        for efecto in self.active_effs:
            efecto.update()

        self.active_effs = [e for e in self.active_effs if e.alpha > 0]


class shopState(State):
    def __init__(self, display, adv_party):
        super().__init__(display)
        self.selected_index = 0
        self.turn = 0
        self.party = adv_party

        self.ui_root = UIPanel(0, 600, display[0].get_width(), 200)
        self.lista_items = HBox(10, 0, display[0].get_width(), spacing=15, wrap=True, align="center")
        self.ui_root.add_child(self.lista_items)

        self._generate_item_pool(shopItems)
        for item in self.shop_items:
            slot = UISlot(display[1][0].render(str(item[0].name), True, (255, 255, 255)).width + 20, 40, item[0].name, lambda i=item: self.comprar(i))
            self.lista_items.add_child(slot)

        self.active_effs = []
        self.lista_items.recalculate_layout()

        self.renderer = shopRenderer(self.display, self.shop_items)
        self.manager = shopManager(self.party, self.shop_items,self._crear_texto_flotante)

    def handle_event(self, event):
        self.ui_root.handle_event(event)

    def comprar(self, item):
        print(f"Lógica de compra: {item[0].name}")

    def _generate_item_pool(self, possible_items):

        options = list(range(2, 11))
        weights = [5, 10, 30, 40, 30, 10, 5, 2, 1]
        amount = random.choices(options, k=1, weights=weights)[0]

        item_pool = []
        for i in range(amount):
            rarity = random.choices([0, 1, 2, 3], k=1, weights=[50, 25, 10, 5])[0]
            item_pool.append(random.choice(possible_items[rarity]))

            if random.randint(1, 20) == 20:
                item_pool.append(random.choice(possible_items[rarity]))

        self.shop_items = item_pool


    def render(self):
        pygame.draw.rect(self.display[0], (50, 50, 50), self.ui_root.global_rect)
        self.ui_root.draw(self.display)

    def _crear_texto_flotante(self, itembox, precio):
        x = itembox.x()
        y = itembox.y()
            
        nuevo_texto = floatingText(precio, x, y, color=(255, 255, 0))
        self.active_effs.append(nuevo_texto)


    def update(self):
        self.ui_root.update()

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
    def __init__(self, display, columns = 1):
        super().__init__(display, ["Continuar", "Guardar", "Salir al Menú"], columns)


class lvlUpState(menuState):
    def __init__(self, display, char):
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
        super().__init__(display, options)
