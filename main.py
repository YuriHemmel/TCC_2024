import utils
import os
import re
import Banco
import tkinter as tk
import cv2
import sys
from dotenv import load_dotenv
from tkinter import *  # Interface gráfica
from tkinter import messagebox  # Caixa de mensagem para confirmações
from tkinter import ttk
from tkinter import filedialog as fd
from tkcalendar import Calendar, DateEntry
from datetime import *
from email_utils import envia_email_alerta
from PIL import Image, ImageTk

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
pagina_cameras = Frame(janela)
pagina_cadastro = Frame(janela)
pagina_alunos = Frame(janela)

# Fontes
fonte = ("Ivy", 11)
fonte_titulo = ("Ivy", 15, 'bold')
fonte_botao = ("Ivy", 8, 'bold')

# Adicionando as páginas
paginas = (pagina_inicial, pagina_cameras, pagina_cadastro, pagina_alunos)

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

# Cadastra pessoas no banco de dados
def cadastra_pessoa():
    # Padrões de regex para cada campo ser validado
    PATTERN_RA = "^[A-z0-9]{7}$"
    PATTERN_NOME = "^(?=^.{2,60}$)^[A-ZÀÁÂĖÈÉÊÌÍÒÓÔÕÙÚÛÇ][a-zàáâãèéêìíóôõùúç]+(?:[ ](?:das?|dos?|de|e|[A-ZÀÁÂĖÈÉÊÌÍÒÓÔÕÙÚÛÇ][a-zàáâãèéêìíóôõùúç]+))*$"
    PATTERN_EMAIL = "^[a-z0-9.]+@aluno\.unip\.br$"

    dados = [pagina_cadastro_pessoa_id.get(), pagina_cadastro_pessoa_nome.get(),
             pagina_cadastro_pessoa_email.get()]

    # Verifica se os campos estão vazios
    for d in dados:
        if d.strip() == "":
            pagina_cadastro_pessoa_label.config(
                text="Por favor, preencha os\ncampos corretamente.")
            return

    # Valida os campos com regex -> RA/ID, nome e email
    ra_valido = re.match(PATTERN_RA, dados[0])
    if ra_valido is None:
        pagina_cadastro_pessoa_label.config(
            text="ID inválido!\nPor favor, preencha o\ncampo de ID corretamente.")
        return

    nome_valido = re.match(PATTERN_NOME, dados[1])
    if nome_valido is None:
        pagina_cadastro_pessoa_label.config(
            text="Nome inválido!\nPor favor, preencha o\ncampo de nome corretamente.")
        return

    email_valido = re.match(PATTERN_EMAIL, dados[2])
    if email_valido is None:
        pagina_cadastro_pessoa_label.config(
            text="Email inválido!\nPor favor, preencha o\ncampo de email corretamente.")
        return

    if pagina_cadastro_pessoa_curso.get() == "Selecione um curso":
        pagina_cadastro_pessoa_label.config(
            text="Por favor, selecione um curso\nválido!")
        return

    # Tira foto em analise, vai falhar
    fotoBin = utils.recebe_foto_binario()

    # Verifica se os dados inseridos pertencem à uma pessoa já registrada
    try:
        pessoa = Pes.Pessoa(dados[0], dados[1], dados[2], 0, fotoBin,
                            utils.retorna_curso_id(pagina_cadastro_pessoa_curso.get()), 0)
        pessoa.insert_pessoa()
    except:  # Exception as e:
        # print(e)
        pagina_cadastro_pessoa_label.config(
            text="Pessoa já cadastrada\nanteriomente.")
        return

    # Cadastro bem sucedido
    pagina_cadastro_pessoa_label.config(text="Pessoa registrada com sucesso.")
    lista_pessoa.insert(0, f"RA: {dados[0]}     Nome: {dados[1]}")

    pagina_cadastro_pessoa_nome.delete(0, END)
    pagina_cadastro_pessoa_id.delete(0, END)
    pagina_cadastro_pessoa_email.delete(0, END)

    return


