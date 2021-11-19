import math

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

        self.color = (255, 255, 255)
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

    def subdivide(self):
        self.northeast = QuadTree(self.boundary.subdivide('ne'), self.capacity)
        self.northwest = QuadTree(self.boundary.subdivide('nw'), self.capacity)
        self.southeast = QuadTree(self.boundary.subdivide('se'), self.capacity)
        self.southwest = QuadTree(self.boundary.subdivide('sw'), self.capacity)

        self.divided = True
        # Remove points from parent and transfer to children
        for p in self.points:
            self.insert(p)
        self.points = []

    def insert(self, point):
        if not self.boundary.contains(point):
            return False

        if not self.divided:
            if len(self.points) < self.capacity:
                self.points.append(point)
                return True
            else:
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

    def draw_qt(self, screen, draw_tree=True, draw_points=True):
        rectt = [self.boundary.left, self.boundary.top,
                 self.boundary.w, self.boundary.h]

        # Define color of the boundary
        color = self.color
        if draw_tree:
            pygame.draw.rect(screen, color, rectt, 1)

        if self.divided:
            self.northwest.draw_qt(screen, draw_tree, draw_points)
            self.northeast.draw_qt(screen, draw_tree, draw_points)
            self.southwest.draw_qt(screen, draw_tree, draw_points)
            self.southeast.draw_qt(screen, draw_tree, draw_points)

        if draw_points:
            for p in self.points:
                # Define color of the points
                pygame.draw.circle(screen, color, [p.x, p.y], 2)

    def classify(self):
        children = self.get_children()
        if len(children) > 0:
            for child in children:
                child.classify()
        else:
            if len(self.points) > 0:
                self.color = (0, 255,   0)
                self.type = "in"
            else:
                self.color = (255, 0, 0)
                self.type = "out"


def _check_input(qtree, toggle_points, toggle_tree, n_points, i):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                screen.fill((0, 0, 0))
                toggle_points = not toggle_points
            if event.key == pygame.K_t:
                screen.fill((0, 0, 0))
                toggle_tree = not toggle_tree
            if i > n_points:
                screen.fill((0, 0, 0))
                qtree.draw_qt(screen, toggle_tree, toggle_points)
    return toggle_points, toggle_tree


def run_random_quadtree(qtree, toggle_points, toggle_tree, n_points):
    i = 0
    rng = np.random.default_rng()

    while True:
        clock.tick(60)
        pygame.display.flip()

        toggle_points, toggle_tree = _check_input(
            qtree, toggle_points, toggle_tree, n_points, i)

        if i <= n_points:
            x = rng.integers(low=0, high=b_w)
            y = rng.integers(low=0, high=b_h)
            p = Point(x, y)

            qtree.insert(p)
            qtree.draw_qt(screen, toggle_tree, toggle_points)
        elif i == n_points+1:
            qtree.classify()
            qtree.draw_qt(screen, toggle_tree, toggle_points)
            print("Finished.")
            pygame.display.set_caption("QuadTree - FINISHED!")
        i += 1


def run_quadtree(qtree, toggle_points, toggle_tree, points):
    i = 0
    n_points = len(points)
    while True:
        clock.tick(60)
        pygame.display.flip()

        toggle_points, toggle_tree = _check_input(
            qtree, toggle_points, toggle_tree, n_points, i)

        if i < n_points:
            qtree.insert(points[i])
            qtree.draw_qt(screen, toggle_tree, toggle_points)

        if i == n_points+1:
            qtree.classify()
            qtree.draw_qt(screen, toggle_tree, toggle_points)
            print("Finished.")
            pygame.display.set_caption("QuadTree - FINISHED!")
        i += 1


def print_childrens(qtree):
    if len(qtree.get_children()) > 0:
        for child in qtree.get_children():
            print_childrens(child)
    print(len(qtree.points))


def read_obj(file) -> list:
    points = []
    for line in file.readlines():
        if line[0] == 'v':
            split_line = line.split()
            x = float(split_line[1])*200
            y = float(split_line[2])*200
            points.append(Point(x, y))
    return points


if __name__ == '__main__':

    screen_w = 1080
    screen_w = 1920
    screen_h = 1080
    # screen_h = 720
    pygame.init()
    pygame.display.set_caption("QuadTree")
    screen = pygame.display.set_mode((screen_w, screen_h))
    clock = pygame.time.Clock()

    b_x = screen_w/2
    b_y = screen_h/2
    b_w = screen_w
    b_h = screen_h
    boundary = Rectangle(b_x, b_y, b_w, b_h)
    capacity = 4
    qtree = QuadTree(boundary, capacity)

    i = 0
    n_points = 1000
    toggle_points = True
    toggle_tree = True

    filename = input("Filename: ")
    if len(filename) > 0:
        with open(filename, 'r') as f:
            points = read_obj(f)
            print(len(points))
            # for point in points: print(point.x, point.y)
        while True:
            try:
                run_quadtree(qtree, toggle_points, toggle_tree, points)
            except RecursionError:
                print("Recursion Error. Increasing Quad Tree capacity from {} to {}.".format(
                    capacity, capacity+1))
                capacity += 1
                qtree = QuadTree(boundary, capacity)
                screen.fill((0, 0, 0))
    else:
        run_random_quadtree(qtree, toggle_points, toggle_tree, n_points)
