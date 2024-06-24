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

model = YOLO('./best.pt')

clients = []

SERVER_IP = '10.43.24.186'
SERVER_PORT = 8080

class Socket:

    def __init__(self, ip, port):
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.sock = None
        self.socketOpen()

    def socketClose(self):
        self.sock.close()
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is close')

    def socketOpen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.bind((self.TCP_IP, self.TCP_PORT))
        self.sock.listen()
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is open')


def receiveImages(conn):
    try:
        while True:
            length = recvall(conn, 64).decode('utf-8')
            if length is None:
                break
            stringData = recvall(conn, int(length))
            data = numpy.frombuffer(base64.b64decode(stringData), numpy.uint8)
            decimg = cv2.imdecode(data, 1)
            cv2.imwrite("saved_image.jpg", decimg)

            results = model.predict("./saved_image.jpg", show=False)

            for result in results:
                cls = result.boxes.cls
                if (cls == 0):
                    value = {"r": 255, "g": 255, "b": 0, "lx": 50, "cls": "Eating person"}
                elif (cls == 1):
                    value = {"r": 204, "g": 0, "b": 0, "lx": 50, "cls": "Sleeping person"}
                elif (cls == 2):
                    value = {"r": 51, "g": 0, "b": 255, "lx": 50, "cls": "Studying person"}
                else:
                    print("No class")
                    continue

                # change format from dict to json
                # create new thread for sending JSON data and start
                json_data = json.dumps(value)
                send_socket(json_data, conn)

    except Exception as e:
        print(e)
    finally:
        clients.remove(conn)
        conn.close()

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf
