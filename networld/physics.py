import random


class Vector:
    @staticmethod
    def random(a, b):
        return Vector(random.uniform(a, b), random.uniform(a, b), random.uniform(a, b))

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __str__(self):
        return 'Vector: [%f, %f, %f]' % (self.x, self.y, self.z)

    def move(self, magnitude, direction):
        self.x += magnitude*direction.x
        self.y += magnitude*direction.y
        self.z += magnitude*direction.z
        return self

    def normalize(self):
        l = (self.x**2 + self.y**2 + self.z**2)**0.5
        self.x /= l
        self.y /= l
        self.z /= l
        return self
