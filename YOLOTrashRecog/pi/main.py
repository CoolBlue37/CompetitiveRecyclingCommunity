import subprocess
import threading
import time
from time import sleep
from gpiozero import AngularServo, LED, Button
import numpy as np
from signal import pause

import cv2
from ultralytics import YOLO

model = YOLO("/home/tanush/yolo/best_ncnn_model", task="classify")
IMGSZ = 224

W, H, FPS = 640, 480, 30          
FRAME_BYTES = W * H * 3 // 2      
LOG = "/tmp/rpicam.log"

latest = None
frame_id = 0          
lock = threading.Lock()
run_lock = threading.Lock()

print("Starting camera...")
log = open(LOG, "w")
cam = subprocess.Popen(
    [
        "rpicam-vid", "-t", "0", "-n",
        "--mode", "1296:972:10:P",
        "--width", str(W), "--height", str(H), "--framerate", str(FPS),
        "--codec", "yuv420",
        "-o", "-",          
    ],
    stdout=subprocess.PIPE,
    stderr=log,   
    bufsize=0,
)


def read_exact(n):
    buf = bytearray()
    while len(buf) < n:
        chunk = cam.stdout.read(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return bytes(buf)


def reader():
    global latest, frame_id
    while True:
        raw = read_exact(FRAME_BYTES)
        if raw is None:
            print("Camera stream ended.")
            break
        yuv = np.frombuffer(raw, np.uint8).reshape(H * 3 // 2, W)
        bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420)
        with lock:
            latest = bgr
            frame_id += 1


threading.Thread(target=reader, daemon=True).start()   

for _ in range(100):
    if latest is not None:
        break
    if cam.poll() is not None:
        break
    time.sleep(0.1)

if latest is None:
    cam.terminate()
    log.close()
    print("Could not get frames from the camera. rpicam-vid said:\n")
    print(open(LOG).read()[-2000:])
    raise SystemExit(1)
print("Camera connected.")

B1 = Button(17, bounce_time=0.05)
B2 = Button(27, bounce_time=0.05)
B3 = Button(22, bounce_time=0.05)
B4 = Button(5, bounce_time=0.05)
Bre = Button(6, bounce_time=0.05)
Btr = Button(13, bounce_time=0.05)
LGr = LED(23)
LRe = LED(24)

servo = AngularServo(18, min_angle=-90, max_angle=90)
servo.angle = 0
sleep(1)

recycle = False
toRecycle = [0, 1, 2, 4, 5]
n = 10


def setRecycle():
    global recycle
    recycle = True
    print("Recycling")


def setTrash():
    global recycle
    recycle = False
    print("Trashing")


def APIstuff(gr):
    pass


def run(gr):
    print("Grade:", gr)
    if not run_lock.acquire(blocking=False):
        return
    try:
        all_probs = []
        last_seen = -1
        deadline = time.time() + 10

        while len(all_probs) < n:
            if time.time() > deadline:
                print("Timed out waiting for frames.")
                return
            with lock:
                if latest is None or frame_id == last_seen:
                    frame = None
                else:
                    frame = latest.copy()
                    last_seen = frame_id
            if frame is None:
                time.sleep(0.01)
                continue
            r = model.predict(frame, imgsz=IMGSZ, verbose=False)[0]
            all_probs.append(r.probs.data.cpu().numpy())

        print("Predictions Complete")

        mean = np.mean(all_probs, axis=0)
        idx = int(mean.argmax())
        trueRecycle = idx in toRecycle

        (LGr if trueRecycle == recycle else LRe).on()
        servo.angle = 90 if trueRecycle else -90
        sleep(4)
        servo.angle = 0
        sleep(1)
        LGr.off()
        LRe.off()
    finally:
        run_lock.release()


Bre.when_released = setRecycle
Btr.when_released = setTrash
B1.when_released = lambda: run(0)
B2.when_released = lambda: run(1)
B3.when_released = lambda: run(2)
B4.when_released = lambda: run(3)

try:
    print("System ready.")
    pause()
except KeyboardInterrupt:
    print("\nShutting down...")
finally:
    cam.terminate()
    log.close()
    servo.close()
