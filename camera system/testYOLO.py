import cv2
from ultralytics import YOLO
from picamera2 import Picamera2

def main():
    model = YOLO("yolo11n.pt")

    picam2 = Picamera2()
    config = picam2.create_preview_configuration(
        main={"size": (640, 480), "format": "RGB888"}
    )
    picam2.configure(config)
    picam2.start()

    while True:
        frame = picam2.capture_array()  # RGB numpy array

        results = model.predict(frame, imgsz=320, conf=0.35, verbose=False)
        annotated = results[0].plot()

        cv2.imshow("YOLO11n (q to quit)", annotated)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()
    picam2.stop()

if __name__ == "__main__":
    main()