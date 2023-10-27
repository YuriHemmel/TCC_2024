import sqlite3

class Banco():
    
    def __init__(self):

        self.conexao = sqlite3.connect('banco.db')
        self.createTable()

    def createTable(self):

        cursor = self.conexao.cursor()

        # Tabela Aulas
        cursor.execute("""CREATE TABLE IF NOT EXISTS aulas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    dia TEXT NOT NULL,
                    hora TEXT NOT NULL,
                    turma_id INTEGER NOT NULL,
                    FOREIGN KEY (turma_id) REFERENCES turmas (id) ON UPDATE CASCADE ON DELETE CASCADE
                    )""")  

        # Tabela Cursos
        cursor.execute("""CREATE TABLE IF NOT EXISTS cursos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    duracao TEXT NOT NULL,
                    preco REAL NOT NULL
                    )""")  

        # Tabela Turmas
        cursor.execute("""CREATE TABLE IF NOT EXISTS turmas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    curso_id INTEGER NOT NULL,
                    data_inicio DATE NOT NULL,
                    FOREIGN KEY (curso_id) REFERENCES cursos (id) ON UPDATE CASCADE ON DELETE CASCADE
                    )""") 

        # Tabela pessoas
        cursor.execute("""CREATE TABLE IF NOT EXISTS alunos (
                    ra TEXT UNIQUE NOT NULL PRIMARY KEY,
                    nome TEXT,
                    email TEXT NOT NULL,
                    telefone TEXT NOT NULL,
                    sexo TEXT,
                    foto TEXT NOT NULL,
                    turma_id INTEGER NOT NULL,
                    faltas INTEGER NOT NULL,
                    presente BOOL NOT NULL,
                    FOREIGN KEY(turma_id) REFERENCES turmas(id) ON DELETE CASCADE
                    )""")
        
        # Tabela Câmeras
        cursor.execute("""CREATE TABLE IF NOT EXISTS cameras (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     nome TEXT NOT NULL,
                     ip TEXT UNIQUE NOT NULL,
                     usuario TEXT NOT NULL,
                     senha TEXT NOT NULL
                     )""")
        
        self.conexao.commit()
        cursor.close()

#Banco()