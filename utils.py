import os
import base64
import io
import cv2 as cv
import sqlite3
from datetime import *
from PIL import Image
import numpy 
from email_utils import envia_email_confirmando_presenca
from customtkinter import CTkImage

global dia_semana

# Dicionário correlacionando dias com números
dia_semana = {0: 'Segunda-feira', 1: 'Terça-feira',
              2: 'Quarta-feira', 3: 'Quinta-feira', 4: 'Sexta-feira', 5: 'Sábado'}


# --------------------------------- Métodos Imagens -------------------------------------------
# Tira foto por meio da Webcam
def tira_foto_binario():
    global bytes_foto

    print('Conectando com a camera...')
    cap = cv.VideoCapture(0)#, cv.CAP_FFMPEG)

    if cap.isOpened():
        validacao, frame = cap.read()
        while validacao:
            validacao, frame = cap.read()
            cv.imshow("Video da Webcam", frame)
            key = cv.waitKey(1)
            if key == ord('q') or key == ord('Q') or key == 27: # 27 == ESC
                break
        cv.imwrite("imagem.jpg", frame)
        bytes_foto = convertToBinaryData("imagem.jpg")
        os.remove("imagem.jpg")
    cap.release()
    cv.destroyAllWindows()
    return bytes_foto


# Codifica imagem em bytes
def convertToBinaryData(filename):
    file = open(filename, 'rb').read()
    bytes_foto = base64.b64encode(file)
    return bytes_foto

# Decodifica bytes em imagem
def convertToImage(bytes_foto):
    string = str(bytes_foto).strip("b'")[:-1]
    code_with_padding = f"{string}{'=' * (len(string) % 4)}"
    binary_data = base64.b64decode(code_with_padding)
    imagem = Image.open(io.BytesIO(binary_data))
    
    return imagem


def recupera_imagem_aluno(bytes_foto):
    string = str(bytes_foto).strip("b'")[:-1]
    code_with_padding = f"{string}{'=' * (len(string) % 4)}"
    binary_data = base64.b64decode(code_with_padding)
    img = numpy.fromstring(binary_data, numpy.uint8)
    return img


def mostra_video_camera(lista):

    nome = str(lista[1]).lower()
    
    if nome == "Webcam".lower():
        webcam = cv.VideoCapture(0)
    else:
        ip = lista[2]
        user = lista[3]
        password = lista[4]

        url = f"rtsp://{user}:{password}@{ip}:554/onvif1"

        webcam = cv.VideoCapture(url, cv.CAP_FFMPEG)

    if webcam.isOpened():
        validacao, frame = webcam.read()
        while validacao:
            validacao, frame = webcam.read()
            cv.imshow(f"Video da {lista[1]}", frame)
            key = cv.waitKey(1)
            if key == ord('q') or key == ord('Q') or key == 27: # ESC
                break
    webcam.release()
    cv.destroyAllWindows()

# Preenche a pasta imagensAlunos com fotos dos alunos que devem comparecer no dia
def adiciona_fotos_alunos(aulas_dia, dia):
    if aulas_dia == []:
        print("Não há aula para esse dia")
        return
    
    conexao = sqlite3.connect("banco.db")
    for aula in aulas_dia:
        print(aula[2])
    
        with conexao:
            cursor = conexao.cursor()

            cursor.execute(
                f"""
                     select al.ra, al.foto from alunos al left join aulas au on al.turma_id = au.turma_id 
                     where au.turma_id = "{aula[2]}" AND au.dia = "{dia_semana[dia]}"; 
                """
            )

            fotos = cursor.fetchall()
            path = 'imagensAlunos'
            for foto in fotos:
                ra = foto[0]

                # Adiciona os alunos na tabela de presença do dia
                cursor.execute(f"""INSERT INTO presenca (ra) VALUES ("{ra}") """)

                path_foto = f"{path}/{ra}.jpeg"
                print(path_foto)

                img = recupera_imagem_aluno(foto[1])
                img = cv.imdecode(img, cv.IMREAD_COLOR)
                cv.imwrite(path_foto, img)
#                aluno_foto = ImageTk.PhotoImage(aluno_foto)

# ============================== Funções de Tabelas =========================================
# --------------------------------- Tabela cursos -------------------------------------------

# Função criar cursos
def cria_curso(lista):
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()

        cursor.execute(
            f"""INSERT INTO cursos (nome, duracao) VALUES ("{lista[0]}", "{lista[1]}") """)

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
        cursor.execute(
            f"""UPDATE cursos SET nome="{lista[1]}", duracao="{lista[2]}" WHERE id="{lista[0]}" """)

# Deleta dados do cursos


