from Banco import Banco
import sqlite3


class Camera(object):

    def __init__(self, idcamera, nome, ip, senha):
        self.info = {}
        self.idcamera = idcamera
        self.nome = nome
        self.ip = ip
        self.senha = senha
        self.banco = Banco()
        self.conexao = sqlite3.connect("banco.db")
        self.cursor = self.conexao.cursor()

    def insert_camera(self):
        self.cursor.execute(f"""
        INSERT INTO cameras VALUES
        ({self.idcamera}, "{self.nome}", "{self.ip}", "{self.senha}")
        """)

        self.conexao.commit()
        self.conexao.close()

def load_camera(nome, info):
        
        conexao = sqlite3.connect("banco.db")
        cursor = conexao.cursor()

        cursor.execute(f"""
        SELECT * FROM cameras
        WHERE nome like "{nome}"
        """)


        results = cursor.fetchone()
        conexao.close()

        #results[0] = id
        #results[1] = nome
        #results[2] = ip
        #results[3] = senha

        return results[info]
        

        

def conta_camera():
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT COUNT(idcamera) FROM cameras
    """)

    results = cursor.fetchone()
    conexao.close()

    return results[0]


def list_camera():
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT * FROM cameras
    """)

    results = cursor.fetchall()
    conexao.close()

    return results

def delete_camera(nome):
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute(f"""
    DELETE FROM cameras
    WHERE nome like "{nome}"
    """)

    conexao.commit()
    conexao.close()

#delete_camera("Camera1")