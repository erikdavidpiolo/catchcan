from picamera2 import Picamera2
import cv2
import numpy as np
from ultralytics import YOLO
import time
import torch

"""
High-FPS camera preview with lightweight YOLO detections on a Raspberry Pi.
- Targets ~30 FPS preview while running detection every N frames.
- Uses BGR888 from the camera to avoid per-frame color conversions.
- Forces 30 FPS camera timing (exposure must be <= 33,333 us; add light if needed).
- Draws boxes manually (faster than results[0].plot()).

Tuning knobs are grouped near the top.
"""

# ---------------------------- TUNING KNOBS ---------------------------- #
CAM_W, CAM_H = 640, 480         # camera output resolution
TARGET_FPS = 30                  # 30 or 60; make sure exposure allows this
IMGSZ = 320                      # YOLO inference size (256/288/320/352/416/512)
CONF = 0.35                      # confidence threshold for detections
IOU = 0.45                       # NMS IoU
DETECT_EVERY = 3                 # run YOLO every N frames; reuse results between
LIMIT_CLASSES = None             # e.g., [0] for person-only; None = all classes
SHOW_TOP_K = 20                  # limit how many boxes we draw for speed
TORCH_THREADS = 4                # CPU threads PyTorch can use
# --------------------------------------------------------------------- #

# 1) Camera
picam2 = Picamera2()
picam2.configure(
    picam2.create_video_configuration(
        main={"size": (CAM_W, CAM_H), "format": "BGR888"}  # BGR so we can draw without conversion
    )
)

# Lock camera timing for smooth preview
if TARGET_FPS == 60:
    picam2.set_controls({"FrameDurationLimits": (16666, 16666)})  # ~60 fps
else:
    picam2.set_controls({"FrameDurationLimits": (33333, 33333)})  # ~30 fps

# Optional: If you want manual exposure, uncomment and set values that are <= frame duration
# picam2.set_controls({
#     "AeEnable": False,
#     "ExposureTime": 8000,   # microseconds
#     "AnalogueGain": 4.0,
# })

picam2.start()

# 2) Model (nano is fastest on Pi)
model = YOLO("yolo11n.pt")  # you can swap to yolo11s.pt, but it will be slower

# Let PyTorch use more cores
try:
    torch.set_num_threads(TORCH_THREADS)
except Exception:
    pass

# Warm-up: stabilize first prediction latency
_ = model.predict(np.zeros((CAM_H, CAM_W, 3), dtype=np.uint8), imgsz=IMGSZ, device="cpu", verbose=False)

# FPS trackers
preview_fps_ema = None
infer_fps_ema = None
prev_time = time.time()
last_infer_time = None

last_results = None
frame_i = 0


def draw_boxes(img_bgr, results, top_k=SHOW_TOP_K):
    if results is None:
        return img_bgr
    r = results[0]
    if r.boxes is None or len(r.boxes) == 0:
        return img_bgr
    # Extract arrays from tensor boxes
    boxes = r.boxes.xyxy.cpu().numpy()
    confs = r.boxes.conf.cpu().numpy()
    clss  = r.boxes.cls.cpu().numpy().astype(int)
    names = r.names

    # Keep top_k by confidence
    idx = np.argsort(-confs)[:top_k]
    for i in idx:
        x1, y1, x2, y2 = boxes[i].astype(int)
        cf = confs[i]
        c = clss[i]
        label = f"{names[c]} {cf:.2f}"
        cv2.rectangle(img_bgr, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img_bgr, label, (x1, max(0, y1 - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
    return img_bgr


window_title = "IMX296 High-FPS Preview + YOLO (every N frames)"

try:
    while True:
        frame_bgr = picam2.capture_array()  # already BGR888

        # Detection cadence control
        if frame_i % DETECT_EVERY == 0:
            t0 = time.time()
            last_results = model.predict(
                frame_bgr,
                imgsz=IMGSZ,
                conf=CONF,
                iou=IOU,
                classes=LIMIT_CLASSES,  # or None
                device="cpu",
                verbose=False,
            )
            t1 = time.time()
            # instantaneous inference FPS
            infer_fps = 1.0 / max(1e-3, (t1 - t0))
            infer_fps_ema = infer_fps if infer_fps_ema is None else 0.9 * infer_fps_ema + 0.1 * infer_fps
            last_infer_time = t1

        annotated = frame_bgr.copy()
        annotated = draw_boxes(annotated, last_results)

        # Preview FPS (measures the whole loop pace)
        now = time.time()
        preview_fps = 1.0 / max(1e-3, (now - prev_time))
        prev_time = now
        preview_fps_ema = preview_fps if preview_fps_ema is None else 0.9 * preview_fps_ema + 0.1 * preview_fps

        # HUD
        cv2.putText(annotated, f"Preview FPS: {preview_fps_ema:.1f}", (10, 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        if infer_fps_ema is not None:
            cv2.putText(annotated, f"Det FPS (~every {DETECT_EVERY}): {infer_fps_ema:.1f}", (10, 52),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(annotated, f"imgsz={IMGSZ}", (10, 78),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)

        cv2.imshow(window_title, annotated)
        frame_i += 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    picam2.stop()
    cv2.destroyAllWindows()

