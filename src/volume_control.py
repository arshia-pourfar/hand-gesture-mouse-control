"""Hand gesture system volume control.

The distance between the thumb tip and the index fingertip controls the
Windows system volume through NirSoft's nircmd.exe.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import cv2
import mediapipe as mp


def find_nircmd():
    """Return the path to nircmd.exe, or None when it is not available."""
    found = shutil.which("nircmd.exe")
    if found:
        return str(Path(found).resolve())

    # Also look in the current folder and in the project root.
    for folder in (Path.cwd(), Path(__file__).resolve().parent.parent):
        candidate = folder / "nircmd.exe"
        if candidate.is_file():
            return str(candidate)

    return None


def run():
    """Start hand gesture volume control until the user presses 'q'."""
    if sys.platform != "win32":
        print("Volume control is only supported on Windows because it uses nircmd.exe.")
        return

    nircmd = find_nircmd()
    if nircmd is None:
        print("Cannot start volume control: nircmd.exe was not found.")
        print("Volume control uses NirSoft's nircmd.exe to change the Windows")
        print("system volume. Download it from:")
        print("    https://www.nirsoft.net/utils/nircmd.html")
        print("Then place nircmd.exe in the project root or add it to PATH.")
        return

    # Initializing MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1)
    mp_draw = mp.solutions.drawing_utils

    # Accessing the camera
    cap = cv2.VideoCapture(0)

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
                    # Drawing landmarks on hand
                    mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Getting the tip of the thumb and the tip of the index finger
                    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    index_tip = hand_landmarks.landmark[
                        mp_hands.HandLandmark.INDEX_FINGER_TIP
                    ]

                    # Calculate the distance between the thumb tip and index finger tip
                    thumb_index_distance = (
                        (thumb_tip.x - index_tip.x) ** 2
                        + (thumb_tip.y - index_tip.y) ** 2
                    ) ** 0.5

                    # Determine whether the hand is open or closed based on the distance
                    if thumb_index_distance > 0.05:  # Threshold value for hand being open
                        # Increase volume
                        subprocess.run([nircmd, "changesysvolume", "200"])
                    else:
                        # Decrease volume
                        subprocess.run([nircmd, "changesysvolume", "-200"])

            cv2.imshow("Image", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        hands.close()
        cv2.destroyAllWindows()
