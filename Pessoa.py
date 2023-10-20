from Banco import Banco
import sqlite3

class Pessoa(object):

    def __init__(self, ID="", nome="", tel="", faltas=0, foto="", CursoID = 0, presente = 0):
        self.info = {}
        self.ID = ID
        self.nome = nome
        self.tel = tel
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
        ("{self.ID}", "{self.nome}", "{self.tel}","{self.faltas}", "{self.foto}", "{self.CursoID}", "{self.presente}")
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

def altera_dados(ID, nome, tel, faltas, CursoID):
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute(f"""
    UPDATE pessoas SET
    nome = "{nome}",
    tel = "{tel}",
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
    WHERE presente = 0
                    """)
    
    results = cursor.fetchall()
    conexao.close()

    return results

def load_pessoa(ID, dado):
    num_elemento = 0

    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    # pessoa[0] = ID
    # pessoa[1] = Nome
    # pessoa[2] = Telefone
    # pessoa[3] = faltas
    # pessoa[4] = foto
    # pessoa[5] = id do curso
    # pessoa[6] = presença no dia

    cursor.execute(f"""
    SELECT * FROM pessoas
    WHERE ID like "{ID}"
    """)

    results = cursor.fetchone()
    conexao.close()

    if dado == "nome":
        num_elemento = 1
    elif dado == "tel":
        num_elemento = 2
    elif dado == "faltas":
        num_elemento = 3
    elif dado == "foto":
        num_elemento = 4
    elif dado == "CursoID":
        num_elemento = 5
    else:
        num_elemento = 6

    return results[num_elemento]