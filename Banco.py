import sqlite3

class Banco():

    def __init__(self):
        self.conexao = sqlite3.connect('banco.db')
        self.createTable()

    def createTable(self):
        cursor = self.conexao.cursor()

        # Tabela pessoas
        cursor.execute("""create table if not exists pessoas (
                     ID text primary key unique not null,
                     nome text not null,
                     tel text unique not null,
                     entrada text not null,
                     saida text not null,
                     faltas int not null,
                     foto text not null)""")
        
        # Tabela Câmeras
        cursor.execute("""create table if not exists cameras (
                     idcamera integer primary key autoincrement unique not null,
                     nome text not null,
                     ip text unique not null,
                     senha text not null,
                     usuario text not null)""")
        
        self.conexao.commit()
        cursor.close()

#Banco()