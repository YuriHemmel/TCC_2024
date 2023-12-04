import utils
import Banco
import schedule
import os
import concurrent.futures
from dotenv import load_dotenv
from tkinter import *  # Interface gráfica
from tkinter import messagebox  # Caixa de mensagem para confirmações
from tkinter import ttk
from tkinter import filedialog as fd
from tkcalendar import DateEntry
from tktimepicker import SpinTimePickerModern
from tktimepicker import constants
from datetime import *
from email_utils import envia_email_alerta, envia_email_acusando_falta, envia_email_aula_comeca
from PIL import Image, ImageTk
from reconhecedor_rostos import inicia_reconhecimento

# Tamanho da janela
WIDTH = 850
HEIGHT = 620

# Cores
AZUL_CLARO = "#71BAFF"
AZUL_ESCURO = "#1C85FF"
PRETO = "#000000"
BRANCO = "#FFFFFF"
VERDE = "#68C177"
VERMELHO = "#FF373E"

# Lê as variáveis de ambiente presentes no arquivo .env
load_dotenv()

# Janela
janela = Tk()
janela.title("Sistema de chamada")
janela.rowconfigure(0, weight=1)
janela.columnconfigure(0, weight=1)
janela.geometry(f"{WIDTH}x{HEIGHT}")
janela.resizable(False, False)

# Páginas
pagina_inicial = Frame(janela)
pagina_cadastro = Frame(janela)

# Fontes
fonte = ("Ivy", 11)
fonte_titulo = ("Ivy", 15, 'bold')
fonte_botao = ("Ivy", 8, 'bold')

# Adicionando as páginas
paginas = (pagina_inicial, pagina_cadastro)

# Adiciona os frames nas páginas
for frame in paginas:
    frame.grid(row=0, column=0, sticky='nsew')

# Mostra o Frame que queremos


def show_frame(frame):
    frame.tkraise()


# Primeira página a aparecer
show_frame(pagina_inicial)

# Cria o banco de dados se não existir ainda
db = Banco.Banco()


# Aulas do dia
global aulas_dia

aulas_dia = []

# Arruma o banco e salva as turmas que terão aula no dia e seus respectivos horários


def prepara_dia():
    global aulas_dia

    current_time = datetime.now()

    # Verifica se hoje é dia de semana ou fim de semana
    dia_semana = current_time.weekday()
    dia_semana = 4

    if dia_semana in [0, 1, 2, 3, 4]:
        # Aulas do dia
        aulas_dia = utils.verifica_aula_dia(dia_semana)
        utils.adiciona_fotos_alunos(aulas_dia, dia_semana)
        inicia_reconhecimento()
        print("Preparação de aulas do dia concluida")


# Computa as faltas do dia


def computa_faltas():
    current_time = datetime.now()

    # Verifica se hoje é dia de semana ou fim de semana
    # dia_semana = current_time.weekday()
    dia_semana = 4

    # 0 = Segunda a 6 = domingo
    if dia_semana in [0, 1, 2, 3, 4]:
        # Turma é Terceiro elemento do "aulas_dia"
        for aula in aulas_dia:
            utils.computa_falta(aula[2], dia_semana)
        utils.reseta_presenca_dia()
        print("Faltas computadas")

# Manda mensagens para os alunos sobre as aulas


def manda_mensagens():
    global aulas_dia

    aulas = utils.tempo_para_aula(aulas_dia)

    for aula in aulas:
        for turma in aulas[aula]:
            # Pega os alunos desta aula
            alunos = utils.alunos_para_avisar(turma[2])

            # Dados de cada aluno
            for aluno in alunos:
                ra = aluno[0]
                nome = aluno[1]
                email = aluno[2]

                if aula == 'antes':
                    # Envia email avisando que a aula vai começar
                    envia_email_aula_comeca(nome, ra, email)
                elif aula == 'durante':
                    # Envia email avisando que o aluno ainda não foi identificado
                    envia_email_alerta(nome, ra, email)
                elif aula == 'depois':
                    # Envia email avisando que o aluno recebeu falta
                    envia_email_acusando_falta(nome, ra, email)

# Função teste para apresentação


def inicia_app():
    prepara_dia()
    manda_mensagens()
    computa_faltas()

# Fecha o aplicativo e seus subprocessos


def sair_app():
    os._exit(0)

# ========================= Schedules ================================


schedule.every(40).minutes.do(manda_mensagens)
schedule.every().day.at("00:00").do(prepara_dia)
schedule.every().day.at("23:59").do(computa_faltas)

# ================ Pagina inicial =======================

pagina_inicial.configure(bg=AZUL_CLARO)

# Frame Titulo
frame_titulo_inicial = Frame(
    pagina_inicial, width=WIDTH, height=52, bg=AZUL_ESCURO)
frame_titulo_inicial.place(x=0, y=0)

casa_icone_titulo = Image.open('images/icon_casa.png')
casa_icone_titulo = casa_icone_titulo.resize((45, 45))
casa_icone_titulo = ImageTk.PhotoImage(casa_icone_titulo)

pagina_inicial_titulo = Label(frame_titulo_inicial, image=casa_icone_titulo, text="  Menu Principal",
                              width=WIDTH, compound=LEFT, anchor=NW, font=fonte_titulo, bg=AZUL_ESCURO, fg=BRANCO)
pagina_inicial_titulo.place(x=10, y=0)

cadastro_icone = Image.open('images/icon_cadastro.png')
cadastro_icone = cadastro_icone.resize((50, 50))
cadastro_icone = ImageTk.PhotoImage(cadastro_icone)

botao_pagina_aluno = Button(pagina_inicial, command=lambda: show_frame(pagina_cadastro), image=cadastro_icone, text="Cadastro geral".upper(),
                            compound=TOP, overrelief=RIDGE, anchor=CENTER, font=fonte, bg=AZUL_ESCURO, foreground=BRANCO)
botao_pagina_aluno['width'] = 160
botao_pagina_aluno['height'] = 160
botao_pagina_aluno.place(x=190 - 45, y=HEIGHT/2 - 80)

iniciar_icone = Image.open('images/icon_iniciar.png')
iniciar_icone = iniciar_icone.resize((50, 50))
iniciar_icone = ImageTk.PhotoImage(iniciar_icone)

botao_iniciar = Button(pagina_inicial, command=inicia_app, image=iniciar_icone, text="Teste".upper(),
                       compound=TOP, overrelief=RIDGE, anchor=CENTER, font=fonte, bg=AZUL_ESCURO, foreground=BRANCO)
botao_iniciar['width'] = 160
botao_iniciar['height'] = 160
botao_iniciar.place(x=190*2 - 45, y=HEIGHT/2 - 80)

saida_icone = Image.open('images/icon_saida.png')
saida_icone = saida_icone.resize((50, 50))
saida_icone = ImageTk.PhotoImage(saida_icone)

botao_sair = Button(pagina_inicial, command=sair_app, image=saida_icone, text="Sair".upper(),
                    compound=TOP, overrelief=RIDGE, anchor=CENTER, font=fonte, bg=AZUL_ESCURO, foreground=BRANCO)
botao_sair['width'] = 160
botao_sair['height'] = 160
botao_sair.place(x=190*3 - 45, y=HEIGHT/2 - 80)

# ================ Pagina de cadastro =======================

pagina_cadastro.configure(bg=AZUL_CLARO)

# -------------------------- Frames da página -------------------------------

# Frame Titulo
frame_titulo_aluno = Frame(pagina_cadastro, width=WIDTH,
                           height=52, bg=AZUL_ESCURO)
frame_titulo_aluno.place(x=0, y=0)

# Frame dos botões
frame_aluno_botoes = Frame(
    pagina_cadastro, width=WIDTH, height=65, bg=AZUL_CLARO)
frame_aluno_botoes.place(x=0, y=53)

# Frame do conteúdo / informações
frame_info = Frame(pagina_cadastro, width=WIDTH,
                   height=230, bg=AZUL_CLARO, padx=10)
frame_info.place(x=0, y=118)

# Frame das tabelas
frame_tabela = Frame(pagina_cadastro, width=WIDTH,
                     height=250, bg=AZUL_CLARO, padx=10)
frame_tabela.place(x=0, y=118+240)

# ----------------------------- Icones de Título ----------------------------------

global titulo_cadastro_label

icone_titulo_aluno = Image.open('images/icon_aluno.png')
icone_titulo_aluno = icone_titulo_aluno.resize((50, 50))
icone_titulo_aluno = ImageTk.PhotoImage(icone_titulo_aluno)

icone_titulo_curso = Image.open('images/icon_cursos.png')
icone_titulo_curso = icone_titulo_curso.resize((50, 50))
icone_titulo_curso = ImageTk.PhotoImage(icone_titulo_curso)

icone_titulo_aula = Image.open('images/icon_aula.png')
icone_titulo_aula = icone_titulo_aula.resize((50, 50))
icone_titulo_aula = ImageTk.PhotoImage(icone_titulo_aula)

icone_titulo_camera = Image.open('images/icon_camera.png')
icone_titulo_camera = icone_titulo_camera.resize((50, 50))
icone_titulo_camera = ImageTk.PhotoImage(icone_titulo_camera)

icone_titulo_faltas = Image.open('images/icon_falta.png')
icone_titulo_faltas = icone_titulo_faltas.resize((50, 50))
icone_titulo_faltas = ImageTk.PhotoImage(icone_titulo_faltas)

# ------------------------ Funções / Sub-paginas de cadastro -----------------------------

# Função de cadastro de alunos


