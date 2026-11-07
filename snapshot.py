from ultralytics import YOLO

model = YOLO("yolo26n.pt")
results = model("road.jpg")
result = results[0]
