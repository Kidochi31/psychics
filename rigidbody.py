from collisions import Collidable
from vector2 import Vector2


class Rigidbody:
    def __init__(self, collider: Collidable, acceleration: Vector2):
        self.collider = collider
        self.velocity = Vector2(0,0)
        self.acceleration = acceleration
    
    def timestep(self, dt: float):
        self.collider.position += self.velocity * dt
        self.velocity += self.acceleration * dt
        