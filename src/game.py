import cv2
import time
import pygame
from hand_tracking import get_hand_landmarks, draw_hand_landmarks
from food import Food
from utils import is_sliced, update_slice_trail, draw_slice_trail

# Initialize sound
pygame.mixer.init()
slice_sound = pygame.mixer.Sound("assets/sounds/slice.wav")
game_over_sound = pygame.mixer.Sound("assets/sounds/gameover.wav")


# Initialize game variables
width, height = 640, 480
score = 0
misses = 0
max_misses = 5
food_list = []
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

last_spawn_time = time.time()
spawn_interval = 2  # seconds between foods
game_over = False


def reset_game():
    """Reset all variables for a fresh start."""
    global score, misses, food_list, game_over, last_spawn_time
    score = 0
    misses = 0
    food_list = []
    game_over = False
    last_spawn_time = time.time()


while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    # Get hand landmarks
    results = get_hand_landmarks(frame)

    # Draw landmarks
    frame = draw_hand_landmarks(frame, results)

    if not game_over:
        # Spawn new food
        if time.time() - last_spawn_time > spawn_interval:
            food_list.append(Food(width, height))
            last_spawn_time = time.time()

        new_food_list = []

        # Handle foods
        for food in food_list:
            food.move()
            food.draw(frame)

            # Track fingertip and draw slice trail
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    x = int(hand_landmarks.landmark[8].x * width)
                    y = int(hand_landmarks.landmark[8].y * height)
                    update_slice_trail(x, y)

                    # Slice detection
                    if not food.sliced and is_sliced(hand_landmarks, food, width, height):
                        food.slice()   # halves created
                        slice_sound.play()
                        score += 1

            # Miss detection (only for whole food)
            if not food.sliced and food.y >= height:
                if not hasattr(food, "missed") or not food.missed:
                    food.missed = True
                    misses += 1

            # Keep foods alive (whole or halves until off screen)
            if (not food.sliced and food.y < height) or (food.sliced and food.halves):
                new_food_list.append(food)

        food_list = new_food_list

        # Draw slice trail
        draw_slice_trail(frame)

        # Display score & misses
        cv2.putText(frame, f"Score: {score}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"Misses: {misses}/{max_misses}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 100, 255), 2)

        # Check game over
        if misses >= max_misses:
            game_over = True
            food_list.clear()
            game_over_sound.play()  # <-- Play the sound once

    else:
        # Game Over Screen
        cv2.putText(frame, "GAME OVER", (width//2 - 150, height//2 - 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
        cv2.putText(frame, f"Final Score: {score}", (width//2 - 150, height//2 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
        cv2.putText(frame, "Press R to Restart", (width//2 - 170, height//2 + 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

    # Show window
    cv2.imshow("Food Slicing Game", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    if key == ord('r') and game_over:
        reset_game()

cap.release()
cv2.destroyAllWindows()
