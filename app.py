"""Hand Gesture Control — main entry point.

Run:  python app.py
"""

import importlib
import sys
from pathlib import Path

# Add the project root to sys.path so the src package can be imported from
# any working directory.
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))


def print_main_menu():
    print()
    print("=================================")
    print("     Hand Gesture Control")
    print("=================================")
    print()
    print("1. Hand Gesture Volume Control")
    print("2. Hand Gesture Mouse Control")
    print("3. Exit")


def run_feature(module_name, label):
    """Import and run one feature module on demand."""
    try:
        module = importlib.import_module(f"src.{module_name}")
    except ModuleNotFoundError as error:
        print()
        print(f"Cannot start {label}: missing Python package '{error.name}'.")
        print("Install the dependencies with:")
        print("    python -m pip install -r requirements.txt")
        return
    except Exception as error:
        print()
        print(f"Cannot start {label}: {error}")
        return

    print()
    print(f"Starting {label}...")
    print("Press 'q' in the camera window to stop.")
    print()

    try:
        module.run()
    except KeyboardInterrupt:
        print()
        print("Feature interrupted.")
    except Exception as error:
        print()
        if type(error).__name__ == "FailSafeException":
            print("Mouse control stopped by PyAutoGUI's failsafe.")
        else:
            print(f"{label} stopped with an error: {error}")

    print()
    print(f"{label} closed. Returning to the main menu.")


def main():
    while True:
        print_main_menu()
        try:
            choice = input("\nChoose an option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            print("Goodbye.")
            return

        if choice == "1":
            run_feature("volume_control", "Hand Gesture Volume Control")
        elif choice == "2":
            run_feature("mouse_control", "Hand Gesture Mouse Control")
        elif choice == "3":
            print("Goodbye.")
            return
        else:
            print("Invalid option. Please enter 1, 2 or 3.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print()
        print("Goodbye.")
