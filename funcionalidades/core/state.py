import pygame, random, copy
from .view import TextoFlotante, gameRenderer, combatRenderer
from .manager import gameManager, combatManager
from vault.enemies import enemies, bosses
from funcionalidades.Utility import addNotification

MAIN_ROOMS = ["fight","chest","shop","event","extra"]
MAIN_ODDS = [55,12,6,22,5]
EXTRA_ROOMS = ["dojo","rest site","school of magic"]
EXTRA_ODDS = [1,3,1]

ROOMS_PER_FLOOR = 9


class State:
    def __init__(self, display):
        self.display = display

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def render(self):
        pass


class gameState(State):
    def __init__(self, display, adv_party, room=0, floor=1, floor_layout=None):
        super().__init__(display)

        self.manager = gameManager(room, floor, floor_layout)
        self.renderer = gameRenderer(self.display)

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def render(self):
        self.renderer.render(
            self.manager.floor_layout,
            self.manager.room,
            self.manager.floor
        )  


class combatState(State):


    def __init__(self, display, party, enemiesS, my_turn, room, floor, activeFloor, pending_levels, addNotification):
        super().__init__(display)
        self.selected_index = 0
        self.ongoing = True
        self.result = ""

        self.party = party
        self.enemies = enemiesS if enemiesS != [] and pending_levels == 0 else self._generate_enemies(random.randint(1,3), enemies, bosses, room, floor, activeFloor)
        self.my_turn = my_turn
        self.party_turn = 0

        self.manager = combatManager(self.party, self.enemies, addNotification, self.crear_texto_flotante)
        self.renderer = combatRenderer(self.display)

        self.sub_state = "SELECT_ACTION"
        self.current_action = None
        self.menu_options = []

        self.active_effs = []    

        self.menu_opt_update()

    def menu_opt_update(self):
        if self.party_turn >= len(self.party):
            return
        
        personaje_actual = self.party[self.party_turn]
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
        """Procesa las entradas del teclado de forma centralizada."""
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_UP:
            self.selected_index = max(0, self.selected_index - 1)
        elif event.key == pygame.K_DOWN:
            limite = len(getattr(self, self.current_action.get("target_team", "enemies"))) if self.sub_state == "SELECT_TARGET" else len(self.menu_options)
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
                enemigo_objetivo = self.enemies[self.selected_index]
                result = self.current_action["execute"](enemigo_objetivo)

                self.combat_flow(result)


    def combat_flow(self, result):
        """Decide qué pasa después de que una acción alteró los números del juego."""
        if result != "CONTINUE":
            self.ongoing = False
            self.result = result

        self.sub_state = "SELECT_ACTION"
        self.selected_index = 0
        self.current_action = None
        
        self.next_turn()
        self.menu_opt_update()


    def next_turn(self):
        self.party_turn += 1
        if self.party_turn >= len(self.party):
            self.party_turn = 0


    def render(self):
        self.renderer.render(
            party=self.party,
            enemies=self.enemies,
            sub_state=self.sub_state,
            selected_index=self.selected_index,
            party_turn=self.party_turn,
            my_turn=self.my_turn,
            current_action=self.current_action,
            menu_options=self.menu_options,
            active_effs=self.active_effs
        )


    def _generate_enemies(self, count, enemies, bosses, level, floor, activeFloor):

        enemyList = [copy.deepcopy(enemy) for enemy in random.choices(enemies, k=count)]
        for i, enemy in enumerate(enemyList):
            enemy.hp = enemy.base_hp + (level * floor)/2

        if activeFloor == "elite":
            boss_count = random.choices([1, 2], weights=[90, 10], k=1)[0]
            bosses_picked = random.choices(bosses, k=boss_count)
            enemyList.append(bosses_picked)

        return enemyList


    def crear_texto_flotante(self, objetivo, cantidad):
        """Calcula dónde está el personaje y genera el efecto visual."""
        x, y = 0, 0
        
        # Averiguamos si el objetivo es un enemigo o un aliado para calcular su X/Y en pantalla.
        # (Estos números los saqué de tu view.py como aproximación)
        if objetivo in self.enemies:
            indice = self.enemies.index(objetivo)
            x = 350  # Posición X aproximada del texto enemigo
            y = 300 + indice * 40 - 20 # Un poco más arriba de su nombre
        elif objetivo in self.party:
            indice = self.party.index(objetivo)
            x = 50 + (indice * 240) # Posición X aproximada de la party
            y = 20 # Arriba del HUD
            
        # Creamos el objeto independiente y lo guardamos
        nuevo_texto = TextoFlotante(cantidad, x, y, color=(255, 50, 50))
        self.active_effs.append(nuevo_texto)


    def update(self):
        """El motor del tiempo de tu estado."""
        # 1. Hacemos que cada efecto mueva sus propias variables
        for efecto in self.active_effs:
            efecto.update()
            
        # 2. Limpieza: Dejamos vivos solo los que aún no se volvieron 100% transparentes
        self.active_effs = [e for e in self.active_effs if e.alpha > 0]


class shopState(State):
    def __init__(self, display):
        super().__init__(display)
        self.selected_index = 0


class eventState(State):
    def __init__(self, display):
        super().__init__(display)
        self.selected_index = 0


class chestState(State):
    def __init__(self, display):
        super().__init__(display)
        self.selected_index = 0


class lvlUpState(State):
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