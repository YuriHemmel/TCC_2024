from Banco import Banco
import sqlite3

class Pessoa(object):

    def __init__(self, ra="", nome="", tel="", email="", foto=""):
        self.info = {}
        self.ra = ra
        self.nome = nome
        self.tel = tel
        self.email = email
        self.foto = foto
        self.banco = Banco()
        self.conexao = sqlite3.connect("banco.db")
        self.cursor = self.conexao.cursor()

    def load_pessoa(self, ra):
        self.cursor.execute(f"""
        SELECT * FROM pessoas
        WHERE ra like "{ra}"
        """)

        results = self.cursor.fetchone()

        self.ra = ra
        self.nome = results[1]
        self.tel = results[2]
        self.email = results[3]

    def insert_pessoa(self):
        self.cursor.execute(f"""
        INSERT INTO pessoas VALUES
        ("{self.ra}", "{self.nome}", "{self.tel}", "{self.email}", "{self.foto}")
        """)

        self.conexao.commit()
        self.conexao.close()
