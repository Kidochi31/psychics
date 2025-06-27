from collisions import collides
from vector2 import Vector2
from psychics import Circle, Line
import math

class Rigidbody:
    def __init__(self, collider: Circle, mass: float, gravity: Vector2):
        self.collider = collider
        self.mass = mass
        self.gravity = gravity
        
        self.last_energy_correct_position = self.collider.position
        self.velocity = Vector2(0,0) # Energy correct velocity @ energy correct position
        self.target_velocity = self.velocity
        self.t_max : float | None = 0
        self.during_velocity = self.velocity

    
    def predict_timestep(self, dt: float):
        # first find if there is a maximum point
        gravity_squared = self.gravity.sqr_magnitude()
        if gravity_squared == 0:
            self.t_max = None
        else:
            self.t_max = -(self.velocity).dot_product(self.gravity) / gravity_squared
        

        if self.t_max is None or self.t_max <= 0 or self.t_max > dt:
            self.target_velocity = self.velocity + self.gravity * dt
            next_position = self.collider.position + self.velocity * dt + self.gravity * dt * dt * 0.5
            if dt == 0:
                self.during_velocity = self.velocity
            else:
                self.during_velocity = (next_position - self.collider.position) / dt
            self.t_max = None
        else: # t_max is not None and 0 < t_max <= dt
            self.target_velocity = self.velocity + self.gravity * self.t_max
            next_position = self.collider.position + self.velocity * self.t_max + self.gravity * self.t_max * self.t_max * 0.5
            self.during_velocity = (next_position - self.collider.position) / self.t_max

    
    def complete_timestep(self, dt: float):
        self.collider.position += self.during_velocity * dt
        self.last_energy_correct_position = self.collider.position
        self.velocity = self.target_velocity
        if self.t_max is not None:
            self.t_max -= dt
            if self.t_max <= 0:
                self.t_max = None

    def timestep(self, dt: float):
        self.collider.position += self.velocity * dt + self.gravity * dt * dt * 0.5
        self.last_energy_correct_position = self.collider.position
        self.last_velocity = self.velocity
        self.velocity += self.gravity * dt

def fix_velocity_to_energy(rigidbody: Rigidbody, dt: float):
    if dt == rigidbody.t_max:
        rigidbody.velocity = rigidbody.target_velocity
        rigidbody.last_energy_correct_position = rigidbody.collider.position
        return
    change_in_position = rigidbody.collider.position - rigidbody.last_energy_correct_position
    magnitude_squared = rigidbody.velocity.sqr_magnitude() + 2 * rigidbody.gravity.dot_product(change_in_position)
    if magnitude_squared < 0:
        new_velocity_magnitude = 0
    else:
        new_velocity_magnitude = math.sqrt(magnitude_squared)
    rigidbody.velocity = rigidbody.during_velocity.normalised() * new_velocity_magnitude
    rigidbody.last_energy_correct_position = rigidbody.collider.position

def move_to_timestep_segment(rigidbodies: list[Rigidbody], dt: float):
    for rigidbody in rigidbodies:
        rigidbody.collider.position += rigidbody.during_velocity * dt

def next_point_of_interest(rigidbodies: list[Rigidbody], lines: list[Line], dt: float) -> tuple[float, list[tuple[Rigidbody, Rigidbody | Line | None]]]:
    min_time = dt + 1
    min_events : list[tuple[Rigidbody, Rigidbody | Line | None]] = []
    # test for all circle-circle collisions
    for k, rigidbody1 in enumerate(rigidbodies):
        for rigidbody2 in rigidbodies[(k + 1):]:
            time = circle_circle_time_of_collision(rigidbody1, rigidbody2, dt)
            if time is not None and time <= min_time:
                if time < min_time:
                    min_events.clear()
                    min_time = time
                min_events.append((rigidbody1, rigidbody2))
    # test for all circle-line collisions
    for rigidbody in rigidbodies:
        for line in lines:
            time = circle_line_time_of_collision(rigidbody, line, dt)
            if time is not None and time <= min_time:
                if time < min_time:
                    min_events.clear()
                    min_time = time
                min_events.append((rigidbody, line))
    
    # test for all maximums
    for rigidbody in rigidbodies:
        time = rigidbody.t_max
        if time is not None and time <= min_time and time != 0:
            if time < min_time:
                min_events.clear()
                min_time = time
            min_events.append((rigidbody, None))
    
    return (min_time, min_events)

