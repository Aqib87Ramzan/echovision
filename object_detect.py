import os
import cv2
import threading
from dotenv import load_dotenv
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

from ultralytics import YOLO
from sound import speak
from note_detection import detect_currency  # Your Roboflow-based detection

# ---------------------------
# Distance Estimation Function
# ---------------------------
def estimate_distance(box_height, known_height=170, focal_length=141):
    if box_height <= 0:
        return None
    distance_cm = (known_height * focal_length) / box_height
    return distance_cm / 100.0  # cm → meters

# ---------------------------
# Async Roboflow Detection
# ---------------------------
note_result = None
note_lock = threading.Lock()

def run_note_detection(frame):
    global note_result
    result = detect_currency(frame)
    with note_lock:
        note_result = result

# ---------------------------
# Main Loop
# ---------------------------
def main():
    global note_result
    model = YOLO("yolo11n.pt")  # Your general object YOLO

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

        # ---------------- YOLO Objects ----------------
        boxes = r[0].boxes
        current_objects = set()
        if boxes is not None and len(boxes) > 0:
            cls_ids = boxes.cls.tolist()
            obj_names = [model.names[int(cid)] for cid in cls_ids]
            current_objects = set(obj_names)
            new_objects = current_objects - last_objects

            for i, obj in enumerate(obj_names):
                if obj in new_objects:
                    box = boxes[i]
                    x1, y1, x2, y2 = box.xyxy[0]
                    height = abs(y2 - y1)
                    dist = estimate_distance(height)

                    if dist is not None:
                        message = f"Detected {obj} at {dist:.1f} meters ahead"
                    else:
                        message = f"Detected {obj}"
                    print("Speaking:", message)
                    speak(message)

            last_objects = current_objects

        # --------------- Roboflow Notes ----------------
        # Run async every announce_interval frames
        if frame_counter % announce_interval == 0:
            threading.Thread(target=run_note_detection, args=(frame.copy(),), daemon=True).start()

        # Speak note detection if available
        with note_lock:
            if note_result:
                message = f"{note_result['friendly_label']} Rs note detected"
                print("Speaking:", message)
                speak(message)
                note_result = None  # clear after speaking

        cv2.imshow("YOLO11 + Currency Notes", tracked_frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
