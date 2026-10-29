import pygame

from core.troop import Troop
from data.troops_data import TROOPS
from screens.base_screen import BaseScreen

from ui.layout import Layout
from ui.button import Button
from ui.slider import Slider
from ui.input_box import InputBox
from ui.scrollbar import Scrollbar
from ui import theme


class SelectScreen(BaseScreen):
    HEADER_HEIGHT = 0.14
    FOOTER_HEIGHT = 0.13
    MARGIN = 0.025
    GAP = 0.015

    def __init__(self, screen_manager, screen, context=None):
        super().__init__(screen_manager, screen, context)

        self.layout = Layout(screen)

        self.players = [self.game_state.player1, self.game_state.player2]

        self.current_player_index = 0
        self.current_player = self.players[0]

        self.troop_keys = list(TROOPS.keys())

        self.selected_troop_key = (self.troop_keys[0] if self.troop_keys else None)

        self.selection = {key: 0 for key in self.troop_keys}

        self.troop_buttons = []
        self.army_rows = []
        self.army_buttons = []

        self.slider = None
        self.amount_input = None
        self.add_button = None
        self.remove_input = None
        self.remove_button = None
        self.confirm_button = None

        self.scrollbar = None
        self.army_scrollbar = None

        self.build_ui()

    # ==========================================================
    # DISTRIBUCIÓ DE LES TRES COLUMNES
    # ==========================================================

    def build_ui(self):
        self.layout.update()

        w, h = self.layout.w, self.layout.h

        margin = int(w * self.MARGIN)
        gap = int(w * self.GAP)

        usable_width = (w - 2 * margin - 2 * gap)

        self.left_width = int(usable_width * 0.31)

        self.center_width = int(usable_width * 0.39)

        self.right_width = (usable_width - self.left_width - self.center_width)

        self.left_x = margin

        self.center_x = (self.left_x + self.left_width + gap)

        self.right_x = (self.center_x + self.center_width + gap)

        self.header_bottom = int(h * self.HEADER_HEIGHT)

        self.footer_top = int(h * (1 - self.FOOTER_HEIGHT))

        self.panel_top = (self.header_bottom + int(h * 0.025))

        self.panel_bottom = (self.footer_top - int(h * 0.025))

        panel_height = max(1, self.panel_bottom - self.panel_top)

        self.left_panel = pygame.Rect(self.left_x, self.panel_top, self.left_width, panel_height)

        self.center_panel = pygame.Rect(self.center_x, self.panel_top, self.center_width, panel_height)

        self.right_panel = pygame.Rect(self.right_x, self.panel_top, self.right_width, panel_height)

        # Construir els elements de cada columna.
        self.build_troop_list()
        self.build_quantity_controls()
        self.build_army_list()
        self.build_remove_controls()
        self.build_confirm_button()
        self.update_quantity_limits()

    # ==========================================================
    # LLISTA CENTRAL I SCROLLBAR
    # ==========================================================

    def build_troop_list(self):
        self.troop_buttons = []

        title_height = int(self.layout.h * 0.065)

        self.list_viewport = pygame.Rect(self.center_panel.x + 8, self.center_panel.y + title_height,
                                         self.center_panel.width - 28,
                                         max(1, self.center_panel.height - title_height - 12))

        self.troop_row_height = max(38, int(self.layout.h * 0.065))

        self.troop_row_gap = max(5, int(self.layout.h * 0.01))

        content_height = len(self.troop_keys) * (self.troop_row_height + self.troop_row_gap)

        self.scrollbar = Scrollbar(self.center_panel.right - 15, self.list_viewport.y, 9, self.list_viewport.height,
                                   content_height=content_height, view_height=self.list_viewport.height)

        for key in self.troop_keys:
            troop = Troop(key)

            button = Button(self.list_viewport.x, self.list_viewport.y, self.list_viewport.width, self.troop_row_height,
                            f"{troop.name} (${troop.cost})", lambda k=key: self.select_troop(k))

            self.troop_buttons.append((key, button))

        self.update_troop_button_positions()

    def update_troop_button_positions(self):
        for index, (_, button) in enumerate(self.troop_buttons):
            button.rect.y = (self.list_viewport.y + index * (
                    self.troop_row_height + self.troop_row_gap) - self.scrollbar.scroll)

    def select_troop(self, troop_key):
        self.selected_troop_key = troop_key

        self.update_quantity_limits()
        self.update_remove_limits()

    # ==========================================================
    # SLIDER, INPUT NUMÈRIC I BOTÓ D'AFEGIR
    # ==========================================================

    def build_quantity_controls(self):
        panel = self.left_panel

        inner_x = panel.x + 12
        inner_width = max(1, panel.width - 24)

        # Títol de la zona de compra
        self.quantity_title_y = panel.bottom - int(self.layout.h * 0.205)

        # Slider i InputBox a la mateixa altura
        slider_y = panel.bottom - int(self.layout.h * 0.145)

        control_height = max(26, int(self.layout.h * 0.038))
        input_width = min(75, max(55, inner_width // 4))
        gap = 10

        slider_width = max(30, inner_width - input_width - gap)

        self.slider = Slider(inner_x, slider_y, slider_width, minimum=0, maximum=0, value=0, height=8)

        self.amount_input = InputBox(inner_x + slider_width + gap, slider_y - (control_height - 8) // 2, input_width,
            control_height, text="0", minimum=0, maximum=0)

        # Botó separat a sota dels dos controls
        add_y = panel.bottom - int(self.layout.h * 0.065) - control_height

        self.add_button = Button(inner_x, add_y, inner_width, control_height, "AFEGIR TROPES", self.add_selected_troops)

    def update_quantity_limits(self):
        if (self.slider is None or self.amount_input is None or self.add_button is None):
            return

        maximum = 0

        if self.selected_troop_key is not None:
            troop = Troop(self.selected_troop_key)

            if troop.cost > 0:
                maximum = (self.current_player.money // troop.cost)
            else:
                # Evitar una divisió per zero.
                maximum = 999

        current_value = (self.amount_input.get_value())

        self.slider.minimum = 0
        self.slider.maximum = maximum

        self.slider.set_value(min(current_value, maximum))

        self.amount_input.minimum = 0
        self.amount_input.maximum = maximum

        self.amount_input.set_value(self.slider.value)

        self.add_button.enabled = (self.selected_troop_key is not None and maximum > 0)

    # ==========================================================
    # ESTADÍSTIQUES DE LA TROPA SELECCIONADA
    # ==========================================================

    def get_selected_troop(self):
        if self.selected_troop_key is None:
            return None

        return Troop(self.selected_troop_key)

    def get_selected_troop_count(self):
        if self.selected_troop_key is None:
            return 0

        return self.selection.get(self.selected_troop_key, 0)

    # ==========================================================
    # COMPRA DE TROPES
    # ==========================================================

    def add_selected_troops(self):
        if self.selected_troop_key is None:
            return

        troop = Troop(self.selected_troop_key)

        amount = self.amount_input.get_value()

        if amount <= 0:
            return

        if not self.current_player.can_afford(troop, amount):
            return

        if not self.current_player.spend_money(troop, amount):
            return

        key = self.selected_troop_key

        self.selection[key] = (self.selection.get(key, 0) + amount)

        self.sync_army_selection()
        self.update_quantity_limits()
        self.build_army_list()

    # ==========================================================
    # SINCRONITZACIÓ AMB EL JUGADOR
    # ==========================================================

    def sync_army_selection(self):
        selected = self.selection.copy()

        self.current_player.troops_selected = (selected.copy())

        self.current_player.army_selection = (selected.copy())

    # ==========================================================
    # RETIRAR TROPES I RECUPERAR DINERS
    # ==========================================================

    def remove_selected_troops(self):
        if self.selected_troop_key is None:
            return

        key = self.selected_troop_key
        current_count = self.selection.get(key, 0)

        if current_count <= 0:
            return

        amount = self.remove_input.get_value()
        amount = min(amount, current_count)

        if amount <= 0:
            return

        troop = Troop(key)

        # Retornar els diners
        self.current_player.money += troop.cost * amount

        # Actualitzar la selecció
        self.selection[key] -= amount

        self.sync_army_selection()

        # Actualitzar la interfície
        self.update_quantity_limits()
        self.build_army_list()
        self.update_remove_limits()
    # ==========================================================
    # COST I QUANTITAT TOTAL
    # ==========================================================

    def get_total_cost(self):
        return sum(TROOPS[key]["cost"] * count for key, count in self.selection.items())

    def get_total_units(self):
        return sum(self.selection.values())

    # ==========================================================
    # LLISTA DE L'EXÈRCIT SELECCIONAT
    # ==========================================================

    def build_army_list(self):
        self.army_rows = []
        self.army_buttons = []

        panel = self.right_panel

        # Àrea visible de la llista
        self.army_viewport = self.get_army_viewport()

        self.army_row_height = max(30, int(self.layout.h * 0.05))
        self.army_row_gap = max(4, int(self.layout.h * 0.008))

        content_height = 0

        for key in self.troop_keys:
            count = self.selection.get(key, 0)

            if count <= 0:
                continue

            troop = Troop(key)

            label = Button(self.army_viewport.x, self.army_viewport.y, self.army_viewport.width, self.army_row_height,
                f"{troop.name}: {count}", lambda k=key: self.select_troop(k), color=theme.SURFACE,
                hover_color=theme.SURFACE_HOVER, border_color=theme.BORDER)

            self.army_rows.append((key, label))

            content_height += self.army_row_height + self.army_row_gap

        self.army_buttons = [(key, label, None, None) for key, label in self.army_rows]

        # Crear el scrollbar vertical
        self.army_scrollbar = Scrollbar(panel.right - 15, self.army_viewport.y, 9, self.army_viewport.height,
            content_height=content_height, view_height=self.army_viewport.height)

        self.update_army_row_positions()

    def update_army_row_positions(self):
        if not self.army_rows or self.army_scrollbar is None:
            return

        for index, (_, button) in enumerate(self.army_rows):
            button.rect.y = (self.army_viewport.y + index * (
                        self.army_row_height + self.army_row_gap) - self.army_scrollbar.scroll)

    def get_army_viewport(self):
        panel = self.right_panel

        top = panel.y + int(self.layout.h * 0.09)
        bottom = panel.bottom - int(self.layout.h * 0.27)

        return pygame.Rect(panel.x + 8, top, panel.width - 28, max(1, bottom - top))

    # ==========================================================
    # CONFIRMACIÓ I CANVI DE JUGADOR
    # ==========================================================

    def build_confirm_button(self):
        width = int(self.layout.w * 0.30)

        height = max(40, int(self.layout.h * 0.075))

        x = (self.layout.w - width - int(self.layout.w * 0.03))

        y = (self.layout.h - height - int(self.layout.h * 0.025))

        self.confirm_button = Button(x, y, width, height, "CONFIRMAR", self.confirm_selection)

    def confirm_selection(self):
        self.sync_army_selection()

        self.current_player_index += 1

        if self.current_player_index < len(self.players):
            self.current_player = self.players[self.current_player_index]

            self.selection = {key: 0 for key in self.troop_keys}

            self.selected_troop_key = (self.troop_keys[0] if self.troop_keys else None)

            self.build_ui()

        else:
            self.sm.change_screen("deploy", self.game_state)

    # ==========================================================
    # GESTIÓ DELS ESDEVENIMENTS
    # ==========================================================

    def handle_event(self, event):

        # ==========================================================
        # CANVI DE MIDA
        # ==========================================================

        if event.type == pygame.VIDEORESIZE:
            self.on_resize(event.w, event.h)
            return

        # ==========================================================
        # SCROLLBAR DE LA LLISTA CENTRAL
        # ==========================================================

        if self.scrollbar.handle_event(event, self.list_viewport):
            self.update_troop_button_positions()
            return

        # ==========================================================
        # SELECCIÓ DE TROPA A LA COLUMNA CENTRAL
        # ==========================================================

        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.list_viewport.collidepoint(event.pos)):
            for key, button in self.troop_buttons:
                if button.rect.collidepoint(event.pos):
                    self.select_troop(key)
                    return

            return

        # ==========================================================
        # COLUMNA DRETA: SELECCIÓ DE TROPES DE L'EXÈRCIT
        # ==========================================================

        # SCROLLBAR DE LA LLISTA CENTRAL
        if self.scrollbar.handle_event(event, self.list_viewport):
            self.update_troop_button_positions()
            return

        # SCROLLBAR DE L'EXÈRCIT SELECCIONAT
        if self.army_scrollbar is not None:
            if self.army_scrollbar.handle_event(event, self.get_army_viewport()):
                self.update_army_row_positions()
                return

        # SELECCIÓ DE TROPES DE L'EXÈRCIT
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            viewport = self.get_army_viewport()

            if viewport.collidepoint(event.pos):
                for key, label in self.army_rows:
                    if label.rect.collidepoint(event.pos):
                        self.select_troop(key)
                        return

                return
        # ==========================================================
        # INPUTBOX DE RETIRADA
        # ==========================================================

        if self.remove_input is not None:
            self.remove_input.handle_event(event)

        # ==========================================================
        # BOTÓ DE RETIRADA
        # ==========================================================

        if self.remove_button is not None:
            if self.remove_button.handle_event(event):
                return

        # ==========================================================
        # SLIDER DE COMPRA
        # ==========================================================

        if self.slider is not None:
            if self.slider.handle_event(event):
                self.amount_input.set_value(self.slider.value)
                return

        # ==========================================================
        # INPUTBOX DE COMPRA
        # ==========================================================

        if self.amount_input is not None:
            if self.amount_input.handle_event(event):
                self.slider.set_value(self.amount_input.get_value())
                return

        # ==========================================================
        # BOTÓ D'AFEGIR TROPES
        # ==========================================================

        if self.add_button is not None:
            if self.add_button.handle_event(event):
                return

        # ==========================================================
        # CONFIRMACIÓ
        # ==========================================================

        if self.confirm_button is not None:
            self.confirm_button.handle_event(event)

    # ==========================================================
    # CANVI DE MIDA DE LA FINESTRA
    # ==========================================================

    def on_resize(self, w, h):
        self.layout.update()
        self.build_ui()

    # ==========================================================
    # FUNCIONS DE DIBUIX
    # ==========================================================

    def draw_panel(self, screen, rect):
        pygame.draw.rect(screen, theme.SURFACE, rect, border_radius=theme.BORDER_RADIUS)

        pygame.draw.rect(screen, theme.BORDER, rect, theme.BORDER_WIDTH, border_radius=theme.BORDER_RADIUS)

    def draw_text(self, screen, text, x, y, size, color=None):
        font = pygame.font.SysFont(theme.FONT_NAME, size)

        surface = font.render(str(text), True, color or theme.TEXT)

        screen.blit(surface, (int(x), int(y)))

    # ==========================================================
    # RENDER PRINCIPAL
    # ==========================================================

    def render(self, screen):
        screen.fill(theme.BACKGROUND)

        # Capçalera
        self.draw_text(screen, f"SELECCIÓ DE L'EXÈRCIT - "
                               f"{self.current_player.name}", self.layout.x(0.025), self.layout.y(0.025),
                       theme.FONT_TITLE)

        self.draw_text(screen, f"Diners: ${self.current_player.money}", self.layout.x(0.70), self.layout.y(0.045),
                       theme.FONT_MEDIUM, theme.SUCCESS)

        # Panells
        self.draw_panel(screen, self.left_panel)
        self.draw_panel(screen, self.center_panel)
        self.draw_panel(screen, self.right_panel)

        # Contingut de cada columna
        self.draw_details(screen)
        self.draw_troop_list(screen)
        self.draw_army_panel(screen)

        # Botó fix inferior
        self.confirm_button.draw(screen)

        # ==========================================================  # COLUMNA ESQUERRA: DETALLS I QUANTITAT  # ==========================================================

    def draw_details(self, screen):
        panel = self.left_panel
        x = panel.x + 12
        y = panel.y + 12

        self.draw_text(screen, "DETALLS DE LA TROPA", x, y, theme.FONT_MEDIUM, theme.PRIMARY_HOVER)

        y += int(self.layout.h * 0.05)

        troop = self.get_selected_troop()

        if troop is None:
            self.draw_text(screen, "No hi ha tropes disponibles.", x, y, theme.FONT_SMALL)
            return

        self.draw_text(screen, f"{troop.name} ({troop.symbol})", x, y, theme.FONT_MEDIUM)

        y += int(self.layout.h * 0.045)

        line_height = max(18, int(self.layout.h * 0.029))

        # ======================================================
        # ESTADÍSTIQUES EN DUES COLUMNES
        # ======================================================

        self.draw_text(screen, "ESTADÍSTIQUES", x, y, theme.FONT_SMALL, theme.PRIMARY_HOVER)

        y += line_height

        stats = [("Cost", f"${troop.cost}"), ("Vida", troop.life), ("Atac", troop.attack), ("Defensa", troop.defence),
            ("Dany", troop.damage), ("Moviment", troop.movement), ("Abast", troop.attack_range), ]

        column_gap = 12
        column_width = max(1, (panel.width - 24 - column_gap) // 2)

        for index, (label, value) in enumerate(stats):
            column = index % 2
            row = index // 2

            stat_x = x + column * (column_width + column_gap)
            stat_y = y + row * line_height

            self.draw_text(screen, f"{label}: {value}", stat_x, stat_y, theme.FONT_SMALL, theme.TEXT_SECONDARY)

        # Tres files d'estadístiques com a màxim.
        y += 4 * line_height

        # ======================================================
        # EQUIPAMENT
        # ======================================================

        self.draw_text(screen, "EQUIPAMENT", x, y, theme.FONT_SMALL, theme.PRIMARY_HOVER)

        y += line_height

        damage_names = {"blunt": "Contús", "slash": "Tallant", "pierce": "Perforant", }

        armor_names = {"unarmored": "Sense armadura", "gambeson": "Gambeson", "mail": "Malla", "plate": "Plaques",
            "scale": "Escates", "lamellar": "Lamellar", "brigantine": "Brigantina", "leather": "Cuir", }

        shield_names = {"no_shield": "Sense escut", "small_shield": "Petit", "shield": "Normal",
            "large_shield": "Gran", }

        modifier_names = {"light": "lleuger", "medium": "mitjà", "heavy": "pesant", }

        damage_type = damage_names.get(troop.damage_type, troop.damage_type)
        damage_modifier = modifier_names.get(troop.damage_modifier, "")

        armor_type = armor_names.get(troop.armor_type, troop.armor_type)
        armor_modifier = modifier_names.get(troop.armor_modifier, "")

        shield_type = shield_names.get(troop.shield_type, troop.shield_type)
        shield_modifier = modifier_names.get(troop.shield_modifier, "")

        equipment = [f"Dany: {damage_type} ({damage_modifier})", f"Armadura: {armor_type} ({armor_modifier})",
            f"Escut: {shield_type} ({shield_modifier})", ]

        for item in equipment:
            self.draw_text(screen, item, x, y, theme.FONT_SMALL, theme.TEXT_SECONDARY)
            y += line_height

        # ======================================================
        # HABILITATS
        # ======================================================

        y += 4

        self.draw_text(screen, "HABILITATS", x, y, theme.FONT_SMALL, theme.PRIMARY_HOVER)

        y += line_height

        abilities = troop.abilities or ["Cap"]

        abilities_bottom = (self.quantity_title_y - int(self.layout.h * 0.02))

        for ability in abilities:
            if y + line_height > abilities_bottom:
                self.draw_text(screen, "...", x, y, theme.FONT_SMALL, theme.TEXT_MUTED)
                break

            self.draw_text(screen, f"- {ability}", x, y, theme.FONT_SMALL, theme.TEXT_SECONDARY)
            y += line_height

        # ======================================================
        # CONTROLS DE COMPRA
        # ======================================================

        self.draw_text(screen, "QUANTITAT A AFEGIR", x, self.quantity_title_y, theme.FONT_SMALL, theme.PRIMARY_HOVER)

        self.draw_text(screen, f"Màxim assequible: {self.slider.maximum}", x, self.slider.y - 23, theme.FONT_SMALL,
            theme.TEXT_SECONDARY)

        self.slider.draw(screen)
        self.amount_input.draw(screen)
        self.add_button.draw(screen)

        # ==========================================================  # COLUMNA CENTRAL: LLISTA DE TROPES  # ==========================================================

    def draw_troop_list(self, screen):
        self.draw_text(screen, "TROPES DISPONIBLES", self.center_panel.x + 10, self.center_panel.y + 10,
                       theme.FONT_MEDIUM, theme.PRIMARY_HOVER)

        old_clip = screen.get_clip()

        screen.set_clip(self.list_viewport)

        for key, button in self.troop_buttons:
            visible = (button.rect.bottom > self.list_viewport.top and button.rect.top < self.list_viewport.bottom)

            if not visible:
                continue

            if key == self.selected_troop_key:
                pygame.draw.rect(screen, theme.PRIMARY_BORDER, button.rect.inflate(4, 4),
                                 border_radius=theme.BORDER_RADIUS)

            button.draw(screen)

        screen.set_clip(old_clip)

        self.scrollbar.draw(screen)

        # ==========================================================  # COLUMNA DRETA: EXÈRCIT SELECCIONAT  # ==========================================================

    def draw_army_panel(self, screen):
        panel = self.right_panel

        x = panel.x + 10
        y = panel.y + 10

        # Títol i total d'unitats
        self.draw_text(screen, "EXÈRCIT SELECCIONAT", x, y, theme.FONT_MEDIUM, theme.PRIMARY_HOVER)

        total_units = sum(self.selection.values())

        self.draw_text(screen, f"Unitats: {total_units}", x, y + int(self.layout.h * 0.04), theme.FONT_SMALL,
            theme.TEXT_SECONDARY)

        # Llista amb retall visual
        viewport = self.get_army_viewport()

        old_clip = screen.get_clip()
        screen.set_clip(viewport)

        for _, button in self.army_rows:
            if (button.rect.bottom > viewport.top and button.rect.top < viewport.bottom):
                button.draw(screen)

        screen.set_clip(old_clip)

        # Scrollbar de la llista
        if self.army_scrollbar is not None:
            self.army_scrollbar.draw(screen)

        # Separador dels controls inferiors
        divider_y = panel.bottom - int(self.layout.h * 0.27)

        pygame.draw.line(screen, theme.BORDER, (panel.x + 10, divider_y), (panel.right - 10, divider_y), 2)

        # Cost total
        self.draw_text(screen, f"Cost total: ${self.get_total_cost()}", x, divider_y + 8, theme.FONT_SMALL,
            theme.SUCCESS)

        # Quantitat a retirar
        if self.remove_input is not None:
            self.draw_text(screen, "QUANTITAT A RETIRAR", x, self.remove_label_y, theme.FONT_SMALL, theme.PRIMARY_HOVER)

            self.remove_input.draw(screen)

        # Botó de retirada
        if self.remove_button is not None:
            self.remove_button.draw(screen)

    def build_remove_controls(self):
        panel = self.right_panel

        margin = 10
        width = panel.width - margin * 2
        h = self.layout.h

        # Zona inferior reservada per retirar tropes
        self.remove_label_y = panel.bottom - int(h * 0.245)

        input_y = panel.bottom - int(h * 0.205)
        input_height = max(30, int(h * 0.045))

        self.remove_input = InputBox(panel.x + margin, input_y, min(100, width), input_height, text="1", minimum=1,
            maximum=1)

        button_y = panel.bottom - int(h * 0.14)
        button_height = max(32, int(h * 0.05))

        self.remove_button = Button(panel.x + margin, button_y, width, button_height, "RETIRAR TROPES",
            self.remove_selected_troops, color=theme.DANGER, hover_color=(240, 100, 100))

        self.update_remove_limits()

    def update_remove_limits(self):
        if self.remove_input is None:
            return

        current_count = 0

        if self.selected_troop_key is not None:
            current_count = self.selection.get(self.selected_troop_key, 0)

        self.remove_input.minimum = 1
        self.remove_input.maximum = max(1, current_count)

        value = self.remove_input.get_value()

        if current_count > 0:
            self.remove_input.set_value(min(max(1, value), current_count))
        else:
            self.remove_input.set_value(1)

        self.remove_button.enabled = current_count > 0


