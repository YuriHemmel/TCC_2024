import sqlite3

class Banco():
    
    def __init__(self):

        self.conexao = sqlite3.connect('banco.db')
        self.createTable()

    def createTable(self):

        cursor = self.conexao.cursor()

        # Tabela Cursos
        cursor.execute("""create table if not exists cursos (
                     CursoID INTEGER PRIMARY KEY AUTOINCREMENT,
                     nome text not null,
                     diaAula text not null,
                     horaEntrada text not null
                     )""")  

        # Tabela pessoas
        cursor.execute("""create table if not exists pessoas (
                     ID text unique not null PRIMARY KEY,
                     nome text not null,
                     email text unique not null,
                     faltas int not null,
                     foto text not null,
                     CursoID int not null,
                     presente bool not null,
                     FOREIGN KEY(CursoID) REFERENCES cursos(CursoID))""")
        
        # Tabela Câmeras
        cursor.execute("""create table if not exists cameras (
                     idcamera INTEGER PRIMARY KEY AUTOINCREMENT,
                     nome text not null,
                     ip text unique not null,
                     senha text not null,
                     usuario text not null)""")
        
        self.conexao.commit()
        cursor.close()

#Banco()