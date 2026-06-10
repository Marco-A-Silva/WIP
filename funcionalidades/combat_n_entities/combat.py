import pygame

class Combat:
    def __init__(self, party, enemies, add_notification):
        self.party = party
        self.enemies = enemies
        self.turn = 0
        self.myTurn = True
        self.bm = BattleManager(self.party, self.enemies, add_notification)

        self.sub_state = "SELECT_ACTION"
        self.selected_index = 0

        self.current_action = None 
        self.current_target = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            
            if self.sub_state == "SELECT_ACTION":
                if event.key == pygame.K_UP:
                    self.selected_index = max(0, self.selected_index - 1)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = min(len(self.menu_options) - 1, self.selected_index + 1)
                
                elif event.key == pygame.K_KP_ENTER:

                    self.current_action = self.menu[self.selected_index]
                    
                    if self.current_action["type"] == "REQUIRES_TARGET":
                        self.sub_state = "SELECT_TARGET"
                        self.selected_index = 0
                    elif self.current_action["type"] == "REQUIRES_SPELL":
                        self.sub_state = "SELECT_SPELL"
                        self.selected_index = 0

            elif self.sub_state == "SELECT_TARGET":
                if event.key == pygame.K_UP:
                    self.selected_index = max(0, self.selected_index - 1)
                
                elif event.key == pygame.K_KP_ENTER:
                    target = self.enemies[self.selected_index]
                    
                    resultado = self.current_action["execute"](target)
                    
                    self.check_battle_status(resultado)