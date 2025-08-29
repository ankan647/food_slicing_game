import cv2
import random
import numpy as np


class Food:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = random.randint(50, width - 50)
        self.y = 0
        self.size = random.randint(20, 40)
        self.speed = random.randint(3, 6)
        self.sliced = False

        # For sliced halves
        self.halves = []  # [(x, y, dx, dy, shape_side), ...]

        # Randomly pick one of 5 shapes
        self.shape = random.choice(
            ["circle", "rectangle", "triangle", "star", "hexagon"])

    def move(self):
        if not self.sliced:
            self.y += self.speed
        else:
            # Move each half separately
            new_halves = []
            for (hx, hy, dx, dy, side) in self.halves:
                hx += dx
                hy += dy
                dy += 0.2  # gravity
                if hy < self.height + 50:  # still visible
                    new_halves.append((hx, hy, dx, dy, side))
            self.halves = new_halves

    def draw(self, frame):
        if not self.sliced:
            self._draw_shape(frame, self.x, self.y, self.size)
        else:
            for (hx, hy, dx, dy, side) in self.halves:
                self._draw_half(frame, hx, hy, self.size, side)

    def slice(self):
        """Mark as sliced and initialize halves motion"""
        if not self.sliced:
            self.sliced = True
            self.halves = [
                (self.x - 10, self.y, -2, self.speed, "left"),
                (self.x + 10, self.y, 2, self.speed, "right")
            ]

    def _draw_shape(self, frame, x, y, size):
        if self.shape == "circle":
            cv2.circle(frame, (x, y), size, (0, 0, 255), -1)

        elif self.shape == "rectangle":
            cv2.rectangle(frame, (x - size, y - size), (x + size, y + size),
                          (255, 0, 0), -1)

        elif self.shape == "triangle":
            pts = [(x, y - size), (x - size, y + size), (x + size, y + size)]
            pts = np.array(pts, np.int32).reshape((-1, 1, 2))
            cv2.fillPoly(frame, [pts], (0, 255, 0))

        elif self.shape == "star":
            pts = self._create_star(x, y, size)
            pts = np.array(pts, np.int32).reshape((-1, 1, 2))
            cv2.fillPoly(frame, [pts], (255, 255, 0))

        elif self.shape == "hexagon":
            pts = self._create_hexagon(x, y, size)
            pts = np.array(pts, np.int32).reshape((-1, 1, 2))
            cv2.fillPoly(frame, [pts], (255, 0, 255))

    def _draw_half(self, frame, x, y, size, side):
        """Draw left or right half of the shape"""
        if self.shape == "circle":
            if side == "left":
                cv2.ellipse(frame, (int(x), int(y)), (size, size // 2),
                            0, 90, 270, (0, 0, 200), -1)
            else:
                cv2.ellipse(frame, (int(x), int(y)), (size, size // 2),
                            0, -90, 90, (0, 0, 200), -1)

        elif self.shape == "rectangle":
            if side == "left":
                cv2.rectangle(frame, (int(x - size), int(y - size)),
                              (int(x), int(y + size)), (200, 0, 0), -1)
            else:
                cv2.rectangle(frame, (int(x), int(y - size)),
                              (int(x + size), int(y + size)), (200, 0, 0), -1)

        elif self.shape == "triangle":
            if side == "left":
                pts = [(x, y - size), (x - size, y + size), (x, y + size)]
            else:
                pts = [(x, y - size), (x + size, y + size), (x, y + size)]
            pts = np.array(pts, np.int32).reshape((-1, 1, 2))
            cv2.fillPoly(frame, [pts], (0, 200, 0))

        elif self.shape == "star":
            pts = self._create_star(x, y, size)
            pts = np.array(pts, np.int32).reshape((-1, 1, 2))
            if side == "left":
                pts = [p[0] for p in pts if p[0][0] <= x]
            else:
                pts = [p[0] for p in pts if p[0][0] > x]
            if pts:
                cv2.fillPoly(frame, [np.array(pts, np.int32).reshape((-1, 1, 2))],
                             (200, 200, 0))

        elif self.shape == "hexagon":
            pts = self._create_hexagon(x, y, size)
            pts = np.array(pts, np.int32).reshape((-1, 1, 2))
            if side == "left":
                pts = [p[0] for p in pts if p[0][0] <= x]
            else:
                pts = [p[0] for p in pts if p[0][0] > x]
            if pts:
                cv2.fillPoly(frame, [np.array(pts, np.int32).reshape((-1, 1, 2))],
                             (200, 0, 200))

    def _create_star(self, x, y, size):
        pts = []
        for i in range(10):
            angle = i * 36
            r = size if i % 2 == 0 else size // 2
            px = int(x + r * np.cos(np.radians(angle)))
            py = int(y + r * np.sin(np.radians(angle)))
            pts.append((px, py))
        return pts

    def _create_hexagon(self, x, y, size):
        pts = []
        for i in range(6):
            angle = i * 60
            px = int(x + size * np.cos(np.radians(angle)))
            py = int(y + size * np.sin(np.radians(angle)))
            pts.append((px, py))
        return pts
