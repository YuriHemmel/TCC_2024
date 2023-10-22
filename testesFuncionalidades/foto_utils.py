import io
import base64
from PIL import Image


def normaliza_fotos_da_matriz(matriz):
    for pessoa in matriz:
        
        binary_data = base64.b64decode(pessoa[0])
        image = Image.open(io.BytesIO(binary_data))
        image.save(f'.tmp/{pessoa[1]}.jpg')

