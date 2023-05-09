import pygame

WIDTH, HEIGHT = 1280, 720

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)

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

def colliding(x_1,y_1,x_2,y_2, x_size = 80, y_size = 80):
    x_range, y_range = range(x_2 + 1, x_2 + x_size), range(y_2 + 1, y_2 + y_size)
    if x_1 + 1 in x_range or x_1 + 80 in x_range:
        return y_1 + 1 in y_range or y_1 + 80 in y_range
    return x_1 < 0 or x_1 > WIDTH - 80 or y_1 < 0 or y_1 > HEIGHT - 80

class Player:
    def __init__(self, x, y, sprite, controls = {pygame.K_w:(0,-1),pygame.K_a:(-1,0),pygame.K_s:(0,1),pygame.K_d:(1,0)}, rotation = 0, speed = 1):
        self.x = x
        self.y = y
        self.sprite = pygame.transform.scale(pygame.transform.rotate(pygame.image.load(sprite), rotation), (80, 80))
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
        prev_x = self.x
        prev_y = self.y
        self.x = int(self.x + self.x_speed)
        self.y = int(self.y + self.y_speed)
        for i in lvl_elements:
            if colliding(self.x, self.y, i.x, i.y, i.width, i.height):
                self.x, self.y = prev_x, prev_y
                self.x_speed, self.y_speed = 0, 0
        self.x_speed = self.x_speed/1.1
        self.y_speed = self.y_speed/1.1
        #moving ^ blit-ing v
        if abs(self.x_speed) < 0.05:
            self.x_speed = 0
        if abs(self.y_speed) < 0.05:
            self.y_speed = 0
        screen.blit(self.sprite,(self.x,self.y))

def main():
    global lvl_elements
    rgb = 0
    lvl_elements = (pygame.Rect(WIDTH//2-20, 0, 20, HEIGHT),)
    ship1 = Player(320, 360, 'assets/ship-p1.png', rotation = -90)
    ship2 = Player(960, 360, 'assets/ship-p2.png', {pygame.K_UP:(0,-1),pygame.K_LEFT:(-1,0),pygame.K_DOWN:(0,1),pygame.K_RIGHT:(1,0)}, rotation = 90)
    background = pygame.image.load("assets/space.png")
    # Doing the pygame stuff
    pygame.init()
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False)
    # Define a variable to control the main loop
    running = True
    while running:
        rgb += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Change the value to False, to exit the main loop
                running = False
        pressed = pygame.key.get_pressed()
        # Start rendering stuff
        screen.blit(background, (0, 0))
        ship1.update(pressed)
        ship2.update(pressed)
        for lvl_element in lvl_elements:
            pygame.draw.rect(screen, hsv_to_rgb(rgb/360,1,1), lvl_element)
        # Render
        pygame.display.flip()
        # Fps stuff
        clock.tick(90)
        pygame.display.set_caption(f"Gam fps:{round(clock.get_fps())}")


if __name__ == '__main__':
    main()