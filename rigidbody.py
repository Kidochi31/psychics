from collisions import collides
from vector2 import Vector2
from psychics import Circle, Line
import math

class Rigidbody:
    def __init__(self, collider: Circle, mass: float, gravity: Vector2):
        self.collider = collider
        self.mass = mass
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
                velocity_excess = displacement_vector * proportion * 2 # no * 2 to just cancel out velocity
                rigidbody.velocity -= velocity_excess

def resolve_rigidbody_circle_collisions(rigidbodies: list[Rigidbody]):
    for k, rigidbody1 in enumerate(rigidbodies):
        collider1 = rigidbody1.collider
        for rigidbody2 in rigidbodies[(k + 1):]:
            collider2 = rigidbody2.collider
            if collides(collider1, collider2):
                mass1 = rigidbody1.mass
                mass2 = rigidbody2.mass

                displacement = collider2.position - collider1.position
                normal = displacement / displacement.magnitude()

                # need to resolve collision by moving each away from each other
                overlap = collider1.radius + collider2.radius - displacement.magnitude()
                # move each circle by half the overlap
                resolution_displacement = normal * overlap
                collider1.position -= resolution_displacement * (mass2 / (mass1 + mass2))
                collider2.position += resolution_displacement * (mass1 / (mass1 + mass2))

                # need to find velocities parallel to the collision normal
                v1 = rigidbody1.velocity.dot_product(normal)
                velocity1 = normal * v1
                v2 = rigidbody2.velocity.dot_product(normal)
                velocity2 = normal * v2

                # remove these components from the velocities of each rb
                rigidbody1.velocity -= velocity1
                rigidbody2.velocity -= velocity2

                # calculate the new velocity
                velocity1_mag = (2 * mass2 * v2 + v1 * (mass1 - mass2)) / (mass1 + mass2)
                velocity2_mag = (2 * mass1 * v1 + v2 * (mass2 - mass1)) / (mass1 + mass2)
                velocity1 = normal * velocity1_mag
                velocity2 = normal * velocity2_mag

                # add on the new velocities
                rigidbody1.velocity += velocity1
                rigidbody2.velocity += velocity2

