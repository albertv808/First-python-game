import pygame

from screens.screen_manager import ScreenManager
from screens.register_screens import register_screens


def main():
    pygame.init()

    # 📐 finestra
    screen = pygame.display.set_mode((1000, 700), pygame.RESIZABLE)
    pygame.display.set_caption("Fantasy Army Battle")

    clock = pygame.time.Clock()

    # 🎮 gestor de pantalles
    sm = ScreenManager(screen)
    # 👉 registrar totes les pantalles
    register_screens(sm)

    # 👉 carregar primera pantalla
    sm.change_screen("initial")

    running = True

    while running:
        events = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            events.append(event)

        # 🎯 update
        sm.update(events)

        # 🖼 render
        sm.draw()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
