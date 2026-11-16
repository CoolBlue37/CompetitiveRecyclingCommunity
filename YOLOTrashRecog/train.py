from ultralytics import YOLO

# Load a model

def main():
    model = YOLO("runs/classify/train-2/weights/best.pt")
    results = model.train(data="data", epochs=50, imgsz=320, batch=8, device=0)

if __name__ == "__main__": 
    main()