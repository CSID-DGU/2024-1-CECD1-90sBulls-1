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
