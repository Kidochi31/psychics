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
from rigidbody import Rigidbody, resolve_rigidbody_line_collision, resolve_rigidbody_circle_collision, resolve_rigidbody_line_collisions, resolve_rigidbody_circle_collisions, next_point_of_interest, move_to_timestep_segment, fix_velocity_to_energy
import pygame.freetype

def main():
    pygame.init()
    time = 0
    dt = 0
    clock = pygame.time.Clock()
    omnomnom = Sound("omnomnom.wav")
    hibaby = Sound("hibaby.wav")
    selected_image = pygame.image.load("omnomnom.png")

    GAME_FONT = pygame.freetype.SysFont("Calibri", 30)

    # Set up the drawing window
    screen = pygame.display.set_mode([1000, 750])
    aabb = AABB((-screen.get_width()//2, screen.get_height()//2), (screen.get_width()//2, -screen.get_height()//2))

    circles : list[Circle] = [Circle((0, 0), 50)]
    lines: list[Line] = [Line((0, -200), 0)]#, Line((0, -200), 5 * math.pi/6)]
    collider_lines: list[Line] = lines
    rigidbodies : list[Rigidbody] = [Rigidbody(circles[0], circles[0].radius ** 2, Vector2(0, -500))]

    beginning_energy = get_total_energy(rigidbodies, Vector2(0, -150))
    # Run until the user asks to quit
    running = True
    while running:

        # Did the user click the window close button?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    circle = Circle(Vector2(randint(-screen.get_width()//2, screen.get_width()//2) * 0, randint(0, screen.get_height()//2)), randint(10, 100))
                    circles.append(circle)
                    rigidbodies.append(Rigidbody(circle, circle.radius ** 2, Vector2(0, -500)))
                    hibaby.play()
                if event.key == pygame.K_l:
                    lines.append(Line(Vector2(randint(-screen.get_width()//2, screen.get_width()//2), randint(-screen.get_height(), screen.get_height()//2)), random() * math.pi))
        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_UP]:
        #     circles[selected_circle].position += Vector2(0,200) * dt
        # if keys[pygame.K_DOWN]:
        #     circles[selected_circle].position += Vector2(0,-200) * dt
        # if keys[pygame.K_RIGHT]:
        #     circles[selected_circle].position += Vector2(200,0) * dt
        # if keys[pygame.K_LEFT]:
        #     circles[selected_circle].position += Vector2(-200,0) * dt
        
        for rigidbody in rigidbodies:
            rigidbody.predict_timestep(dt)
        
        while True:
            time, collision_results = next_point_of_interest(rigidbodies, lines, dt)
            if len(collision_results) == 0:
                break
            new_dt = dt - time
            #print(time)
            # move to position at time of collision
            #print(f"BEFORE: {get_total_energy(rigidbodies, Vector2(0, -150))}")
            move_to_timestep_segment(rigidbodies, time)
            #print(circles[0].position)
            for collision_result in collision_results:
                
                # calculate energy accurate velocity
                fix_velocity_to_energy(collision_result[0], time)
                if isinstance(collision_result[1], Rigidbody):
                    fix_velocity_to_energy(collision_result[1], time)
                #print(f"AFTER: {get_total_energy(rigidbodies, Vector2(0, -150))}")
                # resolve collision using these velocities
                if collision_result[1] is None:
                    pass
                elif isinstance(collision_result[1], Rigidbody):
                    resolve_rigidbody_circle_collision(collision_result[0], collision_result[1])
                else:
                    resolve_rigidbody_line_collision(collision_result[0], collision_result[1])
                # set predicted positions for the resulting collisions
                collision_result[0].predict_timestep(new_dt)
                if isinstance(collision_result[1], Rigidbody):
                    collision_result[1].predict_timestep(new_dt)
            dt = new_dt
            time, collision_results = next_point_of_interest(rigidbodies, lines, dt)
            if len(collision_results) == 0:
                #print(f"end collisions: {circles[0].position}, {rigidbodies[0].velocity}")
                pass

        for rigidbody in rigidbodies:
            rigidbody.complete_timestep(dt)

        #resolve_rigidbody_line_collisions(rigidbodies, collider_lines)
        #resolve_rigidbody_circle_collisions(rigidbodies)

        # Fill the background with white
        screen.fill((255, 255, 255))

        # Draw a solid blue circle in the center
        for _, circle in enumerate(list(circles)):
            draw_image_to_circle(screen, circle, selected_image)

        for line in lines:
            draw_line(screen, line, Color(0,0,0), aabb)
        
        total_energy = get_total_energy(rigidbodies, Vector2(0, -150))
        GAME_FONT.render_to(screen, (20, 20), f"Energy: {total_energy}", (0, 0, 0))

        if abs(total_energy - beginning_energy) > 1:
            pass
            #print("ENERGY BROKEN")
            #print(circles[0].position)

        # Flip the display
        pygame.display.flip()

        dt = clock.tick(60) / 1000
        time += dt

    # Done! Time to quit.
    pygame.quit()

def get_total_energy(circles: list[Rigidbody], relative_to_position: Vector2) -> float:
    return get_total_kinetic_energy(circles) + get_total_gravitational_energy(circles, relative_to_position)

def get_total_kinetic_energy(circles: list[Rigidbody]) -> float:
    energy = 0
    for circle in circles:
        energy += 0.5 * circle.mass * (circle.velocity.magnitude())**2
    return energy

def get_total_gravitational_energy(circles: list[Rigidbody], relative_to_position: Vector2) -> float:
    energy = 0
    for circle in circles:
        energy += circle.mass * (-circle.gravity.dot_product(circle.collider.position - relative_to_position))
    return energy

if __name__ == "__main__":
    main()
