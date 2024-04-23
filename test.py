# Este arquivo é apenas para testar a conexão da câmera, favor não removê-lo por enquanto

import cv2
import os


os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0"


ip = "192.168.1.251"
port = "8554"
url = f"rtsp://{ip}:{port}/mjpeg/1"

cap = cv2.VideoCapture(url)

if not cap.isOpened():
    print("Erro ao abrir esp32 cam")
    exit(2)

print("Conectado com o esp32  cam")

while True:
    ret, frame = cap.read()

    if not ret:
        print("Sem frame ou erro na captura de video")
        break

    cv2.imshow("VIDEO", frame)

    if cv2.waitKey(1) == ord('q'):
        print("Desconectando esp32 cam")
        break

cap.release()
cv2.destroyAllWindows()


print(os.listdir('imagensAlunos'))
