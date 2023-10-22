from Banco import Banco
import sqlite3

class Pessoa(object):

    def __init__(self, ID="", nome="", email="", faltas=0, foto="", CursoID = 0, presente = 0):
        self.info = {}
        self.ID = ID
        self.nome = nome
        self.email = email
        self.faltas = faltas
        self.foto = foto
        self.CursoID = CursoID
        self.presente = presente
        self.banco = Banco()
        self.conexao = sqlite3.connect("banco.db")
        self.cursor = self.conexao.cursor()

    def insert_pessoa(self):

        self.cursor.execute(f"""
        INSERT INTO pessoas VALUES
        ("{self.ID}", "{self.nome}", "{self.email}","{self.faltas}", "{self.foto}", "{self.CursoID}", "{self.presente}")
        """)

        self.conexao.commit()
        self.conexao.close()

def list_pessoa():
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT * FROM pessoas
    """)

    results = cursor.fetchall()
    conexao.close()

    return results

def conta_pessoa():
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT COUNT(ID) FROM pessoas
    """)

    results = cursor.fetchone()
    conexao.close()

    return results[0]

def delete_pessoa(ID):
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute(f"""
    DELETE FROM pessoas
    WHERE ID like "{ID}"
    """)

    conexao.commit()
    conexao.close()

def load_pessoa(ID):
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute(f"""
    SELECT * FROM pessoas
    WHERE ID like "{ID}"
    """)

    results = cursor.fetchone()
    conexao.close()

    return results

def altera_dados(ID, nome, email, faltas, CursoID):
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute(f"""
    UPDATE pessoas SET
    nome = "{nome}",
    email = "{email}",
    faltas = "{faltas}",
    CursoID = "{CursoID}"
    WHERE ID like "{ID}"
    """)

    conexao.commit()
    conexao.close()

def verifica_chegada():

    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute(f"""
    SELECT ID FROM pessoas
    WHERE presente = false
                    """)
    
    results = cursor.fetchall()
    conexao.close()
    
    return results

def recebe_email_por_ID(ID):    
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    # pessoa[0] = ID
    # pessoa[1] = Nome
    # pessoa[2] = Email
    # pessoa[3] = faltas
    # pessoa[4] = foto
    # pessoa[5] = id do curso
    # pessoa[6] = presença no dia

    cursor.execute(f"""
    SELECT email FROM pessoas
    WHERE ID = "{ID}"
    """)

    result = cursor.fetchone()
    conexao.close()

    return result[0]


def recebe_nome_por_ID(ID):    
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    # pessoa[0] = ID
    # pessoa[1] = Nome
    # pessoa[2] = Email
    # pessoa[3] = faltas
    # pessoa[4] = foto
    # pessoa[5] = id do curso
    # pessoa[6] = presença no dia

    cursor.execute(f"""
    SELECT nome FROM pessoas
    WHERE ID = "{ID}"
    """)

    result = cursor.fetchone()
    conexao.close()

    return result[0]
