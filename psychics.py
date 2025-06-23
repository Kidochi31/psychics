from vector2 import Vector2
import math

class AABB:
    def __init__(self, pos1: Vector2 | tuple[float, float], pos2: Vector2 | tuple[float, float]):
        if isinstance(pos1, tuple):
            pos1 = Vector2(pos1[0], pos1[1])
        if isinstance(pos2, tuple):
            pos2 = Vector2(pos2[0], pos2[1])
        
        self.minx = min(pos1.x, pos2.x)
        self.maxx = max(pos1.x, pos2.x)
        self.miny = min(pos1.y, pos2.y)
        self.maxy = max(pos1.y, pos2.y)

class Circle:
    def __init__(self, position: Vector2 | tuple[float, float], radius: float):
        if isinstance(position, tuple):
            self.position = Vector2(position[0], position[1])
        else:
            self.position = position
        self.radius = radius

    def aabb(self) -> tuple[Vector2, Vector2]:
        # top left, bottom right
        return (Vector2(self.position.x - self.radius, self.position.y + self.radius), Vector2(self.position.x + self.radius, self.position.y - self.radius))

    def area(self) -> float:
        return math.pi * self.radius * self.radius 
    
    def add_area(self, area: float):
        self.radius = math.sqrt((self.area() + area) / math.pi)

class Line:
    def __init__(self, position: Vector2 | tuple[float, float], angle: float):
        if isinstance(position, tuple):
            self.position = Vector2(position[0], position[1])
        else:
            self.position = position
        self.angle = angle
    
    def intercepts_with_aabb(self, aabb: AABB) -> tuple[Vector2, Vector2] | Vector2 | None:
        l = self._get_intercepts_with_y_aligned(aabb.minx, aabb.miny, aabb.maxy)
        r = self._get_intercepts_with_y_aligned(aabb.maxx, aabb.miny, aabb.maxy)
        u = self._get_intercepts_with_x_aligned(aabb.maxy, aabb.minx, aabb.maxx)
        d = self._get_intercepts_with_x_aligned(aabb.miny, aabb.minx, aabb.maxx)

        results: list[Vector2] = []
        for pos in [l, r, u, d]:
            if pos is not None and all([not math.isclose(pos.x, other.x) or not math.isclose(pos.y, other.y) for other in results]):
                results.append(pos)
        
        if len(results) == 0:
            return None
        elif len(results) == 2:
            return (results[0], results[1])
        else:
            return results[0]

    def _get_intercepts_with_y_aligned(self, x: float, miny: float, maxy: float) -> Vector2 | None:
        a = self.position.x
        b = self.position.y

        y = b + (x - a) * math.tan(self.angle)
        if miny <= y and y <= maxy:
            return Vector2(x, y)
        return None
    
    def _get_intercepts_with_x_aligned(self, y: float, minx: float, maxx: float) -> Vector2 | None:
        a = self.position.x
        b = self.position.y

        if math.tan(self.angle) == 0:
            return None
        x = a + (y - b) / math.tan(self.angle)
        if minx <= x and x <= maxx:
            return Vector2(x, y)
        return None