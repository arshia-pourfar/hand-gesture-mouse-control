# Hand Gesture Control

A real-time computer vision project that turns hand gestures into desktop actions. It
contains two independent features behind one interactive terminal menu:

- **Hand Gesture Volume Control** — changes the Windows system volume based on the distance
  between your thumb tip and index fingertip.
- **Hand Gesture Mouse Control** — moves the mouse cursor with your index fingertip.

Both features use a webcam, OpenCV, and MediaPipe Hands. The mouse feature uses PyAutoGUI to
move the cursor; the volume feature uses NirSoft's `nircmd.exe` to change the system volume.
The camera is opened only for the feature you select, and resources are released when that
feature exits.

## Project Overview

The repository contains two separate vision pipelines that share the same capture and
hand-tracking approach:

1. A webcam frame is read with OpenCV.
2. The frame is converted from BGR to RGB and passed to MediaPipe Hands.
3. Hand landmarks are drawn on the frame, which is shown in an OpenCV window titled `Image`.
4. The selected feature uses specific landmarks to perform its action.

`app.py` is the single entry point. It displays a menu, imports only the selected feature
module, and starts it. Running a feature does not start the other one, and the webcam is not
initialized until a feature is selected. When a feature stops, its camera is released and its
OpenCV windows are closed.

## Features

- Interactive command-line menu with two features and a clean exit option
- Lazy feature loading, so each feature starts only when selected
- Real-time hand tracking with MediaPipe Hands (`max_num_hands=1`)
- Volume control using the thumb-tip to index-fingertip distance
- Mouse control using the index-fingertip position mapped to the screen
- Live camera preview with hand landmarks drawn on it
- `q` in the OpenCV window stops the active feature and returns to the menu
- Webcam release, MediaPipe cleanup, and OpenCV window cleanup on exit
- Friendly messages for invalid menu choices, missing Python packages, a missing
  `nircmd.exe`, and a camera that cannot be opened

## How It Works

### Shared hand-tracking pipeline

Each feature creates its own `mediapipe.solutions.hands.Hands` instance with
`max_num_hands=1` and opens camera index `0` with `cv2.VideoCapture(0)`. For every frame:

1. `cap.read()` returns the frame.
2. `cv2.cvtColor(..., cv2.COLOR_BGR2RGB)` converts it for MediaPipe.
3. `hands.process(...)` returns up to one hand landmark set.
4. The landmarks are drawn with `mp.solutions.drawing_utils.draw_landmarks`.
5. The annotated frame is displayed with `cv2.imshow("Image", img)`.
6. `cv2.waitKey(1)` checks for the `q` key.

Press `q` while the OpenCV camera window is focused to stop the feature. The `finally` block
then releases the camera, closes the MediaPipe Hands object, and calls
`cv2.destroyAllWindows()`.

### Volume control logic

For each detected hand, the feature reads:

- `THUMB_TIP` (MediaPipe landmark 4)
- `INDEX_FINGER_TIP` (MediaPipe landmark 8)

It computes the Euclidean distance between the two landmarks using their normalized `x` and
`y` coordinates:

```text
distance = sqrt((thumb.x - index.x)^2 + (thumb.y - index.y)^2)
```

If the distance is **greater than `0.05`**, it runs:

```text
nircmd.exe changesysvolume 200
```

Otherwise, it runs:

```text
nircmd.exe changesysvolume -200
```

The check runs for every frame in which a hand is detected, so the volume keeps changing
while the gesture is held. Moving the hand out of the camera view stops the changes.

### Mouse control logic

For each detected hand, the feature reads the `INDEX_FINGER_TIP` landmark, multiplies its
normalized coordinates by the primary screen size reported by `pyautogui.size()`, and calls:

```python
pyautogui.moveTo(x, y)
```

There is no separate activation gesture, smoothing, or click gesture. The cursor follows the
index fingertip whenever a hand is detected. Moving the hand out of view leaves the cursor
where it is.

## Technologies Used

| Technology | Role |
| --- | --- |
| Python 3.12 | Application language (verified with Python 3.12.6) |
| OpenCV (`opencv-contrib-python` 4.10.0.84) | Webcam capture, color conversion, and camera preview |
| MediaPipe 0.10.14 | Hand landmark detection |
| PyAutoGUI 0.9.54 | Mouse cursor movement |
| NirSoft `nircmd.exe` | Windows system volume control |
| `subprocess` (standard library) | Runs `nircmd.exe` with volume arguments |

