import sqlite3

class Banco():

    def __init__(self):
        self.conexao = sqlite3.connect('banco.db')
        self.createTable()

    def createTable(self):
        cursor = self.conexao.cursor()

        # Tabela pessoas
        cursor.execute("""create table if not exists pessoas (
                     ra text primary key unique not null,
                     nome text not null,
                     tel text unique not null,
                     email text unique not null,
                     foto text not null)""")
        
        # Tabela Câmeras
        cursor.execute("""create table if not exists cameras (
                     idcamera integer primary key autoincrement unique not null,
                     nome text not null,
                     ip text unique not null,
                     senha text not null,
                     usuario text not null)""")
        
        # Tabela Cursos
        cursor.execute("""create table if not exists cursos (
                       idcurso integer primary key autoincrement unique not null,
                       nome text not null,
                       lista_materias text not null)""")

#        cursor.execute("""INSERT INTO cursos (nome, lista_materias)
#                       VALUES ("Ciência da computação", "QS, DSD")""")

        # Tabela Matérias
        cursor.execute("""create table if not exists materias (
                       idmateria text primary key unique not null,
                       nome text not null,
                       dia_semana text not null,
                       horario text not null)""")
        
#        cursor.execute("""INSERT INTO materias (idmateria, nome, dia_semana, horario)
#                          VALUES ("QS", "Qualidade de software", "quinta", "19:10")
#                       """)
    
#        cursor.execute("""INSERT INTO materias (idmateria, nome, dia_semana, horario)
#                          VALUES ("DSD", "Desenvolvimento de Sistemas Distribuídos", "sexta", "19:10")
#                       """)

        # Tabela Faltas
        cursor.execute("""create table if not exists faltas (
                       id_falta integer primary key autoincrement unique not null,
                       id_aluno text not null,
                       id_materia text not null,
                       num_faltas integer)""")
        
        self.conexao.commit()
        cursor.close()
