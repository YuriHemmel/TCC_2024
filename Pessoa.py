from Banco import Banco
import sqlite3

class Pessoa(object):

    def __init__(self, ID="", nome="", tel="", entrada="", saida="", faltas=0, foto=""):
        self.info = {}
        self.ID = ID
        self.nome = nome
        self.tel = tel
        self.entrada = entrada
        self.saida = saida
        self.faltas = faltas
        self.foto = foto
        self.banco = Banco()
        self.conexao = sqlite3.connect("banco.db")
        self.cursor = self.conexao.cursor()

    def load_pessoa(self, ID):
        self.cursor.execute(f"""
        SELECT * FROM pessoas
        WHERE ID like "{ID}"
        """)

        results = self.cursor.fetchone()

        self.ID = ID
        self.nome = results[1]
        self.tel = results[2]
        self.entrada = results[3]
        self.saida = results[4]
        self.faltas = results[5]
        self.foto = results[6]

    def insert_pessoa(self):

        self.cursor.execute(f"""
        INSERT INTO pessoas VALUES
        ("{self.ID}", "{self.nome}", "{self.tel}", "{self.entrada}", "{self.saida}", "{self.faltas}", "{self.foto}")
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

def seleciona_pessoa(ID):
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute(f"""
    SELECT * FROM pessoas
    WHERE ID like "{ID}"
    """)

    results = cursor.fetchone()
    conexao.close()

    return results