import cv2
import mediapipe as mp
import numpy as np
import random

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Initialize game variables
width, height = 640, 480
snake = [(100, 100)]  # Snake body (list of tuples)
food = (random.randint(50, width-50), random.randint(50, height-50))
score = 0
speed = 8
snake_length = 1  # Track snake length

def move_towards(target, current, speed):
    dx, dy = target[0] - current[0], target[1] - current[1]
    distance = np.sqrt(dx**2 + dy**2)
    if distance > speed:
        current = (current[0] + int(speed * dx / distance), current[1] + int(speed * dy / distance))
    return current

# Game loop
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)
    
    finger_pos = None
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            finger_pos = (int(hand_landmarks.landmark[8].x * width), int(hand_landmarks.landmark[8].y * height))
    
    # Move snake towards index finger position
    if finger_pos:
        new_head = move_towards(finger_pos, snake[-1], speed)
        
        # Only check self-collision if the snake has grown beyond its initial size
        if len(snake) > snake_length and new_head in snake[:-1]:
            cv2.putText(frame, "Game Over", (width//2 - 100, height//2), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            cv2.imshow("Snake Game", frame)
            cv2.waitKey(3000)
            break
        
        snake.append(new_head)
        if len(snake) > snake_length:
            snake.pop(0)
    
    # Check collision with food
    if abs(snake[-1][0] - food[0]) < 15 and abs(snake[-1][1] - food[1]) < 15:
        score += 1
        snake_length += 1  # Increase snake length
        food = (random.randint(50, width-50), random.randint(50, height-50))
    
    # Draw elements
    for i, segment in enumerate(snake):
        cv2.rectangle(frame, (segment[0] - 5, segment[1] - 5), (segment[0] + 5, segment[1] + 5), (0, 255, 0), -1)
        # Draw eyes on the head
        if i == len(snake) - 1:
            cv2.circle(frame, (segment[0] - 3, segment[1] - 3), 2, (255, 255, 255), -1)
            cv2.circle(frame, (segment[0] + 3, segment[1] - 3), 2, (255, 255, 255), -1)
    
    cv2.circle(frame, food, 7, (0, 0, 255), -1)
    cv2.putText(frame, f"Score: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Check collisions with wall
    if snake[-1][0] < 0 or snake[-1][0] > width or snake[-1][1] < 0 or snake[-1][1] > height:
        cv2.putText(frame, "Game Over", (width//2 - 100, height//2), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
        cv2.imshow("Snake Game", frame)
        cv2.waitKey(3000)
        break
    
    cv2.imshow("Snake Game", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
