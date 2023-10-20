from pynput import mouse, keyboard
from pynput.mouse import Button
from time import sleep
import math

# --------
# Settings
# --------

# The mouse button used to initiate the drag-to-scroll action.
# Options: Button.middle, Button.right
INITIATE_DRAG_BUTTON = Button.middle

# Hotkey to toggle the drag-to-scroll mode.
# This example uses CTRL+ALT+T.
TOGGLE_HOTKEY = {keyboard.Key.ctrl, keyboard.Key.shift, keyboard.Key.f12}

# Determines the initial sensitivity to cursor movements.
# Higher values result in slower initial scroll speeds for small movements.
# It scales the raw cursor movement speed before the logarithmic operation.
SLOW_SPEED_FACTOR = 10

# This factor adjusts the acceleration curve of the scroll speed.
# Values greater than 1 will result in faster acceleration (scroll speed increases more rapidly with cursor speed).
# Values less than 1 will result in slower acceleration.
ACCELERATION_FACTOR = 1.05

# The minimum threshold for the scroll speed to initiate a scroll event.
# Typically set to 0 to ensure even minimal cursor movement contributes to scrolling.
FRACTIONAL_THRESHOLD = 0

# The delay (in seconds) after pressing the INITIATE_DRAG_BUTTON before the drag-to-scroll mode activates.
# This helps distinguish between a regular click and a drag-to-scroll action.
DRAG_ACTIVATION_DELAY = 0.2

# If set to True, the scroll direction will be reversed.
# For example, dragging the mouse up will scroll down and vice versa.
REVERSE_SCROLLING = False

# Multiplier applied to the logarithmic scroll speed.
# Adjusting this will scale the overall scroll speed. Lower values will slow down scrolling, and higher values will speed it up.
SCROLL_SENSITIVITY = 0.7

# Adjusts the curvature of the logarithmic function used to calculate scroll speed.
# Values less than 1 cause the function to increase more slowly, leading to slower scroll speeds at slower cursor speeds.
# This provides granular control over how the scroll speed responds to cursor speed.
LOG_POWER = 0.7


# -----
# START
# -----


# Initial setup
controller = mouse.Controller()
dragging = False
toggle_mode = False
x_init, y_init = 0, 0
accumulated_y = 0
accumulated_x = 0
current_keys = set()

def on_click(x, y, button, pressed):
    global dragging, x_init, y_init, accumulated_y, accumulated_x

    if button == INITIATE_DRAG_BUTTON and not toggle_mode:
        if pressed:
            x_init, y_init = x, y
            sleep(DRAG_ACTIVATION_DELAY)
            dragging = True
        else:
            dragging = False
            accumulated_y = 0
            accumulated_x = 0

def on_key_press(key):
    global toggle_mode, dragging, x_init, y_init
    current_keys.add(key)
    if current_keys == TOGGLE_HOTKEY:
        toggle_mode = not toggle_mode
        if toggle_mode:
            x_init, y_init = controller.position
            dragging = True
        else:
            dragging = False
            accumulated_y = 0
            accumulated_x = 0

def on_key_release(key):
    current_keys.discard(key)

def on_move(x, y):
    global x_init, y_init, accumulated_y, accumulated_x

    if dragging:
        x_delta = x - x_init
        y_delta = y - y_init

        # Calculate dynamic scroll speed based on cursor movement for Y-axis
        raw_speed_y = abs(y_delta / SLOW_SPEED_FACTOR)
        scroll_speed_y = SCROLL_SENSITIVITY * (math.log1p(raw_speed_y) ** LOG_POWER)

        # Calculate dynamic scroll speed based on cursor movement for X-axis
        raw_speed_x = abs(x_delta / SLOW_SPEED_FACTOR)
        scroll_speed_x = SCROLL_SENSITIVITY * (math.log1p(raw_speed_x) ** LOG_POWER)

        if REVERSE_SCROLLING:
            y_delta = -y_delta
            x_delta = -x_delta

        # Accumulate the scroll values
        accumulated_y += scroll_speed_y
        accumulated_x += scroll_speed_x

        # Scrolling vertically
        while accumulated_y >= 1:
            controller.scroll(0, -1 if y_delta > 0 else 1)
            accumulated_y -= 1

        # Scrolling horizontally
        while accumulated_x >= 1:
            controller.scroll(1 if x_delta > 0 else -1, 0)
            accumulated_x -= 1

        # Reset the cursor to the initial position to keep it stationary while scrolling
        controller.position = (x_init, y_init)

if __name__ == "__main__":
    m_listener = mouse.Listener(on_click=on_click, on_move=on_move)
    k_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
    
    m_listener.daemon = True
    k_listener.daemon = True

    m_listener.start()
    k_listener.start()

    try:
        m_listener.join()
        k_listener.join()
    except KeyboardInterrupt:
        pass

