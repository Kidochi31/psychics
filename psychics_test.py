# Import and initialize the pygame library
import pygame
import math
from pygame import Color
from pygame.mixer import Sound
from psychics_test_helper import draw_circle, draw_image_to_circle, draw_line
from psychics import Circle, Line, AABB
from collisions import collides
from vector2 import Vector2
from random import randint, random
from rigidbody import Rigidbody


def main():
    pygame.init()
    dt = 0
    clock = pygame.time.Clock()
    omnomnom = Sound("omnomnom.wav")
    selected_image = pygame.image.load("omnomnom.png")

    # Set up the drawing window
    screen = pygame.display.set_mode([1000, 750])
    aabb = AABB((-screen.get_width()//2, screen.get_height()//2), (screen.get_width()//2, -screen.get_height()//2))

    circles : list[Circle] = [Circle((0, 0), 50), Circle((300, -300), 75)]
    lines: list[Line] = [Line((0,0), 0), Line((0,0), math.pi/2)]
    rigidbodies : list[Rigidbody] = [Rigidbody(circles[0], Vector2(0, -5))]
    
    selected_circle : int = 0

    # Run until the user asks to quit
    running = True
    while running:

        # Did the user click the window close button?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    selected_circle += 1
                    if selected_circle >= len(circles):
                        selected_circle = 0
                if event.key == pygame.K_a:
                    circles.append(Circle(Vector2(randint(-screen.get_width()//2, screen.get_width()//2), randint(-screen.get_height()//2, screen.get_height()//2)), randint(10, 100)))
                if event.key == pygame.K_l:
                    lines.append(Line(Vector2(randint(-screen.get_width()//2, screen.get_width()//2), randint(-screen.get_height(), screen.get_height()//2)), random() * math.pi))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            circles[selected_circle].position += Vector2(0,200) * dt
        if keys[pygame.K_DOWN]:
            circles[selected_circle].position += Vector2(0,-200) * dt
        if keys[pygame.K_RIGHT]:
            circles[selected_circle].position += Vector2(200,0) * dt
        if keys[pygame.K_LEFT]:
            circles[selected_circle].position += Vector2(-200,0) * dt
        
        for rigidbody in rigidbodies:
            rigidbody.timestep(dt)

        # Fill the background with white
        screen.fill((255, 255, 255))

        # Draw a solid blue circle in the center
        for _, circle in enumerate(list(circles)):
            if circle == circles[selected_circle]:
                draw_image_to_circle(screen, circle, selected_image)
            elif collides(circle, circles[selected_circle]):
                # circles.remove(circle)
                # if k < selected_circle:
                #     selected_circle -= 1
                # circles[selected_circle].add_area(circle.area())
                # omnomnom.play()
                draw_circle(screen, circle, Color(255, 0, 0))
            else:
                draw_circle(screen, circle, Color(0, 0, 255))

        for line in lines:
            if collides(circles[selected_circle], line):
                draw_line(screen, line, Color(255,0,0), aabb)
            else:
                draw_line(screen, line, Color(0,0,0), aabb)

        # Flip the display
        pygame.display.flip()

        dt = clock.tick(60) / 1000

    # Done! Time to quit.
    pygame.quit()

if __name__ == "__main__":
    main()
