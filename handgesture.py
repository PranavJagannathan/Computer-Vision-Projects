import cv2
import mediapipe as mp
import numpy as np
import screen_brightness_control as sbc
import pycaw.pycaw as pycaw
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import math

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Initialize volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

# Capture video
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)
    
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Identify hand type
            hand_side = "Left" if hand_landmarks.landmark[0].x > 0.5 else "Right"
            index_tip = hand_landmarks.landmark[8]
            thumb_tip = hand_landmarks.landmark[4]
            middle_tip = hand_landmarks.landmark[12]
            
            # Calculate distance between thumb and index finger
            distance = math.hypot(index_tip.x - thumb_tip.x, index_tip.y - thumb_tip.y)
            scaled_value = np.interp(distance, [0.02, 0.2], [0, 100])
            
            if hand_side == "Left":
                volume.SetMasterVolumeLevelScalar(scaled_value / 100, None)
                cv2.putText(frame, f"Volume: {int(scaled_value)}%", (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            elif hand_side == "Right":
                sbc.set_brightness(int(scaled_value))
                cv2.putText(frame, f"Brightness: {int(scaled_value)}%", (50, 100), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Mute if fist is closed
            fist_distance = math.hypot(index_tip.x - middle_tip.x, index_tip.y - middle_tip.y)
            if fist_distance < 0.03:
                volume.SetMasterVolumeLevelScalar(0, None)
                cv2.putText(frame, "Muted", (50, 150), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # YouTube speed control (1 for normal, 2 for fast)
            fingers_up = sum([1 for i in range(5) if hand_landmarks.landmark[i*4].y < hand_landmarks.landmark[i*4 - 2].y])
            if fingers_up == 1:
                speed = 1.0
            elif fingers_up == 2:
                speed = 2.0
            else:
                speed = 1.0
            cv2.putText(frame, f"YouTube Speed: {speed}x", (50, 200), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow("Hand Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
