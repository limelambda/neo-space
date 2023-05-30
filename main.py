import pygame, socket, pickle, sys, os, random, math, joysticks


def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


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
    def __init__(self, x, y, sprite, rotation = 0, size = 80):
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


class Pwr_up(Entity):
    def __init__(self, x, y, sprite_path):
        super().__init__(x, y, resource_path(sprite_path))
        self.parent = None

    def update(self):
        for ship in ships:
            if colliding(self.rect, ship):
                self.special(ship)
                self.parent = ship
                pwr_ups.remove(self)
                del self
                return
        else:
            SCREEN.blit(self.sprite, (self.rect.x, self.rect.y))

class Invincibility(Pwr_up):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/powerups/invin.png")

    def special(self, ship):
        ship.iframes = 300

class Missle(Entity):
    def __init__(self, x, y, sprite, team, enemy, rotation=0, size=5):
        super().__init__(x, y, sprite, rotation, size)
        self.enemy = enemy
        self.team = team
        self.speed = 20

    def update(self):
        if not (self.rect.x > WIDTH - self.rect.width or self.rect.x <= 0):
            if colliding(self.rect, self.enemy) and self.enemy.iframes < 1:
                self.team.score += 1
                self.enemy.iframes = 5
                missles.remove(self)
                del self
            else:
                self.rect.x += (int(self.rotation < 0) * 2 - 1) * self.speed
                SCREEN.blit(self.sprite, (self.rect.x, self.rect.y))
        else:
            missles.remove(self)
            del self


class Player(Entity):
    def __init__(self, x, y, sprite, controls, rotation=0, size=80, enemy=None):
        super().__init__(x, y, sprite, rotation, size)
        self.controls = controls
        self.score = self.cooldown = self.iframes = 0
        self.enemy = enemy
        print(f"Player crated!")

    def fire(self):
        if self.cooldown <= 0:
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

    def update(self, pressed, coords_overide=None):
        if self.iframes > 0:
            self.iframes -= 1
        self.cooldown -= 0.5
        for key, action in self.controls.items():
            try:
                if key in pressed:
                    if type(action) == tuple:
                        self.x_speed += action[0]
                        self.y_speed += action[1]
                    else:
                        {"fire": self.fire}[action]()
            except KeyError:
                continue
        prev_x = self.rect.x
        prev_y = self.rect.y
        if coords_overide != None:
            self.rect.x = coords_overide[0]
            self.rect.y = coords_overide[1]
        else:
            self.rect.x = round(self.rect.x + self.x_speed)
            self.rect.y = round(self.rect.y + self.y_speed)
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
        # moving ^
        post_sprite = self.sprite.copy()
        if self.iframes > 0:  # ghost effect for invincibility
            post_sprite.set_alpha((math.sin(pygame.time.get_ticks() / 300) + 1.5) * 102)
        # blit-ing v
        SCREEN.blit(post_sprite, (self.rect.x, self.rect.y))


def win(who, FONT):
    SCREEN.blit(
        pygame.font.Font.render(FONT, f"{who} wins!", 10, (255, 155, 155)),
        (
            WIDTH / 2 - (pygame.font.Font.size(FONT, f"{who} wins!")[0] / 2),
            HEIGHT / 2 - (pygame.font.Font.size(FONT, f"{who} wins!")[1] / 2),
        ),
    )
    pygame.display.flip()
    [CLOCK.tick(60) for frame in range(180)]  # Just stop for three seconds
    quit()


