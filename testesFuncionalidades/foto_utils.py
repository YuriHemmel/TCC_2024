import io
import base64
from PIL import Image


def normaliza_fotos_da_matriz(matriz):
    for aluno in matriz:
        binary_data = base64.b64decode(aluno[0])
        image = Image.open(io.BytesIO(binary_data))
        image.save(f'.tmp/{aluno[1]}.jpg')

