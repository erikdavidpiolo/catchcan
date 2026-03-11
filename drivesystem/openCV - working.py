from picamera2 import Picamera2
import cv2
import numpy as np
import time
from collections import deque
import serial

# ---- UART to Pico (you confirmed this works) ----
ser = serial.Serial("/dev/ttyAMA0", 115200, timeout=0)

# ---- Camera setup ----
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()
time.sleep(1)

# ---- Motion detection setup ----
bg = cv2.createBackgroundSubtractorMOG2(history=200, varThreshold=25, detectShadows=False)
kernel = np.ones((5, 5), np.uint8)

trail = deque(maxlen=64)
MIN_AREA = 800     # tune this
triggered = False  # ensures 1 command per throw
last_seen = 0.0
tracking = False

print("Running. Press ESC to quit.")

while True:
    frame = picam2.capture_array()  # RGB
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)

    fg = bg.apply(gray)
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, kernel, iterations=1)
    fg = cv2.dilate(fg, kernel, iterations=2)

    contours, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best = None
    best_area = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area > best_area:
            best_area = area
            best = c

    detected = (best is not None and best_area > MIN_AREA)

    if detected:
        x, y, w, h = cv2.boundingRect(best)
        cx, cy = x + w // 2, y + h // 2

        tracking = True
        last_seen = time.time()
        trail.appendleft((cx, cy))

        # UART trigger: send once per "appearance"
        if not triggered:
            ser.write(b"FIRE\n")
            triggered = True

        cv2.rectangle(frame_bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(frame_bgr, (cx, cy), 5, (255, 0, 0), -1)
        cv2.putText(frame_bgr, f"area={int(best_area)}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 255, 0), 2)
    else:
        # if object disappears, re-arm trigger for next throw
        triggered = False
        if tracking and (time.time() - last_seen) > 0.25:
            tracking = False
            trail.clear()

    for i in range(1, len(trail)):
        cv2.line(frame_bgr, trail[i - 1], trail[i], (255, 255, 255), 2)

    cv2.imshow("Throw tracker", frame_bgr)
    cv2.imshow("Foreground mask", fg)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cv2.destroyAllWindows()
picam2.stop()
ser.close()