def main_pt2(s=None, conn=None):
    global lvl_elements, missles, ships, pwr_ups
    ships = [] 
    pwr_ups = []
    rgb = 0
    lvl_elements = (pygame.Rect(WIDTH // 2 - 10, 0, 20, HEIGHT),)
    background = pygame.transform.scale(
        pygame.image.load(resource_path("assets/space.png")), (WIDTH, HEIGHT)
    )
    x_transform = lambda to_transform: WIDTH - to_transform - 78  # Why 78????
    # Define a variable to control the main loop
    ships.append(Player(
        WIDTH // 4,
        HEIGHT // 2,
        resource_path("assets/ship-p1.png"),
        {
            pygame.K_w: (0, -1),
            pygame.K_a: (-1, 0),
            pygame.K_s: (0, 1),
            pygame.K_d: (1, 0),
            pygame.K_e: "fire",
        },
        rotation=-90,
    ))
    ships.append(Player(
        WIDTH // 4 * 3,
        HEIGHT // 2,
        resource_path("assets/ship-p2.png"),
        {
            pygame.K_w: (0, -1),
            pygame.K_a: (-1, 0),
            pygame.K_s: (0, 1),
            pygame.K_d: (1, 0),
            pygame.K_e: "fire",
        }
        if is_online
        else {
            pygame.K_UP: (0, -1),
            pygame.K_LEFT: (-1, 0),
            pygame.K_DOWN: (0, 1),
            pygame.K_RIGHT: (1, 0),
            pygame.K_SPACE: "fire",
        },
        rotation=90,
        enemy=ships[0],
    ))
    ships[0].enemy = ships[1]
    SPAWN_PWR_UP_EVNT = pygame.USEREVENT+1
    pygame.time.set_timer(SPAWN_PWR_UP_EVNT, 10000)  # Every 1000ms spawn pwr up
    while True:
        rgb += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Change the value to False, to exit the main loop
                quit()
            if event.type == SPAWN_PWR_UP_EVNT:
                pwr_ups.append(Invincibility(random.randrange(0, WIDTH), random.randrange(0, HEIGHT)))
            if event.type == pygame.JOYDEVICEADDED:
                joy = pygame.joystick.Joystick(event.device_index)
                joys.append(joy)
                print(f"Joystick {joy.get_instance_id()} connencted")

        # Convert ScancodeWrapper from a weird totally not a dict to a list
        pressed = [
            i
            for i in (
                119,
                97,
                115,
                100,
                101,
                1073741903,
                1073741904,
                1073741905,
                1073741906,
                32,
            )
            if pygame.key.get_pressed()[i]
        ]
        if pygame.joystick.get_count() > 0:
            pressed.append(joysticks.to_key(joys))

        # Network connectivity lol
        if is_online:
            if is_client:
                # Serialize and send ship & missles
                s.sendall(
                    pickle.dumps(
                        (
                            (ships[0].rect.x, ships[0].rect.y),
                            [
                                (missle.rect.x, missle.rect.y)
                                for missle in missles
                                if missle.team == ships[0]
                            ],
                        )
                    )
                )
                # Receive and deserialize the server data
                recived = pickle.loads(s.recv(1024))
            else:
                # Receive and deserialize the client data
                recived = pickle.loads(conn.recv(1024))
                # Serialize and send ship & missles
                conn.sendall(
                    pickle.dumps(
                        (
                            (ships[0].rect.x, ships[0].rect.y),
                            [
                                (missle.rect.x, missle.rect.y)
                                for missle in missles
                                if missle.team == ships[0]
                            ],
                        )
                    )
                )

        # Start rendering stuff
        SCREEN.blit(background, (0, 0))
        ships[0].update(pressed)
        if is_online:
            missles = [missle for missle in missles if missle.team == ships[0]] + [
                Missle(
                    x_transform(i[0]),
                    i[1],
                    ships[1].sprite,
                    ships[1],
                    ships[1].enemy,
                    rotation=ships[1].rotation,
                    size=50,
                )
                for i in recived[1]
            ]
            ships[1].update([], (x_transform(recived[0][0]), recived[0][1]))
        else:
            ships[1].update(pressed)
        for to_update in missles + pwr_ups:
            to_update.update()
        for lvl_element in lvl_elements:
            pygame.draw.rect(SCREEN, hsv_to_rgb(rgb / 360, 1, 1), lvl_element)
        # Do text shenanigans / check for win
        if ships[0].score > 9:
            win("P1", FONT)
        if ships[1].score > 9:
            win("P2", FONT)
        SCREEN.blit(
            pygame.font.Font.render(FONT, str(ships[0].score), 10, (255, 155, 155)),
            (30, 120),
        )
        SCREEN.blit(
            pygame.font.Font.render(FONT, str(ships[1].score), 10, (255, 155, 155)),
            (WIDTH - (30 + pygame.font.Font.size(FONT, str(ships[1].score))[0]), 120),
        )

        # Render
        pygame.display.flip()
        # Fps stuff
        CLOCK.tick(60)
        pygame.display.set_caption(f"Neo-space fps:{round(CLOCK.get_fps())}")


def main_pt1():
    global WIDTH, HEIGHT
    user_text = ""
    temp_running = True
    while temp_running:
        SCREEN.fill((0, 0, 0))
        if is_client:
            SCREEN.blit(
                pygame.font.Font.render(FONT, user_text, 10, (255, 155, 155)),
                (
                    WIDTH / 2 - (pygame.font.Font.size(FONT, user_text)[0] / 2),
                    HEIGHT / 2,
                ),
            )
            SCREEN.blit(
                pygame.font.Font.render(
                    FONT, "Please type in the hosts IP!", 10, (255, 155, 155)
                ),
                (
                    WIDTH / 2
                    - (
                        pygame.font.Font.size(FONT, "Please type in the hosts IP!")[0]
                        / 2
                    ),
                    HEIGHT / 2
                    - (pygame.font.Font.size(FONT, "Please type in the hosts IP!")[1]),
                ),
            )
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    elif event.key == pygame.K_RETURN:
                        HOST = user_text
                        temp_running = False
                    else:
                        user_text += event.unicode
        else:
            SCREEN.fill((0, 0, 0))
            SCREEN.blit(
                pygame.font.Font.render(
                    FONT, "Waiting for other player!!", 10, (255, 155, 155)
                ),
                (
                    WIDTH / 2
                    - (pygame.font.Font.size(FONT, "Waiting for other player!")[0] / 2),
                    HEIGHT / 2
                    - (pygame.font.Font.size(FONT, "Waiting for other player!")[1] / 2),
                ),
            )
            HOST = "0.0.0.0"
            temp_running = False
        pygame.display.flip()
        CLOCK.tick(60)
        pygame.display.set_caption(f"Neo-space fps:{round(CLOCK.get_fps())}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if is_client:
            s.connect((HOST, PORT))
            # Perform screen size compatiablility stuff
            s.sendall(
                pickle.dumps(
                    (pygame.display.Info().current_w, pygame.display.Info().current_h)
                )
            )
            recived = pickle.loads(
                s.recv(1024)
            )  # Receive and deserialize the server data
            WIDTH, HEIGHT = (
                min(pygame.display.Info().current_w, recived[0]),
                min(pygame.display.Info().current_h, recived[1]),
            )
            main_pt2(s)
        else:
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                # Perform screen size compatiablility stuff
                recived = pickle.loads(
                    conn.recv(1024)
                )  # Receive and deserialize the client data
                conn.sendall(
                    pickle.dumps(
                        (
                            pygame.display.Info().current_w,
                            pygame.display.Info().current_h,
                        )
                    )
                )
                WIDTH, HEIGHT = (
                    min(pygame.display.Info().current_w, recived[0]),
                    min(pygame.display.Info().current_h, recived[1]),
                )
                main_pt2(s, conn)


def menu():
    global is_client, is_online, HOST
    SCREEN.fill((0, 0, 0))
    SCREEN.blit(
        pygame.font.Font.render(
            FONT, "Local will auto start after 5 seconds ", 10, (255, 155, 155)
        ),
        (
            WIDTH / 2
            - pygame.font.Font.size(FONT, "Local will auto start after 5 seconds")[0]
            / 2,
            5,
        ),
    )
    SCREEN.blit(
        pygame.font.Font.render(FONT, "Press L to play locally!", 10, (255, 155, 155)),
        (
            WIDTH / 2 - pygame.font.Font.size(FONT, "Press L to play locally!")[0] / 2,
            HEIGHT / 2 - pygame.font.Font.size(FONT, "Press C to connect!")[1] * 1.5,
        ),
    )
    SCREEN.blit(
        pygame.font.Font.render(FONT, "Press C to connect!", 10, (255, 155, 155)),
        (
            WIDTH / 2 - pygame.font.Font.size(FONT, "Press C to connect!")[0] / 2,
            HEIGHT / 2 - pygame.font.Font.size(FONT, "Press C to connect!")[1] / 2,
        ),
    )
    SCREEN.blit(
        pygame.font.Font.render(FONT, "Press S to host!", 10, (255, 155, 155)),
        (
            WIDTH / 2 - pygame.font.Font.size(FONT, "Press S to host!")[0] / 2,
            HEIGHT / 2 + pygame.font.Font.size(FONT, "Press C to connect!")[1] / 2,
        ),
    )
    pygame.display.flip()
    pygame.display.set_caption(f"Neo-space")
    is_online = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    is_client = False
                    main_pt1()
                elif event.key == pygame.K_c:
                    is_client = True
                    main_pt1()
                elif event.key == pygame.K_l:
                    is_online = False
                    main_pt2()
        if pygame.time.get_ticks() > 0:
            is_online = False
            main_pt2()


if __name__ == "__main__":
    pygame.init()
    pygame.mouse.set_visible(False)
    WIDTH, HEIGHT = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    CLOCK = pygame.time.Clock()
    FONT = pygame.font.Font(resource_path("assets/04B_30__.ttf"), 50)
    MAX_PROJECTILES = 3
    PORT = 24681
    missles = []
    joys = []
    menu()
