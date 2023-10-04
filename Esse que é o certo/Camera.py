from Banco import Banco
import sqlite3


class Camera(object):

    def __init__(self, nome, ip, senha, usuario):
        self.info = {}
        self.nome = nome
        self.ip = ip
        self.senha = senha
        self.usuario = usuario
        self.banco = Banco()
        self.conexao = sqlite3.connect("banco.db")
        self.cursor = self.conexao.cursor()

    def insert_camera(self):
        self.cursor.execute(f"""
        INSERT INTO cameras(nome, ip, senha, usuario) VALUES
        ("{self.nome}", "{self.ip}", "{self.senha}", "{self.usuario}")
        """)

        self.conexao.commit()
        self.conexao.close()

def load_camera(ip, info):
        
        conexao = sqlite3.connect("banco.db")
        cursor = conexao.cursor()

        cursor.execute(f"""
        SELECT * FROM cameras
        WHERE ip like "{ip}"
        """)


        results = cursor.fetchone()
        conexao.close()

        #results[0] = id
        #results[1] = nome
        #results[2] = ip
        #results[3] = senha
        #results[4] = usuario

        return results[info]

def load_camera(ip):
        
        conexao = sqlite3.connect("banco.db")
        cursor = conexao.cursor()

        cursor.execute(f"""
        SELECT * FROM cameras
        WHERE ip like "{ip}"
        """)


        results = cursor.fetchone()
        conexao.close()

        #results[0] = id
        #results[1] = nome
        #results[2] = ip
        #results[3] = senha
        #results[4] = usuario

        return results

def conta_camera():
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT COUNT(idcamera) FROM cameras
    """)

    results = cursor.fetchone()
    if results[0] == 0:
         conexao.close()
         return 0
    else:
        cursor.execute("""
        SELECT MAX(idcamera) FROM cameras
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