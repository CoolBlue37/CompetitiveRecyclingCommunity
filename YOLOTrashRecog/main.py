from ultralytics import YOLO

def main():
    model = YOLO("runs/classify/train-4/weights/best.pt")
    results = model.predict(source=0, show=True, verbose=True)
    # print(results)

if __name__ == "__main__":
    main()