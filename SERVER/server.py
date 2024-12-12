import json
import torch
import os
import socket
import cv2
import numpy
import base64
import glob
import sys
import time
import threading
from datetime import datetime
from ultralytics import YOLO

# CycleGAN 및 YOLO 모델 로드
cyclegan_model = CycleGAN_Turbo(pretrained_name="night_to_day")
cyclegan_model.eval()
cyclegan_model.unet.enable_xformers_memory_efficient_attention()

model = YOLO('./best.pt')

# 클라이언트 연결을 위한 큐
client_queue = queue.Queue()

SERVER_IP = '175.45.194.40'
SERVER_PORT = 8080
TIMEOUT = 10  # 소켓 타임아웃 설정 (10초)

# 소켓 클래스
class Socket:
    def __init__(self, ip, port):
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.sock = None
        self.socketOpen()

    def socketClose(self):
        self.sock.close()
        print(f'Server socket [ TCP_IP: {self.TCP_IP}, TCP_PORT: {self.TCP_PORT} ] is closed')

    def socketOpen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.bind((self.TCP_IP, self.TCP_PORT))
        self.sock.listen()
        self.sock.settimeout(TIMEOUT)  # 타임아웃 설정
        print(f'Server socket [ TCP_IP: {self.TCP_IP}, TCP_PORT: {self.TCP_PORT} ] is open')

# 이미지 밝기 확인 함수
def is_low_light(image, threshold=50):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_brightness = gray.mean()
    return mean_brightness < threshold

# YOLO 모델 예측 및 클래스별 JSON 데이터 생성
def generate_class_value(cls):
    if cls == 0:
        return {"r": 255, "g": 255, "b": 0, "lx": 50, "cls": "Eating person"}
    elif cls == 2:
        return {"r": 204, "g": 0, "b": 0, "lx": 50, "cls": "Sleeping person"}
    elif cls == 3:
        return {"r": 51, "g": 0, "b": 255, "lx": 50, "cls": "Studying person"}
    return None

# CycleGAN 변환 함수
transform = transforms.Compose([
    transforms.Resize((512, 512)),
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5])
])

def enhance_brightness_with_cyclegan(image):
    input_img = transform(image).unsqueeze(0).cuda()
    with torch.no_grad():
        output = cyclegan_model(input_img)
        output_img = output[0].cpu() * 0.5 + 0.5
        output_img = transforms.ToPILImage()(output_img).resize((image.shape[1], image.shape[0]))
    return np.array(output_img)

# 클라이언트로부터 이미지 수신 및 처리 함수
def receiveImages(conn):
    try:
        while True:
            length = recvall(conn, 64).decode('utf-8')
            if length is None:
                break
            compressed_data = recvall(conn, int(length))
            data = np.frombuffer(compressed_data, np.uint8)
            decimg = cv2.imdecode(data, 1)

            if is_low_light(decimg, 50):
                print("Low light detected. Enhancing brightness with CycleGAN.")
                decimg = enhance_brightness_with_cyclegan(decimg)

            results = model.predict(decimg, show=False)

            for result in results:
                cls = result.boxes.cls
                value = generate_class_value(cls)
                if value:
                    json_data = json.dumps(value)
                    send_socket(json_data, conn)
            # 주기적으로 캐시 정리
            manage_memory()

    except Exception as e:
        print(e)
    finally:
        client_queue.put(conn)  # 작업이 끝난 클라이언트를 큐에 반환
        conn.close()

# 소켓에서 데이터 수신
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

# 클라이언트에게 JSON 데이터 전송
def send_socket(data, sender_conn):
    while not client_queue.empty():
        try:
            client = client_queue.get_nowait()
            if client != sender_conn:
                print("Send results to Raspberry")
                client.send(data.encode())
        except queue.Empty:
            break