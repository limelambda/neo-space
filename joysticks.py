import pygame


def to_key(joys):
    pressed = []
    for iter, joy in enumerate(
        joys
    ):  # Joysticks input by converting keys and kinda adding to pressed, defaults to player 1 controller controll
        for button, button_pressed in {
            button: joy.get_button(button) for button in range(joy.get_numbuttons())
        }.items():
            if button == 3 and button_pressed:  # Fire
                pressed.append((pygame.K_e, pygame.K_RCTRL)[iter])
        for axis, value in {
            axis: joy.get_axis(axis) for axis in range(joy.get_numaxes())
        }.items():
            if axis == 1:  # Vert
                if value > 0.5:
                    pressed.append((pygame.K_s, pygame.K_DOWN)[iter])
                if value < -0.5:
                    pressed.append((pygame.K_w, pygame.K_UP)[iter])
            if axis == 0:  # Hor
                if value > 0.5:
                    pressed.append((pygame.K_d, pygame.K_RIGHT)[iter])
                if value < -0.5:
                    pressed.append((pygame.K_a, pygame.K_LEFT)[iter])
    return pressed
