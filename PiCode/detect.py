from ultralytics import YOLO
model = YOLO("/home/tanush/yolo/best_ncnn_model", task="classify")
for _ in model.predict("tcp://127.0.0.1:8888", stream=True, imgsz=224):
    pass