def conecta_camera():
    camSelecionada = lista_cameras.get(ACTIVE)

    if camSelecionada == "":
        messagebox.showinfo('Erro', 'Nenhuma câmera selecionada')
        return

    camSelecionada = camSelecionada.split()[3]

    cam = Cam.load_camera(camSelecionada)

    if cam[1] == "CameraTeste":
        cap = cv2.VideoCapture(0)

    else:
        user = cam[4]
        password = cam[3]
        ip = cam[2]
        port = '554'

        url = f"rtsp://{user}:{password}@{ip}:{port}/onvif1"

        print('Tentando conectar com ' + url)

        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Sem frame ou erro na captura de video")
            break

        cv2.imshow("VIDEO", frame)

        if cv2.waitKey(1) == ord('q'):
            print("Desconectando camera IP")
            break

    cap.release()
    cv2.destroyAllWindows()

# Inicia o programa
def inicia_app():
    # Lista de pessoas que não chegaram
    nao_chegaram = utils.verifica_chegada_aluno()

    # Manda email para cada um na lista
    for item in nao_chegaram:
        ra = item[0]
        aluno = item[1]
        email = item[2]
        envia_email_alerta(aluno, ra, email)
    return


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

botao_pagina_aluno = Button(pagina_inicial, command=lambda: show_frame(pagina_alunos), image=cadastro_icone, text="Cadastro geral".upper(),
                            compound=TOP, overrelief=RIDGE, anchor=CENTER, font=fonte, bg=AZUL_ESCURO, foreground=BRANCO)
botao_pagina_aluno['width'] = 160
botao_pagina_aluno['height'] = 160
botao_pagina_aluno.place(x=190 - 45, y=HEIGHT/2 - 80)

iniciar_icone = Image.open('images/icon_iniciar.png')
iniciar_icone = iniciar_icone.resize((50, 50))
iniciar_icone = ImageTk.PhotoImage(iniciar_icone)

botao_pagina_aluno = Button(pagina_inicial, command=lambda: inicia_app(), image=iniciar_icone, text="Iniciar".upper(),
                            compound=TOP, overrelief=RIDGE, anchor=CENTER, font=fonte, bg=AZUL_ESCURO, foreground=BRANCO)
botao_pagina_aluno['width'] = 160
botao_pagina_aluno['height'] = 160
botao_pagina_aluno.place(x=190*2 - 45, y=HEIGHT/2 - 80)

saida_icone = Image.open('images/icon_saida.png')
saida_icone = saida_icone.resize((50, 50))
saida_icone = ImageTk.PhotoImage(saida_icone)

botao_sair = Button(pagina_inicial, command=lambda: sys.exit(), image=saida_icone, text="Sair".upper(),
                    compound=TOP, overrelief=RIDGE, anchor=CENTER, font=fonte, bg=AZUL_ESCURO, foreground=BRANCO)
botao_sair['width'] = 160
botao_sair['height'] = 160
botao_sair.place(x=190*3 - 45, y=HEIGHT/2 - 80)

# ================ Pagina dos alunos =======================

pagina_alunos.configure(bg=AZUL_CLARO)

# -------------------------- Frames da página -------------------------------

# Frame Titulo
frame_titulo_aluno = Frame(pagina_alunos, width=WIDTH,
                           height=52, bg=AZUL_ESCURO)
frame_titulo_aluno.place(x=0, y=0)

# Frame dos botões
frame_aluno_botoes = Frame(
    pagina_alunos, width=WIDTH, height=65, bg=AZUL_CLARO)
frame_aluno_botoes.place(x=0, y=53)

# Frame do conteúdo / informações
frame_info = Frame(pagina_alunos, width=WIDTH,
                   height=230, bg=AZUL_CLARO, padx=10)
frame_info.place(x=0, y=118)

