import cv2
import face_recognition
import os
import numpy as np

path = 'imagensAlunos'
imagens = []
classnames = []
minhaLista = os.listdir(path)
print(minhaLista)

for aluno in minhaLista:
    current_image = cv2.imread(f'{path}/{aluno}')
    imagens.append(current_image)
    classnames.append(os.path.splitext(aluno)[0])

print(classnames)

def find_encodings(images):
    encode_list = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encode_list.append(encode)

    return encode_list

encode_list_known = find_encodings(imagens)
print('Encoding Complete')

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurrentFrame = face_recognition.face_locations(imgS)
    encodesCurrentFrame = face_recognition.face_encodings(imgS, facesCurrentFrame)

    for encodeFace, faceLoc in zip(encodesCurrentFrame, facesCurrentFrame):
        matches = face_recognition.compare_faces(encode_list_known, encodeFace)
        face_distance = face_recognition.face_distance(encode_list_known, encodeFace)
        print(face_distance)
        matchIndex = np.argmin(face_distance)

        if matches[matchIndex]:
            name = classnames[matchIndex].upper()
            print(name)
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4  
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 + 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

    
    cv2.imshow('Webcam', img)
    cv2.waitKey(1)