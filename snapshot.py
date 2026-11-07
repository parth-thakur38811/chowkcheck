from ultralytics import YOLO
import sys

VEHICLE_CLASSES =[1,2,3,5,7]
MODEL_PATH = "yolo26n.pt"

def count_vehicles(model, image_name):
    detect = model(image_name, classes=VEHICLE_CLASSES)
    result = detect[0]
    counts = {}
    for c in result.boxes.cls:
        name = model.names[int(c)]
        if name in counts:
            counts[name] += 1
        else:
            counts[name] = 1

    result.save(image_name + "_result.jpg")
    return counts


def main():
    try:
        image_name = sys.argv[1]
    except IndexError:
        sys.exit("Please enter a valid file name!!")
    model = YOLO(MODEL_PATH)
    counts = count_vehicles(model, image_name)
    print(counts)


if __name__ == "__main__":
    main()



