import pygame

WIDTH, HEIGHT = 1280, 720

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
CLOCK = pygame.time.Clock()

def hsv_to_rgb(h, s, v):  # Shamelessly stolen code
    if s == 0.0: v*=255; return (v, v, v)
    i = int(h*6.)
    f = (h*6.)-i; p,q,t = int(255*(v*(1.-s))), int(255*(v*(1.-s*f))), int(255*(v*(1.-s*(1.-f)))); v*=255; i%=6
    if i == 0: return (v, t, p)
    if i == 1: return (q, v, p)
    if i == 2: return (p, v, t)
    if i == 3: return (p, q, v)
    if i == 4: return (t, p, v)
    if i == 5: return (v, p, q)

def colliding(rect1 : pygame.rect, rect2 : pygame.rect):
    return rect1.x < 0 or rect1.x > WIDTH - 80 or rect1.y < 0 or rect1.y > HEIGHT - 80 or pygame.Rect.colliderect(rect1, rect2)

class Player:
    def __init__(self, x, y, sprite, controls = {pygame.K_w:(0,-1),pygame.K_a:(-1,0),pygame.K_s:(0,1),pygame.K_d:(1,0)}, rotation = 0, speed = 1):
        self.sprite = pygame.transform.scale(pygame.transform.rotate(pygame.image.load(sprite), rotation), (80, 80))
        self.rect = pygame.Rect(x, y, self.sprite.get_height(), self.sprite.get_width())
        self.x_speed = 0
        self.y_speed = 0
        self.speed = speed
        self.controls = controls
        print(f"Player crated!")

    def update(self, pressed):
        global lvl_elements
        for key, delta in self.controls.items():
            if pressed[key]:
                self.x_speed += delta[0]
                self.y_speed += delta[1]
        prev_x = self.rect.x
        prev_y = self.rect.y
        self.rect.x = int(self.rect.x + self.x_speed / (CLOCK.get_fps() + 1))
        self.rect.y = int(self.rect.y + self.y_speed / (CLOCK.get_fps() + 1))  # +1 tp prevent ZeroDivisionError
        for lvl_element in lvl_elements:
            if colliding(self.rect, lvl_element):
                self.rect.x, self.rect.y = prev_x, prev_y
                self.x_speed, self.y_speed = 0, 0
        delta =  1 + 0.1 / (CLOCK.get_fps() + 1)  # +1 tp prevent ZeroDivisionError
        self.x_speed = self.x_speed/delta
        self.y_speed = self.y_speed/delta
        #moving ^ blit-ing v
        if abs(self.x_speed) < 0.05:
            self.x_speed = 0
        if abs(self.y_speed) < 0.05:
            self.y_speed = 0
        SCREEN.blit(self.sprite, (self.rect.x, self.rect.y))

def main():
    global lvl_elements
    rgb = 0
    lvl_elements = (pygame.Rect(WIDTH//2-20, 0, 20, HEIGHT),)
    ship1 = Player(WIDTH//4, HEIGHT//2, 'assets/ship-p1.png', rotation = -90)
    ship2 = Player(WIDTH//4*3, HEIGHT//2, 'assets/ship-p2.png', {pygame.K_UP:(0,-1),pygame.K_LEFT:(-1,0),pygame.K_DOWN:(0,1),pygame.K_RIGHT:(1,0)}, rotation = 90)
    background = pygame.transform.scale(pygame.image.load("assets/space.png"), (WIDTH, HEIGHT))
    # Doing the pygame stuff
    pygame.init()
    pygame.mouse.set_visible(False)
    # Define a variable to control the main loop
    running = True
    while running:
        rgb += ((CLOCK.get_fps() + 1) / 5400)  # +1 tp prevent ZeroDivisionError
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Change the value to False, to exit the main loop
                running = False
        pressed = pygame.key.get_pressed()
        # Start rendering stuff
        SCREEN.blit(background, (0, 0))
        ship1.update(pressed)
        ship2.update(pressed)
        for lvl_element in lvl_elements:
            pygame.draw.rect(SCREEN, hsv_to_rgb(rgb/360,1,1), lvl_element)
        # Render
        pygame.display.flip()
        # Fps stuff
        CLOCK.tick()
        pygame.display.set_caption(f"Gam fps:{round(CLOCK.get_fps())}")


if __name__ == '__main__':
    main()