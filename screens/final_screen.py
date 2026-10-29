import pygame

from screens.base_screen import BaseScreen
from ui.layout import Layout
from ui.button import Button
from ui import theme


class FinalScreen(BaseScreen):
    def __init__(self, screen_manager, screen, context=None):
        super().__init__(screen_manager, screen, context)

        self.layout = Layout(screen)
        self.build_ui()

    def build_ui(self):
        self.layout.update()

        width = self.layout.width(0.30)
        height = self.layout.height(0.08)
        x = self.layout.x(0.35)

        self.restart_button = Button(
            x,
            self.layout.y(0.62),
            width,
            height,
            "TORNAR A JUGAR",
            self.restart_game
        )

        self.quit_button = Button(
            x,
            self.layout.y(0.74),
            width,
            height,
            "SORTIR DEL JOC",
            self.quit_game
        )

    def restart_game(self):
        # Tornar a la pantalla inicial per crear una partida nova.
        self.sm.change_screen("initial")

    def quit_game(self):
        # Tancar correctament Pygame i el programa.
        pygame.quit()
        raise SystemExit

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            self.on_resize(event.w, event.h)
            return

        self.restart_button.handle_event(event)
        self.quit_button.handle_event(event)

    def render(self, screen):
        screen.fill(theme.BACKGROUND)

        title_font = pygame.font.SysFont(
            theme.FONT_NAME,
            theme.FONT_TITLE,
            bold=True
        )

        subtitle_font = pygame.font.SysFont(
            theme.FONT_NAME,
            theme.FONT_MEDIUM
        )

        winner = getattr(self.game_state, "winner", None)

        if winner is not None:
            title_text = f"GUANYADOR: {winner.name}"
            subtitle_text = "Felicitats per la victòria!"
        else:
            title_text = "FI DE LA BATALLA"
            subtitle_text = "La partida ha acabat."

        title = title_font.render(
            title_text, True, theme.SUCCESS
        )

        subtitle = subtitle_font.render(
            subtitle_text, True, theme.TEXT_SECONDARY
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    self.layout.x(0.5),
                    self.layout.y(0.32)
                )
            )
        )

        screen.blit(
            subtitle,
            subtitle.get_rect(
                center=(
                    self.layout.x(0.5),
                    self.layout.y(0.42)
                )
            )
        )

        self.restart_button.draw(screen)
        self.quit_button.draw(screen)

    def on_resize(self, w, h):
        self.layout.update()
        self.build_ui()

    def update(self):
        pass