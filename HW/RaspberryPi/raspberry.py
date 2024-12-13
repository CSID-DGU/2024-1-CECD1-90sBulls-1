import board
import neopixel
import socket
import json
import asyncio
import time
import paho.mqtt.client as mqtt

# 서버 설정
SERVER_IP = '211.188.63.60'  # 서버 IP 주소
SERVER_PORT = 8080  # 서버 포트 번호

# MQTT 브로커 설정
BROKER = "localhost"  # MQTT 브로커 주소
PORT = 1883  # MQTT 포트 번호
TOPIC_SUBSCRIBE_LIGHT = "app/light"  # 조명 제어 명령을 구독할 토픽
TOPIC_SUBSCRIBE_SCENARIO = "app/scenario"  # 시나리오 업데이트를 구독할 토픽
TOPIC_PUBLISH = "pi/light"  # 조명 상태를 발행할 토픽

# 조명 설정을 저장하는 JSON 파일 경로
JSON_FILE_PATH = "lighting_config.json"

# NeoPixel 스트립 설정
STRIPS_CONFIG = [
    {"pin": board.D18, "num_leds": 45},  # 첫 번째 스트립: 핀 번호와 LED 개수
    {"pin": board.D21, "num_leds": 45},  # 두 번째 스트립
    {"pin": board.D12, "num_leds": 45}   # 세 번째 스트립
]

# NeoPixel 객체 생성
strips = [
    neopixel.NeoPixel(config["pin"], config["num_leds"], auto_write=False)
    for config in STRIPS_CONFIG
]

# 현재 상태를 캐싱하여 불필요한 업데이트 방지
current_state = {"lx": None, "color": (None, None, None)}

# 조명 색상 설정 함수
def set_color(color):
    """모든 NeoPixel 스트립의 색상을 설정합니다."""
    for strip in strips:
        strip.fill(color)  # 모든 LED를 동일한 색상으로 설정
        strip.show()

# 밝기 설정 함수
def set_brightness(brightness):
    """모든 NeoPixel 스트립의 밝기를 설정합니다."""
    for strip in strips:
        strip.brightness = brightness  # 밝기 설정
        strip.show()

# 조명 끄기 함수
def turn_off():
    """모든 NeoPixel 스트립의 조명을 끕니다."""
    for strip in strips:
        strip.fill((0, 0, 0))  # LED를 모두 검은색(꺼짐)으로 설정
        strip.show()