`opencv-contrib-python` is used instead of `opencv-python` because MediaPipe depends on it;
it provides the `cv2` module imported by both features. NumPy is installed transitively by
MediaPipe/OpenCV but is not imported directly by this project's code.

## Project Structure

```text
.
├── app.py                  # Single entry point and interactive menu
├── README.md
├── requirements.txt
├── .gitignore
├── nircmd.exe              # Add locally for volume control (Windows only; not committed)
└── src/
    ├── __init__.py
    ├── volume_control.py   # Thumb/index distance -> system volume
    └── mouse_control.py    # Index fingertip -> mouse cursor
```

## Requirements

- **Python 3.12** — verified with Python 3.12.6 on Windows. Other Python versions were not
  tested.
- **A webcam** that OpenCV can open as camera index `0`.
- **Windows** for the volume feature, because `nircmd.exe` is a Windows utility.
- **NirSoft `nircmd.exe`** for volume control. It is not bundled with this repository and is
  not installable with `pip`. Download it from
  <https://www.nirsoft.net/utils/nircmd.html>, extract `nircmd.exe`, and place it in the
  project root or somewhere on your `PATH`.
- **Camera permission** for desktop applications. On Windows, check
  **Settings → Privacy & security → Camera** and make sure desktop apps are allowed to use the
  camera.

The mouse feature uses PyAutoGUI, which also supports other operating systems, but this
project has **not** been verified on macOS or Linux. The volume feature is Windows-only as
written.

## Installation

Windows (PowerShell), from the project root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, allow it for the current session only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

Then set up `nircmd.exe` for volume control:

1. Download the NirCmd package from the link above.
2. Extract `nircmd.exe` (use the 32-bit or 64-bit package for your Windows installation).
3. Place `nircmd.exe` in the project root, next to `app.py`, or add its folder to `PATH`.
4. Do not rename the file; the application looks for `nircmd.exe`.

`nircmd.exe` is intentionally listed in `.gitignore`, so it is not committed to the
repository.

## How to Run

From the project root:

```bash
python app.py
```

The application displays this menu:

```text
=================================
     Hand Gesture Control
=================================

1. Hand Gesture Volume Control
2. Hand Gesture Mouse Control
3. Exit

Choose an option:
```

- Choose `1` to start volume control. The camera opens only after this selection.
- Choose `2` to start mouse control. The camera opens only after this selection.
- Choose `3` to exit the application.
- Any other input prints `Invalid option. Please enter 1, 2 or 3.` and shows the menu again.

While a feature is running, its camera preview is shown in an OpenCV window named `Image`.
Press **`q`** in that window to stop the feature. The application then releases the camera and
returns to the main menu. Each feature starts fresh when selected again.

## Volume Control Gestures

The volume feature tracks **one hand** and uses only the **thumb tip** and **index fingertip**.

| Hand state | Condition | Action |
| --- | --- | --- |
| Thumb and index finger separated | `thumb_index_distance > 0.05` | Increase system volume by 200 units (`changesysvolume 200`) |
| Thumb and index finger together | `thumb_index_distance <= 0.05` | Decrease system volume by 200 units (`changesysvolume -200`) |

The distance is calculated in MediaPipe's normalized image coordinates, so it is not measured
in pixels. The threshold `0.05` is fixed in `src/volume_control.py`.

Important details:

- The code comments call this "hand being open", but the actual measurement is the distance
  between the **thumb tip and index fingertip**, not the openness of all five fingers.
- There is no neutral zone or cooldown: while a hand is visible, one of the two commands runs
  on every processed frame. The volume can change quickly, so move your hand out of the frame
  or press `q` when you reach the desired level.
- The feature changes the **Windows system volume** through `nircmd.exe`. It does not mute or
  unmute, and it does not provide an on-screen volume indicator.
- If `nircmd.exe` is missing, the feature prints instructions and returns to the menu without
  opening the camera. On non-Windows platforms it refuses to start because `nircmd.exe` is a
  Windows utility.

## Mouse Control Gestures

The mouse feature tracks **one hand** and uses the **index fingertip** as the cursor position.

| Input | Action |
| --- | --- |
| Index fingertip visible | The cursor moves to the corresponding position on the primary screen |
| Index fingertip moved | The cursor follows the fingertip on every processed frame |
| Hand not detected | The cursor stays at its last position |

Important details:

- There is **no click, double-click, drag, scroll, or right-click gesture** in the current
  implementation. It moves the cursor only.
