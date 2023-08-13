from tflite_runtime.interpreter import Interpreter

import datetime
import socket
import time
import cv2
import os

frame_rate = 30

def load_tflite_model(filename):
    interpreter = Interpreter(filename)
    signature = interpreter.get_signature_runner()
    return signature

detection_signature = load_tflite_model("face_detection.tflite")
location_signature = load_tflite_model("face_location.tflite")

def load_image(cap):
    cap.set(cv2.CAP_PROP_POS_FRAMES, 2)
    ret, frame = cap.read()
    print(frame)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resized = cv2.resize(rgb, (120, 120))
    numpy = np.expand_dims(resized / 255.0, 0)
    return numpy

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    print("Searching")
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect(("10.0.0.87", 10001))
    now = datetime.datetime.now()
    prev = now.strftime("%H")
    filename = now.strftime('%Y-%m-%d %H:%M')
    f = open(f"recordings/stream{filename}.h264", "wb")

    print("Connected")
    while True:
        if now.strftime("%H") == "21":
            break
        sock.sendall(b"Connected")
        print("Message sent")
        data = sock.recv(2056)
        f.write(data)
        print("Image recieved")        
        now = datetime.datetime.now()
        #cap = cv2.VideoCapture(f"recordings/stream{filename}.h264")
        #print(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        #image = load_image(cap)
        
        if now.strftime("%H") != prev:
            sock.close()
            time.sleep(2)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            sock.connect(("10.0.0.87", 10001))
            
            f.close()
            filename = now.strftime('%Y-%m-%d %H:%M')
            f = open(f"recordings/stream{filename}.h264", "wb")
            prev = now.strftime("%H")
    sock.close()
    f.close()
