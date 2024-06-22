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

    controller = MainController(PIR_PIN, TCP_IP, TCP_PORT, YOLO_MODEL_PATH)
    controller.run()