def apaga_curso(id):
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""DELETE FROM cursos WHERE id="{id}" """)

# --------------------------------- Tabela turmas -------------------------------------------

# Função criar turma


def cria_turma(lista):
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()

        cursor.execute(
            f"""INSERT INTO turmas (nome, curso_id, data_inicio) VALUES ("{lista[0]}", "{lista[1]}", "{lista[2]}") """)

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
        cursor.execute(
            f"""UPDATE turmas SET nome="{lista[1]}", curso_id="{lista[2]}", data_inicio="{lista[3]}" WHERE id="{lista[0]}" """)

# Deleta dados do cursos


def apaga_turma(id):
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        # Apagando aulas associadas à essa turma
        cursor.execute(
            f"""DELETE FROM aulas WHERE turma_id = (SELECT nome FROM turmas WHERE id = "{id}")  """)
        # Apagando turma
        cursor.execute(f"""DELETE FROM turmas WHERE id="{id}" """)


# --------------------------------- Tabela aulas -------------------------------------------

# Função criar aula
def cria_aula(lista):
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()

        cursor.execute(f"""INSERT INTO aulas (nome, dia, hora, turma_id)
                            VALUES ("{lista[0]}", "{lista[1]}", "{lista[2]}", "{lista[3]}") """)

# Função criar aula
def cria_aula_id(lista):
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()

        cursor.execute(f"""INSERT INTO aulas (id, nome, dia, hora, turma_id)
                            VALUES ("{lista[0]}", "{lista[1]}", "{lista[2]}", "{lista[3]}", "{lista[4]}") """)


# Mostra as aulas


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


# Pesquisa dados da aula pelo nome
def pesquisa_aula(nome):
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""SELECT * FROM aulas
                       WHERE LOWER(nome) = "{nome}" """)

        results = cursor.fetchone()

    return results

# Atualiza dados da aula


def atualiza_aula(lista):
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""UPDATE aulas SET nome="{lista[1]}", dia="{lista[2]}", hora="{lista[3]}", turma_id="{lista[4]}"
                       WHERE id="{lista[0]}" """)

# Deleta dados da aula


def apaga_aula(id):
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""DELETE FROM aulas WHERE id="{id}" """)

# Verifica as aulas do dia
def verifica_aula_dia(dia):
    global dia_semana

    # Selecionando as aulas de hoje
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""SELECT id, hora, turma_id FROM aulas
                       WHERE dia = "{dia_semana[dia]}" """)
        results = cursor.fetchall()

    # Se não tiver aula hoje, retorna vazio
    # Se tiver, retorna o id, hora de início e id da turma
    return results

# Verifica qual a próxima aula
def tempo_para_aula(aulas):
    muito_antes = []
    antes = []
    durante = []
    depois = []
    muito_depois = []

    current = datetime.now()
    dia = current.strftime("%Y/%m/%d")

    # Se tiver aula hoje, vê se tem aula daqui a 40 min
    for aula in aulas:
        tempo = datetime.strptime(f"{dia} {aula[1]}", "%Y/%m/%d %H:%M")
        tempo_restante = tempo - current
        if tempo_restante > timedelta(minutes=40):
            muito_antes.append(aula)
        # Se faltar menos de 40 min pra aula, adiciona a turma à lista
        elif tempo_restante <= timedelta(minutes=40) and tempo_restante > timedelta(minutes=0):
            antes.append(aula)
        # Aula começou
        elif tempo_restante >= timedelta(minutes=-40) and tempo_restante < timedelta(minutes=0):
            durante.append(aula)
        # 40 minutos depois da aula
        elif tempo_restante < timedelta(minutes=-40) and tempo_restante >= timedelta(minutes=-80):
            depois.append(aula)
        elif tempo_restante < timedelta(minutes=-40) and tempo_restante >= timedelta(minutes=-80):
            muito_depois.append(aula)

    todas_aulas = {"muito_antes": muito_antes, "antes": antes, "durante": durante, "depois": depois, "muito_depois":muito_depois}

    return todas_aulas

#Verifica última aula criada
def ultima_aula_criada():
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()
        cursor.execute("""SELECT MAX(id) FROM aulas """)

        results = cursor.fetchone()

    return results[0]

# --------------------------------- Tabela faltas -------------------------------------------

# Função criar falta
def cria_falta(lista):
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()

        cursor.execute(f"""INSERT INTO faltas (ra, id_aula, falta)
                            VALUES ("{lista[0]}", "{lista[1]}", "{lista[2]}")""")
        cursor.close()

# Atualiza as faltas
def atualiza_falta(lista):
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()

        cursor.execute(f"""UPDATE faltas SET ra = "{lista[0]}"
                            WHERE ra = "{lista[1]}" """)
        cursor.close()

# Apaga faltas pelo ra do aluno
def apaga_falta_aluno(ra):
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""DELETE FROM faltas WHERE ra="{ra}" """)
        cursor.close()

