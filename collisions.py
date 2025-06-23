from psychics import Circle, Line
import math

Collidable = Circle | Line

def collides(a: Collidable, b: Collidable):
    if isinstance(a, Circle) and isinstance(b, Circle):
        return circle_collides_circle(a, b)
    if isinstance(a, Line) and isinstance(b, Circle):
        return circle_collides_line(b, a)
    if isinstance(a, Circle) and isinstance(b, Line):
        return circle_collides_line(a, b)

def circle_collides_circle(a: Circle, b: Circle):
    return a.position.distance_between(b.position) <= (a.radius + b.radius)

def circle_collides_line(a: Circle, b: Line):
    sin = math.sin(b.angle)
    cos = math.cos(b.angle)
    distance = abs(sin * (a.position.x - b.position.x) + cos * (b.position.y - a.position.y))
    return distance <= a.radius
    