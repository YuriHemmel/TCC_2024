# Este arquivo é apenas para testar a conexão da câmera, favor não removê-lo por enquanto

import cv2
import os

'''
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0"

user = "admin"
password = "arifym2023"
ip = "192.168.1.16"
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


print(os.listdir('imagensAlunos'))
'''

'''
tabview = CTkTabview(master=app)
tabview.pack(padx=20, pady=20)

tabview.add("Alunos")
tabview.add("Aulas")
tabview.add("Câmeras")

btn = CTkButton(master=tabview.tab("Alunos"), text="Clica ali", corner_radius=32, fg_color=("#DB3E39", "#821D1A"),
                border_color="#FFCC70", border_width=2)
btn.place(relx=0.5, rely=0.5, anchor="center")
'''
