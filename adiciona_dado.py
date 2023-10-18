import sqlite3
import Banco

Banco.Banco()

conexao = sqlite3.connect('banco.db')

cursor = conexao.cursor()

cursor.execute("""INSERT INTO cursos (nome, diaAula, horaEntrada) VALUES ('Ciência da computação', 'qui-sex', '19:10')""")
cursor.execute("""INSERT INTO cursos (nome, diaAula, horaEntrada) VALUES ('Engenharia', 'qui-sex', '19:10')""")

conexao.commit()
conexao.close()
