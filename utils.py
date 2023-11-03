import os
import base64
import io
import cv2 as cv
import sqlite3
from datetime import *
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
    return image
#============================== Funções de Tabelas ========================================= 

def verifica_quem_recebe_email(lista):
    conexao = sqlite3.connect("banco.db")
    
    with conexao:
        cursor = conexao.cursor()

        cursor.execute(f"""SELECT ra, al.nome, email, au.hora FROM alunos al JOIN aulas au
                        ON al.turma_id = au.turma_id WHERE presente = 0
                        """)
        results = cursor.fetchall()
    
    return results

# Verifica qual a próxima aula
def verifica_aula_do_dia():

    # Dicionário correlacionando dias com números
    dia_semana = {0:'Segunda-feira', 1:'Terça-feira', 2:'Quarta-feira', 3:'Quinta-feira', 4:'Sexta-feira'}

    # Dia e hora atuais
    current = datetime.now()
    current_day = int(current.strftime("%w")) - 1
    current_time = current.strftime("%Y/%m/%d")

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


def tempo_para_aula(results):
    lista = []

    current = datetime.now()
    current_time = current.strftime("%Y/%m/%d")
    
    # Se tiver aula hoje, vê se tem aula daqui a 30 min
    for aula in results:
        tempo = datetime.strptime(f"{current_time} {aula[1]}","%Y/%m/%d %H:%M")
        proximo = tempo - current
        # Se faltar menos de 30 min pra aula, adiciona o id da turma à lista
        if proximo <= timedelta(minutes=30):
            lista.append(aula[2])
    
    return lista

# Verifica qual a próxima aula
def retorna_hora_aula():

    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""SELECT id, hora FROM aulas""")
        results = cursor.fetchall()

    return results
        


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
        # Apagando aulas associadas à essa turma
        cursor.execute(f"""DELETE FROM aulas WHERE turma_id = (SELECT nome FROM turmas WHERE id = "{id}")  """)
        # Apagando turma
        cursor.execute(f"""DELETE FROM turmas WHERE id="{id}" """)


#--------------------------------- Tabela aulas -------------------------------------------

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

def ultima_aula_adicionada():
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(""" SELECT MAX(id) FROM aulas """)

        results = cursor.fetchone

    return results
#--------------------------------- Tabela faltas -------------------------------------------

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
        cursor.execute(f"""SELECT f.id, f.ra, al.nome, tu.nome, au.nome, f.falta FROM faltas f
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
        cursor.execute(f"""SELECT f.id, f.ra, al.nome, tu.nome, au.nome, f.falta FROM faltas f
                       JOIN alunos al ON al.ra = f.ra
                       JOIN aulas au ON au.id = f.id_aula
                       JOIN turmas tu ON tu.nome = au.turma_id
                       WHERE LOWER(au.nome) = "{nome_aula}"
                       """)
        
        results = cursor.fetchall()
        cursor.close()     
        
    return results

#--------------------------------- Tabela alunos -------------------------------------------

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

# Atualiza dados do cursos
def atualiza_aluno(lista):
    conexao = sqlite3.connect("banco.db")
    with conexao:
        cursor = conexao.cursor()
        cursor.execute(f"""UPDATE alunos SET ra = "{lista[0]}", nome="{lista[1]}", email="{lista[2]}", telefone="{lista[3]}", sexo="{lista[4]}",
                       foto="{lista[5]}", turma_id="{lista[6]}" 
                       WHERE ra="{lista[7]}" """)

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

def verifica_nao_chegada_aluno():

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