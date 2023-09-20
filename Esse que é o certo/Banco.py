import sqlite3

class Banco():

    def __init__(self):
        self.conexao = sqlite3.connect('banco.db')
        self.createTable()

    def createTable(self):
        cursor = self.conexao.cursor()

        cursor.execute("""create table if not exists pessoas (
                     ra text primary key unique not null,
                     nome text not null,
                     tel text unique not null,
                     email text unique not null,
                     foto text not null)""")
        
        cursor.execute("""create table if not exists cameras (
                     idcamera integer primary key unique not null,
                     nome text not null,
                     ip text unique not null,
                     senha text not null)""")
        
        #cursor.execute("""
        #            INSERT INTO pessoas values
        #            ("F22HFA-7", "Yuri Hemmel Modolin", "+55(11)91107-2205",
        #            "amodolin@gmail.com", "AAAAAAAAAA")
        #            """)

        #cursor.execute("""
                    #DELETE FROM cameras
                    #""")

        #cursor.execute("""
                    #DELETE FROM pessoas
                    #""")
        
        self.conexao.commit()
        cursor.close()