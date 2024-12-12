from ultralytics import YOLO
import RPi.GPIO as GPIO
import time
import cv2
import os
import numpy as np
import socket
import base64
import sys
import threading
import torch
import gc

class ClientSocket:
    def __init__(self, ip, port):
        self.TCP_SERVER_IP = ip
        self.TCP_SERVER_PORT = port
        self.connect_count = 0
        self.connect_server()

    def connect_server(self):
        try:
            self.sock = socket.socket()
            self.sock.connect((self.TCP_SERVER_IP, self.TCP_SERVER_PORT))
            print(f'클라이언트 소켓이 서버 소켓과 연결되었습니다 [ IP: {self.TCP_SERVER_IP}, PORT: {self.TCP_SERVER_PORT} ]')
            self.connect_count = 0
        except Exception as e:
            print(e)
            self.connect_count += 1
            if self.connect_count == 10:
                print(f'{self.connect_count}회 연결 실패. 프로그램 종료')
                sys.exit()
            print(f'{self.connect_count}회 서버와 연결 시도 중')
            time.sleep(5)
            self.connect_server()

    def send_images(self, image_path):
        image = cv2.imread(image_path)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]  # JPEG 품질 설정
        result, imgencode = cv2.imencode('.jpg', image, encode_param)
        data = np.array(imgencode)
        string_data = base64.b64encode(data)
        length = str(len(string_data))
        self.sock.sendall(length.encode('utf-8').ljust(64))
        self.sock.send(string_data)
        print("이미지 전송 완료")

class Camera:
    def __init__(self):
        # CSI 카메라를 OpenCV로 제어
        self.cap = cv2.VideoCapture("nvarguscamerasrc ! video/x-raw(memory:NVMM), width=640, height=480, format=I420 ! videoconvert ! appsink", cv2.CAP_GSTREAMER)
        if not self.cap.isOpened():
            print("카메라를 열 수 없습니다.")
            sys.exit()

        self.frame_count = 0

    def capture_frame(self):
        ret, frame = self.cap.read()
        self.frame_count += 1
        return frame

    def save_frame(self, frame, img_name="img.jpg"):
        cv2.imwrite(img_name, frame)
        print(f"저장됨 {img_name}")

class MotionDetector:
    def __init__(self, pir_pin, camera, client_socket, model):
        self.PIR_PIN = pir_pin
        self.camera = camera
        self.client_socket = client_socket
        self.model = model

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PIR_PIN, GPIO.IN)
        GPIO.add_event_detect(self.PIR_PIN, GPIO.RISING, callback=self.motion_detected)

    def motion_detected(self, channel):
        print("동작 감지됨")
    
        while GPIO.input(self.PIR_PIN):
            frame = self.camera.capture_frame()
            if self.camera.frame_count % 30 == 0:
                img_name = "img.jpg"
                self.camera.save_frame(frame, img_name)
                self.detect_human(img_name)
