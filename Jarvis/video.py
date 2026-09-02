import threading
import time
import cv2
import numpy as np

CURRENT_MODE = "girl"
CURRENT_STATE = "listening"
STATE_LOCK = threading.Lock()


def set_avatar_mode(mode):
    global CURRENT_MODE
    with STATE_LOCK:
        CURRENT_MODE = mode.lower() if mode.lower() in {"girl", "boy"} else "girl"


def set_avatar_state(state):
    global CURRENT_STATE
    with STATE_LOCK:
        state = state.lower()
        if state in {"listening", "speaking", "idle"}:
            CURRENT_STATE = state


def create_avatar_frame(mode="girl", state="listening", speaking=False, blink=0.0, t=0.0):
    """Create a neon female AI robot avatar."""
    height, width = 480, 640
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:] = (10, 12, 22)

    cx, cy = width // 2, height // 2
    head_center = (cx, cy - 20)

    if mode == "girl":
        skin = (245, 225, 218)
        hair = (120, 80, 150)
        jacket = (95, 110, 255)
        glow = (80, 220, 255)
    else:
        skin = (210, 200, 190)
        hair = (80, 70, 80)
        jacket = (80, 120, 220)
        glow = (80, 180, 255)

    for r in range(180, 0, -12):
        color = (18 + r // 8, 22 + r // 7, 44 + r // 6)
        cv2.circle(frame, head_center, r, color, thickness=1)

    # Head and shoulders
    cv2.ellipse(frame, (cx, cy), (142, 166), 0, 0, 360, skin, -1)
    cv2.ellipse(frame, (cx, cy + 195), (170, 70), 0, 0, 360, jacket, -1)
    cv2.rectangle(frame, (cx - 45, cy + 150), (cx + 45, cy + 180), (140, 160, 255), -1)

    # Hair
    if mode == "girl":
        cv2.ellipse(frame, (cx, cy - 72), (128, 110), 0, 180, 360, hair, -1)
        cv2.ellipse(frame, (cx, cy - 98), (78, 28), 0, 0, 180, hair, -1)
        cv2.line(frame, (cx - 98, cy - 42), (cx - 34, cy - 105), hair, 18)
        cv2.line(frame, (cx + 98, cy - 42), (cx + 34, cy - 105), hair, 18)
        cv2.line(frame, (cx - 72, cy - 98), (cx - 18, cy - 118), hair, 12)
        cv2.line(frame, (cx + 72, cy - 98), (cx + 18, cy - 118), hair, 12)
    else:
        cv2.ellipse(frame, (cx, cy - 70), (120, 86), 0, 180, 360, hair, -1)
        cv2.line(frame, (cx - 74, cy - 35), (cx - 22, cy - 78), hair, 16)
        cv2.line(frame, (cx + 74, cy - 35), (cx + 22, cy - 78), hair, 16)

    # Eyes with glowing iris
    eye_y = cy - 10
    if state == "speaking":
        eye_open = 12
    else:
        eye_open = 18 if blink < 0.2 else 4

    left = (cx - 52, eye_y)
    right = (cx + 52, eye_y)
    cv2.ellipse(frame, left, (34, eye_open), 0, 0, 360, (245, 245, 255), -1)
    cv2.ellipse(frame, right, (34, eye_open), 0, 0, 360, (245, 245, 255), -1)
    cv2.circle(frame, (left[0] - 9, eye_y - 2), 6, glow, -1)
    cv2.circle(frame, (right[0] + 9, eye_y - 2), 6, glow, -1)

    # Blush and nose
    cv2.circle(frame, (cx - 80, cy + 18), 9, (255, 165, 190), -1)
    cv2.circle(frame, (cx + 80, cy + 18), 9, (255, 165, 190), -1)
    cv2.line(frame, (cx, cy + 2), (cx, cy + 18), (190, 140, 130), 2)

    mouth_y = cy + 58
    mouth_w = 70
    if speaking or state == "speaking":
        mouth_h = 16 + int(10 * abs(np.sin(t * 10)))
        cv2.ellipse(frame, (cx, mouth_y), (mouth_w, mouth_h), 0, 180, 360, (200, 70, 100), -1)
    else:
        cv2.ellipse(frame, (cx, mouth_y), (mouth_w, 8), 0, 180, 360, (160, 90, 120), 2)

    # Futuristic collar / ring
    cv2.rectangle(frame, (cx - 55, cy + 145), (cx + 55, cy + 170), glow, -1)
    cv2.circle(frame, (cx, cy + 225), 18, glow, 2)
    cv2.circle(frame, (cx, cy + 225), 8, glow, -1)

    return frame


def run_avatar_window():
    """Background avatar loop for Jarvis."""
    window_name = "Jarvis Avatar"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    start_time = time.time()

    try:
        while True:
            with STATE_LOCK:
                mode = CURRENT_MODE
                state = CURRENT_STATE

            elapsed = time.time() - start_time
            blink = abs(np.sin(elapsed * 2.3))
            speaking = state == "speaking"
            frame = create_avatar_frame(mode=mode, state=state, speaking=speaking, blink=blink, t=elapsed)
            cv2.imshow(window_name, frame)

            key = cv2.waitKey(30) & 0xFF
            if key == ord('q'):
                break
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                break
    finally:
        cv2.destroyAllWindows()


def start_avatar_loop(mode="girl"):
    """Start the avatar in a non-blocking background thread."""
    set_avatar_mode(mode)
    set_avatar_state("listening")
    avatar_thread = threading.Thread(target=run_avatar_window, daemon=True)
    avatar_thread.start()
    return avatar_thread


def start_avatar(mode="girl"):
    start_avatar_loop(mode)


def start_boy_avatar():
    start_avatar_loop(mode="boy")


def start_girl_avatar():
    start_avatar_loop(mode="girl")


if __name__ == "__main__":
    print("Press q to quit.")
    start_avatar_loop(mode="girl")
    while True:
        time.sleep(0.5)
