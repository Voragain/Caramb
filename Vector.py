
# -*- coding: utf-8 -*-

from math import pi, cos, sin, sqrt, atan2

class Vector:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def copy(self):
        return Vector(self.x, self.y)

    def length_sqrd(self):
        return self.x*self.x + self.y*self.y

    def length(self):
        return sqrt(self.length_sqrd())

    def normalize(self):
        l = self.length()
        if l != 0.0:
            self.x /= l
            self.y /= l
        return self

    def invert(self):
        self.x = -self.x
        self.y = -self.y
        return self

    def plus(self, vec):
        self.x += vec.x
        self.y += vec.y
        return self

    def minus(self, vec):
        self.x -= vec.x
        self.y -= vec.y
        return self

    def scale(self, factor):
        self.x *= factor
        self.y *= factor
        return self

    def modify(self, x, y):
        self.x = x
        self.y = y
        return self

    def rotate(self, angle):
        ca = cos(angle)
        sa = sin(angle)
        sx = self.x
        sy = self.y
        self.x = ca*sx - sa*sy
        self.y = ca*sy + sa*sx
        return self

    def rotate_deg(self, angle):
        self.rotate(angle / 180.0 * pi)
        return self

    def angle(self):
        return atan2(self.y, self.x)

    def angle_deg(self):
        return self.angle() / pi * 180.0

    def __str__(self):
        return "V2(" + str(self.x) + ", " + str(self.y) + ")"

    @staticmethod
    def Normalized(vec):
        return vec.copy().normalize()

    @staticmethod
    def Scaled(vec, factor):
        return vec.copy().scale(factor)

    @staticmethod
    def Add(vec1, vec2):
        return Vector(vec1.x+vec2.x, vec1.y+vec2.y)

    @staticmethod
    def Substract(vec1, vec2):
        return Vector(vec1.x-vec2.x, vec1.y-vec2.y)
    
    @staticmethod
    def Inverted(vec):
        return vec.copy().invert()

    @staticmethod
    def Dot(vec1, vec2):
        return vec1.x*vec2.x + vec1.y*vec2.y

    @staticmethod
    def ProjectedOn(vec1, vec2):
        norm = vec2.copy().normalize()
        return norm.scale(Vector.Dot(vec1, norm))

    @staticmethod
    def Rotated(vec, angle):
        return vec.copy().rotate(angle)

    @staticmethod
    def Rotated_deg(vec, angle):
        return vec.copy().rotate_deg(angle)

    @staticmethod
    def ToNormalPerp(vec):
        normal = Vector.Normalized(vec)
        perp = normal.copy()
        px = perp.x
        perp.x = perp.y
        perp.y = -px
        return (normal, perp)        
