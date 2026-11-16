import subprocess
import threading
import time
from time import sleep
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from gpiozero import AngularServo
from gpiozero import LED, Button
import numpy as np

import cv2
from ultralytics import YOLO

latest = None
lock = threading.Lock()
model = YOLO("/home/tanush/yolo/best_ncnn_model", task="classify")
IMGSZ=224

PORT = 8000
STREAM = "tcp://127.0.0.1:8888"

print("Starting camera...")
cam = subprocess.Popen(
    [
        "rpicam-vid", "-t", "0", "-n",
        "--mode", "1296:972:10:P",
        "--width", "640", "--height", "480", "--framerate", "10",
        "--codec", "libav", "--libav-format", "mpegts",
        "-o", STREAM + "?listen=1",
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

cap = None
for _ in range(20):
    time.sleep(1)
    cap = cv2.VideoCapture(STREAM)
    if cap.isOpened():
        break
if cap is None or not cap.isOpened():
    cam.terminate()
    raise SystemExit("Could not connect to the camera. Is another camera command still running?")
print("Camera connected.")

def reader():
    global latest
    while True:
        ok, frame = cap.read()
        if ok:
            with lock:
                latest = frame
        else:
            time.sleep(0.05)

threading.Thread(target=reader, daemon=True).start()

def infer():
    global jpeg
    with lock:
        frame = None if latest is None else latest.copy()
    if frame is None:
        time.sleep(0.05)
        return

    r = model.predict(frame, imgsz=IMGSZ, verbose=False)[0]

    return r


B1 = Button(0)
B2 = Button(2)
B3 = Button(3)
B4 = Button(21)
Bre = Button(6)
Btr = Button(7)
LGr = LED(8)
LRe = LED(9)
Srvo = 1

# Adjust min/max pulse widths to match your servo's datasheet
servo = AngularServo(Srvo, min_angle=-90, max_angle=90)

servo.angle = 0
sleep(1)

recycle = 0

toRecycle=[0, 1, 2, 4, 5]

def setRecycle():
    global recycle
    recycle = True

def setTrash():
    global recycle
    recycle = False

Bre.when_released = setRecycle
Btr.when_released = setTrash

B1.when_released = lambda: run(0)
B2.when_released = lambda: run(1)
B3.when_released = lambda: run(2)
B4.when_released = lambda: run(3)

n = 10

def APIstuff(gr):
    pass

def run(gr):
    all_probs = []
    for _ in range(n):
       r = infer()
       all_probs.append(r.probs.data.cpu().numpy())

    mean = np.mean(all_probs, axis=0)     # average per class
    idx = int(mean.argmax())

    trueRecycle = idx in toRecycle

    if trueRecycle == recycle: LGr.on()
    else: LRe.on()

    if trueRecycle:
        servo.angle = 90
    else:
        servo.angle = -90

    sleep(4)

    servo.angle = 0
    sleep(1)

    LGr.off()
    LRe.off()