# Apaga faltas pelo id da aula
def apaga_falta_aula(id_aula):
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""DELETE FROM faltas WHERE id_aula="{id_aula}" """)
        cursor.close()

# Mostra as faltas
def mostra_falta():
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()
        cursor.execute("""SELECT f.id, f.ra, al.nome, au.nome, tu.nome, f.falta FROM faltas f
                       JOIN alunos al ON al.ra = f.ra
                       JOIN aulas au ON au.id = f.id_aula
                       JOIN turmas tu ON tu.nome = au.turma_id
                       """)
        results = cursor.fetchall()
        cursor.close()

    return results

# Pesquisa as faltas pelo ra do aluno
def pesquisa_falta_aluno(ra):
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""SELECT f.id, f.ra, al.nome, au.nome, tu.nome, f.falta FROM faltas f
                       JOIN alunos al ON al.ra = f.ra
                       JOIN aulas au ON au.id = f.id_aula
                       JOIN turmas tu ON tu.nome = au.turma_id
                       WHERE UPPER(f.ra) = "{ra}"
                       """)

        results = cursor.fetchall()
        cursor.close()

    return results

# Retorna apenas os dados da falta via ra (Usado para o "Undo")
def mostra_falta_aluno(ra):
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""SELECT ra, id_aula, falta FROM faltas
                       WHERE UPPER(ra) = "{ra}"
                       """)

        results = cursor.fetchall()
        cursor.close()

    return results

# Retorna apenas os dados da falta via nome da aula (Usado para o "Undo")
def mostra_falta_aula(nome_aula):
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""SELECT f.ra, f.id_aula, f.falta FROM faltas f
                       JOIN aulas au ON au.id = f.id_aula
                       WHERE LOWER(au.nome) = "{nome_aula}"
                       """)

        results = cursor.fetchall()
        cursor.close()

    return results

# Pesquisa as faltas pelo nome da aula
def pesquisa_falta_aula(nome_aula):
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""SELECT f.id, f.ra, al.nome, au.nome, tu.nome, f.falta FROM faltas f
                       JOIN alunos al ON al.ra = f.ra
                       JOIN aulas au ON au.id = f.id_aula
                       JOIN turmas tu ON tu.nome = au.turma_id
                       WHERE LOWER(au.nome) = "{nome_aula}"
                       """)

        results = cursor.fetchall()
        cursor.close()

    return results


def reseta_presenca_dia():
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""UPDATE alunos SET
                        presente = 0
                        WHERE presente = 1
                        """)
        cursor.execute("""DELETE FROM presenca""")

    # Remove fotos da pasta imagensAlunos/
    path = 'imagensAlunos'
    imagens = os.listdir(path)

    if imagens != []:
        print('Limpando as imagens de alunos do dia')
    
        for imagem in imagens:
            os.remove(f'{path}/{imagem}')

# Computa as faltas no final do dia
def computa_falta(turma, dia):
    global dia_semana

    conexao = sqlite3.connect("banco.db")
    ra_alunos = []
    with conexao:
        append_alunos(turma, ra_alunos, conexao)
        
        for ra in ra_alunos:
            update_faltas(ra, dia, turma, conexao)

        cursor = conexao.cursor()
        
        cursor.execute("""DELETE FROM presenca""")

        cursor.close()

# Confere tempo de aula do aluno
def confere_presenca():
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()
    with conexao:

        cursor.execute("""SELECT * FROM presenca""")

        results = cursor.fetchall()

        for aluno in results:
            if aluno[3] == None:
                cursor.execute(f"""UPDATE alunos SET presente = 0 WHERE ra = '{aluno[1]}' """)
            else:
                entrada = datetime.strptime(f"{aluno[2]}", "%H:%M")
                saida = datetime.strptime(f"{aluno[3]}", "%H:%M")
                tempo_aula = saida - entrada
                if tempo_aula < timedelta(minutes=2):
                    cursor.execute(f"""UPDATE alunos SET presente = 0 WHERE ra = '{aluno[1]}' """)
                elif tempo_aula >= timedelta(minutes=2):
                    cursor.execute(f"""UPDATE alunos SET presente = 1 WHERE ra = '{aluno[1]}' """)

        cursor.close()

# Adiciona à lista ra_alunos cada aluno daquela turma
def append_alunos(turma, ra_alunos, conexao):
    cursor = conexao.cursor()

    with conexao:
        cursor.execute(f"""SELECT ra FROM alunos WHERE turma_id = "{turma}" AND presente = 0""")
        for elemento in (cursor.fetchall()):
            ra_alunos.append(elemento[0])
    
        cursor.close()

