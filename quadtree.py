import math

import numpy as np


class Point():

    def __init__(self, x, y, z=None, data=None) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.data = data

    def sqDistanceFrom(self, other):
        dx = other.x - self.x
        dy = other.y - self.y

        return dx*dx + dy*dy

    def distanceFrom(self, other):
        return math.sqrt(self.sqDistanceFrom(other))


class Rectangle():

    def __init__(self, x, y, w, h) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.left = x - w / 2
        self.right = x + w / 2
        self.top = y - h / 2
        self.bottom = y + h / 2

    def contains(self, point):
        return (
            self.left <= point.x and point.x <= self.right and self.top <= point.y and self.y <= self.bottom
        )

    def intersects(self, range):
        return not(self.right < range.left or range.right < self.left or self.bottom < range.top or range.bottom < self.top)

    def subdivide(self, quadrant):
        if quadrant == 'ne':
            return Rectangle(self.x + self.w / 4, self.y - self.h / 4, self.w / 2, self.h / 2)
        elif 'nw':
            return Rectangle(self.x - self.w / 4, self.y - self.h / 4, self.w / 2, self.h / 2)
        elif 'se':
            return Rectangle(self.x + self.w / 4, self.y + self.h / 4, self.w / 2, self.h / 2)
        elif 'sw':
            return Rectangle(self.x - self.w / 4, self.y + self.h / 4, self.w / 2, self.h / 2)


class QuadTree():

    def __init__(self, boundary, capacity) -> None:
        self.boundary = boundary
        self.capacity = capacity
        self.points = []
        self.divided = False

    def get_children(self):
        if self.divided:
            return [
                self.northeast,
                self.northwest,
                self.southeast,
                self.southwest
            ] 
        else:
            return []

    def create(self):
        DEFAULT_CAPACITY = 4
        bounds = Rectangle(self.w/2, self.h/2, self.w, self.h)
        return QuadTree(bounds, DEFAULT_CAPACITY)

    def subdivide(self):
        self.northeast = QuadTree(self.boundary.subdivide('ne'), self.capacity)
        self.northwest = QuadTree(self.boundary.subdivide('nw'), self.capacity)
        self.southeast = QuadTree(self.boundary.subdivide('se'), self.capacity)
        self.southwest = QuadTree(self.boundary.subdivide('sw'), self.capacity)

        self.divided = True

    def insert(self, point):
        if not self.boundary.contains(point):
            return False

        if len(self.points) < self.capacity:
            self.points.append(point)
            return True

        if not self.divided:
            self.subdivide()

        return self.northeast.insert(point) or self.northwest.insert(point) or self.southeast.insert(point) or self.southwest.insert(point)

    def query(self, range, found):
        if not found:
            found = []
        
        if not range.intersects(self.boundary):
            return found

        for p in self.points:
            if range.contains(p):
                found.append(p)
        
        if self.divided:
            self.northwest.query(range, found)
            self.northeast.query(range, found)
            self.southwest.query(range, found)
            self.southeast.query(range, found)

        return found

    