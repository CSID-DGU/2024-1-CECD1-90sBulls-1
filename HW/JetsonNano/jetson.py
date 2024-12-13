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

# 클라이언트 소켓 클래스
class ClientSocket:
    def __init__(self, ip, port):
        # 서버 IP와 포트 설정
        self.TCP_SERVER_IP = ip  # 서버의 IP 주소
        self.TCP_SERVER_PORT = port  # 서버의 포트 번호
        self.connect_count = 0  # 연결 시도 횟수 초기화
        self.connect_server()  # 서버 연결 시도

    def connect_server(self):
        # 서버와 연결을 시도
        try:
            self.sock = socket.socket()  # TCP 소켓 생성
            self.sock.connect((self.TCP_SERVER_IP, self.TCP_SERVER_PORT))  # 서버에 연결
            print(f'클라이언트 소켓이 서버 소켓과 연결되었습니다 [ IP: {self.TCP_SERVER_IP}, PORT: {self.TCP_SERVER_PORT} ]')
            self.connect_count = 0  # 연결 성공 시 연결 시도 횟수 초기화
        except Exception as e:
            # 연결 실패 시 예외 처리
            print(e)
            self.connect_count += 1  # 연결 시도 횟수 증가
            if self.connect_count == 10:  # 10회 이상 연결 실패 시 프로그램 종료
                print(f'{self.connect_count}회 연결 실패. 프로그램 종료')
                sys.exit()
            print(f'{self.connect_count}회 서버와 연결 시도 중')
            time.sleep(5)  # 5초 후 다시 연결 시도
            self.connect_server()

    def send_images(self, image_path):
        # 이미지를 서버로 전송
        image = cv2.imread(image_path)  # 이미지 파일 읽기
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]  # JPEG 이미지 품질 설정
        result, imgencode = cv2.imencode('.jpg', image, encode_param)  # 이미지 인코딩
        data = np.array(imgencode)  # 인코딩된 이미지를 NumPy 배열로 변환
        string_data = base64.b64encode(data)  # Base64로 인코딩
        length = str(len(string_data))  # 데이터 길이를 문자열로 변환
        self.sock.sendall(length.encode('utf-8').ljust(64))  # 데이터 길이를 전송
        self.sock.send(string_data)  # 인코딩된 이미지 데이터 전송
        print("이미지 전송 완료")

# 카메라 관리 클래스 (OpenCV 사용)
class Camera:
    def __init__(self):
        # CSI 카메라를 OpenCV로 제어
        self.cap = cv2.VideoCapture(
            "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=640, height=480, format=I420 ! videoconvert ! appsink",
            cv2.CAP_GSTREAMER
        )
        if not self.cap.isOpened():  # 카메라 초기화 실패 시 오류 처리
            print("카메라를 열 수 없습니다.")
            sys.exit()

        self.frame_count = 0  # 캡처된 프레임 수 초기화

    def capture_frame(self):
        # 프레임을 캡처
        ret, frame = self.cap.read()  # 프레임 읽기
        self.frame_count += 1  # 캡처된 프레임 수 증가
        return frame

    def save_frame(self, frame, img_name="img.jpg"):
        # 캡처된 프레임을 파일로 저장
        cv2.imwrite(img_name, frame)  # 이미지를 파일로 저장
        print(f"저장됨 {img_name}")

