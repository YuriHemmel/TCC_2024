# def reconhece_rosto(rosto):
#     reconhecido = False
#     # rosto = face_recognition.load_image_file(url_rosto)
#     rostos = face_recognition.face_encodings(rosto)

#     if (len(rostos) > 0):
#         reconhecido = True
    
#     return reconhecido, rostos


# def recebe_rostos():
#     rostos_conhecidos = []
#     id_rostos = []
#     pessoas = foto_utils.normaliza_fotos_da_matriz(Pessoa.recebe_fotos_e_ids_do_banco())

#     for foto, id in pessoas:
#         foto_normalizada = decode_foto(foto)
#         if (reconhece_rosto(foto_normalizada)[0]):
#             rostos_conhecidos.append(foto[1][0])
#             id_rostos.append(id)

#     return rostos_conhecidos, id_rostos

import cv2 
import os

def find_files(filename, search_path):
   result = []

# Procura o path do arquivo no disco (para windows C:, para raspberry deve ser /home/pi/)
   for root, dir, files in os.walk(search_path):
      if filename in files:
         result.append(os.path.join(root, filename))
   return result

xml_path = find_files('haarcascade_frontalface_alt2.xml', 'C:')[0]
# xml_path = os.path.join(haar_path, xml_name)

# TODO: Inicializar Classificador
clf = cv2.CascadeClassifier(xml_path)

# Inicializar webcam
#os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0"

# url = "rtsp://admin:arifym2023@192.168.1.16:554/onvif1"
cap = cv2.VideoCapture(0)

# Loop para leitura do conteúdo
while True:
    # Capturar proximo frame
    ret, frame = cap.read()

    # TODO: Converter para tons de cinza
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # TODO: Classificar
    faces = clf.detectMultiScale(gray)

    # TODO: Desenhar retangulo
    for x, y, w, h in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0))

    # Visualizar
    cv2.imshow('frame', frame)

    if cv2.waitKey(1) == ord('q'):
        print("Desconectando camera IP")
        break

# Desligar a webcam
cap.release()

#Fechar janela do vídeo
cv2.destroyAllWindows()