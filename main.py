import pygame

pygame.display.init()
WIDTH, HEIGHT = (pygame.display.Info().current_w, pygame.display.Info().current_h)
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
CLOCK = pygame.time.Clock()
MAX_PROJECTILES = 3


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
        or rect1.x > WIDTH - rect1.width
        or rect1.y < 0
        or rect1.y > HEIGHT - rect1.height
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
        if not (self.rect.x > WIDTH - self.rect.width or self.rect.x <= 0):
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
            try:
                if pressed[0][key] or pressed[1][key]:
                    if type(action) == tuple:
                        self.x_speed += action[0]
                        self.y_speed += action[1]
                    else:
                        {"fire": self.fire}[action]()
            except KeyError:
                continue
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


def win(who, FONT):
    SCREEN.blit(
        pygame.font.Font.render(FONT, f"{who} wins!", 10, (255, 155, 155)),
        (
            WIDTH / 2 - (pygame.font.Font.size(FONT, f"{who} wins!")[0] / 2),
            HEIGHT / 2 - (pygame.font.Font.size(FONT, f"{who} wins!")[1] / 2),
        ),
    )
    pygame.display.flip()
    [CLOCK.tick(90) for frame in range(180)]  # Just stop for two seconds
    quit()


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
    FONT = pygame.font.Font("04B_30__.ttf", 50)
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
            if event.type == pygame.JOYDEVICEADDED:
                joy = pygame.joystick.Joystick(event.device_index)
                joys.append(joy)
                print(f"Joystick {joy.get_instance_id()} connencted")
        pressed = pygame.key.get_pressed()
        fakepressed = {}
        if pygame.joystick.get_count() > 1:  # Fake joysticks input by converting keys and adding to pressed
            for iter, joy in enumerate(joys):
                for button, button_pressed in {button:joy.get_button(button) for button in range(joy.get_numbuttons())}.items():
                    if button == 3 and button_pressed:  # Fire
                        fakepressed[(pygame.K_e,pygame.K_RCTRL)[iter]] = True
                for axis, value in {axis:joy.get_axis(axis) for axis in range(joy.get_numaxes())}.items():
                    print(axis, value, joy.get_numaxes())
                    if axis == 1:  # Vert
                        if value > 0.5:
                            fakepressed[(pygame.K_s,pygame.K_DOWN)[iter]] = True
                        if value < -0.5:
                            fakepressed[(pygame.K_w,pygame.K_UP)[iter]] = True
                    if axis == 0:  # Hor
                        if value > 0.5:
                            fakepressed[(pygame.K_d,pygame.K_RIGHT)[iter]] = True
                        if value < -0.5:
                            fakepressed[(pygame.K_a,pygame.K_LEFT)[iter]] = True
        pressed = (pressed, fakepressed)
        # Start rendering stuff
        SCREEN.blit(background, (0, 0))
        ship1.update(pressed)
        ship2.update(pressed)
        for missle in missles:
            missle.update()
        for lvl_element in lvl_elements:
            pygame.draw.rect(SCREEN, hsv_to_rgb(rgb / 360, 1, 1), lvl_element)
        # Do text shenanigans / check for win
        if ship1.score > 9:
            win("P1", FONT)
        if ship2.score > 9:
            win("P2", FONT)
        SCREEN.blit(
            pygame.font.Font.render(FONT, str(ship1.score), 10, (255, 155, 155)),
            (30, 120),
        )
        SCREEN.blit(
            pygame.font.Font.render(FONT, str(ship2.score), 10, (255, 155, 155)),
            (WIDTH - (30 + pygame.font.Font.size(FONT, str(ship2.score))[0]), 120),
        )
        # Render
        pygame.display.flip()
        # Fps stuff
        CLOCK.tick(90)
        pygame.display.set_caption(f"Gam fps:{round(CLOCK.get_fps())}")


if __name__ == "__main__":
    missles = []
    joys = []
    main()
