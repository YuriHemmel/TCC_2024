import face_recognition
import Pessoa
import foto_utils


def reconhece_rosto(rosto):
    reconhecido = False
    # rosto = face_recognition.load_image_file(url_rosto)
    rostos = face_recognition.face_encodings(rosto)

    if (len(rostos) > 0):
        reconhecido = True
    
    return reconhecido, rostos


def recebe_rostos():
    rostos_conhecidos = []
    id_rostos = []
    pessoas = foto_utils.normaliza_fotos_da_matriz(Pessoa.recebe_fotos_e_ids_do_banco())

    for foto, id in pessoas:
        foto_normalizada = decode_foto(foto)
        if (reconhece_rosto(foto_normalizada)[0]):
            rostos_conhecidos.append(foto[1][0])
            id_rostos.append(id)

    return rostos_conhecidos, id_rostos

