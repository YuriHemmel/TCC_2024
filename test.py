# Este arquivo é apenas para testar a conexão da câmera, favor não removê-lo por enquanto

import cv2
import os

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0"

user = "admin"
password = "arifym2023"
ip = "192.168.1.220"
port = "554"
url = f"rtsp://{user}:{password}@{ip}:{port}/onvif1"

cap = cv2.VideoCapture(url)

if not cap.isOpened():
    print("Erro ao abrir camera IP")
    exit(2)

print("Conectado com a camera IP")

while True:
    ret, frame = cap.read()

    if not ret:
        print("Sem frame ou erro na captura de video")
        break

    cv2.imshow("VIDEO", frame)

    if cv2.waitKey(1) == ord('q'):
        print("Desconectando camera IP")
        break

cap.release()
cv2.destroyAllWindows()
