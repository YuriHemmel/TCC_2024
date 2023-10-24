import os
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

    for curso in results:
        nome_curso = ""
        for letra in curso:
            nome_curso = nome_curso + letra
        lista_cursos.append(nome_curso)

    return lista_cursos

# Retorna id do curso cadastrado
def retorna_curso_id(nome_curso):
    
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute(f"""SELECT CursoID FROM cursos
                    WHERE nome like "{nome_curso}" """)

    results = cursor.fetchone()
    conexao.close()

    return results[0]

def retorna_curso_nome(curso_id):
    
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute(f"""SELECT nome FROM cursos
                    WHERE CursoID like "{curso_id}" """)

    results = cursor.fetchone()
    conexao.close()

    return results[0]

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