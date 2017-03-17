import math
import random


class Vector:
    @staticmethod
    def random(a=0, b=1):
        return Vector(random.uniform(a, b), random.uniform(a, b), random.uniform(a, b))

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        return\
            math.isclose(self.x, other.x, abs_tol=1e-4) and\
            math.isclose(self.y, other.y, abs_tol=1e-4) and\
            math.isclose(self.z, other.z, abs_tol=1e-4)

    def __str__(self):
        return 'Vector[%.02f, %.02f, %.02f]' % (self.x, self.y, self.z)

    def move(self, magnitude, direction):
        self.x += magnitude * direction.x
        self.y += magnitude * direction.y
        self.z += magnitude * direction.z
        return self

    def normalize(self):
        l = (self.x**2 + self.y**2 + self.z**2)**0.5
        self.x /= l
        self.y /= l
        self.z /= l
        return self

# class Quaternion:
#     # @staticmethod
#     # def from_euler(x, y, z):
#     #     return Vector(uniform(a, b), uniform(a, b), uniform(a, b))

#     def __init__(self, x, y, z, w):
#         self.x = x
#         self.y = y
#         self.z = z
#         self.w = w

#     def __str__(self):
#         return '[%f, %f, %f, %f]' % (self.x, self.y, self.z, self.w)

# def testAABB(a, b):
#     if abs(a.center.x - b.center.x) > (a.size.x/2 + b.size.x/2):
#         return False
#     if abs(a.center.y - b.center.y) > (a.size.y/2 + b.size.y/2):
#         return False
#     if abs(a.center.z - b.center.z) > (a.size.z/2 + b.size.z/2):
#         return False
#     return True
