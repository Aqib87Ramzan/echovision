import os
import cv2
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

from ultralytics import YOLO
from sound import speak   # JS-like speaking


# ---------------------------
# Distance Estimation Function
# ---------------------------
def estimate_distance(box_height, known_height=170, focal_length=141):
    """
    Estimate distance from bounding box height.
    known_height = average height of a person/object in cm
    focal_length = approx. webcam focal length (works well around 800-1000)
    Returns distance in meters.
    """
    if box_height <= 0:
        return None
    distance_cm = (known_height * focal_length) / box_height
    return distance_cm / 100.0  # cm → meters


def main():

    model = YOLO("yolo11n.pt")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot access webcam")
        return

    last_objects = set()
    announce_interval = 10
    frame_counter = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame")
            break

        r = model.track(frame, persist=True, verbose=False)
        tracked_frame = r[0].plot()

        frame_counter += 1

        if frame_counter % announce_interval == 0:

            boxes = r[0].boxes
            current_objects = set()

            if boxes is not None and len(boxes) > 0:

                cls_ids = boxes.cls.tolist()
                obj_names = [model.names[int(cid)] for cid in cls_ids]

                current_objects = set(obj_names)

                # --- Detect NEW objects ---
                new_objects = current_objects - last_objects

                for i, obj in enumerate(obj_names):
                    if obj in new_objects:

                        # Get bounding box height in pixels
                        box = boxes[i]
                        x1, y1, x2, y2 = box.xyxy[0]
                        height = abs(y2 - y1)

                        # Estimate distance
                        dist = estimate_distance(height)

                        if dist is not None:
                            message = f"Detected {obj} at {dist:.1f} meters ahead"
                        else:
                            message = f"Detected {obj}"

                        print("Speaking:", message)
                        speak(message)

                # Update memory
                last_objects = current_objects

        cv2.imshow("YOLO11 — Tracking + Distance", tracked_frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
