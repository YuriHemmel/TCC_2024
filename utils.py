import base64
import io
import cv2 as cv
import sqlite3
from datetime import *
from PIL import Image

global dia_semana

# Dicionário correlacionando dias com números
dia_semana = {0: 'Segunda-feira', 1: 'Terça-feira',
              2: 'Quarta-feira', 3: 'Quinta-feira', 4: 'Sexta-feira', 5: 'Sábado'}

# Tira foto por meio da Webcam
def tira_foto_binario():
    global bytes
    #cam = Camera.load_camera("192.168.1.220")

    user = "admin"
    password = "arifym2023"
    ip = "192.168.1.220"
    port = '554'

    url = f"rtsp://{user}:{password}@{ip}:{port}/onvif1"

    print('Tentando conectar com ' + url)

    cap = cv.VideoCapture(url, cv.CAP_FFMPEG)

    if cap.isOpened():
        validacao, frame = cap.read()
        while validacao:
            cv.imshow("Video da Webcam", frame)
            if cv.waitKey(1) == ord('q') or cv.waitKey(1) == ord('Q') or cv.waitKey(1) == 27:
                break
        cv.imwrite("imagem.jpg", frame)
        
    cap.release()
    cv.destroyAllWindows()
    return bytes
'''

# Codifica imagem em bytes
def convertToBinaryData(filename):
    file = open(filename, 'rb').read()
    bytes = base64.b64encode(file)
    return bytes

# Decodifica bytes em imagem
def convertToImage(bytes):
    string = str(bytes).strip("b'")
    binary_data = base64.b64decode(string)
    imagem = Image.open(io.BytesIO(binary_data))

    return imagem
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
                       WHERE UPPER(nome) = "{nome}" """)

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
def verifica_aula_dia():
    global dia_semana
    # Dia e hora atuais
    current = datetime.now()
    current_day = current.weekday()

    # Selecionando as aulas de hoje
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""SELECT id, hora, turma_id FROM aulas
                       WHERE dia = "{dia_semana[current_day]}" """)
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

    current = datetime.now()
    dia = current.strftime("%Y/%m/%d")

    # Se tiver aula hoje, vê se tem aula daqui a 30 min
    for aula in aulas:
        tempo = datetime.strptime(f"{dia} {aula[1]}", "%Y/%m/%d %H:%M")
        tempo_restante = tempo - current
        if tempo_restante > timedelta(minutes=40):
            muito_antes.append(aula)
        # Se faltar menos de 40 min pra aula, adiciona a turma à lista
        elif tempo_restante <= timedelta(minutes=40) and tempo_restante > timedelta(minutes=0):
            antes.append(aula)
        # Aula começou
        elif tempo_restante >= timedelta(minutes=-40):
            durante.append(aula)
        # 40 minutos depois da aula
        elif tempo_restante < timedelta(minutes=-40):
            depois.append(aula)

    todas_aulas = {"muito_antes": muito_antes, "antes": antes, "durante": durante, "depois": depois}

    return todas_aulas


# --------------------------------- Tabela faltas -------------------------------------------

# Função criar falta


def cria_falta(lista):
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()

        cursor.execute(f"""INSERT INTO faltas (ra, id_aula, falta)
                            VALUES ("{lista[0]}", "{lista[1]}", 0)""")
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


def computa_falta(turma, dia):
    global dia_semana
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()

        cursor.execute(f"""UPDATE faltas SET
                        falta = falta + 1
                        WHERE ra = (SELECT ra FROM alunos WHERE turma_id in {turma} AND presente = 0)
                        AND id_aula = (SELECT id FROM aulas WHERE dia = "{dia_semana[dia]}")
                        """)

        cursor.execute(f"""UPDATE alunos SET
                        presente = 0
                        WHERE presente = 1
                        """)

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
    conexao = sqlite3.connect("banco.db")

    with conexao:
        cursor = conexao.cursor()

        cursor.execute(f"""UPDATE alunos SET presente = 1
                        WHERE ra = "{ra}"
                        """)

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
        cursor.execute(
            f"""UPDATE cameras SET nome="{lista[1]}", ip="{lista[2]}", usuario="{lista[3]}"  WHERE id="{lista[0]}" """)

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
