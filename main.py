import pygame

WIDTH, HEIGHT = 1280, 720

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
CLOCK = pygame.time.Clock()
MAX_PROJECTILES = 3
FONT = pygame.font.SysFont("Cooper", 60)


def hsv_to_rgb(h, s, v):  # Shamelessly stolen code
    if s == 0.0:
        v *= 255
        return (v, v, v)
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p, q, t = (
        int(255 * (v * (1.0 - s))),
        int(255 * (v * (1.0 - s * f))),
        int(255 * (v * (1.0 - s * (1.0 - f)))),
    )
    v *= 255
    i %= 6
    if i == 0:
        return (v, t, p)
    if i == 1:
        return (q, v, p)
    if i == 2:
        return (p, v, t)
    if i == 3:
        return (p, q, v)
    if i == 4:
        return (t, p, v)
    if i == 5:
        return (v, p, q)


def colliding(rect1: pygame.rect, rect2: pygame.rect):
    return (
        rect1.x < 0
        or rect1.x > WIDTH - 80
        or rect1.y < 0
        or rect1.y > HEIGHT - 80
        or pygame.Rect.colliderect(rect1, rect2)
    )


class Entity:
    def __init__(self, x, y, sprite, rotation, size):
        if type(sprite) == str:
            self.sprite = pygame.transform.scale(
                pygame.transform.rotate(pygame.image.load(sprite), rotation),
                (size, size),
            )
        else:
            self.sprite = pygame.transform.scale(sprite, (size, size))
        self.rect = pygame.Rect(x, y, self.sprite.get_height(), self.sprite.get_width())
        self.x_speed = 0.0
        self.y_speed = 0.0
        self.rotation = rotation


class Missle(Entity):
    def __init__(self, x, y, sprite, team, enemy, rotation=0, size=5):
        super().__init__(x, y, sprite, rotation, size)
        self.enemy = enemy
        self.team = team

    def update(self):
        if not (self.rect.x > WIDTH or self.rect.x < 0):
            if colliding(self.rect, self.enemy):
                self.team.score += 1
                missles.remove(self)
                del self
            else:
                self.rect.x += (int(self.rotation < 0) * 2 - 1) * 10
                SCREEN.blit(self.sprite, (self.rect.x, self.rect.y))
        else:
            missles.remove(self)
            del self


class Player(Entity):
    def __init__(self, x, y, sprite, controls, rotation=0, size=80, enemy=None):
        super().__init__(x, y, sprite, rotation, size)
        self.controls = controls
        self.score = 0
        self.enemy = enemy
        self.cooldown = 0
        print(f"Player crated!")

    def fire(self):
        if self.cooldown <= 0:
            print("Missle fired!")
            if (
                len([missle for missle in missles if missle.team is self])
                <= MAX_PROJECTILES
            ):
                missles.append(
                    Missle(
                        self.rect.x,
                        self.rect.y,
                        self.sprite,
                        self,
                        self.enemy,
                        rotation=self.rotation,
                        size=50,
                    )
                )
                self.cooldown = 10

    def update(self, pressed):
        global lvl_elements
        self.cooldown -= 0.5
        for key, action in self.controls.items():
            if pressed[key]:
                if type(action) == tuple:
                    self.x_speed += action[0]
                    self.y_speed += action[1]
                else:
                    {"fire": self.fire}[action]()
        prev_x = self.rect.x
        prev_y = self.rect.y
        self.rect.x += self.x_speed
        self.rect.y += self.y_speed
        for lvl_element in lvl_elements:
            if colliding(self.rect, lvl_element):
                self.rect.x, self.rect.y = prev_x, prev_y
                self.x_speed, self.y_speed = 0, 0
        if abs(self.x_speed) < 0.1:
            self.x_speed = 0
        if abs(self.y_speed) < 0.1:
            self.y_speed = 0
        self.x_speed /= 1.1
        self.y_speed /= 1.1
        # moving ^ blit-ing v
        SCREEN.blit(self.sprite, (self.rect.x, self.rect.y))


def main():
    global lvl_elements
    rgb = 0
    lvl_elements = (pygame.Rect(WIDTH // 2 - 20, 0, 20, HEIGHT),)
    background = pygame.transform.scale(
        pygame.image.load("assets/space.png"), (WIDTH, HEIGHT)
    )
    # Doing the pygame stuff
    pygame.init()
    pygame.mouse.set_visible(False)
    # Define a variable to control the main loop
    running = True
    ship1 = Player(
        WIDTH // 4,
        HEIGHT // 2,
        "assets/ship-p1.png",
        {
            pygame.K_w: (0, -1),
            pygame.K_a: (-1, 0),
            pygame.K_s: (0, 1),
            pygame.K_d: (1, 0),
            pygame.K_e: "fire",
        },
        rotation=-90,
    )
    ship2 = Player(
        WIDTH // 4 * 3,
        HEIGHT // 2,
        "assets/ship-p2.png",
        {
            pygame.K_UP: (0, -1),
            pygame.K_LEFT: (-1, 0),
            pygame.K_DOWN: (0, 1),
            pygame.K_RIGHT: (1, 0),
            pygame.K_RCTRL: "fire",
        },
        rotation=90,
        enemy=ship1,
    )
    ship1.enemy = ship2
    while running:
        rgb += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Change the value to False, to exit the main loop
                running = False
        pressed = pygame.key.get_pressed()
        # Start rendering stuff
        SCREEN.blit(background, (0, 0))
        ship1.update(pressed)
        ship2.update(pressed)
        for missle in missles:
            missle.update()
        for lvl_element in lvl_elements:
            pygame.draw.rect(SCREEN, hsv_to_rgb(rgb / 360, 1, 1), lvl_element)
        # Do text shenanigans
        draw_text(ship1.score, 0, 0, 'tl')
        draw_text(ship2.score, WIDTH, 0, 'tr')
        # Render
        pygame.display.flip()
        # Fps stuff
        CLOCK.tick(90)
        pygame.display.set_caption(f"Gam fps:{round(CLOCK.get_fps())}")


def draw_text(text, x, y, alignment = 'c'):
    text_renderer = FONT.render(text, 1, (255, 255, 255))
    if alignment == 'c':
        SCREEN.blit(
            text_renderer,
            (
                x - text_renderer.get_width() / 2,
                y - text_renderer.get_height() / 2,
            ),
        )
    # update the display
    pygame.display.update()
    # pause then restart
    pygame.time.delay(5000)


if __name__ == "__main__":
    missles = []
    main()