def alunos():
    # Titulo da página
    global titulo_cadastro_label

    titulo_cadastro_label = Label(frame_titulo_aluno, image=icone_titulo_aluno, text="Cadastro de alunos",
                                  width=WIDTH, compound=LEFT, relief=RAISED, anchor=NW, font=fonte_titulo, bg=AZUL_ESCURO, fg=BRANCO)
    titulo_cadastro_label.place(x=0, y=0)
    ttk.Separator(pagina_cadastro, orient=HORIZONTAL).place(
        x=0, y=52, width=WIDTH)

    # ------------------------------------------------- Detalhes do Aluno ---------------------------------------------------

    global undo_list, botao_undo, undo_falta
    undo_list = []
    undo_falta = []

    # Função novo aluno
    def novo_aluno():
        # Dados da Imagem
        global aluno_foto, label_foto, foto_string

        try:
            # Dados do aluno
            ra = entry_ra.get()
            nome = entry_nome_aluno.get()
            email = entry_email.get()
            telefone = entry_telefone.get()
            sexo = combobox_sexo.get()
            foto = foto_string
            turma = combobox_turma.get()

            # Deixa o RA em letras maiúsculas
            ra = ra.upper()

            lista = [ra, nome, email, telefone, sexo, foto, turma]

            # Verifica se os campos fora preenchidos
            for item in lista:
                if item == "":
                    messagebox.showerror(
                        "Erro", "Preencha os campos corretamente.")
                    return

            aulas = utils.mostra_aula()

            # Criando aluno
            utils.cria_aluno(lista)

            # Mensagem de sucesso na criação do aluno
            messagebox.showinfo(
                "Sucesso", "Os dados fora inseridos com sucesso.")

            for aula in aulas:
                if turma == aula[4]:
                    utils.cria_falta([ra, aula[0], 0])

            entry_ra.delete(0, END)
            entry_nome_aluno.delete(0, END)
            entry_email.delete(0, END)
            entry_telefone.delete(0, END)
            combobox_sexo.set("")
            combobox_turma.set("")

            label_foto.destroy()

            mostra_alunos()
        except:
            messagebox.showerror("Erro", "RA já cadastrado")

    # Carrega informações do aluno
    def carregar_aluno():
        global botao_undo, aluno_foto, label_foto, foto_string, undo_list

        try:
            tree_itens = tree_alunos.focus()
            tree_dicionario = tree_alunos.item(tree_itens)
            tree_lista = tree_dicionario["values"]

            # Guarda RA antigo
            ra_antigo = tree_lista[0]

            undo_list = [tree_lista[0], tree_lista[1], tree_lista[2], tree_lista[3],
                         tree_lista[4], tree_lista[5], tree_lista[6]]

            # Limpa os campos
            entry_ra.delete(0, END)
            entry_nome_aluno.delete(0, END)
            entry_email.delete(0, END)
            entry_telefone.delete(0, END)
            combobox_sexo.set("")
            combobox_turma.set("")

            # Inserindo dados nas entrys
            entry_ra.insert(0, tree_lista[0])
            entry_nome_aluno.insert(0, tree_lista[1])
            entry_email.insert(0, tree_lista[2])
            entry_telefone.insert(0, tree_lista[3])
            combobox_sexo.set(tree_lista[4])
            combobox_turma.set(tree_lista[6])

            aluno_foto = tree_lista[5]

            foto_string = aluno_foto

            aluno_foto = utils.convertToImage(aluno_foto)
            aluno_foto = aluno_foto.resize((130, 130))
            aluno_foto = ImageTk.PhotoImage(aluno_foto)

            label_foto = Label(frame_info, image=aluno_foto,
                               bg=AZUL_CLARO, fg=BRANCO)
            label_foto.place(x=300, y=10)

            botao_undo.destroy()

            def atualiza():
                global botao_undo, undo_falta
                # Dados do aluno
                ra = entry_ra.get()
                nome = entry_nome_aluno.get()
                email = entry_email.get()
                telefone = entry_telefone.get()
                sexo = combobox_sexo.get()
                foto = foto_string
                turma = combobox_turma.get()

                ra = ra.upper()

                undo_list.append(ra)

                undo_falta = [ra_antigo, ra]

                # Lista dos dados
                lista = [ra, nome, email, telefone,
                         sexo, foto, turma, ra_antigo]

                # Verifica se os campos fora preenchidos
                for item in lista:
                    if item == "":
                        messagebox.showerror(
                            "Erro", "Preencha os campos corretamente.")
                        return

                # Confirmação para apagar
                res = messagebox.askquestion(
                    'Confirmação', 'Deseja alterar os dados deste aluno?')

                if res == 'yes':
                    # Atualizando dados do aluno
                    utils.atualiza_aluno(lista)
                    # Atualizando lista de faltas
                    utils.atualiza_falta([ra, ra_antigo])
                else:
                    return

                # Mensagem de sucesso na criação do aluno
                messagebox.showinfo(
                    "Sucesso", "Os dados fora alterados com sucesso.")

                # Limpa os campos
                entry_ra.delete(0, END)
                entry_nome_aluno.delete(0, END)
                entry_email.delete(0, END)
                entry_telefone.delete(0, END)
                combobox_sexo.set("")
                combobox_turma.set("")

                # Destruindo Labels, Entry e botão desnecessários
                label_foto.destroy()
                botao_salvar.destroy()

                # Atualiza tabela
                mostra_alunos()

                # Botão desfazer alteração do aluno
                botao_undo = Button(frame_info, command=undo_atualiza, anchor=CENTER, text='DESFAZER', width=10,
                                    overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
                botao_undo.place(x=726, y=110)

            # Botão salvar alterações do aluno
            botao_salvar = Button(frame_info, command=atualiza, anchor=CENTER, text='Salvar alterações'.upper(
            ), overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
            botao_salvar.place(x=700, y=145)

        except IndexError:
            messagebox.showerror("Erro", "Selecione um aluno na tabela.")

    # Função apagar aluno
    def apagar_aluno():
        try:
            tree_itens = tree_alunos.focus()
            tree_dicionario = tree_alunos.item(tree_itens)
            tree_lista = tree_dicionario["values"]

            valor_ra = tree_lista[0]

            faltas = utils.mostra_falta_aluno(valor_ra)

            # Confirmação para apagar
            res = messagebox.askquestion(
                'Confirmação', 'Deseja apagar os dados deste aluno?')

            if res == 'yes':
                # Apagando os dados do aluno
                utils.apaga_aluno(valor_ra)
                # Apagando dados de faltas do aluno
                utils.apaga_falta_aluno(valor_ra)
            else:
                return

            messagebox.showinfo(
                "Sucesso", "Os dados foram apagados com sucesso")

            mostra_alunos()

            # Desfaz a ação de apagar o aluno
            def undo_apaga():
                utils.cria_aluno(tree_lista)
                mostra_alunos()
                botao_desfazer.destroy()

                for falta in faltas:
                    utils.cria_falta([falta[0], falta[1], falta[2]])

            # Botão desfazer deleção de aluno
            botao_desfazer = Button(frame_info, command=undo_apaga, anchor=CENTER, text='DESFAZER', width=9,
                                    overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
            botao_desfazer.place(x=726, y=110)

        except IndexError:
            messagebox.showerror("Erro", "Selecione um aluno na tabela.")

    # Pesquisa informações do aluno pelo RA
    def pesquisa_aluno():
        global aluno_foto, label_foto, foto_string, undo_list

        valor_ra = entry_procura.get()

        valor_ra = valor_ra.upper()

        try:
            dados = utils.pesquisa_aluno(valor_ra)

            undo_list = [dados[0], dados[1], dados[2], dados[3],
                         dados[4], dados[5], dados[6]]

            # Limpa os campos
            entry_procura.delete(0, END)
            entry_ra.delete(0, END)
            entry_nome_aluno.delete(0, END)
            entry_email.delete(0, END)
            entry_telefone.delete(0, END)
            combobox_sexo.set("")
            combobox_turma.set("")

            # Inserindo dados nas entrys
            entry_ra.insert(0, dados[0])
            entry_nome_aluno.insert(0, dados[1])
            entry_email.insert(0, dados[2])
            entry_telefone.insert(0, dados[3])
            combobox_sexo.set(dados[4])
            combobox_turma.set(dados[6])

            aluno_foto = dados[5]
            foto_string = aluno_foto

            # Inserindo foto do Aluno na tela
            aluno_foto = utils.convertToImage(aluno_foto)
            aluno_foto = aluno_foto.resize((130, 130))
            aluno_foto = ImageTk.PhotoImage(aluno_foto)

            label_foto = Label(frame_info, image=aluno_foto,
                               bg=AZUL_CLARO, fg=BRANCO)
            label_foto.place(x=300, y=10)

            def atualiza():
                global botao_undo, undo_falta
                # Dados do aluno
                ra = entry_ra.get()
                nome = entry_nome_aluno.get()
                email = entry_email.get()
                telefone = entry_telefone.get()
                sexo = combobox_sexo.get()
                foto = foto_string
                turma = combobox_turma.get()

                ra = ra.upper()

                undo_list.append(ra)

                undo_falta = [valor_ra, ra]

                # Lista dos dados
                lista = [ra, nome, email, telefone,
                         sexo, foto, turma, valor_ra]

                # Verifica se os campos fora preenchidos
                for item in lista:
                    if item == "":
                        messagebox.showerror(
                            "Erro", "Preencha os campos corretamente.")
                        return

                # Confirmação para alterar
                res = messagebox.askquestion(
                    'Confirmação', 'Deseja alterar os dados deste aluno?')

                if res == 'yes':
                    # Atualizando dados do aluno
                    utils.atualiza_aluno(lista)
                    # Atualizando dados das faltas
                    utils.atualiza_falta([ra, valor_ra])
                else:
                    return

                # Mensagem de sucesso na alteração do aluno
                messagebox.showinfo(
                    "Sucesso", "Os dados fora alterados com sucesso.")

                # Limpa os campos
                entry_ra.delete(0, END)
                entry_nome_aluno.delete(0, END)
                entry_email.delete(0, END)
                entry_telefone.delete(0, END)
                combobox_sexo.set("")
                combobox_turma.set("")

                # Destruindo Labels, Entry e botão desnecessários
                label_foto.destroy()
                botao_salvar.destroy()

                # Atualiza tabela
                mostra_alunos()

                # Botão desfazer alteração do aluno
                botao_undo = Button(frame_info, command=undo_atualiza, anchor=CENTER, text='DESFAZER', width=10,
                                    overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
                botao_undo.place(x=726, y=110)

            # Botão salvar alterações do aluno
            botao_salvar = Button(frame_info, command=atualiza, anchor=CENTER, text='Salvar alterações'.upper(
            ), overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
            botao_salvar.place(x=700, y=145)

        except:
            messagebox.showerror("Erro", "Aluno não encontrado.")

    # Mostra informações do aluno pela tabela
    def info_aluno():
        global aluno_foto, label_foto, foto_string

        try:
            tree_itens = tree_alunos.focus()
            tree_dicionario = tree_alunos.item(tree_itens)
            tree_lista = tree_dicionario["values"]

            # Limpa os campos
            entry_ra.delete(0, END)
            entry_nome_aluno.delete(0, END)
            entry_email.delete(0, END)
            entry_telefone.delete(0, END)
            combobox_sexo.set("")
            combobox_turma.set("")

            # Inserindo dados nas entrys
            entry_ra.insert(0, tree_lista[0])
            entry_nome_aluno.insert(0, tree_lista[1])
            entry_email.insert(0, tree_lista[2])
            entry_telefone.insert(0, tree_lista[3])
            combobox_sexo.set(tree_lista[4])
            combobox_turma.set(tree_lista[6])

            aluno_foto = tree_lista[5]
            foto_string = aluno_foto

            # Inserindo foto do Aluno na tela
            aluno_foto = utils.convertToImage(aluno_foto)
            aluno_foto = aluno_foto.resize((130, 130))
            aluno_foto = ImageTk.PhotoImage(aluno_foto)

            label_foto = Label(frame_info, image=aluno_foto,
                               bg=AZUL_CLARO, fg=BRANCO)
            label_foto.place(x=300, y=10)

        except IndexError:
            messagebox.showerror("Erro", "Selecione um aluno na tabela.")

    # Label e entry do Nome do aluno
    label_nome = Label(frame_info, text="Nome *",
                       height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_nome.place(x=10, y=10)

    entry_nome_aluno = Entry(frame_info, width=45,
                             justify='left', relief=SOLID)
    entry_nome_aluno.place(x=12, y=40)

    # Label e entry do email
    label_email = Label(frame_info, text="Email *",
                        height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_email.place(x=10, y=70)

    entry_email = Entry(frame_info, width=45,
                        justify='left', relief=SOLID)
    entry_email.place(x=12, y=100)

    # Label e entry do Telefone
    label_telefone = Label(frame_info, text="Telefone *",
                           height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_telefone.place(x=10, y=130)

    entry_telefone = Entry(frame_info, width=20,
                           justify='left', relief=SOLID)
    entry_telefone.place(x=12, y=160)

    # Label e combobox do Sexo
    label_sexo = Label(frame_info, text="Sexo *",
                       height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_sexo.place(x=190, y=130)

    combobox_sexo = ttk.Combobox(frame_info, width=12, font=fonte_botao)
    combobox_sexo['values'] = ['Masculino', 'Feminino']
    combobox_sexo['state'] = 'readonly'
    combobox_sexo.place(x=190, y=160)

    # Label e entry do RA
    label_ra = Label(frame_info, text="RA *",
                     height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_ra.place(x=451, y=70)

    entry_ra = Entry(frame_info, width=20,
                     justify='left', relief=SOLID)
    entry_ra.place(x=455, y=100)

    # Pegando as Turmas
    turmas = utils.mostra_turma()
    turma = []

    for item in turmas:
        turma.append(item[1])

    # Label e combobox do Curso
    label_turma = Label(frame_info, text="Turma *",
                        height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_turma.place(x=451, y=130)

    combobox_turma = ttk.Combobox(frame_info, width=20, font=fonte_botao)
    combobox_turma['values'] = turma
    combobox_turma['state'] = 'readonly'
    combobox_turma.place(x=455, y=160)

    # Dados da Imagem
    global aluno_foto, label_foto, foto_string

    # Função para escolher imagem
    def escolhe_imagem():
        global aluno_foto, label_foto, foto_string

        try:
            aluno_foto = fd.askopenfilename()

            aluno_foto = utils.convertToBinaryData(aluno_foto)

            foto_string = aluno_foto

            # Abrindo imagem
            aluno_foto = utils.convertToImage(aluno_foto)
            aluno_foto = aluno_foto.resize((130, 130))
            aluno_foto = ImageTk.PhotoImage(aluno_foto)

            label_foto = Label(frame_info, image=aluno_foto,
                               bg=AZUL_CLARO, fg=BRANCO)
            label_foto.place(x=300, y=10)

            botao_carregar['text'] = "TROCAR DE FOTO"
        except:
            # Se não for selecionada nenhuma foto, apenas retorna
            return

    # Função tira foto do aluno
    def tira_foto():
        global aluno_foto, label_foto, foto_string

        foto_string = utils.tira_foto_binario()

        try:
            aluno_foto = utils.convertToImage(foto_string)
            aluno_foto = aluno_foto.resize((130, 130))
            aluno_foto = ImageTk.PhotoImage(aluno_foto)

            label_foto = Label(frame_info, image=aluno_foto,
                               bg=AZUL_CLARO, fg=BRANCO)
            label_foto.place(x=300, y=10)
        except:
            messagebox.showerror(
                'Erro', 'Não foi possível processar a foto corretamente.\nPor favor tente novamente')

    # Desfaz a ação de atualizar o aluno

    def undo_atualiza():
        global undo_list, botao_undo, undo_falta
        utils.atualiza_aluno(undo_list)
        mostra_alunos()
        botao_undo.destroy()
        utils.atualiza_falta(undo_falta)

    # Botão desfazer alteração do aluno
    botao_undo = Button(frame_info, command=undo_atualiza, anchor=CENTER, text='DESFAZER', width=10,
                        overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
    botao_undo.place(x=726, y=110)

    botao_undo.destroy()

    # Botão Tira foto
    botao_foto = Button(frame_info, command=tira_foto, text='Tirar foto'.upper(
    ), width=18, compound=CENTER, overrelief=RIDGE, anchor=CENTER, font=fonte_botao, bg=AZUL_ESCURO, foreground=BRANCO)
    botao_foto.place(x=300, y=160)

    # Botão Carregar Foto
    botao_carregar = Button(frame_info, command=escolhe_imagem, text='Carregar foto'.upper(
    ), width=18, compound=CENTER, overrelief=RIDGE, anchor=CENTER, font=fonte_botao, bg=AZUL_ESCURO, foreground=BRANCO)
    botao_carregar.place(x=300, y=200)

    # Linha de separação
    label_linha = Label(frame_info, relief=GROOVE, text='h', width=1,
                        height=200, anchor=NW, font=("Ivy, 1"), bg=PRETO, fg=PRETO)
    label_linha.place(x=605, y=0)
    label_linha = Label(frame_info, relief=GROOVE, text='h', width=1,
                        height=200, anchor=NW, font=("Ivy, 1"), bg=BRANCO, fg=PRETO)
    label_linha.place(x=603, y=0)

    # Procura Aluno
    label_procura_nome = Label(frame_info, text="Procurar Aluno [Entrar com RA]",
                               height=1, anchor=NW, font=("Ivy, 10"), bg=AZUL_CLARO, fg=PRETO)
    label_procura_nome.place(x=620, y=10)

    entry_procura = Entry(frame_info, width=17,
                          justify='left', relief=SOLID, font=("Ivy, 10"))
    entry_procura.place(x=622, y=35)

    botao_procurar = Button(frame_info, command=pesquisa_aluno, text="Pesquisar",
                            font=fonte_botao, compound=LEFT, overrelief=RIDGE, bg=AZUL_ESCURO, fg=BRANCO)
    botao_procurar.place(x=757, y=33)

    # ------------------------------------ Botões ---------------------------------

    # Botão adicionar aluno
    botao_adicionar = Button(frame_info, command=novo_aluno, anchor=CENTER, text='ADICIONAR', width=9,
                             overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
    botao_adicionar.place(x=617, y=110)

    # Botão alterar aluno
    botao_alterar = Button(frame_info, command=carregar_aluno, anchor=CENTER, text='ALTERAR',
                           width=9, overrelief=RIDGE, font=fonte_botao, bg=AZUL_ESCURO, foreground=BRANCO)
    botao_alterar.place(x=617, y=145)

    # Botão deletar aluno
    botao_deletar = Button(frame_info, command=apagar_aluno, anchor=CENTER, text='DELETAR', width=9,
                           overrelief=RIDGE, font=fonte_botao, bg=VERMELHO, foreground=BRANCO)
    botao_deletar.place(x=617, y=180)

    # Botão informações do aluno
    botao_mostrar = Button(frame_info, command=info_aluno, anchor=CENTER, text='INFO', width=9,
                           overrelief=RIDGE, font=fonte_botao, bg=AZUL_ESCURO, foreground=BRANCO)
    botao_mostrar.place(x=727, y=180)

    # Mostra a tabela com os alunos
    def mostra_alunos():
        tabela_alunos_label = Label(frame_info, text="Tabela de alunos",
                                    height=1, relief="flat", anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
        tabela_alunos_label.place(x=0, y=210)

        lista_cabecalho = ['RA', 'Nome', 'Email',
                           'Telefone', 'Sexo', 'Foto', 'Turma']

        lista_itens = utils.mostra_aluno()

        global tree_alunos

        tree_alunos = ttk.Treeview(
            frame_tabela, selectmode="extended", columns=lista_cabecalho, show='headings')

        # Scrollbars
        scroll_vertical = ttk.Scrollbar(
            frame_tabela, orient='vertical', command=tree_alunos.yview)
        scroll_horizontal = ttk.Scrollbar(
            frame_tabela, orient="horizontal", command=tree_alunos.xview)

        tree_alunos.configure(yscrollcommand=scroll_vertical,
                              xscrollcommand=scroll_horizontal)

        tree_alunos.place(x=0, y=0, width=WIDTH - 60, height=200)
        scroll_vertical.place(x=WIDTH - 60, y=0 + 1, height=200)
        scroll_horizontal.place(x=0, y=200, width=WIDTH - 60)

        posicao_coluna = ["nw", "nw", "nw", "center",
                          "center", "center", "center"]
        largura_coluna = [60, 150, 150, 70, 70, 70, 80]
        cont = 0

        for coluna in lista_cabecalho:
            tree_alunos.heading(coluna, text=coluna.title(), anchor=NW)
            tree_alunos.column(
                coluna, width=largura_coluna[cont], anchor=posicao_coluna[cont])

            cont += 1

        for item in lista_itens:
            tree_alunos.insert('', 'end', values=item)

    mostra_alunos()

# Função de cadastro de cursos e turmas


def cursos_turmas():
    # Titulo da página
    global titulo_cadastro_label

    titulo_cadastro_label = Label(frame_titulo_aluno, image=icone_titulo_curso, text="Cadastro de Cursos e Turmas",
                                  width=WIDTH, compound=LEFT, relief=RAISED, anchor=NW, font=fonte_titulo, bg=AZUL_ESCURO, fg=BRANCO)
    titulo_cadastro_label.place(x=0, y=0)
    ttk.Separator(pagina_cadastro, orient=HORIZONTAL).place(
        x=0, y=52, width=WIDTH)

    # Tabela de cursos
    frame_tabela_cursos = Frame(
        frame_tabela, width=300, height=200, bg=AZUL_CLARO)
    frame_tabela_cursos.place(x=30, y=0)

    # Divisão entre cursos e turmas
    frame_linha = Frame(
        frame_tabela, width=15, height=200, bg=AZUL_CLARO)
    frame_linha.place(x=300 + 85, y=0)

    # -------------------- Detalhes do Curso -----------------------------------

    global undo_list, botao_undo_curso
    undo_list = []

    # Função novo curso
    def novo_curso():
        try:
            nome = entry_nome_curso.get()
            duracao = entry_duracao.get()

            lista = [nome, duracao]

            # Se os campos não forem preenchidos corretamente
            for item in lista:
                if item == "":
                    messagebox.showerror("Erro", "Preencha todos os campos")
                    return

            # Cria o Curso
            utils.cria_curso(lista)

            messagebox.showinfo(
                "Sucesso", "Os dados foram inseridos com sucesso")

            entry_nome_curso.delete(0, END)
            entry_duracao.delete(0, END)

            controle('cursos')
        except:
            messagebox.showerror("Erro", "Curso já cadastrado")

    # Função carregar/atualizar curso
    def carregar_curso():
        global undo_list
        try:
            tree_itens = tree_cursos.focus()
            tree_dicionario = tree_cursos.item(tree_itens)
            tree_lista = tree_dicionario['values']

            # Salva o id
            valor_id = tree_lista[0]

            undo_list = [tree_lista[0], tree_lista[1], tree_lista[2]]

            # Limpa os campos
            entry_nome_curso.delete(0, END)
            entry_duracao.delete(0, END)

            # Insere dados nas Entrys
            entry_nome_curso.insert(0, tree_lista[1])
            entry_duracao.insert(0, tree_lista[2])

            # Atualiza
            def atualiza():
                global botao_undo_curso
                nome = entry_nome_curso.get()
                duracao = entry_duracao.get()

                lista = [valor_id, nome, duracao]

                # Se os campos não forem preenchidos corretamente
                for item in lista:
                    if item == "":
                        messagebox.showerror(
                            "Erro", "Preencha todos os campos")
                        return

                # Confirmação para apagar
                res = messagebox.askquestion(
                    'Confirmação', 'Deseja alterar os dados deste curso?')

                if res == 'yes':
                    # Atualiza os dados do curso
                    utils.atualiza_curso(lista)
                else:
                    return

                messagebox.showinfo(
                    "Sucesso", "Os dados foram atualizados com sucesso")

                entry_nome_curso.delete(0, END)
                entry_duracao.delete(0, END)

                # atualiza os dados da tabela
                mostra_cursos()

                mostra_turmas()

                botao_salvar.destroy()

                # Botão desfazer alteração do aluno
                botao_undo_curso = Button(frame_info, command=undo_atualiza_curso, anchor=CENTER, text='DESFAZER', width=10,
                                          overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
                botao_undo_curso.place(x=240, y=130)

            botao_salvar = Button(frame_info, command=atualiza, anchor=CENTER, text="Salvar alterações".upper(
            ), overrelief=RIDGE, font=fonte_botao, bg=VERDE, fg=BRANCO)
            botao_salvar.place(x=190, y=130)
        except IndexError:
            messagebox.showerror("Erro", "Selecione um curso na tabela.")

    # Função apagar curso
    def apagar_curso():
        try:
            tree_itens = tree_cursos.focus()
            tree_dicionario = tree_cursos.item(tree_itens)
            tree_lista = tree_dicionario['values']

            # Salva o id
            valor_id = tree_lista[0]

            # Confirmação para apagar
            res = messagebox.askquestion(
                'Confirmação', 'Deseja apagar os dados deste curso?')

            if res == 'yes':
                # Apagando os dados do curso
                utils.apaga_curso(valor_id)
            else:
                return

            messagebox.showinfo(
                "Sucesso", "Os dados foram apagados com sucesso")

            # atualiza os dados da tabela
            mostra_cursos()
            mostra_turmas()

            # Desfaz a ação de apagar o aluno
            def undo_apaga():
                utils.cria_curso([tree_lista[1], tree_lista[2]])
                mostra_cursos()
                mostra_turmas()
                botao_desfazer.destroy()

            # Botão desfazer deleção de aluno
            botao_desfazer = Button(frame_info, command=undo_apaga, anchor=CENTER, text='DESFAZER', width=10,
                                    overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
            botao_desfazer.place(x=240, y=130)

        except IndexError:
            messagebox.showerror("Erro", "Selecione um curso na tabela.")

    # Label e entry do Nome do curso
    label_nome = Label(frame_info, text="Nome do Curso *",
                       height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_nome.place(x=10, y=10)

    entry_nome_curso = Entry(frame_info, width=35,
                             justify='left', relief=SOLID)
    entry_nome_curso.place(x=12, y=40)

    # Label e entry da Duração do curso
    label_duracao = Label(frame_info, text="Duração *",
                          height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_duracao.place(x=10, y=70)

    entry_duracao = Entry(frame_info, width=20,
                          justify='left', relief=SOLID)
    entry_duracao.place(x=12, y=100)

    # Botão salvar curso
    botao_curso_adicionar = Button(frame_info, command=novo_curso, anchor=CENTER, text='ADICIONAR', width=10,
                                   overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
    botao_curso_adicionar.place(x=20, y=160)

    # Botão atualizar curso
    botao_curso_alterar = Button(frame_info, command=carregar_curso, anchor=CENTER, text='ALTERAR',
                                 width=10, overrelief=RIDGE, font=fonte_botao, bg=AZUL_ESCURO, foreground=BRANCO)
    botao_curso_alterar.place(x=130, y=160)

    # Botão deletar curso
    botao_curso_deletar = Button(frame_info, command=apagar_curso, anchor=CENTER, text='DELETAR', width=10,
                                 overrelief=RIDGE, font=fonte_botao, bg=VERMELHO, foreground=BRANCO)
    botao_curso_deletar.place(x=240, y=160)

    # Mostra Tabela Cursos
    def mostra_cursos():
        tabela_cursos_label = Label(frame_info, text="Tabela de cursos",
                                    height=1, relief="flat", anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
        tabela_cursos_label.place(x=0, y=210)

        lista_cabecalho = ['ID', 'Curso', 'Duração']

        lista_itens = utils.mostra_curso()

        global tree_cursos

        tree_cursos = ttk.Treeview(
            frame_tabela, selectmode="extended", columns=lista_cabecalho, show='headings')

        # Scrollbars
        scroll_vertical = ttk.Scrollbar(
            frame_tabela, orient='vertical', command=tree_cursos.yview)
        scroll_horizontal = ttk.Scrollbar(
            frame_tabela, orient="horizontal", command=tree_cursos.xview)

        tree_cursos.configure(yscrollcommand=scroll_vertical,
                              xscrollcommand=scroll_horizontal)

        tree_cursos.place(x=0, y=0, width=340, height=200)
        scroll_vertical.place(x=340, y=0, height=200)
        scroll_horizontal.place(x=0, y=200, width=340)

        posicao_coluna = ["nw", "nw", "e"]
        largura_coluna = [30, 150, 80]
        cont = 0

        for coluna in lista_cabecalho:
            tree_cursos.heading(coluna, text=coluna.title(), anchor=NW)
            tree_cursos.column(
                coluna, width=largura_coluna[cont], anchor=posicao_coluna[cont])

            cont += 1

        for item in lista_itens:
            tree_cursos.insert('', 'end', values=item)

    # Desfaz a ação de atualizar o curso
    def undo_atualiza_curso():
        global undo_list, botao_undo_curso
        utils.atualiza_curso(undo_list)
        mostra_cursos()
        mostra_turmas()
        botao_undo_curso.destroy()

    # Botão desfazer alteração do aluno
    botao_undo_curso = Button(frame_info, command=undo_atualiza_curso, anchor=CENTER, text='DESFAZER', width=9,
                              overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
    botao_undo_curso.place(x=190, y=130)

    botao_undo_curso.destroy()

    mostra_cursos()

    # ------------------------------- Linha Separatória ---------------------------------------

    # Linha separatória info
    label_linha = Label(frame_info, relief=GROOVE, text='h', width=1,
                        height=200, anchor=NW, font=("Ivy, 1"), bg=PRETO, fg=PRETO)
    label_linha.place(x=390, y=0)
    label_linha = Label(frame_info, relief=GROOVE, text='h', width=1,
                        height=200, anchor=NW, font=("Ivy, 1"), bg=BRANCO, fg=PRETO)
    label_linha.place(x=388, y=0)

    # Linha separatória tabela
    label_linha = Label(frame_linha, relief=GROOVE, text='h', width=1,
                        height=200, anchor=NW, font=("Ivy, 1"), bg=PRETO, fg=PRETO)
    label_linha.place(x=5, y=0)
    label_linha = Label(frame_linha, relief=GROOVE, text='h', width=1,
                        height=200, anchor=NW, font=("Ivy, 1"), bg=BRANCO, fg=PRETO)
    label_linha.place(x=3, y=0)

    # ------------------------------ Detalhes das Turmas ------------------------------------

    global combobox_curso, botao_undo_turma

    # Função novo turma
    def nova_turma():
        try:
            nome = entry_nome_turma.get()
            curso = combobox_curso.get()
            data = data_inicio.get_date()

            lista = [nome, curso, data]

            # Se os campos não forem preenchidos corretamente
            for item in lista:
                if item == "":
                    messagebox.showerror("Erro", "Preencha todos os campos")
                    return

            # Cria o turma
            utils.cria_turma(lista)

            messagebox.showinfo(
                "Sucesso", "Os dados foram inseridos com sucesso")

            entry_nome_turma.delete(0, END)
            combobox_curso.set("")
            data_inicio.delete(0, END)

            # Atualiza a tabela
            mostra_turmas()
        except:
            messagebox.showerror("Erro", "Turma já cadastrada")

    # Função carregar/atualizar turma
    def carregar_turma():
        global undo_list
        try:
            tree_itens = tree_turma.focus()
            tree_dicionario = tree_turma.item(tree_itens)
            tree_lista = tree_dicionario['values']

            # Salva o id
            valor_id = tree_lista[0]

            undo_list = tree_lista

            # Limpa os campos
            entry_nome_turma.delete(0, END)
            combobox_curso.delete(0, END)
            data_inicio.delete(0, END)

            # Insere dados nas Entrys
            entry_nome_turma.insert(0, tree_lista[1])
            combobox_curso.set(tree_lista[2])
            data_inicio.insert(0, tree_lista[3])

            # Atualiza
            def atualiza():
                global botao_undo_turma
                nome = entry_nome_turma.get()
                curso = combobox_curso.get()
                data = data_inicio.get_date()

                lista = [valor_id, nome, curso, data]

                # Se os campos não forem preenchidos corretamente
                for item in lista:
                    if item == "":
                        messagebox.showerror(
                            "Erro", "Preencha todos os campos")
                        return

                # Confirmação para apagar
                res = messagebox.askquestion(
                    'Confirmação', 'Deseja alterar os dados desta turma?')

                if res == 'yes':
                    # Atualiza os dados do turma
                    utils.atualiza_turma(lista)
                else:
                    return

                messagebox.showinfo(
                    "Sucesso", "Os dados foram atualizados com sucesso")

                entry_nome_turma.delete(0, END)
                combobox_curso.delete(0, END)
                data_inicio.delete(0, END)

                # atualiza os dados da tabela
                mostra_turmas()

                botao_salvar.destroy()

                # Botão desfazer alteração do aluno
                botao_undo_turma = Button(frame_info, command=undo_atualiza_turma, anchor=CENTER, text='DESFAZER', width=10,
                                          overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
                botao_undo_turma.place(x=687, y=130)

            botao_salvar = Button(frame_info, command=atualiza, anchor=CENTER, text="Salvar alterações".upper(
            ), overrelief=RIDGE, font=fonte_botao, bg=VERDE, fg=BRANCO)
            botao_salvar.place(x=637, y=130)
        except IndexError:
            messagebox.showerror("Erro", "Selecione um turma na tabela.")

    # Função apagar turma
    def apagar_turma():
        try:
            tree_itens = tree_turma.focus()
            tree_dicionario = tree_turma.item(tree_itens)
            tree_lista = tree_dicionario['values']

            # Salva o id
            valor_id = tree_lista[0]

            # Confirmação para apagar
            res = messagebox.askquestion(
                'Confirmação', 'Deseja apagar os dados deste turma?')

            if res == 'yes':
                # Apagando os dados do turma
                utils.apaga_turma(valor_id)
            else:
                return

            messagebox.showinfo(
                "Sucesso", "Os dados foram apagados com sucesso")

            # atualiza os dados da tabela
            mostra_turmas()

            # Desfaz a ação de apagar o aluno
            def undo_apaga():
                utils.cria_turma([tree_lista[1], tree_lista[2], tree_lista[3]])
                mostra_turmas()
                botao_desfazer.destroy()

            # Botão desfazer deleção de aluno
            botao_desfazer = Button(frame_info, command=undo_apaga, anchor=CENTER, text='DESFAZER', width=10,
                                    overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
            botao_desfazer.place(x=687, y=130)

        except IndexError:
            messagebox.showerror("Erro", "Selecione um turma na tabela.")

    label_nome = Label(frame_info, text="Nome Turma *",
                       height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_nome.place(x=404, y=10)
    entry_nome_turma = Entry(frame_info, width=35,
                             justify=LEFT, relief="solid")
    entry_nome_turma.place(x=407, y=40)

    label_curso_turma = Label(frame_info, text="Curso *",
                              height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_curso_turma.place(x=404, y=70)

    # Pegando os cursos
    cursos = utils.mostra_curso()
    curso = []

    for item in cursos:
        curso.append(item[1])

    combobox_curso = ttk.Combobox(frame_info, width=20, font=fonte_botao)
    combobox_curso['values'] = curso
    combobox_curso['state'] = 'readonly'
    combobox_curso.place(x=407, y=100)

    label_data_inicio = Label(frame_info, text="Data de início *",
                              height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_data_inicio.place(x=406, y=130)

    data_inicio = DateEntry(frame_info, width=10, background=AZUL_ESCURO,
                            foreground=BRANCO, borderwidth=2, year=2023)
    data_inicio.place(x=407, y=160)

    # Botão adicionar turma
    botao_turma_adicionar = Button(frame_info, command=nova_turma, anchor=CENTER, text='ADICIONAR', width=10,
                                   overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
    botao_turma_adicionar.place(x=507, y=160)

    # Botão alterar turma
    botao_turma_alterar = Button(frame_info, command=carregar_turma, anchor=CENTER, text='ALTERAR',
                                 width=10, overrelief=RIDGE, font=fonte_botao, bg=AZUL_ESCURO, foreground=BRANCO)
    botao_turma_alterar.place(x=597, y=160)

    # Botão deletar turma
    botao_turma_deletar = Button(frame_info, command=apagar_turma, anchor=CENTER, text='DELETAR', width=10,
                                 overrelief=RIDGE, font=fonte_botao, bg=VERMELHO, foreground=BRANCO)
    botao_turma_deletar.place(x=687, y=160)

    def mostra_turmas():
        global combobox_curso

        combobox_curso.destroy()

        # Atualiza o combobox dos cursos
        # Pegando os cursos
        cursos = utils.mostra_curso()
        curso = []

        for item in cursos:
            curso.append(item[1])

        combobox_curso = ttk.Combobox(frame_info, width=20, font=fonte_botao)
        combobox_curso['values'] = curso
        combobox_curso['state'] = 'readonly'
        combobox_curso.place(x=407, y=100)

        tabela_turma_label = Label(frame_info, text="Tabela de turmas",
                                   height=1, relief="flat", anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
        tabela_turma_label.place(x=410, y=210)

        lista_cabecalho = ['ID', 'Nome da Turma', 'Curso', 'Inicio']

        lista_itens = utils.mostra_turma()

        global tree_turma

        tree_turma = ttk.Treeview(
            frame_tabela, selectmode="extended", columns=lista_cabecalho, show='headings')

        # Scrollbars
        scroll_vertical = ttk.Scrollbar(
            frame_tabela, orient='vertical', command=tree_turma.yview)
        scroll_horizontal = ttk.Scrollbar(
            frame_tabela, orient="horizontal", command=tree_turma.xview)

        tree_turma.configure(yscrollcommand=scroll_vertical,
                             xscrollcommand=scroll_horizontal)

        tree_turma.place(x=410, y=0, width=395, height=200)
        scroll_vertical.place(x=410 + 395, y=0, height=200)
        scroll_horizontal.place(x=410, y=200, width=395)

        posicao_coluna = ["nw", "nw", "e", "e"]
        largura_coluna = [30, 130, 150, 80]
        cont = 0

        for coluna in lista_cabecalho:
            tree_turma.heading(coluna, text=coluna.title(), anchor=NW)
            tree_turma.column(
                coluna, width=largura_coluna[cont], anchor=posicao_coluna[cont])

            cont += 1

        for item in lista_itens:
            tree_turma.insert('', 'end', values=item)

    # Desfaz a ação de atualizar o turma
    def undo_atualiza_turma():
        global undo_list, botao_undo_turma
        utils.atualiza_turma(undo_list)
        mostra_turmas()
        botao_undo_turma.destroy()

    # Botão desfazer alteração do aluno
    botao_undo_turma = Button(frame_info, command=undo_atualiza_turma, anchor=CENTER, text='DESFAZER', width=10,
                              overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
    botao_undo_turma.place(x=190, y=130)

    botao_undo_turma.destroy()

    mostra_turmas()

# Função de cadastro de aulas


def aulas():
    # ------------------------------------------------- Titulo da página ----------------------------------------------------
    global titulo_cadastro_label

    titulo_cadastro_label = Label(frame_titulo_aluno, image=icone_titulo_aula, text="Cadastro de Aulas",
                                  width=WIDTH, compound=LEFT, relief=RAISED, anchor=NW, font=fonte_titulo, bg=AZUL_ESCURO, fg=BRANCO)
    titulo_cadastro_label.place(x=0, y=0)
    ttk.Separator(pagina_cadastro, orient=HORIZONTAL).place(
        x=0, y=52, width=WIDTH)

    # ------------------------------------------------- Detalhes da aula ---------------------------------------------------

    global undo_falta

    undo_falta = []

    # Função nova aula
    def nova_aula():
        valor_hora = entry_hora.time()

        nome = entry_nome_aula.get()
        dia = combobox_dia.get()
        hora = f"{valor_hora[0]}:{valor_hora[1]}"
        turma = combobox_turma.get()

        lista = [nome, dia, hora, turma]

        # Se os campos não forem preenchidos corretamente
        for item in lista:
            if item == "":
                messagebox.showerror("Erro", "Preencha todos os campos")
                return

        # Cria a aula
        utils.cria_aula(lista)

        alunos = utils.mostra_aluno_da_turma(turma)
        for aluno in alunos:
            falta = [aluno[0], utils.ultima_aula_criada(), 0]
            utils.cria_falta(falta)

        messagebox.showinfo("Sucesso", "Os dados foram inseridos com sucesso")

        # Limpa os campos
        entry_nome_aula.delete(0, END)
        combobox_dia.set("")
        entry_hora.set24Hrs(0)
        entry_hora.setMins(0)
        combobox_turma.set("")

        mostra_aula()

    # Função carregar/atualizar curso
    def carregar_aula():
        global undo_list
        try:
            tree_itens = tree_aulas.focus()
            tree_dicionario = tree_aulas.item(tree_itens)
            tree_lista = tree_dicionario['values']

            # Salva o id
            valor_id = tree_lista[0]

            undo_list = tree_lista

           # Limpa os campos
            entry_nome_aula.delete(0, END)
            entry_hora.set24Hrs(0)
            entry_hora.setMins(0)

            hora = tree_lista[3].split(":")

            minuto = hora[1]
            hora = hora[0]

            # Insere dados nas Entrys
            entry_nome_aula.insert(0, tree_lista[1])
            combobox_dia.set(tree_lista[2])
            entry_hora.set24Hrs(hora)
            entry_hora.setMins(minuto)
            combobox_turma.set(tree_lista[4])

            # Atualiza
            def atualiza():
                global botao_undo

                valor_hora = entry_hora.time()

                nome = entry_nome_aula.get()
                dia = combobox_dia.get()
                hora = f"{valor_hora[0]}:{valor_hora[1]}"
                turma = combobox_turma.get()

                lista = [valor_id, nome, dia, hora, turma]

                # Se os campos não forem preenchidos corretamente
                for item in lista:
                    if item == "":
                        messagebox.showerror(
                            "Erro", "Preencha todos os campos")
                        return

                # Confirmação para apagar
                res = messagebox.askquestion(
                    'Confirmação', 'Deseja alterar os dados desta aula?')

                if res == 'yes':
                    # Atualiza os dados da aula
                    utils.atualiza_aula(lista)
                else:
                    return

                messagebox.showinfo(
                    "Sucesso", "Os dados foram atualizados com sucesso")

                # Limpa os campos
                entry_nome_aula.delete(0, END)
                combobox_dia.set("")
                entry_hora.set24Hrs(0)
                entry_hora.setMins(0)
                combobox_turma.set("")

                # atualiza os dados da tabela
                mostra_aula()

                # Botão desfazer alteração do aula
                botao_undo = Button(frame_info, command=undo_atualiza, anchor=CENTER, text='DESFAZER', width=10,
                                    overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
                botao_undo.place(x=726, y=110)

                botao_salvar.destroy()

            botao_salvar = Button(frame_info, command=atualiza, anchor=CENTER, text="Salvar alterações".upper(
            ), overrelief=RIDGE, font=fonte_botao, bg=VERDE, fg=BRANCO)
            botao_salvar.place(x=700, y=145)
        except IndexError:
            messagebox.showerror("Erro", "Selecione uma aula na tabela.")

    # Função apagar aula
    def apagar_aula():
        try:
            tree_itens = tree_aulas.focus()
            tree_dicionario = tree_aulas.item(tree_itens)
            tree_lista = tree_dicionario['values']

            # Salva o id
            valor_id = tree_lista[0]

            nome = tree_lista[1]

            nome = str(nome).lower()

            faltas = utils.mostra_falta_aula(nome)

            # Confirmação para apagar
            res = messagebox.askquestion(
                'Confirmação', 'Deseja apagar os dados desta aula?')

            if res == 'yes':
                # Apagando os dados da aula
                utils.apaga_aula(valor_id)
                # Apagando os dados das faltas dessa aula
                utils.apaga_falta_aula(valor_id)
            else:
                return

            messagebox.showinfo(
                "Sucesso", "Os dados foram apagados com sucesso")

            # atualiza os dados da tabela
            mostra_aula()

            # Desfaz a ação de apagar a aula
            def undo_apaga():
                utils.cria_aula_id(tree_lista)
                mostra_aula()
                botao_desfazer.destroy()

                for falta in faltas:
                    utils.cria_falta([falta[0], falta[1], falta[2]])

            # Botão desfazer deleção de aluno
            botao_desfazer = Button(frame_info, command=undo_apaga, anchor=CENTER, text='DESFAZER', width=9,
                                    overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
            botao_desfazer.place(x=726, y=110)

        except IndexError:
            messagebox.showerror("Erro", "Selecione uma aula na tabela.")

    # Função pesquisa aula
    def pesquisa_aula():
        global undo_list

        nome = entry_procura.get()

        nome = nome.lower()

        try:
            dados = utils.pesquisa_aula(nome)

            undo_list = [dados[1], dados[2], dados[3], dados[4]]

            valor_id = dados[0]

            # Limpa os campos
            entry_procura.delete(0, END)
            entry_nome_aula.delete(0, END)
            entry_hora.set24Hrs(0)
            entry_hora.setMins(0)

            hora = dados[3].split(":")

            minuto = hora[1]
            hora = hora[0]

            # Inserindo dados nas entrys
            entry_nome_aula.insert(0, dados[1])
            combobox_dia.set(dados[2])
            entry_hora.set24Hrs(hora)
            entry_hora.setMins(minuto)
            combobox_turma.set(dados[4])

            def atualiza():
                global botao_undo

                valor_hora = entry_hora.time()

                # Dados da aula
                nome = entry_nome_aula.get()
                dia = combobox_dia.get()
                hora = f"{valor_hora[0]}:{valor_hora[1]}"
                turma = combobox_turma.get()

                # Lista dos dados
                lista = [valor_id, nome, dia, hora, turma]

                # Verifica se os campos fora preenchidos
                for item in lista:
                    if item == "":
                        messagebox.showerror(
                            "Erro", "Preencha os campos corretamente.")
                        return

                # Confirmação para atualizar
                res = messagebox.askquestion(
                    'Confirmação', 'Deseja alterar os dados deste aluno?')

                if res == 'yes':
                    # Atualizando dados da aula
                    utils.atualiza_aula(lista)
                else:
                    return

                # Mensagem de sucesso na alteração da aula
                messagebox.showinfo(
                    "Sucesso", "Os dados fora alterados com sucesso.")

                # Limpa os campos
                entry_nome_aula.delete(0, END)
                combobox_dia.set("")
                entry_hora.set24Hrs(0)
                entry_hora.setMins(0)
                combobox_turma.set("")

                # Destruindo Labels, Entry e botão desnecessários
                botao_salvar.destroy()

                # Atualiza tabela
                mostra_aula()

                # Botão desfazer alteração do aula
                botao_undo = Button(frame_info, command=undo_atualiza, anchor=CENTER, text='DESFAZER', width=10,
                                    overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
                botao_undo.place(x=726, y=110)

            # Botão salvar alterações da aula
            botao_salvar = Button(frame_info, command=atualiza, anchor=CENTER, text='Salvar alterações'.upper(
            ), overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
            botao_salvar.place(x=700, y=145)

        except:
            messagebox.showerror("Erro", "Aula não encontrada.")

    # Função mostra info da aula
    def info_aula():
        try:
            tree_itens = tree_aulas.focus()
            tree_dicionario = tree_aulas.item(tree_itens)
            tree_lista = tree_dicionario['values']

            # Limpa os campos
            entry_procura.delete(0, END)
            entry_nome_aula.delete(0, END)

            hora = tree_lista[3].split(":")

            minuto = hora[1]
            hora = hora[0]

            # Inserindo dados nas entrys
            entry_nome_aula.insert(0, tree_lista[1])
            combobox_dia.set(tree_lista[2])
            entry_hora.set24Hrs(hora)
            entry_hora.setMins(minuto)
            combobox_turma.set(tree_lista[4])

        except IndexError:
            messagebox.showerror("Erro", "Selecione uma aula na tabela.")

    # Label e entry do Nome da aula
    label_nome = Label(frame_info, text="Nome *",
                       height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_nome.place(x=10, y=10)

    entry_nome_aula = Entry(frame_info, width=45,
                            justify='left', relief=SOLID)
    entry_nome_aula.place(x=12, y=40)

    # Label e entry do dia
    label_dia = Label(frame_info, text="Dia da Semana *",
                      height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_dia.place(x=10, y=70)

    # Dias da semana
    dia_semana = ['Segunda-feira', 'Terça-feira',
                  'Quarta-feira', 'Quinta-feira', 'Sexta-feira']

    combobox_dia = ttk.Combobox(frame_info, width=20, font=fonte_botao)
    combobox_dia['values'] = dia_semana
    combobox_dia['state'] = 'readonly'
    combobox_dia.place(x=12, y=100)

    # Label e entry da hora de inicio
    label_hora = Label(frame_info, text="Hora de inicio *",
                       height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_hora.place(x=10, y=130)

    entry_hora = SpinTimePickerModern(frame_info)
    entry_hora.addAll(constants.HOURS24)
    entry_hora.configureAll(bg=AZUL_CLARO, height=1, fg=BRANCO, font=fonte_titulo, hoverbg=AZUL_CLARO,
                            hovercolor=AZUL_ESCURO, clickedbg=AZUL_ESCURO, clickedcolor=BRANCO)
    entry_hora.configure_separator(bg=AZUL_CLARO, fg=BRANCO)
    entry_hora.place(x=12, y=155)

    # Pegando as Turmas
    turmas = utils.mostra_turma()
    turma = []

    for item in turmas:
        turma.append(item[1])

    # Label e combobox do Sexo
    label_turma = Label(frame_info, text="Turma *",
                        height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_turma.place(x=167, y=130)

    combobox_turma = ttk.Combobox(frame_info, width=15, font=fonte_botao)
    combobox_turma['values'] = turma
    combobox_turma['state'] = 'readonly'
    combobox_turma.place(x=170, y=160)

    # Procura aula
    label_procura_nome = Label(frame_info, text="Procurar aula [Entrar com nome]",
                               height=1, anchor=NW, font=("Ivy, 10"), bg=AZUL_CLARO, fg=PRETO)
    label_procura_nome.place(x=620, y=10)

    entry_procura = Entry(frame_info, width=17,
                          justify='left', relief=SOLID, font=("Ivy, 10"))
    entry_procura.place(x=622, y=35)

    # Linha de separação
    label_linha = Label(frame_info, relief=GROOVE, text='h', width=1,
                        height=200, anchor=NW, font=("Ivy, 1"), bg=PRETO, fg=PRETO)
    label_linha.place(x=605, y=0)
    label_linha = Label(frame_info, relief=GROOVE, text='h', width=1,
                        height=200, anchor=NW, font=("Ivy, 1"), bg=BRANCO, fg=PRETO)
    label_linha.place(x=603, y=0)

    # ------------------------------------ Botões ---------------------------------

    # Botão adicionar aula
    botao_adicionar = Button(frame_info, command=nova_aula, anchor=CENTER, text='ADICIONAR', width=9,
                             overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
    botao_adicionar.place(x=617, y=110)

    # Botão alterar aula
    botao_alterar = Button(frame_info, command=carregar_aula, anchor=CENTER, text='ALTERAR',
                           width=9, overrelief=RIDGE, font=fonte_botao, bg=AZUL_ESCURO, foreground=BRANCO)
    botao_alterar.place(x=617, y=145)

    # Botão deletar aula
    botao_deletar = Button(frame_info, command=apagar_aula, anchor=CENTER, text='DELETAR', width=9,
                           overrelief=RIDGE, font=fonte_botao, bg=VERMELHO, foreground=BRANCO)
    botao_deletar.place(x=617, y=180)

    # Botão informações do aula
    botao_mostrar = Button(frame_info, command=info_aula, anchor=CENTER, text='INFO', width=9,
                           overrelief=RIDGE, font=fonte_botao, bg=AZUL_ESCURO, foreground=BRANCO)
    botao_mostrar.place(x=727, y=180)

    # Botão pesquisa aula
    botao_procurar = Button(frame_info, command=pesquisa_aula, text="Pesquisar",
                            font=fonte_botao, compound=LEFT, overrelief=RIDGE, bg=AZUL_ESCURO, fg=BRANCO)
    botao_procurar.place(x=757, y=33)
    # ---------------------------------- Tabela das aulas -------------------------------------

    def mostra_aula():
        tabela_aula_label = Label(frame_info, text="Tabela de aulas",
                                  height=1, relief="flat", anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
        tabela_aula_label.place(x=0, y=210)

        lista_cabecalho = ['ID', 'Nome', 'Dia', 'Hora', 'ID Turma']

        lista_itens = utils.mostra_aula()

        global tree_aulas

        tree_aulas = ttk.Treeview(
            frame_tabela, selectmode="extended", columns=lista_cabecalho, show='headings')

        # Scrollbars
        scroll_vertical = ttk.Scrollbar(
            frame_tabela, orient='vertical', command=tree_aulas.yview)
        scroll_horizontal = ttk.Scrollbar(
            frame_tabela, orient="horizontal", command=tree_aulas.xview)

        tree_aulas.configure(yscrollcommand=scroll_vertical,
                             xscrollcommand=scroll_horizontal)

        tree_aulas.place(x=0, y=0, width=WIDTH - 60, height=200)
        scroll_vertical.place(x=WIDTH - 60, y=0 + 1, height=200)
        scroll_horizontal.place(x=0, y=200, width=WIDTH - 60)

        posicao_coluna = ["nw", "nw", "nw", "nw",
                          "nw"]
        largura_coluna = [60, 150, 150, 70, 150]
        cont = 0

        for coluna in lista_cabecalho:
            tree_aulas.heading(coluna, text=coluna.title(), anchor=NW)
            tree_aulas.column(
                coluna, width=largura_coluna[cont], anchor=posicao_coluna[cont])

            cont += 1

        for item in lista_itens:
            tree_aulas.insert('', 'end', values=item)

        # Desfaz a ação de atualizar o aluno

    def undo_atualiza():
        global undo_list, botao_undo
        utils.atualiza_aula(undo_list)
        mostra_aula()
        botao_undo.destroy()

    # Botão desfazer alteração do aula
    botao_undo = Button(frame_info, command=undo_atualiza, anchor=CENTER, text='DESFAZER', width=10,
                        overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
    botao_undo.place(x=726, y=110)

    botao_undo.destroy()

    mostra_aula()

# Função da relação de faltas


def faltas():
    # ------------------------------------------------- Titulo da página ----------------------------------------------------
    global titulo_cadastro_label

    titulo_cadastro_label = Label(frame_titulo_aluno, image=icone_titulo_faltas, text="Faltas",
                                  width=WIDTH, compound=LEFT, relief=RAISED, anchor=NW, font=fonte_titulo, bg=AZUL_ESCURO, fg=BRANCO)
    titulo_cadastro_label.place(x=0, y=0)
    ttk.Separator(pagina_cadastro, orient=HORIZONTAL).place(
        x=0, y=52, width=WIDTH)

    # ------------------------------------------------- Detalhes das faltas ---------------------------------------------------

    global dados_falta
    dados_falta = []

    # Pesquisa os dados de faltas do aluno
    def pesquisa_faltas_aluno():
        global dados_falta
        valor_ra = entry_procura_aluno.get().upper()
        entry_procura_aluno.delete(0, END)
        try:
            dados_falta = utils.pesquisa_falta_aluno(valor_ra)
            mostra_falta("aluno")
        except:
            messagebox.showerror("Erro", "Aluno não encontrado.")

    # Pesquisa os dados de faltas da aula
    def pesquisa_faltas_aula():
        global dados_falta
        nome_aula = entry_procura_aula.get().lower()
        entry_procura_aula.delete(0, END)
        try:
            dados_falta = utils.pesquisa_falta_aula(nome_aula)
            mostra_falta("aula")
        except:
            messagebox.showerror("Erro", "Aula não encontrada.")

    # Procura por aluno
    label_procura_aluno = Label(frame_tabela, text="Procurar aluno [Entrar com RA]",
                                height=1, anchor=NW, font=("Ivy, 10"), bg=AZUL_CLARO, fg=PRETO)
    label_procura_aluno.place(x=40, y=10)

    entry_procura_aluno = Entry(frame_tabela, width=17,
                                justify='left', relief=SOLID, font=("Ivy, 10"))
    entry_procura_aluno.place(x=42, y=35)

    # Botão pesquisa aluno
    botao_procura_aluno = Button(frame_tabela, command=pesquisa_faltas_aluno, text="Pesquisar Aluno",
                                 font=fonte_botao, compound=LEFT, overrelief=RIDGE, bg=AZUL_ESCURO, fg=BRANCO)
    botao_procura_aluno.place(x=167, y=33)

    # Procura por aula
    label_procura_aula = Label(frame_tabela, text="Procurar aula [Entrar com nome]",
                               height=1, anchor=NW, font=("Ivy, 10"), bg=AZUL_CLARO, fg=PRETO)
    label_procura_aula.place(x=310, y=10)

    entry_procura_aula = Entry(frame_tabela, width=17,
                               justify='left', relief=SOLID, font=("Ivy, 10"))
    entry_procura_aula.place(x=312, y=35)

    # Botão pesquisa aula
    botao_procurar_aula = Button(frame_tabela, command=pesquisa_faltas_aula, text="Pesquisar Aula",
                                 font=fonte_botao, compound=LEFT, overrelief=RIDGE, bg=AZUL_ESCURO, fg=BRANCO)
    botao_procurar_aula.place(x=439, y=33)

    # Botão mostra tabela de faltas, sem pesquisa
    botao_procurar_aula = Button(frame_tabela, command=lambda: mostra_falta(""), text="Cancelar procura",
                                 font=fonte_botao, compound=LEFT, overrelief=RIDGE, bg=AZUL_ESCURO, fg=BRANCO)
    botao_procurar_aula.place(x=610, y=33)

    # ---------------------------------- Tabela das faltas -------------------------------------

    def mostra_falta(tipo):
        global dados_falta

        frame_info['height'] = 370
        frame_tabela.place(x=0, y=118+380)

        lista_cabecalho = ['ID', 'RA',
                           'Nome do Aluno', 'Aula', 'Turma', 'Faltas']

        if tipo == "":
            lista_itens = utils.mostra_falta()
        elif tipo == "aluno" or tipo == "aula":
            lista_itens = dados_falta
            dados_falta = []

        tree_faltas = ttk.Treeview(
            frame_info, selectmode="extended", columns=lista_cabecalho, show='headings')

        # Scrollbars
        scroll_vertical = ttk.Scrollbar(
            frame_info, orient='vertical', command=tree_faltas.yview)
        scroll_horizontal = ttk.Scrollbar(
            frame_info, orient="horizontal", command=tree_faltas.xview)

        tree_faltas.configure(yscrollcommand=scroll_vertical,
                              xscrollcommand=scroll_horizontal)

        tree_faltas.place(x=0, y=10, width=WIDTH - 60, height=340)
        scroll_vertical.place(x=WIDTH - 60, y=10, height=350)
        scroll_horizontal.place(x=0, y=350, width=WIDTH - 60)

        posicao_coluna = ["nw", "nw", "nw", "nw",
                          "nw", "nw"]
        largura_coluna = [40, 60, 150, 70, 150, 60]
        cont = 0

        for coluna in lista_cabecalho:
            tree_faltas.heading(coluna, text=coluna.title(), anchor=NW)
            tree_faltas.column(
                coluna, width=largura_coluna[cont], anchor=posicao_coluna[cont])

            cont += 1

        for item in lista_itens:
            tree_faltas.insert('', 'end', values=item)

    mostra_falta("")


# Função de cadastro de cameras

def cameras():
    # ------------------------------------------------- Titulo da página ----------------------------------------------------
    global titulo_cadastro_label

    titulo_cadastro_label = Label(frame_titulo_aluno, image=icone_titulo_camera, text="Cadastro de cameras",
                                  width=WIDTH, compound=LEFT, relief=RAISED, anchor=NW, font=fonte_titulo, bg=AZUL_ESCURO, fg=BRANCO)
    titulo_cadastro_label.place(x=0, y=0)
    ttk.Separator(pagina_cadastro, orient=HORIZONTAL).place(
        x=0, y=52, width=WIDTH)

    # ------------------------------------------------- Detalhes da Camera ---------------------------------------------------

    # Função nova camera
    def nova_camera():
        try:
            nome = entry_nome_camera.get()
            ip = entry_ip.get()
            usuario = entry_usuario.get()
            senha = entry_senha.get()

            lista = [nome, ip, usuario, senha]

            # Se os campos não forem preenchidos corretamente
            for item in lista:
                if item == "":
                    messagebox.showerror("Erro", "Preencha todos os campos")
                    return

            # Cria a camera
            utils.cria_camera(lista)

            messagebox.showinfo(
                "Sucesso", "Os dados foram inseridos com sucesso")

            entry_nome_camera.delete(0, END)
            entry_ip.delete(0, END)
            entry_usuario.delete(0, END)
            entry_senha.delete(0, END)

            mostra_camera()
        except:
            messagebox.showerror("Erro", "IP já registrado")

    # Função carregar/atualizar curso
    def carregar_camera():
        global undo_list
        try:
            tree_itens = tree_cameras.focus()
            tree_dicionario = tree_cameras.item(tree_itens)
            tree_lista = tree_dicionario['values']

            # Salva o id
            valor_id = tree_lista[0]

            dados = utils.pesquisa_camera_id(valor_id)
            undo_list = dados

            # Limpa os campos
            entry_nome_camera.delete(0, END)
            entry_ip.delete(0, END)
            entry_usuario.delete(0, END)
            entry_senha.delete(0, END)

            # Insere dados nas Entrys
            entry_nome_camera.insert(0, dados[1])
            entry_ip.insert(0, dados[2])
            entry_usuario.insert(0, dados[3])
            entry_senha.insert(0, dados[4])

            # Atualiza
            def atualiza():
                global botao_undo
                nome = entry_nome_camera.get()
                ip = entry_ip.get()
                usuario = entry_usuario.get()
                senha = entry_senha.get()

                lista = [valor_id, nome, ip, usuario, senha]

                # Se os campos não forem preenchidos corretamente
                for item in lista:
                    if item == "":
                        messagebox.showerror(
                            "Erro", "Preencha todos os campos")
                        return

                # Confirmação para apagar
                res = messagebox.askquestion(
                    'Confirmação', 'Deseja alterar os dados desta camera?')

                if res == 'yes':
                    # Atualiza os dados da camera
                    utils.atualiza_camera(lista)
                else:
                    return

                messagebox.showinfo(
                    "Sucesso", "Os dados foram atualizados com sucesso")

                # Limpa os campos
                entry_nome_camera.delete(0, END)
                entry_ip.delete(0, END)
                entry_usuario.delete(0, END)
                entry_senha.delete(0, END)

                botao_salvar.destroy()

                # atualiza os dados da tabela
                mostra_camera()

                # Botão desfazer alteração do aula
                botao_undo = Button(frame_info, command=undo_atualiza, anchor=CENTER, text='DESFAZER', width=9,
                                    overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
                botao_undo.place(x=726, y=110)

            botao_salvar = Button(frame_info, command=atualiza, anchor=CENTER, text="Salvar alterações".upper(
            ), overrelief=RIDGE, font=fonte_botao, bg=VERDE, fg=BRANCO)
            botao_salvar.place(x=700, y=145)

        except IndexError:
            messagebox.showerror("Erro", "Selecione uma camera na tabela.")

    # Função apagar camera
    def apagar_camera():
        try:
            tree_itens = tree_cameras.focus()
            tree_dicionario = tree_cameras.item(tree_itens)
            tree_lista = tree_dicionario['values']

            # Salva o id
            valor_id = tree_lista[0]

            dados = utils.pesquisa_camera_id(valor_id)

            # Confirmação para apagar
            res = messagebox.askquestion(
                'Confirmação', 'Deseja apagar os dados desta camera?')

            if res == 'yes':
                # Apagando os dados do curso
                utils.apaga_camera(valor_id)
            else:
                return

            messagebox.showinfo(
                "Sucesso", "Os dados foram apagados com sucesso")

            # atualiza os dados da tabela
            mostra_camera()

            # Desfaz a ação de apagar o aluno
            def undo_apaga():
                utils.cria_camera([dados[1], dados[2], dados[3], dados[4]])
                mostra_camera()
                botao_desfazer.destroy()

            # Botão desfazer deleção de aluno
            botao_desfazer = Button(frame_info, command=undo_apaga, anchor=CENTER, text='DESFAZER', width=9,
                                    overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
            botao_desfazer.place(x=726, y=110)

        except IndexError:
            messagebox.showerror("Erro", "Selecione uma camera na tabela.")

    # Função pesquisa camera
    def pesquisa_camera():
        global undo_list
        ip = entry_procura.get()

        try:
            dados = utils.pesquisa_camera(ip)

            undo_list = dados

            valor_id = dados[0]

            # Limpa os campos
            entry_procura.delete(0, END)
            entry_nome_camera.delete(0, END)
            entry_ip.delete(0, END)
            entry_usuario.delete(0, END)
            entry_senha.delete(0, END)

            # Inserindo dados nas entrys
            entry_nome_camera.insert(0, dados[1])
            entry_ip.insert(0, dados[2])
            entry_usuario.insert(0, dados[3])
            entry_senha.insert(0, dados[4])

            def atualiza():
                global botao_undo
                # Dados da camera
                nome = entry_nome_camera.get()
                ip = entry_ip.get()
                usuario = entry_usuario.get()
                senha = entry_senha.get()

                # Lista dos dados
                lista = [valor_id, nome, ip, usuario, senha]

                # Verifica se os campos fora preenchidos
                for item in lista:
                    if item == "":
                        messagebox.showerror(
                            "Erro", "Preencha os campos corretamente.")
                        return

                # Confirmação para atualizar
                res = messagebox.askquestion(
                    'Confirmação', 'Deseja alterar os dados deste aluno?')

                if res == 'yes':
                    # Atualizando dados da camera
                    utils.atualiza_camera(lista)
                else:
                    return

                # Mensagem de sucesso na alteração da camera
                messagebox.showinfo(
                    "Sucesso", "Os dados fora alterados com sucesso.")

                # Limpa os campos
                entry_nome_camera.delete(0, END)
                entry_ip.delete(0, END)
                entry_usuario.delete(0, END)
                entry_senha.delete(0, END)

                # Destruindo Labels, Entry e botão desnecessários
                botao_salvar.destroy()

                # Atualiza tabela
                mostra_camera()

                # Botão desfazer alteração do aula
                botao_undo = Button(frame_info, command=undo_atualiza, anchor=CENTER, text='DESFAZER', width=10,
                                    overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
                botao_undo.place(x=726, y=110)

            # Botão salvar alterações da camera
            botao_salvar = Button(frame_info, command=atualiza, anchor=CENTER, text='Salvar alterações'.upper(
            ), overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
            botao_salvar.place(x=700, y=145)

        except:
            messagebox.showerror("Erro", "Camera não encontrada.")

    # Função mostra info da camera
    def info_camera():
        try:
            tree_itens = tree_cameras.focus()
            tree_dicionario = tree_cameras.item(tree_itens)
            tree_lista = tree_dicionario['values']

            # Limpa os campos
            entry_nome_camera.delete(0, END)
            entry_ip.delete(0, END)
            entry_usuario.delete(0, END)
            entry_senha.delete(0, END)

            # Insere dados nas Entrys
            entry_nome_camera.insert(0, tree_lista[1])
            entry_ip.insert(0, tree_lista[2])
            entry_usuario.insert(0, tree_lista[3])
            entry_senha.insert(0, tree_lista[4])

        except IndexError:
            messagebox.showerror("Erro", "Selecione uma camera na tabela.")

    def mostra_imagem():
        try:
            tree_itens = tree_cameras.focus()
            tree_dicionario = tree_cameras.item(tree_itens)
            tree_lista = tree_dicionario['values']

            # Salva o id
            valor_id = tree_lista[0]

            dados = utils.pesquisa_camera_id(valor_id)

            utils.mostra_video_camera(dados)

        except IndexError:
            messagebox.showerror("Erro", "Selecione uma camera na tabela.")

    # Label e entry do Nome da camera
    label_nome = Label(frame_info, text="Nome *",
                       height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_nome.place(x=10, y=10)

    entry_nome_camera = Entry(frame_info, width=45,
                              justify='left', relief=SOLID)
    entry_nome_camera.place(x=12, y=40)

    # Label e entry do ip
    label_ip = Label(frame_info, text="IP *",
                     height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_ip.place(x=10, y=70)

    entry_ip = Entry(frame_info, width=45,
                     justify='left', relief=SOLID)
    entry_ip.place(x=12, y=100)

    # Label e entry do usuario
    label_usuario = Label(frame_info, text="Usuario *",
                          height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_usuario.place(x=10, y=130)

    entry_usuario = Entry(frame_info, width=20,
                          justify='left', relief=SOLID)
    entry_usuario.place(x=12, y=160)

    # Label e combobox do Sexo
    label_senha = Label(frame_info, text="Senha *", height=1,
                        anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_senha.place(x=157, y=130)

    entry_senha = Entry(frame_info, width=20,
                        justify='left', relief=SOLID)
    entry_senha['show'] = "*"
    entry_senha.place(x=160, y=160)

    # Procura Aluno
    label_procura_nome = Label(frame_info, text="Procurar camera [Entrar com ip]",
                               height=1, anchor=NW, font=("Ivy, 10"), bg=AZUL_CLARO, fg=PRETO)
    label_procura_nome.place(x=620, y=10)

    entry_procura = Entry(frame_info, width=17,
                          justify='left', relief=SOLID, font=("Ivy, 10"))
    entry_procura.place(x=622, y=35)

    # Linha de separação
    label_linha = Label(frame_info, relief=GROOVE, text='h', width=1,
                        height=200, anchor=NW, font=("Ivy, 1"), bg=PRETO, fg=PRETO)
    label_linha.place(x=605, y=0)
    label_linha = Label(frame_info, relief=GROOVE, text='h', width=1,
                        height=200, anchor=NW, font=("Ivy, 1"), bg=BRANCO, fg=PRETO)
    label_linha.place(x=603, y=0)

    # ------------------------------------ Botões ---------------------------------

    # Botão adicionar camera
    botao_adicionar = Button(frame_info, command=nova_camera, anchor=CENTER, text='ADICIONAR', width=9,
                             overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
    botao_adicionar.place(x=617, y=110)

    # Botão alterar camera
    botao_alterar = Button(frame_info, command=carregar_camera, anchor=CENTER, text='ALTERAR',
                           width=9, overrelief=RIDGE, font=fonte_botao, bg=AZUL_ESCURO, foreground=BRANCO)
    botao_alterar.place(x=617, y=145)

    # Botão deletar camera
    botao_deletar = Button(frame_info, command=apagar_camera, anchor=CENTER, text='DELETAR', width=9,
                           overrelief=RIDGE, font=fonte_botao, bg=VERMELHO, foreground=BRANCO)
    botao_deletar.place(x=617, y=180)

    # Botão informações do camera
    botao_mostrar = Button(frame_info, command=info_camera, anchor=CENTER, text='INFO', width=9,
                           overrelief=RIDGE, font=fonte_botao, bg=AZUL_ESCURO, foreground=BRANCO)
    botao_mostrar.place(x=727, y=180)

    # Botão pesquisa camera
    botao_procurar = Button(frame_info, command=pesquisa_camera, text="Pesquisar",
                            font=fonte_botao, compound=LEFT, overrelief=RIDGE, bg=AZUL_ESCURO, fg=BRANCO)
    botao_procurar.place(x=757, y=33)

    # Botão mostra visão da camera
    botao_imagem = Button(frame_info, command=mostra_imagem, anchor=CENTER, text='Mostrar Vídeo', width=13,
                          overrelief=RIDGE, font=fonte_botao, bg=AZUL_ESCURO, foreground=BRANCO)
    botao_imagem.place(x=665, y=75)

    # ---------------------------------- Tabela das cameras -------------------------------------

    def mostra_camera():
        tabela_camera_label = Label(frame_info, text="Tabela de cameras",
                                    height=1, relief="flat", anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
        tabela_camera_label.place(x=0, y=210)

        lista_cabecalho = ['ID', 'Nome', 'IP', 'Usuario']

        lista_itens = utils.mostra_camera()

        global tree_cameras

        tree_cameras = ttk.Treeview(
            frame_tabela, selectmode="extended", columns=lista_cabecalho, show='headings')

        # Scrollbars
        scroll_vertical = ttk.Scrollbar(
            frame_tabela, orient='vertical', command=tree_cameras.yview)
        scroll_horizontal = ttk.Scrollbar(
            frame_tabela, orient="horizontal", command=tree_cameras.xview)

        tree_cameras.configure(yscrollcommand=scroll_vertical,
                               xscrollcommand=scroll_horizontal)

        tree_cameras.place(x=0, y=0, width=WIDTH - 60, height=200)
        scroll_vertical.place(x=WIDTH - 60, y=0 + 1, height=200)
        scroll_horizontal.place(x=0, y=200, width=WIDTH - 60)

        posicao_coluna = ["nw", "nw", "nw", "nw"]
        largura_coluna = [60, 150, 150, 70]
        cont = 0

        for coluna in lista_cabecalho:
            tree_cameras.heading(coluna, text=coluna.title(), anchor=NW)
            tree_cameras.column(
                coluna, width=largura_coluna[cont], anchor=posicao_coluna[cont])

            cont += 1

        for item in lista_itens:
            tree_cameras.insert('', 'end', values=item)

    def undo_atualiza():
        global undo_list, botao_undo
        utils.atualiza_camera(undo_list)
        mostra_camera()
        botao_undo.destroy()

    # Botão desfazer alteração do aula
    botao_undo = Button(frame_info, command=undo_atualiza, anchor=CENTER, text='DESFAZER', width=9,
                        overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
    botao_undo.place(x=726, y=110)

    botao_undo.destroy()

    mostra_camera()

# Função para voltar


def voltar():
    alunos()
    show_frame(pagina_inicial)

# Função de troca de janelas


def controle(comando_botao):

    frame_info['height'] = 230
    frame_tabela.place(x=0, y=118+240)

    for widget in frame_info.winfo_children():
        widget.destroy()

    for widget in frame_tabela.winfo_children():
        widget.destroy()

    titulo_cadastro_label.destroy()

    if comando_botao == 'alunos':
        alunos()

    if comando_botao == 'cursos':
        cursos_turmas()

    if comando_botao == 'aulas':
        aulas()

    if comando_botao == 'faltas':
        faltas()

    if comando_botao == 'cameras':
        cameras()

    if comando_botao == 'voltar':
        voltar()

# ------------------------ Botões de navegação -----------------------------


icone_aluno_cadastro = Image.open('images/icon_aluno_2.png')
icone_aluno_cadastro = icone_aluno_cadastro.resize((20, 20))
icone_aluno_cadastro = ImageTk.PhotoImage(icone_aluno_cadastro)

botao_cadastro = Button(frame_aluno_botoes, command=lambda: controle('alunos'), image=icone_aluno_cadastro,
                        text="Alunos", width=100, compound=LEFT, overrelief=RIDGE, font=fonte, bg=AZUL_ESCURO, fg=BRANCO)
botao_cadastro.place(x=10, y=30)

icone_cursos = Image.open('images/icon_cursos.png')
icone_cursos = icone_cursos.resize((20, 20))
icone_cursos = ImageTk.PhotoImage(icone_cursos)

botao_cursos = Button(frame_aluno_botoes, command=lambda: controle('cursos'), image=icone_cursos,
                      text="Cursos/Turmas", width=130, compound=LEFT, overrelief=RIDGE, font=fonte, bg=AZUL_ESCURO, fg=BRANCO)
botao_cursos.place(x=130, y=30)

icone_aula = Image.open('images/icon_aula.png')
icone_aula = icone_aula.resize((20, 20))
icone_aula = ImageTk.PhotoImage(icone_aula)

botao_aula = Button(frame_aluno_botoes, command=lambda: controle('aulas'), image=icone_aula,
                    text=" Aula", width=100, compound=LEFT, overrelief=RIDGE, font=fonte, bg=AZUL_ESCURO, fg=BRANCO)
botao_aula.place(x=280, y=30)

icone_faltas = Image.open('images/icon_falta.png')
icone_faltas = icone_faltas.resize((20, 20))
icone_faltas = ImageTk.PhotoImage(icone_faltas)

botao_faltas = Button(frame_aluno_botoes, command=lambda: controle('faltas'), image=icone_faltas,
                      text="Faltas", width=100, compound=LEFT, overrelief=RIDGE, font=fonte, bg=AZUL_ESCURO, fg=BRANCO)
botao_faltas.place(x=400, y=30)

icone_camera = Image.open('images/icon_camera.png')
icone_camera = icone_camera.resize((20, 20))
icone_camera = ImageTk.PhotoImage(icone_camera)

botao_camera = Button(frame_aluno_botoes, command=lambda: controle('cameras'), image=icone_camera,
                      text="Cameras", width=100, compound=LEFT, overrelief=RIDGE, font=fonte, bg=AZUL_ESCURO, fg=BRANCO)
botao_camera.place(x=520, y=30)

icone_voltar = Image.open('images/icon_voltar.png')
icone_voltar = icone_voltar.resize((20, 20))
icone_voltar = ImageTk.PhotoImage(icone_voltar)

botao_voltar = Button(frame_aluno_botoes, command=lambda: controle('voltar'), image=icone_voltar,
                      text=" Voltar", width=100, compound=LEFT, overrelief=RIDGE, font=fonte, bg=AZUL_ESCURO, fg=BRANCO)
botao_voltar.place(x=640, y=30)

ttk.Separator(pagina_cadastro, orient=HORIZONTAL).place(
    x=0, y=118, width=WIDTH)

# ===================================== Método de inicialização =========================================

# Primeira "janela" na tela de cadastros é a de alunos
alunos()

# Ao fechar pelo "X" da janela, encerra todos os processos
janela.protocol("WM_DELETE_WINDOW", sair_app)

# ===================================== Main loop =========================================

# Janela principal


def run():
    janela.mainloop()

# Inicia as schedules


def run_schedules():
    while True:
        schedule.run_pending()


# "IF" necessário para não gerar subprocessos
if __name__ == "__main__":
    # Multiprocessamento
    with concurrent.futures.ProcessPoolExecutor() as executor:
        codigo_janela = executor.submit(run)
        codigo_dia_semana = executor.submit(run_schedules)
