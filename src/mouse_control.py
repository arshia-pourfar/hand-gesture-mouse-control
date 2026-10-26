"""Hand gesture mouse control.

The mouse cursor follows the index fingertip detected by MediaPipe Hands.
"""

import cv2
import mediapipe as mp
import pyautogui


def run():
    """Start hand gesture mouse control until the user presses 'q'."""
    # Initializing MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1)
    mp_draw = mp.solutions.drawing_utils

    # Accessing the camera
    cap = cv2.VideoCapture(0)
    screen_width, screen_height = pyautogui.size()

    try:
        if not cap.isOpened():
            print("Could not open the webcam (camera index 0).")
            return

        while True:
            success, img = cap.read()
            if not success:
                print("Could not read a frame from the webcam.")
                break

            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = hands.process(img_rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Getting the tip of the index finger
                    index_finger_tip = hand_landmarks.landmark[
                        mp_hands.HandLandmark.INDEX_FINGER_TIP
                    ]

                    # Converting the hand coordinates to screen coordinates
                    x = int(index_finger_tip.x * screen_width)
                    y = int(index_finger_tip.y * screen_height)

                    # Moving the mouse to the new position
                    pyautogui.moveTo(x, y)

            cv2.imshow("Image", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        hands.close()
        cv2.destroyAllWindows()