- The mapping is direct: normalized landmark coordinates are multiplied by
  `pyautogui.size()`. There is no smoothing, acceleration, or dead zone, so small landmark
  movements can produce visible cursor jitter.
- The code uses the primary screen size and does not handle multiple monitors or
  negative-coordinate secondary displays.
- **Safely stopping mouse control:** press **`q`** in the OpenCV window. If the cursor moves
  unexpectedly and the window is not focused, press `Alt+Tab` to focus the camera window and
  press `q`, or press `Ctrl+C` in the terminal. The feature's cleanup code runs when it exits.
- PyAutoGUI's default failsafe is enabled (`pyautogui.FAILSAFE` is `True` in the verified
  environment). Moving the pointer to a screen corner makes PyAutoGUI raise
  `FailSafeException`; the application catches it, closes the feature, and returns to the
  menu. Treat `q` as the primary exit method, not the failsafe.

## Troubleshooting

### `ModuleNotFoundError: No module named 'cv2'` (or `mediapipe`, `pyautogui`)

The dependencies are not installed in the active Python environment. Activate the virtual
environment and reinstall:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### `Cannot start volume control: nircmd.exe was not found`

`nircmd.exe` is missing. Download it from <https://www.nirsoft.net/utils/nircmd.html>, place
`nircmd.exe` in the project root or on `PATH`, and try option `1` again. Volume control is
Windows-only; on macOS and Linux the feature prints a message and returns to the menu.

### The camera window does not open

- Close other applications that may be using the camera (video calls, recording software).
- Check Windows camera permissions for desktop applications.
- The code uses camera index `0`. If your webcam has a different index, it must be changed in
  `src/volume_control.py` and `src/mouse_control.py`.
- If the camera is opened but frames cannot be read, the feature prints a message and returns
  to the menu.

### The cursor moves unexpectedly

Press `q` in the OpenCV window as soon as possible, or press `Ctrl+C` in the terminal. Keep the
terminal reachable before starting mouse control. The direct index-fingertip mapping and lack
of smoothing can cause fast or jumpy movements.

### The volume changes too quickly or in the wrong direction

The feature applies `+200` or `-200` on every frame while a hand is detected. Separate the
thumb and index finger to increase the volume, bring them together to decrease it, and move
the hand out of the frame to stop. The threshold and step are hardcoded.

### MediaPipe or TensorFlow Lite prints warnings

MediaPipe may print informational messages such as TensorFlow Lite XNNPACK or inference
feedback warnings when it initializes. In the verified environment these appeared during
normal operation and were not fatal. They are library messages, not application output.

### `FailSafeException`

PyAutoGUI's failsafe was triggered. Move the pointer away from the screen corner, run option
`2` again, and use `q` to exit.

## Limitations and Future Improvements

### Current limitations

- **Volume control is Windows-only** because it depends on the external `nircmd.exe` utility,
  which is not bundled with the repository.
- **No neutral state for volume.** Every frame with a detected hand sends either `+200` or
  `-200`; there is no dead zone, cooldown, or rate limit.
- **Fixed gesture parameters.** The `0.05` distance threshold and the `200` volume step are
  constants; there is no calibration for hand size or camera distance.
- **Mouse movement only.** There are no click, drag, scroll, or other mouse-button gestures.
- **No smoothing or dead zone for the mouse**, so the cursor can jitter or jump.
- **One hand, camera index `0`, and the primary monitor only.** The camera index and
  resolution are not configurable from the menu, and multi-monitor setups are not handled.
- **No automated test suite and no performance metrics are included.** The repository does
  not claim accuracy, latency, or FPS results.
- **The MediaPipe `solutions.hands` API is used as-is.** Future MediaPipe releases may change
  or deprecate this API.
- **No graphical installer or packaged executable.** The application runs from Python.

### Possible future improvements (not implemented)

- Configurable volume step, distance threshold, and a neutral gesture zone
- Mouse smoothing, acceleration, and a dead zone to reduce jitter
- Click, drag, and scroll gestures
- A cross-platform volume backend that does not require an external `.exe`
- Camera and monitor selection from the menu
- Automated tests for gesture math and resource cleanup
- Optional packaging as a standalone desktop application

## License

No `LICENSE` file has been added to this repository. All rights are reserved by the author by
default. Third-party libraries and tools used by this project keep their own licenses and
terms; refer to their documentation.
#   h a n d - g e s t u r e - m o u s e - c o n t r o l  
 