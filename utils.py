import base64
import io
import cv2 as cv
import sqlite3
from PIL import Image


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


# TODO: consertar e adaptar ao novo banco
'''
def recebe_foto_binario():
    global bytes
    cam = Camera.load_camera("192.168.1.220")

    user = cam[4]
    password = cam[3]
    ip = cam[2]
    port = '554'

    url = f"rtsp://{user}:{password}@{ip}:{port}/onvif1"

    print('Tentando conectar com ' + url)

    cap = cv.VideoCapture(url, cv.CAP_FFMPEG)

    if cap.isOpened():
        validacao, frame = cap.read()
        while validacao:
            validacao, frame = cap.read()
            cv.imshow("VIDEO", frame)

            if cv.waitKey(1) == ord('q'):
                print("Desconectando da camera IP")
                break
        cv.imwrite("imagem.jpg", frame)
        bytes = convertToBinaryData("imagem.jpg")

    cap.release()
    cv.destroyAllWindows()
    return bytes
'''


def convertToBinaryData(filename):
    file = open(filename, 'rb').read()
    return base64.b64encode(file)


def convertToImage(bytes):
    binary_data = base64.b64decode(bytes)
    image = Image.open(io.BytesIO(binary_data))
    image.save('imagem_binario.jpg')

#============================== Funções de Tabelas ========================================= 

#--------------------------------- Tabela cursos -------------------------------------------

# Função criar cursos
def cria_curso(lista):
    conexao = sqlite3.connect("banco.db")
    
    with conexao:
        cursor = conexao.cursor()

        cursor.execute(f"""INSERT INTO cursos (nome, duracao, preco) VALUES ("{lista[0]}", "{lista[1]}", "{lista[2]}") """)

# Mostra os cursos
def mostra_curso():
    lista = []

    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()
    
    cursor.execute("""SELECT * FROM cursos""")

    results = cursor.fetchall()
    conexao.close()

    for row in results:
        lista.append(row)
    
    return lista

# Atualiza dados do cursos
def atualiza_curso(lista):
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""UPDATE cursos SET nome="{lista[1]}", duracao="{lista[2]}", preco="{lista[3]}" WHERE id="{lista[0]}" """)

# Deleta dados do cursos
def apaga_curso(id):
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""DELETE FROM cursos WHERE id="{id}" """)

#--------------------------------- Tabela turmas -------------------------------------------

# Função criar turma
def cria_turma(lista):
    conexao = sqlite3.connect("banco.db")
    
    with conexao:
        cursor = conexao.cursor()

        cursor.execute(f"""INSERT INTO turmas (nome, curso_id, data_inicio) VALUES ("{lista[0]}", "{lista[1]}", "{lista[2]}") """)

# Mostra as turmas
def mostra_turma():
    lista = []
    conexao = sqlite3.connect("banco.db")
    
    with conexao:
        cursor = conexao.cursor()
        cursor.execute("""SELECT * FROM turmas""")
        results = cursor.fetchall()

        for linha in results:
            lista.append(linha)
    
    return lista

# Atualiza dados do cursos
def atualiza_turma(lista):
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""UPDATE turmas SET nome="{lista[1]}", curso_id="{lista[2]}", data_inicio="{lista[3]}" WHERE id="{lista[0]}" """)

# Deleta dados do cursos
def apaga_turma(id):
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""DELETE FROM turmas WHERE id="{id}" """)

#--------------------------------- Tabela aulas -------------------------------------------

# Função criar aula
def cria_aula(lista):
    conexao = sqlite3.connect("banco.db")
    
    with conexao:
        cursor = conexao.cursor()

        cursor.execute(f"""INSERT INTO aulas (nome, dia, hora, turma_id)
                                    VALUES ("{lista[0]}", "{lista[1]}", "{lista[2]}", "{lista[3]}") """)

# Mostra os aulas
def mostra_aula():
    lista = []
    conexao = sqlite3.connect("banco.db")
    
    with conexao:
        cursor = conexao.cursor()
        cursor.execute("""SELECT * FROM aulas""")
        results = cursor.fetchall()

        for linha in results:
            lista.append(linha)
    
    return lista

