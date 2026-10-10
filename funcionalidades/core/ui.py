import pygame
from .decor import requiere_active


class UIElement:
    def __init__(self, x, y, width, height):
        self.local_rect = pygame.Rect(x, y, width, height)
        self.parent = None
        self.is_active = True
        self.is_hovered = False
        self.is_selected = False

    @property
    def global_x(self):
        if self.parent:
            return self.parent.global_x + self.local_rect.x
        return self.local_rect.x

    @property
    def global_y(self):
        if self.parent:
            return self.parent.global_y + self.local_rect.y
        return self.local_rect.y

    @property
    def global_rect(self):
        return pygame.Rect(self.global_x, self.global_y, self.local_rect.width, self.local_rect.height)

    @requiere_active
    def update(self, *args, **kwargs):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.global_rect.collidepoint(mouse_pos)

    @requiere_active
    def draw(self, surface, *args, **kwargs):
        pass

    @requiere_active
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.global_rect.collidepoint(event.pos):
                self.execute()
        
    def execute(self):
        pass


class UIPanel(UIElement):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.children = []

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def update(self, *args, **kwargs):
        super().update(args, kwargs)
        for child in reversed(self.children):
            child.update()

    @requiere_active
    def handle_event(self, event):
        pass

    @requiere_active
    def draw(self, surface):
        for child in self.children:
            child.draw(surface)


class VBox(UIPanel):
    def __init__(self, x, y, max_height, spacing=10, wrap=False, align="top"):
        super().__init__(x, y, 0, max_height)
        self.spacing = spacing
        self.max_height = max_height
        self.wrap = wrap
        self.align = align  

    def add_child(self, child):
        super().add_child(child)

    def recalculate_layout(self):
        if not self.children:
            self.local_rect.width = 0
            return

        columns = []

        if self.wrap:
            act_column = []
            act_column_height = 0
            
            for child in self.children:
                child_h = child.local_rect.height
                
                if act_column and (act_column_height + self.spacing + child_h > self.max_height):
                    columns.append({"items": act_column, "height": act_column_height})
                    act_column = [child]
                    act_column_height = child_h
                else:
                    act_column.append(child)
                    if len(act_column) > 1:
                        act_column_height += self.spacing + child_h
                    else:
                        act_column_height = child_h
            if act_column:
                columns.append({"items": act_column, "height": act_column_height})
        else:
            alto_total = sum(c.local_rect.height for c in self.children) + self.spacing * (len(self.children) - 1)
            columns.append({"items": self.children, "height": alto_total})

        cursor_x = 0
        
        for column in columns:
            if self.align == "center":
                cursor_y = (self.max_height - column["height"]) // 2
            elif self.align == "bottom":
                cursor_y = self.max_height - column["height"]
            else:  # "top"
                cursor_y = 0

            column_max_width = 0
            
            for item in column["items"]:
                item.local_rect.x = cursor_x
                item.local_rect.y = cursor_y
                
                cursor_y += item.local_rect.height + self.spacing
                
                if item.local_rect.width > column_max_width:
                    column_max_width = item.local_rect.width
            
            cursor_x += column_max_width + self.spacing

        self.local_rect.width = cursor_x - self.spacing if cursor_x > 0 else 0
        
        if not self.wrap:
            self.local_rect.height = columns[0]["height"]

class HBox(UIPanel):
    def __init__(self, x, y, max_width, spacing=10, wrap=False, align="left"):
        super().__init__(x, y, max_width, 0)
        self.spacing = spacing
        self.max_width = max_width
        self.wrap = wrap
        self.align = align

    def add_child(self, child):
        super().add_child(child)

    def recalculate_layout(self):
        if not self.children:
            self.local_rect.height = 0
            return

        rows = []

        if self.wrap:
            act_row = []
            act_row_width = 0
            
            for child in self.children:
                child_w = child.local_rect.width
                
                if act_row and (act_row_width + self.spacing + child_w > self.max_width):
                    rows.append({"items": act_row, "width": act_row_width})
                    act_row = [child]
                    act_row_width = child_w
                else:
                    act_row.append(child)
                    if len(act_row) > 1:
                        act_row_width += self.spacing + child_w
                    else:
                        act_row_width = child_w
            if act_row:
                rows.append({"items": act_row, "width": act_row_width})
        else:
            ancho_total = sum(c.local_rect.width for c in self.children) + self.spacing * (len(self.children) - 1)
            rows.append({"items": self.children, "width": ancho_total})

        cursor_y = 0
        
        for row in rows:
            if self.align == "center":
                cursor_x = (self.max_width - row["width"]) // 2
            elif self.align == "right":
                cursor_x = self.max_width - row["width"]
            else:  # "left"
                cursor_x = 0

            row_max_height = 0
            
            for item in row["items"]:
                item.local_rect.x = cursor_x
                item.local_rect.y = cursor_y
                
                cursor_x += item.local_rect.width + self.spacing
                
                if item.local_rect.height > row_max_height:
                    row_max_height = item.local_rect.height
            
            cursor_y += row_max_height + self.spacing

        self.local_rect.height = cursor_y - self.spacing if cursor_y > 0 else 0
        
        if not self.wrap:
            self.local_rect.width = rows[0]["width"]


class UILabel(UIElement):
    def __init__(self, text, font, color=(255, 255, 255)):
        width, height = font.size(text)
        super().__init__(0, 0, width, height)
        self.text = text
        self.font = font
        self.color = color

    def draw(self, display):
        surface = display[0]
        text_surf = self.font.render(self.text, True, self.color)
        surface.blit(text_surf, (self.global_x, self.global_y))


class SItemSlot(UIElement):
    def __init__(self, width, height, name, data):
        super().__init__(0, 0, width, height)
        self.name = name
        self.data = data

    def draw(self, display):
        if self.is_hovered or self.is_selected:
            color_fondo = (80, 80, 80)
            color_borde = (255, 255, 0)
            grosor_borde = 3
        else:
            color_fondo = (50, 50, 50)
            color_borde = (200, 200, 200)
            grosor_borde = 2

        pygame.draw.rect(display[0], color_fondo, self.global_rect)
        pygame.draw.rect(display[0], color_borde, self.global_rect, grosor_borde)
        
        text_surface = display[1][0].render(str(self.name), True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.global_rect.center)
        
        display[0].blit(text_surface, text_rect)

    def execute(self):
        if callable(self.data):
            self.data()
            
class CharSlot(UIElement):
    def __init__(self, width, height, char, index, open_details):
        super().__init__(0, 0, width, height)
        self.char = char
        self.index = index
        self.open_details = open_details
        
    def execute(self):
        self.open_details(self.char)

class SCharSlot(CharSlot):
    def __init__(self, width, height, char, index, set_active_shopper, open_details):
        super().__init__(width, height, char, index, open_details)
        self.set_active_shopper = set_active_shopper

class DetailsMenu(UIPanel):
    def __init__(self, screen_width, screen_height, entity, fonts, close_callback):
        super().__init__(0, 0, screen_width, screen_height)
        self.entity = entity
        self.close_callback = close_callback
        font_title = fonts[1]
        font_text = fonts[0]