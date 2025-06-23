import pygame
from pygame import Surface, Color
from psychics import Circle, Line, AABB
from vector2 import Vector2

def convert_world_to_screen_position(screen:Surface, position: Vector2) -> tuple[float, float]:
    return (screen.get_width() / 2 + position.x, screen.get_height() /2 - position.y)

def draw_circle(screen: Surface, circle: Circle, color: Color):
    pygame.draw.circle(screen, color, convert_world_to_screen_position(screen, circle.position), circle.radius)

def draw_image_to_circle(screen: Surface, circle: Circle, image: Surface):
    size = (circle.radius * 2, circle.radius * 2)
    scaled_image = pygame.transform.scale(image, size)
    upper_left = circle.position + Vector2(-circle.radius, circle.radius)
    screen.blit(scaled_image, convert_world_to_screen_position(screen, upper_left))

def draw_line(screen: Surface, line: Line, color: Color, aabb: AABB):
    positions = line.intercepts_with_aabb(aabb)
    if not isinstance(positions, tuple):
        return
    a, b = positions
    pygame.draw.line(screen, color, convert_world_to_screen_position(screen, a), convert_world_to_screen_position(screen, b), 5)