# 동작 감지 및 사람 감지 클래스
class MotionDetector:
    def __init__(self, pir_pin, camera, client_socket, model):
        # 동작 감지 센서와 관련된 핀 및 의존성 초기화
        self.PIR_PIN = pir_pin  # PIR 센서 핀 번호
        self.camera = camera  # Camera 객체
        self.client_socket = client_socket  # ClientSocket 객체
        self.model = model  # YOLO 모델 객체

        # PIR 센서 초기 설정
        GPIO.setwarnings(False)  # GPIO 경고 메시지 비활성화
        GPIO.setmode(GPIO.BCM)  # GPIO 핀 모드 설정 (BCM)
        GPIO.setup(self.PIR_PIN, GPIO.IN)  # PIR 센서를 입력 모드로 설정
        GPIO.add_event_detect(self.PIR_PIN, GPIO.RISING, callback=self.motion_detected)  # 동작 감지 이벤트 등록

    def motion_detected(self, channel):
        # 동작 감지 이벤트 발생 시 호출되는 콜백 함수
        print("동작 감지됨")

        while GPIO.input(self.PIR_PIN):  # PIR 센서가 신호를 감지하는 동안 반복
            frame = self.camera.capture_frame()  # 카메라로 프레임 캡처
            if self.camera.frame_count % 30 == 0:  # 30번째 프레임마다 처리
                img_name = "img.jpg"
                self.camera.save_frame(frame, img_name)  # 프레임 저장
                self.detect_human(img_name)  # YOLO 모델로 사람 감지

    def detect_human(self, input_image_path):
        # YOLO 모델을 사용하여 사람 감지
        results = self.model(input_image_path)  # YOLO 모델로 이미지 분석

        for result in results:  # 분석 결과 처리
            person_boxes = [box for box in result.boxes if box.cls == 0]  # 사람 클래스 필터링

            if len(person_boxes) > 0:  # 사람이 감지된 경우
                print("사람 감지됨")
                self.process_image(input_image_path, "preprocessed_img.jpg")  # 이미지 전처리
                print("전처리 완료")
                self.client_socket.send_images("preprocessed_img.jpg")  # 전처리된 이미지 서버 전송
            else:
                print("사람 없음")

    @staticmethod
    def process_image(input_image_path, output_image_path):
        # 이미지를 전처리 (노이즈 제거 및 크기 조정)
        image = cv2.imread(input_image_path)  # 이미지 파일 읽기
        denoised_image = cv2.GaussianBlur(image, (5, 5), 0)  # 가우시안 블러로 노이즈 제거
        resized_image = cv2.resize(denoised_image, (640, 640), interpolation=cv2.INTER_LINEAR)  # 크기 조정
        cv2.imwrite(output_image_path, resized_image)  # 전처리된 이미지 저장

# 메모리 관리 스레드
def manage_memory():
    # CPU 및 GPU 메모리 캐시를 주기적으로 관리
    while True:
        gc.collect()  # CPU 메모리 캐시 삭제
        if torch.cuda.is_available():
            torch.cuda.empty_cache()  # GPU 메모리 캐시 삭제
        print("메모리 캐시 삭제 완료")
        time.sleep(60)  # 60초마다 반복

# 메인 컨트롤러 클래스
class MainController:
    def __init__(self, pir_pin, tcp_ip, tcp_port, yolo_model_path):
         # 주요 구성 요소 초기화
        self.client_socket = ClientSocket(tcp_ip, tcp_port)  # 클라이언트 소켓 생성
        self.camera = Camera()  # 카메라 객체 생성
        self.model = YOLO(yolo_model_path)  # YOLO 모델 로드
        self.motion_detector = MotionDetector(pir_pin, self.camera, self.client_socket, self.model)  # MotionDetector 초기화

    def run(self):
        # 메인 실행 로직
        print("동작 대기 중...")
        memory_manager = threading.Thread(target=manage_memory)  # 메모리 관리 스레드 생성
        memory_manager.start()  # 메모리 관리 스레드 실행

        try:
            while True:
                time.sleep(1)  # 메인 스레드 대기
        except KeyboardInterrupt:
            print("사용자에 의해 중지됨")
        finally:
            GPIO.cleanup()  # GPIO 핀 정리

# 프로그램 실행 진입점
if __name__ == "__main__":
    PIR_PIN = 18  # PIR 센서 핀 번호
    TCP_IP = '175.45.194.40'  # 서버 IP 주소
    TCP_PORT = 8080  # 서버 포트 번호
    YOLO_MODEL_PATH = 'yolov8n.pt'  # YOLO 모델 파일 경로

    controller = MainController(PIR_PIN, TCP_IP, TCP_PORT, YOLO_MODEL_PATH)  # MainController 생성
    controller.run()  # 프로그램 실행
