import cv2
import face_recognition
import os
import numpy as np
from utils import presenca_aluno


def find_encodings(images):
    encode_list = []
    for img_index in range(0, len(images)):
        img = cv2.cvtColor(images[img_index], cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encode_list.append(encode)

    return encode_list


def inicia_reconhecimento():
    path = 'imagensAlunos'
    imagens = []
    classnames = []
    presentes = []
    minhaLista = os.listdir(path)
    for aluno in minhaLista:
        current_image = cv2.imread(f'{path}/{aluno}')
        imagens.append(current_image)
        classnames.append(os.path.splitext(aluno)[0])


    encode_list_known = find_encodings(imagens)
    print('Encoding Completo')

    cap = cv2.VideoCapture(0)

    while True:
        success, img = cap.read()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurrentFrame = face_recognition.face_locations(imgS)
        encodesCurrentFrame = face_recognition.face_encodings(imgS, facesCurrentFrame)

        for encodeFace, faceLoc in zip(encodesCurrentFrame, facesCurrentFrame):
            matches = face_recognition.compare_faces(encode_list_known, encodeFace, 0.5)
            face_distance = face_recognition.face_distance(encode_list_known, encodeFace)
            print(face_distance)
            matchIndex = np.argmin(face_distance)

            if matches[matchIndex]:
                name = str(classnames[matchIndex]).upper().strip()
                print(name)

                if name is not None and name != "" and name not in presentes:
                    presentes.append(name)
                    presenca_aluno(name)
                
            if (len(presentes) == len(imagens)):
                print('Todos os alunos estão presentes')
                break
        
        cv2.imshow('Webcam', img)
        key = cv2.waitKey(1)
        if key == ord('p'): 
            print(presentes)
        if key == ord('q') or key == ord('Q') or key == 27: # 27 == ESC
            cap.release()
            cv2.destroyAllWindows()
            break
