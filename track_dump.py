import csv
import sys
import cv2
import os
from ultralytics import YOLO

MODEL_PATH = "yolo26n.pt"
VEHICLE_CLASSES = [1, 2, 3, 5, 7]
OUTPUT_CSV = "output/tracks.csv"


def dump_tracks(model, video_path, csv_path):
    video = cv2.VideoCapture(video_path)

    if not video.isOpened():
        sys.exit("Re-check video path!!")
    fps = video.get(cv2.CAP_PROP_FPS)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter("output/tracked.mp4", fourcc, fps, (width, height))

    headers = ["time","track_id", "type", "x", "y"]
    with open(csv_path, "w", newline="") as result_file:
        writer = csv.writer(result_file)
        writer.writerow(headers)

        rows = 0
        try:
            while True:
                ok, frame = video.read()
                if not ok:
                    break                                   
                t = video.get(cv2.CAP_PROP_POS_MSEC) / 1000
                result = model.track(frame, persist=True, classes=VEHICLE_CLASSES, verbose=False)[0]
                annotated = result.plot()
                out.write(annotated)
                if result.boxes.id is None:
                    continue

                for box, track_id, cls in zip(result.boxes.xyxy, result.boxes.id, result.boxes.cls):
                    x1, y1, x2, y2 = box.tolist()

                    x = (x1+x2) / 2
                    y = y2
                    name = model.names[int(cls)]

                    writer.writerow([round(t, 2), int(track_id), name, round(x), round(y)])
                    rows += 1

        finally:
            video.release()
            out.release()
        return rows



def main():
    try:
        video_path = sys.argv[1]
    except IndexError:
        sys.exit("Enter a valid image or video path!!")
    model = YOLO(MODEL_PATH)
    os.makedirs("output", exist_ok=True)
    rows = dump_tracks(model, video_path, OUTPUT_CSV)
    print(f"Wrote {rows} rows to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()



