import cv2
from collections import deque

# ----------------------------
# Slice Trail Effect
# ----------------------------
slice_trail = deque(maxlen=20)  # store fingertip positions


def update_slice_trail(x, y):
    """Add a fingertip position to the trail"""
    slice_trail.append((x, y))


def draw_slice_trail(frame):
    """Draw glowing fingertip trail"""
    for i in range(1, len(slice_trail)):
        if slice_trail[i - 1] is None or slice_trail[i] is None:
            continue

        thickness = max(1, int(10 * (1 - i / len(slice_trail))))  # always ≥ 1

        cv2.line(frame, slice_trail[i - 1], slice_trail[i],
                 (0, 255, 255), thickness)  # yellow line


# ----------------------------
# Collision Detection
# ----------------------------
def is_sliced(hand_landmarks, food, width, height):
    """
    Detects if fingertip trajectory intersects with a food item.
    Uses index fingertip (landmark 8).
    """
    x = int(hand_landmarks.landmark[8].x * width)
    y = int(hand_landmarks.landmark[8].y * height)

    # food rectangle bounds
    fx1, fy1 = food.x, food.y
    fx2, fy2 = food.x + food.size, food.y + food.size

    # check fingertip inside food bounds
    if fx1 <= x <= fx2 and fy1 <= y <= fy2:
        return True
    return False