def circle_line_time_of_collision(a: Rigidbody, b: Line, dt: float) -> float | None:
    sin = math.sin(b.angle)
    cos = math.cos(b.angle)
    a_minus_x_sin = (b.position.x - a.collider.position.x) * sin
    y_minus_b_cos = (a.collider.position.y - b.position.y) * cos
    ux_sin_minus_uy_cos = a.during_velocity.x * sin - a.during_velocity.y * cos
    if ux_sin_minus_uy_cos == 0:
        return None
    r = a.collider.radius

    top_term = a_minus_x_sin + y_minus_b_cos
    t1 = (top_term - r) / ux_sin_minus_uy_cos
    if t1 > dt:
        return None
    if t1 > 0:
        return t1
    
    # t1 <= 0 -> test t2
    # t2 = (top_term + r) / ux_sin_minus_uy_cos
    # if t2 > 0:
    #     print("chose t2")
    #     print(t1)
    #     return t2
    return None


def circle_circle_time_of_collision(a: Rigidbody, b: Rigidbody, dt: float) -> float | None:
    du = b.during_velocity - a.during_velocity
    ds = b.collider.position - a.collider.position
    s_squared = ds.sqr_magnitude()
    s_dot_u = ds.dot_product(du)
    r = (a.collider.radius + b.collider.radius)
    # firstly if (distance a and b could move towards each other) < (distance a and b are from each other) -> ignore
    #if s_dot_u * dt < s_squared - (r * math.sqrt(s_squared)):
        #return None
    
    # otherwise, calculate time of collision
    u_squared = du.sqr_magnitude()
    r_squared = r * r
    discriminant = s_dot_u * s_dot_u - (u_squared * (s_squared - r_squared))
    if discriminant < 0:
        return None
    sqrt_discriminant = math.sqrt(discriminant)
    t1 = (-s_dot_u - sqrt_discriminant) / u_squared
    if t1 > dt:
        return None
    if t1 > 0:
        return t1
    # t1 <= 0 -> test t2
    # t2 = (-s_dot_u + sqrt_discriminant) / u_squared
    # if t2 > 0:
    #     return t2
    return None

def resolve_rigidbody_line_collision(rigidbody: Rigidbody, line: Line):
    collider = rigidbody.collider
    # make time go backwards until no longer colliding
    # dt = 0
    # while collides(collider, line):
    #     dt -= 0.005
    #     rigidbody.timeset(time + dt)

    # resolve collision
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

    # now set it back to the current time
    # rigidbody.set_init(time + dt)
    # rigidbody.timeset(time)

def resolve_rigidbody_line_collisions(rigidbodies: list[Rigidbody], lines: list[Line]):
    for rigidbody in rigidbodies:
        for line in lines:
            collider = rigidbody.collider
            if collides(collider, line):
                resolve_rigidbody_line_collision(rigidbody, line)

def resolve_rigidbody_circle_collision(rigidbody1: Rigidbody, rigidbody2: Rigidbody):
    # make time go backwards until no longer colliding
    # dt = 0
    # while collides(collider1, collider2):
    #     dt -= 0.005
    #     rigidbody1.timeset(time + dt)
    #     rigidbody2.timeset(time + dt)
    collider1 = rigidbody1.collider
    collider2 = rigidbody2.collider
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

    # now set it back to the current time
    # rigidbody1.set_init(time + dt)
    # rigidbody1.timeset(time)
    # rigidbody2.set_init(time + dt)
    # rigidbody2.timeset(time)

def resolve_rigidbody_circle_collisions(rigidbodies: list[Rigidbody]):
    for k, rigidbody1 in enumerate(rigidbodies):
        collider1 = rigidbody1.collider
        for rigidbody2 in rigidbodies[(k + 1):]:
            collider2 = rigidbody2.collider
            if collides(collider1, collider2):
                resolve_rigidbody_circle_collision(rigidbody1, rigidbody2)

