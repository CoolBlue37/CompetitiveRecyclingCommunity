import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import cv2
from ultralytics import YOLO

MODEL = "/home/tanush/yolo/best_ncnn_model"
IMGSZ = 224          # match imgsz in best_ncnn_model/metadata.yaml
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

latest = None
lock = threading.Lock()


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

print("Loading model...")
model = YOLO(MODEL, task="classify")
jpeg = None


def infer():
    global jpeg
    while True:
        with lock:
            frame = None if latest is None else latest.copy()
        if frame is None:
            time.sleep(0.05)
            continue

        start = time.time()
        r = model.predict(frame, imgsz=IMGSZ, verbose=False)[0]
        fps = 1 / max(time.time() - start, 1e-6)

        top = r.probs.top5[:3]
        confs = r.probs.top5conf[:3].tolist()
        y = 40
        for i, (c, p) in enumerate(zip(top, confs)):
            text = f"{r.names[c]} {p * 100:.0f}%"
            scale = 1.1 if i == 0 else 0.7
            color = (0, 255, 0) if i == 0 else (255, 255, 255)
            cv2.putText(frame, text, (12, y), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), 5)
            cv2.putText(frame, text, (12, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 2)
            y += 40 if i == 0 else 28
        cv2.putText(frame, f"{fps:.1f} fps", (12, 465), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 4)
        cv2.putText(frame, f"{fps:.1f} fps", (12, 465), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        print(f"{r.names[top[0]]} {confs[0] * 100:.0f}%  ({fps:.1f} fps)")

        ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if ok:
            jpeg = buf.tobytes()


threading.Thread(target=infer, daemon=True).start()

PAGE = b"""<!DOCTYPE html>
<html><head><title>Trash Classifier</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  body{margin:0;background:#111;color:#eee;font-family:sans-serif;
       display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh}
  img{max-width:100%;max-height:90vh;border-radius:8px}
  h1{font-size:18px;font-weight:500;margin:8px}
</style></head>
<body><h1>Trash Classifier - live</h1><img src="/stream"></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(PAGE)))
            self.end_headers()
            self.wfile.write(PAGE)
        elif self.path == "/stream":
            self.send_response(200)
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            last = None
            try:
                while True:
                    j = jpeg
                    if j is not None and j is not last:
                        self.wfile.write(
                            b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: "
                            + str(len(j)).encode()
                            + b"\r\n\r\n" + j + b"\r\n"
                        )
                        last = j
                    time.sleep(0.05)
            except (BrokenPipeError, ConnectionResetError):
                pass
        else:
            self.send_error(404)


server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
print(f"Open http://tanush-pi.local:{PORT} in your browser. Ctrl+C to stop.")
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    server.server_close()
    cam.terminate()
    print("Stopped.")