# Frame das tabelas
frame_tabela = Frame(pagina_alunos, width=WIDTH,
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

icone_titulo_camera = Image.open('images/icon_camera.png')
icone_titulo_camera = icone_titulo_camera.resize((50, 50))
icone_titulo_camera = ImageTk.PhotoImage(icone_titulo_camera)

# ------------------------ Funções / Sub-paginas de alunos -----------------------------

# Função de cadastro de alunos
def alunos():
    # Titulo da página
    global titulo_cadastro_label

    titulo_cadastro_label = Label(frame_titulo_aluno, image=icone_titulo_aluno, text="Cadastro de alunos",
                                  width=WIDTH, compound=LEFT, relief=RAISED, anchor=NW, font=fonte_titulo, bg=AZUL_ESCURO, fg=BRANCO)
    titulo_cadastro_label.place(x=0, y=0)
    ttk.Separator(pagina_alunos, orient=HORIZONTAL).place(
        x=0, y=52, width=WIDTH)

    # ------------------------------------------------- Detalhes do Aluno ---------------------------------------------------

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

            lista = [ra, nome, email, telefone, sexo, foto, turma]

            # Verifica se os campos fora preenchidos
            for item in lista:
                if item == "":
                    messagebox.showerror(
                        "Erro", "Preencha os campos corretamente.")
                    return

            # Criando aluno
            utils.cria_aluno(lista)

            # Mensagem de sucesso na criação do aluno
            messagebox.showinfo(
                "Sucesso", "Os dados fora inseridos com sucesso.")

            entry_ra.delete(0, END)
            entry_nome_aluno.delete(0, END)
            entry_email.delete(0, END)
            entry_telefone.delete(0, END)
            combobox_sexo.delete(0, END)
            combobox_turma.delete(0, END)

            mostra_alunos()
        except:
            messagebox.showerror("Erro", "RA já cadastrado")

    # Carrega informações do aluno
    def carregar_aluno():
        global aluno_foto, label_foto, foto_string

        try:
            tree_itens = tree_alunos.focus()
            tree_dicionario = tree_alunos.item(tree_itens)
            tree_lista = tree_dicionario["values"]

            # Guarda RA antigo
            ra_antigo = tree_lista[0]

            # Limpa os campos
            entry_ra.delete(0, END)
            entry_nome_aluno.delete(0, END)
            entry_email.delete(0, END)
            entry_telefone.delete(0, END)
            combobox_sexo.delete(0, END)
            combobox_turma.delete(0, END)

            # Label e Entry das faltas
            label_faltas = Label(frame_info, text="Faltas",
                                 height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
            label_faltas.place(x=451, y=10)

            entry_faltas = Entry(frame_info, width=10,
                                 justify=LEFT, relief=SOLID)
            entry_faltas.place(x=455, y=40)

            # Inserindo dados nas entrys
            entry_ra.insert(0, tree_lista[0])
            entry_nome_aluno.insert(0, tree_lista[1])
            entry_email.insert(0, tree_lista[2])
            entry_telefone.insert(0, tree_lista[3])
            combobox_sexo.set(tree_lista[4])
            combobox_turma.set(tree_lista[6])
            entry_faltas.insert(0, tree_lista[7])

            aluno_foto = tree_lista[5]
            foto_string = aluno_foto

            # Inserindo foto do Aluno na tela
            aluno_foto = Image.open(aluno_foto)
            aluno_foto = aluno_foto.resize((130, 130))
            aluno_foto = ImageTk.PhotoImage(aluno_foto)

            label_foto = Label(frame_info, image=aluno_foto,
                               bg=AZUL_CLARO, fg=BRANCO)
            label_foto.place(x=300, y=10)

            def atualiza():

                # Dados do aluno
                ra = entry_ra.get()
                nome = entry_nome_aluno.get()
                email = entry_email.get()
                telefone = entry_telefone.get()
                sexo = combobox_sexo.get()
                foto = foto_string
                turma = combobox_turma.get()
                faltas = entry_faltas.get()

                # Lista dos dados
                lista = [ra, nome, email, telefone,
                         sexo, foto, turma, faltas, ra_antigo]

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
                label_faltas.destroy()
                entry_faltas.destroy()
                botao_salvar.destroy()

                # Atualiza tabela
                mostra_alunos()

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

            # Confirmação para apagar
            res = messagebox.askquestion(
                'Confirmação', 'Deseja apagar os dados deste aluno?')

            if res == 'yes':
                # Apagando os dados do aluno
                utils.apaga_aluno(valor_ra)
            else:
                return

            messagebox.showinfo(
                "Sucesso", "Os dados foram apagados com sucesso")

            mostra_alunos()

        except IndexError:
            messagebox.showerror("Erro", "Selecione um aluno na tabela.")

    # Pesquisa informações do aluno pelo RA
    def pesquisa_aluno():
        global aluno_foto, label_foto, foto_string

        valor_ra = entry_procura.get()

        try:
            dados = utils.pesquisa_aluno(valor_ra)

            # Limpa os campos
            entry_procura.delete(0, END)
            entry_ra.delete(0, END)
            entry_nome_aluno.delete(0, END)
            entry_email.delete(0, END)
            entry_telefone.delete(0, END)
            combobox_sexo.delete(0, END)
            combobox_turma.delete(0, END)

            # Label e Entry das faltas
            label_faltas = Label(frame_info, text="Faltas",
                                 height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
            label_faltas.place(x=451, y=10)

            entry_faltas = Entry(frame_info, width=10,
                                 justify=LEFT, relief=SOLID)
            entry_faltas.place(x=455, y=40)

            # Inserindo dados nas entrys
            entry_ra.insert(0, dados[0])
            entry_nome_aluno.insert(0, dados[1])
            entry_email.insert(0, dados[2])
            entry_telefone.insert(0, dados[3])
            combobox_sexo.set(dados[4])
            combobox_turma.set(dados[6])
            entry_faltas.insert(0, dados[7])

            aluno_foto = dados[5]
            foto_string = aluno_foto

            # Inserindo foto do Aluno na tela
            aluno_foto = Image.open(aluno_foto)
            aluno_foto = aluno_foto.resize((130, 130))
            aluno_foto = ImageTk.PhotoImage(aluno_foto)

            label_foto = Label(frame_info, image=aluno_foto,
                               bg=AZUL_CLARO, fg=BRANCO)
            label_foto.place(x=300, y=10)

            def atualiza():

                # Dados do aluno
                ra = entry_ra.get()
                nome = entry_nome_aluno.get()
                email = entry_email.get()
                telefone = entry_telefone.get()
                sexo = combobox_sexo.get()
                foto = foto_string
                turma = combobox_turma.get()
                faltas = entry_faltas.get()

                # Lista dos dados
                lista = [ra, nome, email, telefone,
                         sexo, foto, turma, faltas, valor_ra]

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
                label_faltas.destroy()
                entry_faltas.destroy()
                botao_salvar.destroy()

                # Atualiza tabela
                mostra_alunos()

            # Botão salvar alterações do aluno
            botao_salvar = Button(frame_info, command=atualiza, anchor=CENTER, text='Salvar alterações'.upper(
            ), overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
            botao_salvar.place(x=700, y=145)

        except:
            label_faltas.destroy()
            entry_faltas.destroy()
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
            combobox_sexo.delete(0, END)
            combobox_turma.delete(0, END)

            # Label e Entry das faltas
            label_faltas = Label(frame_info, text="Faltas",
                                 height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
            label_faltas.place(x=451, y=10)

            entry_faltas = Entry(frame_info, width=10,
                                 justify=LEFT, relief=SOLID)
            entry_faltas.place(x=455, y=40)

            # Inserindo dados nas entrys
            entry_ra.insert(0, tree_lista[0])
            entry_nome_aluno.insert(0, tree_lista[1])
            entry_email.insert(0, tree_lista[2])
            entry_telefone.insert(0, tree_lista[3])
            combobox_sexo.set(tree_lista[4])
            combobox_turma.set(tree_lista[6])
            entry_faltas.insert(0, tree_lista[7])

            aluno_foto = tree_lista[5]
            foto_string = aluno_foto

            # Inserindo foto do Aluno na tela
            aluno_foto = Image.open(aluno_foto)
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

        aluno_foto = fd.askopenfilename()
        foto_string = aluno_foto

        # Abrindo imagem
        aluno_foto = Image.open(aluno_foto)
        aluno_foto = aluno_foto.resize((130, 130))
        aluno_foto = ImageTk.PhotoImage(aluno_foto)

        label_foto = Label(frame_info, image=aluno_foto,
                           bg=AZUL_CLARO, fg=BRANCO)
        label_foto.place(x=300, y=10)

        botao_carregar['text'] = "TROCAR DE FOTO"

    # Botão Carregar
    botao_carregar = Button(frame_info, command=escolhe_imagem, text='Carregar foto'.upper(
    ), width=18, compound=CENTER, overrelief=RIDGE, anchor=CENTER, font=fonte_botao, bg=AZUL_ESCURO, foreground=BRANCO)
    botao_carregar.place(x=300, y=160)

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

    def mostra_alunos():
        tabela_alunos_label = Label(frame_info, text="Tabela de alunos",
                                    height=1, relief="flat", anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
        tabela_alunos_label.place(x=0, y=210)

        lista_cabecalho = ['RA', 'Nome', 'Email',
                           'Telefone', 'Sexo', 'Foto', 'Turma', 'Faltas']

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
                          "center", "center", "center", "center"]
        largura_coluna = [60, 150, 150, 70, 70, 70, 80, 100]
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
    ttk.Separator(pagina_alunos, orient=HORIZONTAL).place(
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

    # Função novo curso
    def novo_curso():
        nome = entry_nome_curso.get()
        duracao = entry_duracao.get()
        preco = entry_preco.get()

        lista = [nome, duracao, preco]

        # Se os campos não forem preenchidos corretamente
        for item in lista:
            if item == "":
                messagebox.showerror("Erro", "Preencha todos os campos")
                return

        # Cria o Curso
        utils.cria_curso(lista)

        messagebox.showinfo("Sucesso", "Os dados foram inseridos com sucesso")

        entry_nome_curso.delete(0, END)
        entry_duracao.delete(0, END)
        entry_preco.delete(0, END)

        mostra_cursos()

    # Função carregar/atualizar curso
    def carregar_curso():
        try:
            tree_itens = tree_cursos.focus()
            tree_dicionario = tree_cursos.item(tree_itens)
            tree_lista = tree_dicionario['values']

            # Salva o id
            valor_id = tree_lista[0]

            # Limpa os campos
            entry_nome_curso.delete(0, END)
            entry_duracao.delete(0, END)
            entry_preco.delete(0, END)

            # Insere dados nas Entrys
            entry_nome_curso.insert(0, tree_lista[1])
            entry_duracao.insert(0, tree_lista[2])
            entry_preco.insert(0, tree_lista[3])

            # Atualiza
            def atualiza():

                nome = entry_nome_curso.get()
                duracao = entry_duracao.get()
                preco = entry_preco.get()

                lista = [valor_id, nome, duracao, preco]

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
                entry_preco.delete(0, END)

                # atualiza os dados da tabela
                mostra_cursos()

                botao_salvar.destroy()

            botao_salvar = Button(frame_info, command=atualiza, anchor=CENTER, text="Salvar alterações".upper(
            ), overrelief=RIDGE, font=fonte_botao, bg=VERDE, fg=BRANCO)
            botao_salvar.place(x=235, y=130)
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

    # Label e entry do Preço do curso
    label_preco = Label(frame_info, text="Preço *",
                        height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_preco.place(x=10, y=130)

    entry_preco = Entry(frame_info, width=10,
                        justify='left', relief=SOLID)
    entry_preco.place(x=12, y=160)

    # Botão salvar curso
    botao_curso_adicionar = Button(frame_info, command=novo_curso, anchor=CENTER, text='ADICIONAR', width=10,
                                   overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
    botao_curso_adicionar.place(x=107, y=160)

    # Botão atualizar curso
    botao_curso_alterar = Button(frame_info, command=carregar_curso, anchor=CENTER, text='ALTERAR',
                                 width=10, overrelief=RIDGE, font=fonte_botao, bg=AZUL_ESCURO, foreground=BRANCO)
    botao_curso_alterar.place(x=197, y=160)

    # Botão deletar curso
    botao_curso_deletar = Button(frame_info, command=apagar_curso, anchor=CENTER, text='DELETAR', width=10,
                                 overrelief=RIDGE, font=fonte_botao, bg=VERMELHO, foreground=BRANCO)
    botao_curso_deletar.place(x=287, y=160)

    # Mostra Tabela Cursos
    def mostra_cursos():
        tabela_cursos_label = Label(frame_info, text="Tabela de cursos",
                                    height=1, relief="flat", anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
        tabela_cursos_label.place(x=0, y=210)

        lista_cabecalho = ['ID', 'Curso', 'Duração', 'Preço']

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

        posicao_coluna = ["nw", "nw", "e", "e"]
        largura_coluna = [30, 150, 80, 60]
        cont = 0

        for coluna in lista_cabecalho:
            tree_cursos.heading(coluna, text=coluna.title(), anchor=NW)
            tree_cursos.column(
                coluna, width=largura_coluna[cont], anchor=posicao_coluna[cont])

            cont += 1

        for item in lista_itens:
            tree_cursos.insert('', 'end', values=item)

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

    # Função novo turma
    def nova_turma():
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

        messagebox.showinfo("Sucesso", "Os dados foram inseridos com sucesso")

        entry_nome_turma.delete(0, END)
        combobox_curso.delete(0, END)
        data_inicio.delete(0, END)

        # Atualiza a tabela
        mostra_turmas()

    # Função carregar/atualizar turma
    def carregar_turma():
        try:
            tree_itens = tree_turma.focus()
            tree_dicionario = tree_turma.item(tree_itens)
            tree_lista = tree_dicionario['values']

            # Salva o id
            valor_id = tree_lista[0]

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

    mostra_turmas()

# Função de cadastro de cameras
def cameras():
    # ------------------------------------------------- Titulo da página ----------------------------------------------------
    global titulo_cadastro_label

    titulo_cadastro_label = Label(frame_titulo_aluno, image=icone_titulo_camera, text="Cadastro de cameras",
                                  width=WIDTH, compound=LEFT, relief=RAISED, anchor=NW, font=fonte_titulo, bg=AZUL_ESCURO, fg=BRANCO)
    titulo_cadastro_label.place(x=0, y=0)
    ttk.Separator(pagina_alunos, orient=HORIZONTAL).place(
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

            messagebox.showinfo("Sucesso", "Os dados foram inseridos com sucesso")

            entry_nome_camera.delete(0, END)
            entry_ip.delete(0, END)
            entry_usuario.delete(0, END)
            entry_senha.delete(0, END)

            mostra_camera()
        except:
            messagebox.showerror("Erro", "IP já registrado")

    # Função carregar/atualizar curso
    def carregar_camera():
        try:
            tree_itens = tree_cameras.focus()
            tree_dicionario = tree_cameras.item(tree_itens)
            tree_lista = tree_dicionario['values']

            # Salva o id
            valor_id = tree_lista[0]

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

            # Atualiza
            def atualiza():

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

                # atualiza os dados da tabela
                mostra_camera()

                botao_salvar.destroy()

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

        except IndexError:
            messagebox.showerror("Erro", "Selecione uma camera na tabela.")

    # Função pesquisa camera
    def pesquisa_camera():

        ip = entry_procura.get()

        try:
            dados = utils.pesquisa_camera(ip)

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

            # Salva o id
            valor_id = tree_lista[0]

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
    label_senha = Label(frame_info, text="Senha *",
                        height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_senha.place(x=157, y=130)

    entry_senha = Entry(frame_info, width=20,
                        justify='left', relief=SOLID)
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

    # ---------------------------------- Tabela das cameras -------------------------------------

    def mostra_camera():
        tabela_camera_label = Label(frame_info, text="Tabela de cameras",
                                    height=1, relief="flat", anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
        tabela_camera_label.place(x=0, y=210)

        lista_cabecalho = ['ID', 'Nome', 'IP', 'Usuario', 'Senha']

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

        posicao_coluna = ["nw", "nw", "nw", "nw",
                          "nw"]
        largura_coluna = [60, 150, 150, 70, 70]
        cont = 0

        for coluna in lista_cabecalho:
            tree_cameras.heading(coluna, text=coluna.title(), anchor=NW)
            tree_cameras.column(
                coluna, width=largura_coluna[cont], anchor=posicao_coluna[cont])

            cont += 1

        for item in lista_itens:
            tree_cameras.insert('', 'end', values=item)

    mostra_camera()

# Função para voltar
def voltar():
    alunos()
    show_frame(pagina_inicial)

# Função de troca de janelas


def controle(comando_botao):

    if comando_botao == 'alunos':
        for widget in frame_info.winfo_children():
            widget.destroy()

        for widget in frame_tabela.winfo_children():
            widget.destroy()

        titulo_cadastro_label.destroy()
        alunos()

    if comando_botao == 'cursos':
        for widget in frame_info.winfo_children():
            widget.destroy()

        for widget in frame_tabela.winfo_children():
            widget.destroy()

        titulo_cadastro_label.destroy()
        cursos_turmas()

    if comando_botao == 'cameras':
        for widget in frame_info.winfo_children():
            widget.destroy()

        for widget in frame_tabela.winfo_children():
            widget.destroy()

        titulo_cadastro_label.destroy()
        cameras()

    if comando_botao == 'voltar':
        for widget in frame_info.winfo_children():
            widget.destroy()

        for widget in frame_tabela.winfo_children():
            widget.destroy()

        titulo_cadastro_label.destroy()
        voltar()

# ------------------------ Botões de navegação -----------------------------


icone_cadastro = Image.open('images/icon_aluno_2.png')
icone_cadastro = icone_cadastro.resize((20, 20))
icone_cadastro = ImageTk.PhotoImage(icone_cadastro)

botao_cadastro = Button(frame_aluno_botoes, command=lambda: controle('alunos'), image=icone_cadastro,
                        text="Alunos", width=100, compound=LEFT, overrelief=RIDGE, font=fonte, bg=AZUL_ESCURO, fg=BRANCO)
botao_cadastro.place(x=10, y=30)

icone_cursos = Image.open('images/icon_cursos.png')
icone_cursos = icone_cursos.resize((20, 20))
icone_cursos = ImageTk.PhotoImage(icone_cursos)

botao_cursos = Button(frame_aluno_botoes, command=lambda: controle('cursos'), image=icone_cursos,
                      text="Cursos/Turmas", width=130, compound=LEFT, overrelief=RIDGE, font=fonte, bg=AZUL_ESCURO, fg=BRANCO)
botao_cursos.place(x=130, y=30)

icone_camera = Image.open('images/icon_camera.png')
icone_camera = icone_camera.resize((20, 20))
icone_camera = ImageTk.PhotoImage(icone_camera)

botao_camera = Button(frame_aluno_botoes, command=lambda: controle('cameras'), image=icone_camera,
                      text="Cameras", width=100, compound=LEFT, overrelief=RIDGE, font=fonte, bg=AZUL_ESCURO, fg=BRANCO)
botao_camera.place(x=280, y=30)

icone_voltar = Image.open('images/icon_voltar.png')
icone_voltar = icone_voltar.resize((20, 20))
icone_voltar = ImageTk.PhotoImage(icone_voltar)

botao_voltar = Button(frame_aluno_botoes, command=lambda: controle('voltar'), image=icone_voltar,
                      text=" Voltar", width=100, compound=LEFT, overrelief=RIDGE, font=fonte, bg=AZUL_ESCURO, fg=BRANCO)
botao_voltar.place(x=400, y=30)

ttk.Separator(pagina_alunos, orient=HORIZONTAL).place(x=0, y=118, width=WIDTH)

# ================ Método de inicialização =======================

alunos()

# ================ Main Loop =======================

janela.mainloop()