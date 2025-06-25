from math import sqrt

class Vector2:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Position({self.x}, {self.y})"

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __mul__(self, other: float) -> 'Vector2':
        return Vector2(self.x * other, self.y * other)
    
    def __truediv__(self, other: float) -> 'Vector2':
        return Vector2(self.x / other, self.y / other)

    def __add__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __neg__(self) -> 'Vector2':
        return Vector2(-self.x, -self.y)
    
    def __pos__(self) -> 'Vector2':
        return Vector2(self.x, self.y)
    
    def magnitude(self) -> float:
        return sqrt(self.x * self.x + self.y * self.y)
    
    def sqr_magnitude(self) -> float:
        return self.x * self.x + self.y * self.y
    
    def distance_between(self, other: 'Vector2') -> float:
        return (self - other).magnitude()
    
    def sqr_distance_between(self, other: 'Vector2') -> float:
        return (self - other).sqr_magnitude() 
    
    def __iter__(self):
        yield self.x
        yield self.y

    def dot_product(self, other: 'Vector2') -> float:
        return self.x * other.x + self.y * other.y