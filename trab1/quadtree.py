import math
import random
from time import sleep

import numpy as np
import pygame


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
            self.left <= point.x and
            point.x <= self.right and
            self.top <= point.y and
            point.y <= self.bottom
        )

    def intersects(self, range):
        return not(self.right < range.left or range.right < self.left or self.bottom < range.top or range.bottom < self.top)

    def subdivide(self, quadrant):
        if quadrant == 'ne':
            return Rectangle(self.x + self.w / 4, self.y - self.h / 4, self.w / 2, self.h / 2)
        elif quadrant == 'nw':
            return Rectangle(self.x - self.w / 4, self.y - self.h / 4, self.w / 2, self.h / 2)
        elif quadrant == 'se':
            return Rectangle(self.x + self.w / 4, self.y + self.h / 4, self.w / 2, self.h / 2)
        elif quadrant == 'sw':
            return Rectangle(self.x - self.w / 4, self.y + self.h / 4, self.w / 2, self.h / 2)


class Circle():

    def __init__(self, x, y, r) -> None:
        self.x = x
        self.y = y
        self.r = r
        self.r_squared = self.r**2

    def contains(self, point):
        d = (point.x - self.x)**2 + (point.y - self.y)**2
        return d <= self.r_squared

    def intersects(self, range):
        x_dist = abs(range.x - self.x)
        y_dist = abs(range.y - self.y)

        r = self.r
        w = range.w/2
        h = range.h/2

        edges = (x_dist - w)**2 + (y_dist - h)**2

        if x_dist > (r+w) or y_dist > (r+h):
            return False

        if x_dist <= w or y_dist <= h:
            return True

        return edges <= self.r_squared


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

    def create(self, w, h, capacity=None):
        if not capacity:
            capacity = self.capacity
        bounds = Rectangle(w/2, h/2, w, h)
        # print("BOUNDS", bounds)
        return QuadTree(bounds, capacity)

    def subdivide(self):
        self.northeast = QuadTree(self.boundary.subdivide('ne'), self.capacity)
        self.northwest = QuadTree(self.boundary.subdivide('nw'), self.capacity)
        self.southeast = QuadTree(self.boundary.subdivide('se'), self.capacity)
        self.southwest = QuadTree(self.boundary.subdivide('sw'), self.capacity)

        self.divided = True

    def insert(self, point):
        if not self.boundary.contains(point):
            return False
        # print(len(self.points))
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

    def closest(self, search_point, max_count=1, max_distance=math.inf):
        squared_max_distance = max_distance**2
        return self.k_nearest(search_point, max_count, squared_max_distance, 0, 0)

    def draw_qt(self, screen, colors=None, draw_points=True):
        rectt = [self.boundary.left, self.boundary.top,
                 self.boundary.w, self.boundary.h]
        # if not colors:
        #     color = (255, 255, 255)
        # else:
        #     print(colors)
        #     color = random.choice(colors)
        color = (255, 0, 255)
        pygame.draw.rect(screen, WHITE, rectt, 1)

        if self.divided:
            self.northwest.draw_qt(screen, color, draw_points)
            self.northeast.draw_qt(screen, color, draw_points)
            self.southwest.draw_qt(screen, color, draw_points)
            self.southeast.draw_qt(screen, color, draw_points)

        if draw_points:
            for p in self.points:
                pygame.draw.circle(screen, color, [p.x, p.y], 2)


def print_childrens(qtree):
    if len(qtree.get_children()) > 0:
        for child in qtree.get_children():
            print_childrens(child)
    print(len(qtree.points))


if __name__ == '__main__':

    screen_w = 1080
    screen_h = 720
    pygame.init()
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("QuadTree")
    clock = pygame.time.Clock()

    BLACK = (0,   0,   0)
    WHITE = (255, 255, 255)
    BLUE = (0,   0, 255)
    GREEN = (0, 255,   0)
    RED = (255,   0,   0)

    colors = [WHITE, BLUE, GREEN, RED]

    b_x = screen_w/2
    b_y = screen_h/2
    b_w = screen_w
    b_h = screen_h
    boundary = Rectangle(b_x, b_y, b_w, b_h)
    qtree = QuadTree(boundary, 5)
    qtree.create(b_w, b_h)
    rng = np.random.default_rng()

    i = 0
    toggle_points = False
    while True:
        clock.tick(60)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    screen.fill((0,0,0))
                    toggle_points = not toggle_points

        if i <= 5000:
            x = rng.integers(low=0, high=b_w)
            y = rng.integers(low=0, high=b_h)

            p = Point(x, y)

            qtree.insert(p)
            qtree.draw_qt(screen, colors=colors, draw_points=toggle_points)
        elif i == 5001:
            print("Finished.")
        i += 1
