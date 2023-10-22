import cv2
import mediapipe as mp 
import os

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"]="rtsp_transport;0"

url = f"rtsp://admin:arifym2023@192.168.1.220:554/onvif1"

webcam = cv2.VideoCapture(url, cv2.CAP_FFMPEG) # para conectar o python com a camera ip

reconhecimento_rosto = mp.solutions.face_detection # ativando a solução de reconhecimento de rosto
desenho = mp.solutions.drawing_utils # ativando a solução de desenho
reconhecedor_rosto = reconhecimento_rosto.FaceDetection() # criando o item que consegue ler uma imagem e reconhecer os rostos 

while webcam.isOpened():
    validacao, frame = webcam.read() # lê a imagem da camera ip
    if not validacao:
        break
    imagem = frame
    lista_rostos = reconhecedor_rosto.process(imagem) # usa o reconhecedor para criar uma lista com os rostos reconhecidos
    
    if lista_rostos.detections: # caso algum rosto tenha sido reconhecido
        for rosto in lista_rostos.detections: # para cada rosto que foi reconhecido
            desenho.draw_detection(imagem, rosto) # desenha o rosto na imagem
    
    cv2.imshow("Rostos na sua webcam", imagem) # mostra a imagem da webcam para a gente
    if cv2.waitKey(1) == 27: # ESC # garante que o código vai ser pausado ao apertar ESC (código 27) e que o código vai esperar 5 milisegundos a cada leitura da camera ip
        break
webcam.release() # encerra a conexão com a camera
cv2.destroyAllWindows() # fecha a janela que mostra o que a camera está vendo