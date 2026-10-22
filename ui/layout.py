class Layout:

    def __init__(self, screen):
        self.screen = screen
        self.update()

    def update(self):
        self.w, self.h = self.screen.get_size()

    # 📐 Percentatges
    def x(self, p):
        return self.w * p

    def y(self, p):
        return self.h * p

    def width(self, p):
        return self.w * p

    def height(self, p):
        return self.h * p

    # 📍 Cantonada inferior dreta
    def bottom_right(self, width, height, margin_x=0.03, margin_y=0.03):

        x = self.w - width - self.width(margin_x)
        y = self.h - height - self.height(margin_y)

        return x, y