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
