import os
from PIL import Image
import base64
import io
import cv2 as cv
import sqlite3


def tira_foto():
    webcam = cv.VideoCapture(0)

    if webcam.isOpened():
        validacao, frame = webcam.read()
        while validacao:
            validacao, frame = webcam.read()
            cv.imshow("Video da Webcam", frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
        cv.imwrite("imagem_atual.jpg", frame)
    webcam.release()
    cv.destroyAllWindows()


def recebe_foto_binario():
    global bytes
    webcam = cv.VideoCapture(0)

    if webcam.isOpened():
        validacao, frame = webcam.read()
        while validacao:
            validacao, frame = webcam.read()
            cv.imshow("Video da Webcam", frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
        cv.imwrite("imagem.jpg", frame)
        bytes = convertToBinaryData("imagem.jpg")
    webcam.release()
    cv.destroyAllWindows()
    os.remove("imagem.jpg")
    return bytes


def convertToBinaryData(filename):
    file = open(filename, 'rb').read()
    return base64.b64encode(file)


def convertToImage(bytes):
    binary_data = base64.b64decode(bytes)
    image = Image.open(io.BytesIO(binary_data))
    image.save('imagem_binario.jpg')


def listar_cursos():
    lista_cursos = []

    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute("""SELECT nome FROM cursos""")

    results = cursor.fetchall()
    conexao.close()

    for c in results:
        curso = ""
        for l in c:
            curso = curso + l
        lista_cursos.append(curso)

    return lista_cursos