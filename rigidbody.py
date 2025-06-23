from collisions import collides
from vector2 import Vector2
from psychics import Circle, Line
import math

class Rigidbody:
    def __init__(self, collider: Circle, gravity: Vector2):
        self.collider = collider
        self.velocity = Vector2(0,0)
        self.gravity = gravity
    
    def timestep(self, dt: float):
        self.collider.position += self.velocity * dt
        self.velocity += self.gravity * dt

def resolve_rigidbody_line_collision(rigidbodies: list[Rigidbody], lines: list[Line]):
    for rigidbody in rigidbodies:
        for line in lines:
            collider = rigidbody.collider
            if collides(collider, line):
                sin = math.sin(line.angle)
                cos = math.cos(line.angle)
                normalised_vector = Vector2(-sin, cos)
                displacement = sin * (collider.position.x - line.position.x) + cos * (line.position.y - collider.position.y)
                abs_displacement = abs(displacement)
                displacement_vector = normalised_vector * displacement # this is from centre circle to line
                # the vector from the edge of the circle to the line is in the opposite direction, with a magnitude of radius - magnitude of displacement
                resolution_vector = -displacement_vector * ((collider.radius - abs_displacement) / abs_displacement)

                # now need to resolve collider's position
                collider.position += resolution_vector

                # remove all parts of the rigidbody's velocity in the direction of the line
                proportion = rigidbody.velocity.dot_product(displacement_vector) / abs_displacement / abs_displacement
                velocity_excess = displacement_vector * proportion
                rigidbody.velocity -= velocity_excess
