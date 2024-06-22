from ultralytics import YOLO
import RPi.GPIO as GPIO
import time
import jetson.utils
import cv2
import os
import numpy as np
import socket
import base64
import sys

class ClientSocket:
    def __init__(self, ip, port):
        self.TCP_SERVER_IP = ip
        self.TCP_SERVER_PORT = port
        self.connectCount = 0
        self.connectServer()

    def connectServer(self):
        try:
            self.sock = socket.socket()
            self.sock.connect((self.TCP_SERVER_IP, self.TCP_SERVER_PORT))
            print(
                f'클라이언트 소켓이 서버 소켓과 연결되었습니다 [ TCP_SERVER_IP: {self.TCP_SERVER_IP}, TCP_SERVER_PORT: {self.TCP_SERVER_PORT} ]')
            self.connectCount = 0
        except Exception as e:
            print(e)
            self.connectCount += 1
            if self.connectCount == 10:
                print(f'{self.connectCount}회 연결 실패. 프로그램 종료')
                sys.exit()
            print(f'{self.connectCount}회 서버와 연결 시도 중')
            time.sleep(5)
            self.connectServer()


		def sendImages(self, image_path):
		    image = cv2.imread(image_path)
		    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
		    result, imgencode = cv2.imencode('.jpg', image, encode_param)
		    data = np.array(imgencode)
		    stringData = base64.b64encode(data)
		    length = str(len(stringData))
		    self.sock.sendall(length.encode('utf-8').ljust(64))
		    self.sock.send(stringData)
		    print("전송 완료")


class Camera:
    def __init__(self):
        self.camera = jetson.utils.videoSource("csi://0")  # CSI 카메라 초기화
        self.frame_count = 0

    def capture_frame(self):
        frame = self.camera.Capture()
        self.frame_count += 1
        return frame

    def save_frame(self, frame, img_name="img.jpg"):
        jetson.utils.saveImageRGBA(img_name, frame)
        print(f"저장됨 {img_name}")

