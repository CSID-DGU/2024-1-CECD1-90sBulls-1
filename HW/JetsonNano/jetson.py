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

    def detect_human(self, input_image_path):
        # 사람 인식을 위한 YOLO 모델 사용
        results = self.model(source=input_image_path)

        for result in results:
            # 사람 클래스 (ID: 0)만 필터링
            person_boxes = [box for box in result.boxes if box.cls == 0]

            if len(person_boxes) > 0:
                print("사람 감지됨")
                self.process_image(input_image_path, "preprocessed_img.jpg")
                print("전처리 완료")
                self.client_socket.sendImages("preprocessed_img.jpg")
            else:
                print("사람 없음")
		    
   @staticmethod
    def process_image(input_image_path, output_image_path):
        image = cv2.imread(input_image_path)
        denoised_image = cv2.GaussianBlur(image, (5, 5), 0)
        resized_image = cv2.resize(denoised_image, (640, 640), interpolation=cv2.INTER_LINEAR)
        cv2.imwrite(output_image_path, resized_image)

class MainController:
    def __init__(self, pir_pin, tcp_ip, tcp_port, yolo_model_path):
        self.client_socket = ClientSocket(tcp_ip, tcp_port)
        self.camera = Camera()
        self.model = YOLO(yolo_model_path)
        self.motion_detector = MotionDetector(pir_pin, self.camera, self.client_socket, self.model)
	    
    def run(self):
        print("동작 대기 중...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("사용자에 의해 중지됨")
        finally:
            GPIO.cleanup()

if __name__ == "__main__":
    PIR_PIN = 18
    TCP_IP = '110.234.18.234'
    TCP_PORT = 8080
    YOLO_MODEL_PATH = 'yolov8n.pt'