# 조명 설정 파일 로드 함수
def load_lighting_config():
    """조명 설정 JSON 파일을 로드합니다."""
    try:
        with open(JSON_FILE_PATH, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: 설정 파일 '{JSON_FILE_PATH}'을 찾을 수 없습니다.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: 설정 파일 '{JSON_FILE_PATH}'의 JSON 형식이 잘못되었습니다.")
        return {}

# 조명 설정 파일 저장 함수
def save_lighting_config(config):
    """조명 설정 JSON 파일을 저장합니다."""
    try:
        with open(JSON_FILE_PATH, "w") as file:
            json.dump(config, file, indent=4)
    except Exception as e:
        print(f"Error: 설정 파일 저장 실패 - {e}")

# 조명 설정 적용 함수
def apply_lighting(class_type):
    """제공된 클래스 타입에 따라 조명 설정을 적용합니다."""
    global current_state
    config = load_lighting_config()  # 조명 설정 파일 로드

    # 주어진 클래스의 설정을 검색
    if str(class_type) in config:
        settings = config[str(class_type)]
        brightness = settings.get("lx", 1.0)  # 밝기 값 가져오기 (기본값 1.0)
        color = (settings.get("r", 255), settings.get("g", 255), settings.get("b", 255))  # 색상 값 가져오기

        # 중복 업데이트 방지
        if current_state["lx"] != brightness or current_state["color"] != color:
            print(f"클래스 {class_type}에 대한 조명 적용: {settings}")
            set_brightness(brightness)
            set_color(color)
            current_state = {"lx": brightness, "color": color}
    else:
        print(f"클래스 타입 {class_type}이 설정에 없습니다. 조명을 끕니다.")
        turn_off()

# MQTT 연결 시 호출되는 함수
def on_connect(client, userdata, flags, rc):
    print(f"MQTT 연결 성공: 결과 코드 {rc}")
    client.publish(TOPIC_PUBLISH, "!", retain=True)  # 초기 상태 발행
    client.subscribe(TOPIC_SUBSCRIBE_LIGHT)  # 조명 제어 토픽 구독
    client.subscribe(TOPIC_SUBSCRIBE_SCENARIO)  # 시나리오 토픽 구독

# MQTT 메시지 수신 시 호출되는 함수
def on_message(client, userdata, msg):
    global current_state
    print(f"앱으로부터 메시지 수신: {msg.payload.decode()}")
    try:
        data = json.loads(msg.payload.decode())
        if msg.topic == TOPIC_SUBSCRIBE_LIGHT:
            # 직접 NeoPixel 업데이트
            lx = data.get("lx", 1.0)
            r = data.get("r", 255)
            g = data.get("g", 255)
            b = data.get("b", 255)
            print(f"조명 업데이트: lx={lx}, 색상=({r}, {g}, {b})")
            set_brightness(lx)
            set_color((r, g, b))
            current_state = {"lx": lx, "color": (r, g, b)}
        elif msg.topic == TOPIC_SUBSCRIBE_SCENARIO:
            # 설정 파일 업데이트
            class_type = str(data.get("class"))
            lx = data.get("lx", 1.0)
            r = data.get("r", 255)
            g = data.get("g", 255)
            b = data.get("b", 255)
            config = load_lighting_config()
            config[class_type] = {"lx": lx, "r": r, "g": g, "b": b}
            save_lighting_config(config)
            print(f"클래스 {class_type}에 대한 시나리오 업데이트: {config[class_type]}")
    except json.JSONDecodeError:
        print("Error: 수신된 데이터가 유효한 JSON 형식이 아닙니다.")

# MQTT 클라이언트 생성
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# MQTT 루프 시작 함수
def start_mqtt_loop():
    """MQTT 클라이언트 루프를 별도의 스레드에서 실행합니다."""
    client.connect(BROKER, PORT, 60)
    client.loop_start()

# 서버와의 통신을 처리하는 비동기 함수
async def handle_server_communication():
    """서버와의 통신을 처리하는 비동기 함수."""
    while True:
        try:
            reader, writer = await asyncio.open_connection(SERVER_IP, SERVER_PORT)
            print("서버에 연결되었습니다.")

            while True:
                data = await reader.read(1024)
                if not data:
                    print("서버 연결이 종료되었습니다.")
                    break

                print(f"서버로부터 데이터 수신: {data.decode()}")
                try:
                    data_json = json.loads(data.decode())
                    class_type = data_json.get("class")
                    if class_type is not None:
                        apply_lighting(class_type)  # 조명 설정 적용
                    else:
                        print("경고: 수신 데이터에 'class' 키가 없습니다.")
                except json.JSONDecodeError:
                    print("Error: 수신된 데이터가 유효한 JSON 형식이 아닙니다.")
        except (ConnectionRefusedError, ConnectionResetError, OSError) as e:
            print(f"Error: 서버 연결 문제 - {e}")
            print("5초 후 재연결 시도...")
            await asyncio.sleep(5)

# 메인 함수
async def main():
    """서버 및 애플리케이션 통신 태스크를 실행하는 메인 함수."""
    try:
        start_mqtt_loop()  # MQTT 루프 시작
        await handle_server_communication()  # 서버와의 통신 처리
    except KeyboardInterrupt:
        print("사용자에 의해 중단되었습니다. 조명을 끕니다.")
        turn_off()
        client.loop_stop()

if __name__ == "__main__":
    asyncio.run(main())