# Atualiza o quadro de faltas de cada aula
def update_faltas(ra, dia, turma, conexao):
    cursor = conexao.cursor()
    with conexao:
        cursor.execute(f"""SELECT f.id FROM faltas f
                       JOIN alunos al ON f.ra = al.ra
                       JOIN aulas au ON f.id_aula = au.id
                       WHERE al.turma_id = "{turma}" AND au.dia = "{dia_semana[dia]}" """)
        id = cursor.fetchall()
        for id_aula in id:
            cursor.execute(f"""UPDATE faltas SET falta = falta + 1 WHERE ra = "{ra}"
                                AND id = "{id_aula[0]}"
                                """)
    cursor.close()


# --------------------------------- Tabela alunos -------------------------------------------

# Função criar aluno
def cria_aluno(lista):
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()

        cursor.execute(f"""INSERT INTO alunos (ra, nome, email, telefone, sexo, foto, turma_id, presente)
                                       VALUES ("{lista[0]}", "{lista[1]}", "{lista[2]}", "{lista[3]}", "{lista[4]}", "{lista[5]}", "{lista[6]}", 0 ) """)

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

# Pesquisa os alunos com base na turma
def mostra_aluno_da_turma(turma):
    lista = []
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""SELECT * FROM alunos
                       WHERE turma_id = "{turma}" """)
        results = cursor.fetchall()

        for linha in results:
            lista.append(linha)

    return lista

# Pesquisa alunos pelo ra
def pesquisa_aluno(ra):
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""SELECT * FROM alunos
                       WHERE UPPER(ra) = "{ra}" """)

        results = cursor.fetchone()

    return results

# Atualiza dados do aluno
def atualiza_aluno(lista):
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""UPDATE alunos SET ra = "{lista[0]}", nome="{lista[1]}", email="{lista[2]}", telefone="{lista[3]}", sexo="{lista[4]}",
                       foto="{lista[5]}", turma_id="{lista[6]}" 
                       WHERE ra="{lista[7]}" """)

# Deleta dados do aluno
def apaga_aluno(ra):
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""DELETE FROM alunos WHERE ra="{ra}" """)

# Conta presença parar o aluno
def presenca_aluno(ra):

    h_entrada = hora_chegada(ra)

    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()
    with conexao:
        cursor.execute(f"""SELECT nome, email FROM alunos WHERE ra = "{ra}" """)
        results = cursor.fetchone()
        #cursor.execute(f"""UPDATE alunos SET presente = 1 WHERE ra = "{ra}" """)

    envia_email_confirmando_presenca(results[0], ra, results[1], h_entrada)

def hora_chegada(ra):
    
    hora = datetime.now().strftime("%H:%M")
    
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()
    with conexao:
        cursor.execute(f"""SELECT hora_entrada FROM presenca WHERE ra = "{ra}" """)
        results = cursor.fetchone()

        if results[0] == None:
            cursor.execute(f"""UPDATE presenca SET hora_entrada = "{hora}" WHERE ra = "{ra}" """)
        elif results[0] != None:
            cursor.execute(f"""UPDATE presenca SET hora_saida = "{hora}" WHERE ra = "{ra}" """)

    return hora

# Verifica os alunos que não chegaram na aula, por meio da turma
def alunos_para_avisar(turma):

    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f""" SELECT ra, nome, email FROM alunos
                            WHERE turma_id = "{turma}" 
                            AND presente = 0
                        """)

        results = cursor.fetchall()

    return results


# --------------------------------- Tabela cameras -------------------------------------------

# Função criar camera


def cria_camera(lista):
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()

        cursor.execute(
            f"""INSERT INTO cameras (nome, ip, usuario, senha) VALUES ("{lista[0]}", "{lista[1]}", "{lista[2]}", "{lista[3]}") """)

# Mostra as cameras


def mostra_camera():
    lista = []
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()
        cursor.execute("""SELECT id, nome, ip, usuario, senha FROM cameras""")
        results = cursor.fetchall()

        for linha in results:
            lista.append(linha)

    return lista

# Atualiza dados do cursos


def atualiza_camera(lista):
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(
            f"""UPDATE cameras SET nome="{lista[1]}", ip="{lista[2]}", usuario="{lista[3]}", senha="{lista[4]}"  WHERE id="{lista[0]}" """)

# Deleta dados do cursos


def apaga_camera(id):
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""DELETE FROM cameras WHERE id="{id}" """)

# Pesquisa a câmera pelo ip
def pesquisa_camera(ip):
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""SELECT id, nome, ip, usuario, senha FROM cameras
                       WHERE ip = "{ip}" """)

        results = cursor.fetchone()

    return results

# Pesquisa a câmera pelo id
def pesquisa_camera_id(id):
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""SELECT id, nome, ip, usuario, senha FROM cameras
                       WHERE id = "{id}" """)

        results = cursor.fetchone()

    return results