def pesquisa_aula(nome):
    conexao = sqlite3.connect("banco.db")
    
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""SELECT * FROM aulas
                       WHERE nome = "{nome}" """)
        
        results = cursor.fetchone()
    
    return results

# Atualiza dados do cursos
def atualiza_aula(lista):
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""UPDATE aulas SET nome="{lista[1]}", dia="{lista[2]}", hora="{lista[3]}", turma_id="{lista[4]}"
                       WHERE id="{lista[0]}" """)

# Deleta dados do cursos
def apaga_aula(id):
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""DELETE FROM aulas WHERE id="{id}" """)

#--------------------------------- Tabela alunos -------------------------------------------

# Função criar aluno
def cria_aluno(lista):
    conexao = sqlite3.connect("banco.db")
    
    with conexao:
        cursor = conexao.cursor()

        cursor.execute(f"""INSERT INTO alunos (ra, nome, email, telefone, sexo, foto, turma_id, faltas, presente)
                                       VALUES ("{lista[0]}", "{lista[1]}", "{lista[2]}", "{lista[3]}", "{lista[4]}", "{lista[5]}", "{lista[6]}", 0, 0 ) """)

# Mostra os alunos
def mostra_aluno():
    lista = []
    conexao = sqlite3.connect("banco.db")
    
    with conexao:
        cursor = conexao.cursor()
        cursor.execute("""SELECT * FROM alunos""")
        results = cursor.fetchall()

        for linha in results:
            lista.append(linha)
    
    return lista

def pesquisa_aluno(ra):
    conexao = sqlite3.connect("banco.db")
    
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""SELECT * FROM alunos
                       WHERE ra = "{ra}" """)
        
        results = cursor.fetchone()
    
    return results

# Atualiza dados do cursos
def atualiza_aluno(lista):
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""UPDATE alunos SET ra = "{lista[0]}", nome="{lista[1]}", email="{lista[2]}", telefone="{lista[3]}", sexo="{lista[4]}",
                       foto="{lista[5]}", turma_id="{lista[6]}", faltas="{lista[7]}" 
                       WHERE ra="{lista[8]}" """)

# Deleta dados do cursos
def apaga_aluno(ra):
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""DELETE FROM alunos WHERE ra="{ra}" """)

# Conta presença parar o aluno
def presenca_aluno(ra):
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()

        cursor.execute(f"""UPDATE alunos SET presente = 1
                        WHERE ra = "{ra}"
                        """)

def computa_falta():
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()

        cursor.execute(f"""UPDATE alunos SET
                        faltas = faltas + 1
                        WHERE presente = 0
                        """)
        
        cursor.execute(f"""UPDATE alunos SET
                        presente = 0
                        WHERE presente = 1
                        """)

def verifica_chegada_aluno():

    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()

        cursor.execute(f"""
        SELECT ra, nome, email FROM alunos
        WHERE presente = 0
                        """)
        
        results = cursor.fetchall()

    return results

#--------------------------------- Tabela cameras -------------------------------------------

# Função criar camera
def cria_camera(lista):
    conexao = sqlite3.connect("banco.db")
    
    with conexao:
        cursor = conexao.cursor()

        cursor.execute(f"""INSERT INTO cameras (nome, ip, usuario, senha) VALUES ("{lista[0]}", "{lista[1]}", "{lista[2]}", "{lista[3]}") """)

# Mostra as cameras
def mostra_camera():
    lista = []
    conexao = sqlite3.connect("banco.db")
    
    with conexao:
        cursor = conexao.cursor()
        cursor.execute("""SELECT id, nome, ip, usuario FROM cameras""")
        results = cursor.fetchall()

        for linha in results:
            lista.append(linha)
    
    return lista

# Atualiza dados do cursos
def atualiza_camera(lista):
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""UPDATE cameras SET nome="{lista[1]}", ip="{lista[2]}", usuario="{lista[3]}"  WHERE id="{lista[0]}" """)

# Deleta dados do cursos
def apaga_camera(id):
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""DELETE FROM cameras WHERE id="{id}" """)

def pesquisa_camera(ip):
    conexao = sqlite3.connect("banco.db")
    
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""SELECT id, nome, ip, usuario FROM cameras
                       WHERE ip = "{ip}" """)
        
        results = cursor.fetchone()
    
    return results