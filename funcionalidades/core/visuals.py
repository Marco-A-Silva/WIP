import pygame

class animation:
    def __init__(self, velocity):
        self.alpha = 0
        self.velocity = velocity
        self.is_done = False
        self.In = False
        self.phase = "OUT"

    def render(self, screen):
        ancho_pantalla = screen.get_width()
        alto_pantalla = screen.get_height()

        overlay = pygame.Surface((ancho_pantalla, alto_pantalla), pygame.SRCALPHA)
        overlay.fill((0, 0, 0))
        overlay.set_alpha(self.alpha)
        screen.blit(overlay, (0, 0))


    def update(self):
        if self.phase == "OUT":
            self.alpha += self.velocity
            if self.alpha >= 255:
                self.alpha = 255
                self.phase = "IN"
                self.In = True # Marcamos que estamos en negro
        else:
            self.alpha -= self.velocity
            if self.alpha <= 0:
                self.alpha = 0
                self.is_done = True


class floatingText:
    def __init__(self, texto, x, y, color=(255, 50, 50)):
        self.texto = str(texto)
        self.x = x
        self.y = y
        self.color = color
        self.alpha = 255
        self.velocidad_y = -1  

    def update(self):
        """El objeto maneja su propio paso del tiempo."""
        self.y += self.velocidad_y
        self.alpha -= 4  # Se desvanece
        
    def draw(self, surface, font):
        """El objeto sabe cómo dibujarse a sí mismo."""
        superficie_texto = font.render(self.texto, True, self.color)
        superficie_texto.set_alpha(max(0, self.alpha))
        surface.blit(superficie_texto, (self.x, self.y))
