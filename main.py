import utils
import os
import re
import Banco
import Camera as Cam
import Pessoa as Pes
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

TEMP_ID = ""
TAMANHO_BOTAO = 15

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
pagina_cadastro_pessoa = Frame(janela)
pagina_alunos = Frame(janela)
pagina_list_pessoa = Frame(janela)
pagina_edit_pessoa = Frame(janela)

# Fontes
fonte = ("Ivy", 11)
fonte_titulo = ("Arial", 13, 'bold')
fonte_icone = ("Ivy", 15, 'bold')
fonte_botao = ("Ivy", 8, 'bold')

# Adicionando as páginas
paginas = (pagina_inicial, pagina_cameras, pagina_cadastro,
           pagina_cadastro_pessoa, pagina_list_pessoa, pagina_edit_pessoa, pagina_alunos)

# Adiciona os frames nas páginas
for frame in paginas:
    frame.grid(row=0, column=0, sticky='nsew')

# Lista de cursos
lista_cursos = tk.StringVar()

# Mostra o Frame que queremos


def show_frame(frame):
    frame.tkraise()


# Primeira página a aparecer
#show_frame(pagina_inicial)
show_frame(pagina_alunos)


# Cria o banco de dados se não existir ainda
db = Banco.Banco()


# Lista as cameras já cadastradas no sistema
def listar_cameras():
    cams = Cam.list_camera()

    for c in cams:
        lista_cameras.insert(c[0], f"Nome: {c[1]}       IP: {c[2]}")


# Lista pessoas já cadastradas no sistema
def listar_pessoas():
    pessoas = Pes.list_pessoa()

    for p in pessoas:
        lista_pessoa.insert(0, f"RA: {p[0]}     Nome: {p[1]}")


# Cadastra câmeras no banco de dados
def cadastra_camera():
    # Recebe as informações de cada campo do formulário
    dados = [pagina_cadastro_nome.get(), pagina_cadastro_ip.get(),
             pagina_cadastro_senha.get(), pagina_cadastro_usuario.get()]

    # Verifica se os campos estão vazios
    for d in dados:
        if d.strip() == "":
            pagina_cadastro_label.config(
                text="Por favor, preencha os\ncampos corretamente.")
            return

    # Verifica se os dados inseridos pertencem à uma câmera já registrada
    try:
        camera = Cam.Camera(dados[0], dados[1], dados[2], dados[3])
        camera.insert_camera()

    except:  # Exception as e:
        pagina_cadastro_label.config(
            text="Câmera já cadastrada\nanteriormente.")
        return

    # Cadastro bem sucedido
    pagina_cadastro_label.config(text="Camera registrada com sucesso.")
    lista_cameras.insert(END, f"Nome: {dados[0]}  IP: {dados[1]}")

    pagina_cadastro_nome.delete(0, END)
    pagina_cadastro_ip.delete(0, END)
    pagina_cadastro_usuario.delete(0, END)
    pagina_cadastro_senha.delete(0, END)

    return


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


def guarda_id(valor):
    global TEMP_ID

    TEMP_ID = valor


def direciona_editar_pessoa():
    selecionada = lista_pessoa.get(ACTIVE)

    # Se não tiver pessoa registrada, dá erro
    if selecionada == "":
        messagebox.showinfo('Erro', 'Nenhuma pessoa selecionada')
        return

    selecionada = selecionada.split()[1]

    pessoa = Pes.load_pessoa(selecionada)

    # pessoa[0] = ID
    # pessoa[1] = Nome
    # pessoa[2] = Email
    # pessoa[3] = faltas
    # pessoa[4] = foto
    # pessoa[5] = id do curso
    # pessoa[6] = presença no dia

    pagina_edit_pessoa_nome.insert(index=0, string=f"{pessoa[1]}")
    pagina_edit_pessoa_email.insert(index=0, string=f"{pessoa[2]}")
    pagina_edit_pessoa_falta.insert(index=0, string=f"{pessoa[3]}")
    pagina_edit_pessoa_curso.set(f"{utils.retorna_curso_nome(pessoa[5])}")

    guarda_id(pessoa[0])

    show_frame(pagina_edit_pessoa)


# Salva novas informações no banco
def alterar_info(varId):
    dados = [pagina_edit_pessoa_nome.get(), pagina_edit_pessoa_email.get(),
             pagina_edit_pessoa_falta.get()]

    # Verifica se os campos estão vazios
    for d in dados:
        if d == "":
            messagebox.showinfo('Erro', 'Preencha os campos corretamente')
            return

    res = messagebox.askquestion(
        'Confirmação', f'Deseja alterar os dados de {varId}?')

    if res == 'yes':
        for pessoa in lista_pessoa.curselection():
            lista_pessoa.delete(pessoa)
            lista_pessoa.insert(pessoa, f"ID: {varId} Nome: {dados[0]}")
        Pes.altera_dados(varId, dados[0], dados[1], dados[2], utils.retorna_curso_id(
            pagina_edit_pessoa_curso.get()))


# Indo para a página de cadastro (atualiza o campo de nome automáticamente)
def show_pag_cadastro():
    # pagina_cadastro_nome.insert(index=1, string=f"Camera{Cam.conta_camera()}")
    show_frame(pagina_cadastro)


# Limpa os campos da página de cadastro de câmera
def volta_pag_cadastro():
    pagina_cadastro_nome.delete(0, END)
    pagina_cadastro_ip.delete(0, END)
    pagina_cadastro_senha.delete(0, END)
    pagina_cadastro_label.config(text="")

    show_frame(pagina_inicial)


# Limpa os campos da página de editar pessoas
def volta_pag_edit_pessoa():
    pagina_edit_pessoa_nome.delete(0, END)
    pagina_edit_pessoa_email.delete(0, END)
    pagina_edit_pessoa_falta.delete(0, END)

    guarda_id("")

    show_frame(pagina_list_pessoa)


# Limpa os campos da página de cadastro de pessoa
def volta_pag_pessoa():
    pagina_cadastro_pessoa_nome.delete(0, END)
    pagina_cadastro_pessoa_id.delete(0, END)
    pagina_cadastro_pessoa_email.delete(0, END)
    pagina_cadastro_pessoa_label.config(text="")

    show_frame(pagina_inicial)


# Apaga camera do banco de dados
def confirma_apagar_camera():
    camSelecionada = lista_cameras.get(ACTIVE)

    # Se não tiver câmera registrada, dá erro
    if camSelecionada == "":
        messagebox.showinfo('Erro', 'Nenhuma câmera selecionada')
        return

    camSelecionada = camSelecionada.split()[1]

    # Cria caixa de mensagem para confirmação
    res = messagebox.askquestion(
        "Apagar câmera", f"Deseja apagar informações da câmera: {camSelecionada}?")

    if res == 'yes':
        lista_cameras.delete(lista_cameras.curselection())
        Cam.delete_camera(camSelecionada)


# Apaga pessoa do banco de dados
def confirma_apagar_pessoa():
    selecionada = lista_pessoa.get(ACTIVE)

    # Se não tiver pessoa registrada, dá erro
    if selecionada == "":
        messagebox.showinfo('Erro', 'Nenhuma pessoa selecionada')
        return

    # Pega o nome da pessoa
    nome_selecionado = selecionada.split()[3::]

    # Se a pessoa só tiver o primeiro nome cadastrado, não aparecer "primeiroNome primeiroNome ra"
    if nome_selecionado[0] == nome_selecionado[len(nome_selecionado) - 1]:
        nome = f"{nome_selecionado[0]}"
    else:
        nome = f"{nome_selecionado[0]} {nome_selecionado[len(nome_selecionado) - 1]}"

    # Pega o ID
    selecionada = selecionada.split()[1]

    # Cria caixa de mensagem para confirmação
    res = messagebox.askquestion(
        "Apagar pessoa", f"Deseja apagar informações de {nome} {selecionada}?")

    if res == 'yes':
        lista_pessoa.delete(lista_pessoa.curselection())
        Pes.delete_pessoa(selecionada)


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

# Manda mensagem por email


def inicia_app():
    nao_chegaram = Pes.verifica_chegada()

    for item in nao_chegaram:
        ID = item[0]
        email = Pes.recebe_email_por_ID(ID)
        aluno = Pes.recebe_nome_por_ID(ID)
        envia_email_alerta(aluno, ID, email)
    return


# ================ Pagina inicial =======================


pagina_inicial.configure(bg=AZUL_CLARO)

pagina_inicial_titulo = Label(
    pagina_inicial, text="Menu Inicial", font=fonte_titulo)
pagina_inicial_titulo.configure(bg=AZUL_CLARO)
pagina_inicial_titulo.place(x=WIDTH/2 - 45, y=20)


pagina_inicial_camsLabel = Label(
    pagina_inicial, text="Lista de câmera", font=fonte)
pagina_inicial_camsLabel.configure(bg=AZUL_CLARO)
pagina_inicial_camsLabel.place(x=60 - 10, y=105)

pagina_inicial_cams = Button(pagina_inicial, text="Lista de cameras",
                             font=fonte, command=lambda: show_frame(pagina_cameras))
pagina_inicial_cams['width'] = TAMANHO_BOTAO
pagina_inicial_cams.place(x=50 - 10, y=135)

pagina_inicial_listPesLabel = Label(
    pagina_inicial, text="Listar Pessoas", font=fonte)
pagina_inicial_listPesLabel.configure(bg=AZUL_CLARO)
pagina_inicial_listPesLabel.place(x=65 - 10, y=210)

pagina_inicial_listPes = Button(pagina_inicial, text="Lista de pessoas",
                                font=fonte, command=lambda: show_frame(pagina_list_pessoa))
pagina_inicial_listPes['width'] = TAMANHO_BOTAO
pagina_inicial_listPes.place(x=50 - 10, y=240)

pagina_inicial_iniciaLabel = Label(
    pagina_inicial, text="Iniciar app", font=fonte)
pagina_inicial_iniciaLabel.configure(bg=AZUL_CLARO)
pagina_inicial_iniciaLabel.place(x=280 - 10, y=105)

pagina_inicial_inicia = Button(pagina_inicial, text="Iniciar",
                               font=fonte, command=lambda: inicia_app())
pagina_inicial_inicia['width'] = TAMANHO_BOTAO
pagina_inicial_inicia.place(x=250 - 10, y=135)

pagina_inicial_sairLabel = Label(
    pagina_inicial, text="Sair do app", font=fonte)
pagina_inicial_sairLabel.configure(bg=AZUL_CLARO)
pagina_inicial_sairLabel.place(x=265, y=210)

pagina_inicial_sair = Button(
    pagina_inicial, text="Sair", font=fonte, command=lambda: sys.exit())
pagina_inicial_sair['width'] = TAMANHO_BOTAO
pagina_inicial_sair.place(x=240, y=240)

pagina_inicial_cadLabel = Label(
    pagina_inicial, text="Cadastrar câmeras", font=fonte)
pagina_inicial_cadLabel.configure(bg=AZUL_CLARO)
pagina_inicial_cadLabel.place(x=330 + 111, y=105)

pagina_inicial_cadastro = Button(
    pagina_inicial, text="Cadastrar Câmera", font=fonte, command=lambda: show_pag_cadastro())
pagina_inicial_cadastro['width'] = TAMANHO_BOTAO
pagina_inicial_cadastro.place(x=330 + 108, y=135)

pagina_inicial_pessoaLabel = Label(
    pagina_inicial, text="Cadastrar pessoas", font=fonte)
pagina_inicial_pessoaLabel.configure(bg=AZUL_CLARO)
pagina_inicial_pessoaLabel.place(x=330 + 112, y=210)

pagina_inicial_pessoa = Button(
    pagina_inicial, text="Cadastrar Pessoa", font=fonte, command=lambda: show_frame(pagina_cadastro_pessoa))
pagina_inicial_pessoa['width'] = TAMANHO_BOTAO
pagina_inicial_pessoa.place(x=330 + 108, y=240)

# ================ Pagina dos alunos =======================

pagina_alunos.configure(bg=AZUL_CLARO)

# -------------------------- Frames da página -------------------------------

# Frame "Cadastro de Aluno"
frame_titulo = Frame(pagina_alunos, width=WIDTH, height=52, bg=AZUL_ESCURO)
frame_titulo.place(x=0, y=0)

# Frame dos botões
frame_aluno_botoes = Frame(
    pagina_alunos, width=WIDTH, height=65, bg=AZUL_CLARO)
frame_aluno_botoes.place(x=0, y=53)

# Frame do conteúdo / informações
frame_aluno_info = Frame(pagina_alunos, width=WIDTH,
                         height=230, bg=AZUL_CLARO, padx=10)
frame_aluno_info.place(x=0, y=118)

# Frame das tabelas
frame_aluno_tabela = Frame(pagina_alunos, width=WIDTH,
                           height=250, bg=AZUL_CLARO, padx=10)
frame_aluno_tabela.place(x=0, y=118+240)

# ----------------------------- Título ----------------------------------

aluno_icone_titulo = Image.open('images/icon_student.png')
aluno_icone_titulo = aluno_icone_titulo.resize((50, 50))
aluno_icone_titulo = ImageTk.PhotoImage(aluno_icone_titulo)

aluno_icone_titulo_label = Label(frame_titulo, image=aluno_icone_titulo, text="Cadastro de alunos",
                                 width=WIDTH, compound=LEFT, relief=RAISED, anchor=NW, font=fonte_icone, bg=AZUL_ESCURO, fg=BRANCO)
aluno_icone_titulo_label.place(x=0, y=0)

ttk.Separator(pagina_alunos, orient=HORIZONTAL).place(x=0, y=52, width=WIDTH)

# ------------------------ Funções / Sub-paginas de alunos -----------------------------

# Função de cadastro de alunos


def alunos():
    # Label e entry do Nome do aluno
    label_nome = Label(frame_aluno_info, text="Nome *",
                       height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_nome.place(x=10, y=10)

    entry_nome_curso = Entry(frame_aluno_info, width=45,
                             justify='left', relief=SOLID)
    entry_nome_curso.place(x=12, y=40)

    # Label e entry do email
    label_duracao = Label(frame_aluno_info, text="Email *",
                          height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_duracao.place(x=10, y=70)

    entry_duracao = Entry(frame_aluno_info, width=45,
                          justify='left', relief=SOLID)
    entry_duracao.place(x=12, y=100)

    # Label e entry do Telefone
    label_telefone = Label(frame_aluno_info, text="Telefone *",
                           height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_telefone.place(x=10, y=130)

    entry_telefone = Entry(frame_aluno_info, width=20,
                           justify='left', relief=SOLID)
    entry_telefone.place(x=12, y=160)

    # Label e combobox do Sexo
    label_sexo = Label(frame_aluno_info, text="Sexo *",
                       height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_sexo.place(x=190, y=130)

    combobox_sexo = ttk.Combobox(frame_aluno_info, width=12, font=fonte_botao)
    combobox_sexo['values'] = ['Masculino', 'Feminino']
    combobox_sexo['state'] = 'readonly'
    combobox_sexo.place(x=190, y=160)

    # Label e Entry das faltas
    label_faltas = Label(frame_aluno_info, text="Faltas",
                         height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_faltas.place(x=451, y=10)

    faltas = Entry(frame_aluno_info, width=10, justify=LEFT, relief=SOLID)
    faltas.place(x=455, y=40)

    # Label e entry do RA
    label_ra = Label(frame_aluno_info, text="RA *",
                     height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_ra.place(x=451, y=70)

    entry_ra = Entry(frame_aluno_info, width=20,
                     justify='left', relief=SOLID)
    entry_ra.place(x=455, y=100)

    # Pegando as Turmas
    turmas = ['Turma A', 'Turma B']
    turma = []

    for item in turmas:
        turma.append(item)

    # Label e combobox do Curso
    label_turma = Label(frame_aluno_info, text="Turma *",
                        height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_turma.place(x=451, y=130)

    combobox_turma = ttk.Combobox(frame_aluno_info, width=20, font=fonte_botao)
    combobox_turma['values'] = turma
    combobox_turma['state'] = 'readonly'
    combobox_turma.place(x=455, y=160)

    # Função para escolher imagem
    global aluno_foto, label_foto, foto_string

    def escolhe_imagem():
        global aluno_foto, label_foto, foto_string

        aluno_foto = fd.askopenfilename()
        foto_string = aluno_foto

        # Abrindo imagem
        aluno_foto = Image.open(aluno_foto)
        aluno_foto = aluno_foto.resize((130, 130))
        aluno_foto = ImageTk.PhotoImage(aluno_foto)

        label_foto = Label(frame_aluno_info, image=aluno_foto,
                           bg=AZUL_CLARO, fg=BRANCO)
        label_foto.place(x=300, y=10)

        botao_carregar['text'] = "TROCAR DE FOTO"

    # Botão Carregar
    botao_carregar = Button(frame_aluno_info, command=escolhe_imagem, text='Carregar foto'.upper(
    ), width=18, compound=CENTER, overrelief=RIDGE, anchor=CENTER, font=fonte_botao, bg=AZUL_ESCURO, foreground=BRANCO)
    botao_carregar.place(x=300, y=160)

    # Linha de separação
    label_linha = Label(frame_aluno_info, relief=GROOVE, text='h', width=1,
                        height=200, anchor=NW, font=("Ivy, 1"), bg=PRETO, fg=PRETO)
    label_linha.place(x=605, y=0)
    label_linha = Label(frame_aluno_info, relief=GROOVE, text='h', width=1,
                        height=200, anchor=NW, font=("Ivy, 1"), bg=BRANCO, fg=PRETO)
    label_linha.place(x=603, y=0)

    # Procura Aluno
    label_procura_nome = Label(frame_aluno_info, text="Procurar Aluno [Entrar com o nome]",
                               height=1, anchor=NW, font=("Ivy, 10"), bg=AZUL_CLARO, fg=PRETO)
    label_procura_nome.place(x=620, y=10)

    entry_procura_nome = Entry(frame_aluno_info, width=17,
                               justify='left', relief=SOLID, font=("Ivy, 10"))
    entry_procura_nome.place(x=622, y=35)

    botao_procurar = Button(frame_aluno_info, text='Procurar', width=9, overrelief=RIDGE,
                            anchor=CENTER, font=("Ivy, 8 bold"), bg=AZUL_ESCURO, foreground=BRANCO)
    botao_procurar.place(x=757, y=35)

    # Botões

    # Botão salvar aluno
    botao_salvar = Button(frame_aluno_info, anchor=CENTER, text='SALVAR', width=9,
                          overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
    botao_salvar.place(x=627, y=110)

    # Botão atualizar aluno
    botao_atualizar = Button(frame_aluno_info, anchor=CENTER, text='ATUALIZAR',
                             width=9, overrelief=RIDGE, font=fonte_botao, bg=AZUL_ESCURO, foreground=BRANCO)
    botao_atualizar.place(x=627, y=145)

    # Botão deletar aluno
    botao_deletar = Button(frame_aluno_info, anchor=CENTER, text='DELETAR', width=9,
                           overrelief=RIDGE, font=fonte_botao, bg=VERMELHO, foreground=BRANCO)
    botao_deletar.place(x=627, y=180)

    # Botão ver aluno
    botao_mostrar = Button(frame_aluno_info, anchor=CENTER, text='VER', width=9,
                           overrelief=RIDGE, font=fonte_botao, bg=AZUL_ESCURO, foreground=BRANCO)
    botao_mostrar.place(x=727, y=180)

    def mostra_alunos():
        tabela_alunos_label = Label(frame_aluno_info, text="Tabela de alunos",
                                    height=1, relief="flat", anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
        tabela_alunos_label.place(x=0, y=210)

        lista_cabecalho = ['RA', 'Nome', 'Email',
                           'Telefone', 'Sexo', 'imagem', 'Faltas', 'Curso']

        lista_itens = []

        global tree_alunos

        tree_alunos = ttk.Treeview(
            frame_aluno_tabela, selectmode="extended", columns=lista_cabecalho, show='headings')

        # Scrollbars
        scroll_vertical = ttk.Scrollbar(
            frame_aluno_tabela, orient='vertical', command=tree_alunos.yview)
        scroll_horizontal = ttk.Scrollbar(
            frame_aluno_tabela, orient="horizontal", command=tree_alunos.xview)

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


# Função para cursos e turmas


def cursos_turmas():
    # Tabela de cursos
    frame_tabela_cursos = Frame(
        frame_aluno_tabela, width=300, height=200, bg=AZUL_CLARO)
    frame_tabela_cursos.place(x=30, y=0)

    # Divisão entre cursos e turmas
    frame_linha = Frame(
        frame_aluno_tabela, width=15, height=200, bg=AZUL_CLARO)
    frame_linha.place(x=300 + 85, y=0)

    # Tabela de turmas
    frame_tabela_turma = Frame(
        frame_aluno_tabela, width=300, height=200, bg=AZUL_CLARO)
    frame_tabela_turma.place(x=300 + 150, y=0)

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
                        messagebox.showerror("Erro", "Preencha todos os campos")
                        return

                # Confirmação para apagar
                res = messagebox.askquestion('Confirmação', 'Deseja alterar os dados deste curso?')

                if res == 'yes':
                    # Atualiza os dados do curso
                    utils.atualiza_curso(lista)
                else:
                    return

                messagebox.showinfo("Sucesso", "Os dados foram atualizados com sucesso")

                entry_nome_curso.delete(0, END)
                entry_duracao.delete(0, END)
                entry_preco.delete(0, END)

                #atualiza os dados da tabela
                mostra_cursos()

                botao_salvar.destroy()

            botao_salvar = Button(frame_aluno_info, command=atualiza, anchor=CENTER, text="Salvar alterações".upper(), overrelief=RIDGE, font=fonte_botao, bg=VERDE, fg=BRANCO)
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
            res = messagebox.askquestion('Confirmação', 'Deseja apagar os dados deste curso?')

            if res == 'yes':
                # Apagando os dados do curso
                utils.apaga_curso(valor_id)
            else:
                return
            
            messagebox.showinfo("Sucesso", "Os dados foram apagados com sucesso")

            #atualiza os dados da tabela
            mostra_cursos()

        except IndexError:
            messagebox.showerror("Erro", "Selecione um curso na tabela.")

    # Label e entry do Nome do curso
    label_nome = Label(frame_aluno_info, text="Nome do Curso *",
                       height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_nome.place(x=10, y=10)

    entry_nome_curso = Entry(frame_aluno_info, width=35,
                             justify='left', relief=SOLID)
    entry_nome_curso.place(x=12, y=40)

    # Label e entry da Duração do curso
    label_duracao = Label(frame_aluno_info, text="Duração *",
                          height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_duracao.place(x=10, y=70)

    entry_duracao = Entry(frame_aluno_info, width=20,
                          justify='left', relief=SOLID)
    entry_duracao.place(x=12, y=100)

    # Label e entry do Preço do curso
    label_preco = Label(frame_aluno_info, text="Preço *",
                        height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_preco.place(x=10, y=130)

    entry_preco = Entry(frame_aluno_info, width=10,
                        justify='left', relief=SOLID)
    entry_preco.place(x=12, y=160)

    # Botão salvar curso
    botao_curso_adicionar = Button(frame_aluno_info, command=novo_curso, anchor=CENTER, text='ADICIONAR', width=10,
                                overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
    botao_curso_adicionar.place(x=107, y=160)

    # Botão atualizar curso
    botao_curso_alterar = Button(frame_aluno_info, command=carregar_curso, anchor=CENTER, text='ALTERAR',
                                   width=10, overrelief=RIDGE, font=fonte_botao, bg=AZUL_ESCURO, foreground=BRANCO)
    botao_curso_alterar.place(x=197, y=160)

    # Botão deletar curso
    botao_curso_deletar = Button(frame_aluno_info, command=apagar_curso, anchor=CENTER, text='DELETAR', width=10,
                                 overrelief=RIDGE, font=fonte_botao, bg=VERMELHO, foreground=BRANCO)
    botao_curso_deletar.place(x=287, y=160)

    # Mostra Tabela Cursos
    def mostra_cursos():
        tabela_cursos_label = Label(frame_aluno_info, text="Tabela de cursos",
                                    height=1, relief="flat", anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
        tabela_cursos_label.place(x=0, y=210)

        lista_cabecalho = ['ID', 'Curso', 'Duração', 'Preço']

        lista_itens = utils.mostra_curso()

        global tree_cursos

        tree_cursos = ttk.Treeview(
            frame_aluno_tabela, selectmode="extended", columns=lista_cabecalho, show='headings')

        # Scrollbars
        scroll_vertical = ttk.Scrollbar(
            frame_aluno_tabela, orient='vertical', command=tree_cursos.yview)
        scroll_horizontal = ttk.Scrollbar(
            frame_aluno_tabela, orient="horizontal", command=tree_cursos.xview)

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
    label_linha = Label(frame_aluno_info, relief=GROOVE, text='h', width=1,
                        height=200, anchor=NW, font=("Ivy, 1"), bg=PRETO, fg=PRETO)
    label_linha.place(x=390, y=0)
    label_linha = Label(frame_aluno_info, relief=GROOVE, text='h', width=1,
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
            combobox_curso.insert(0, tree_lista[2])
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
                        messagebox.showerror("Erro", "Preencha todos os campos")
                        return

                # Confirmação para apagar
                res = messagebox.askquestion('Confirmação', 'Deseja alterar os dados desta turma?')

                if res == 'yes':
                    # Atualiza os dados do turma
                    utils.atualiza_turma(lista)
                else:
                    return

                messagebox.showinfo("Sucesso", "Os dados foram atualizados com sucesso")

                entry_nome_turma.delete(0, END)
                combobox_curso.delete(0, END)
                data_inicio.delete(0, END)

                #atualiza os dados da tabela
                mostra_turmas()

                botao_salvar.destroy()

            botao_salvar = Button(frame_aluno_info, command=atualiza, anchor=CENTER, text="Salvar alterações".upper(), overrelief=RIDGE, font=fonte_botao, bg=VERDE, fg=BRANCO)
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
            res = messagebox.askquestion('Confirmação', 'Deseja apagar os dados deste turma?')

            if res == 'yes':
                # Apagando os dados do turma
                utils.apaga_turma(valor_id)
            else:
                return
            
            messagebox.showinfo("Sucesso", "Os dados foram apagados com sucesso")

            #atualiza os dados da tabela
            mostra_turmas()

        except IndexError:
            messagebox.showerror("Erro", "Selecione um turma na tabela.")

    label_nome = Label(frame_aluno_info, text="Nome Turma *",
                       height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_nome.place(x=404, y=10)
    entry_nome_turma = Entry(frame_aluno_info, width=35,
                             justify=LEFT, relief="solid")
    entry_nome_turma.place(x=407, y=40)

    label_curso_turma = Label(frame_aluno_info, text="Curso *",
                              height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_curso_turma.place(x=404, y=70)

    # Pegando os cursos
    cursos = utils.mostra_curso()
    curso = []

    for item in cursos:
        curso.append(item[1])

    combobox_curso = ttk.Combobox(frame_aluno_info, width=20, font=fonte_botao)
    combobox_curso['values'] = curso
    combobox_curso['state'] = 'readonly'
    combobox_curso.place(x=407, y=100)

    label_data_inicio = Label(frame_aluno_info, text="Data de início *",
                              height=1, anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
    label_data_inicio.place(x=406, y=130)

    data_inicio = DateEntry(frame_aluno_info, width=10, background=AZUL_ESCURO,
                            foreground=BRANCO, borderwidth=2, year=2023)
    data_inicio.place(x=407, y=160)

    # Botão adicionar turma
    botao_turma_adicionar = Button(frame_aluno_info, command=nova_turma, anchor=CENTER, text='ADICIONAR', width=10,
                                overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
    botao_turma_adicionar.place(x=507, y=160)

    # Botão alterar turma
    botao_turma_alterar = Button(frame_aluno_info, command=carregar_turma, anchor=CENTER, text='ALTERAR',
                                   width=10, overrelief=RIDGE, font=fonte_botao, bg=AZUL_ESCURO, foreground=BRANCO)
    botao_turma_alterar.place(x=597, y=160)

    # Botão deletar turma
    botao_turma_deletar = Button(frame_aluno_info, command=apagar_turma, anchor=CENTER, text='DELETAR', width=10,
                                 overrelief=RIDGE, font=fonte_botao, bg=VERMELHO, foreground=BRANCO)
    botao_turma_deletar.place(x=687, y=160)

    def mostra_turmas():
        tabela_turma_label = Label(frame_aluno_info, text="Tabela de turmas",
                                   height=1, relief="flat", anchor=NW, font=fonte, bg=AZUL_CLARO, fg=PRETO)
        tabela_turma_label.place(x=410, y=210)

        lista_cabecalho = ['ID', 'Nome da Turma', 'Curso', 'Inicio']

        lista_itens = utils.mostra_turma()

        global tree_turma

        tree_turma = ttk.Treeview(
            frame_aluno_tabela, selectmode="extended", columns=lista_cabecalho, show='headings')

        # Scrollbars
        scroll_vertical = ttk.Scrollbar(
            frame_aluno_tabela, orient='vertical', command=tree_turma.yview)
        scroll_horizontal = ttk.Scrollbar(
            frame_aluno_tabela, orient="horizontal", command=tree_turma.xview)

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

# Função para salvar


def salvar():
    print("Salvar")

# Função de troca de janelas


def controle(comando_botao):

    if comando_botao == 'cadastro':
        for widget in frame_aluno_info.winfo_children():
            widget.destroy()

        for widget in frame_aluno_tabela.winfo_children():
            widget.destroy()

        alunos()

    if comando_botao == 'cursos':
        for widget in frame_aluno_info.winfo_children():
            widget.destroy()

        for widget in frame_aluno_tabela.winfo_children():
            widget.destroy()

        cursos_turmas()

    if comando_botao == 'salvar':
        for widget in frame_aluno_info.winfo_children():
            widget.destroy()

        for widget in frame_aluno_tabela.winfo_children():
            widget.destroy()

        salvar()

# ------------------------ Botões de navegação -----------------------------


icone_aluno_cadastro = Image.open('images/icon_add.png')
icone_aluno_cadastro = icone_aluno_cadastro.resize((20, 20))
icone_aluno_cadastro = ImageTk.PhotoImage(icone_aluno_cadastro)

aluno_cadastro_botao = Button(frame_aluno_botoes, command=lambda: controle('cadastro'), image=icone_aluno_cadastro,
                              text="Cadastro", width=100, compound=LEFT, overrelief=RIDGE, font=fonte, bg=AZUL_ESCURO, fg=BRANCO)
aluno_cadastro_botao.place(x=10, y=30)

icone_aluno_cursos = Image.open('images/icon_cursos.png')
icone_aluno_cursos = icone_aluno_cursos.resize((20, 20))
icone_aluno_cursos = ImageTk.PhotoImage(icone_aluno_cursos)

aluno_cursos = Button(frame_aluno_botoes, command=lambda: controle('cursos'), image=icone_aluno_cursos,
                      text="Cursos/Turmas", width=130, compound=LEFT, overrelief=RIDGE, font=fonte, bg=AZUL_ESCURO, fg=BRANCO)
aluno_cursos.place(x=130, y=30)

icone_aluno_salvar = Image.open('images/icon_salvar.png')
icone_aluno_salvar = icone_aluno_salvar.resize((20, 20))
icone_aluno_salvar = ImageTk.PhotoImage(icone_aluno_salvar)

aluno_salvar = Button(frame_aluno_botoes, command=lambda: controle('salvar'), image=icone_aluno_salvar,
                      text="Salvar", width=100, compound=LEFT, overrelief=RIDGE, font=fonte, bg=AZUL_ESCURO, fg=BRANCO)
aluno_salvar.place(x=280, y=30)

ttk.Separator(pagina_alunos, orient=HORIZONTAL).place(x=0, y=118, width=WIDTH)


# ================ Pagina de Cadastro de Pessoas =======================

pagina_cadastro_pessoa.configure(bg=AZUL_CLARO)

pagina_cadastro_pessoa_titulo = Label(
    pagina_cadastro_pessoa, text="Cadastre a Pessoa", font=fonte_titulo)
pagina_cadastro_pessoa_titulo.configure(bg=AZUL_CLARO)
pagina_cadastro_pessoa_titulo.place(x=300 - 75, y=30)

pagina_cadastro_pessoa_nomeLabel = Label(
    pagina_cadastro_pessoa, text="Nome:", font=fonte)
pagina_cadastro_pessoa_nomeLabel.configure(bg=AZUL_CLARO)
pagina_cadastro_pessoa_nomeLabel.place(x=220 - 43, y=87)

pagina_cadastro_pessoa_nome = Entry(pagina_cadastro_pessoa)
pagina_cadastro_pessoa_nome["width"] = 20
pagina_cadastro_pessoa_nome["font"] = fonte
pagina_cadastro_pessoa_nome.place(x=300 - 70, y=90)

pagina_cadastro_pessoa_idLabel = Label(
    pagina_cadastro_pessoa, text="ID:", font=fonte)
pagina_cadastro_pessoa_idLabel.configure(bg=AZUL_CLARO)
pagina_cadastro_pessoa_idLabel.place(x=220 - 20, y=137)

pagina_cadastro_pessoa_id = Entry(pagina_cadastro_pessoa)
pagina_cadastro_pessoa_id["width"] = 20
pagina_cadastro_pessoa_id["font"] = fonte
pagina_cadastro_pessoa_id.place(x=300 - 70, y=140)

pagina_cadastro_pessoa_emailLabel = Label(
    pagina_cadastro_pessoa, text="Email:", font=fonte)
pagina_cadastro_pessoa_emailLabel.configure(bg=AZUL_CLARO)
pagina_cadastro_pessoa_emailLabel.place(x=220 - 40, y=187)

pagina_cadastro_pessoa_email = Entry(pagina_cadastro_pessoa)
pagina_cadastro_pessoa_email["width"] = 20
pagina_cadastro_pessoa_email["font"] = fonte
pagina_cadastro_pessoa_email.place(x=300 - 70, y=190)

pagina_cadastro_pessoa_cursoLabel = Label(
    pagina_cadastro_pessoa, text="Curso:", font=fonte)
pagina_cadastro_pessoa_cursoLabel.configure(bg=AZUL_CLARO)
pagina_cadastro_pessoa_cursoLabel.place(x=220 - 40, y=237)

pagina_cadastro_pessoa_curso = ttk.Combobox(
    pagina_cadastro_pessoa, textvariable=lista_cursos)
pagina_cadastro_pessoa_curso['values'] = utils.listar_cursos()
pagina_cadastro_pessoa_curso['state'] = 'readonly'
pagina_cadastro_pessoa_curso.set(value="Selecione um curso")
pagina_cadastro_pessoa_curso.place(x=300 - 70, y=240)

pagina_cadastro_pessoa_cadastrar = Button(pagina_cadastro_pessoa, text="Cadastrar",
                                          font=fonte, command=lambda: cadastra_pessoa())
pagina_cadastro_pessoa_cadastrar["width"] = TAMANHO_BOTAO
pagina_cadastro_pessoa_cadastrar.place(x=WIDTH/2 - 62, y=290)

pagina_cadastro_pessoa_label = Label(
    pagina_cadastro_pessoa, text="", font=fonte)
pagina_cadastro_pessoa_label.configure(bg=AZUL_CLARO)
pagina_cadastro_pessoa_label.place(x=375, y=300)

pagina_cadastro_pessoa_voltar = Button(pagina_cadastro_pessoa, text="Voltar",
                                       font=fonte, command=lambda: volta_pag_pessoa())
pagina_cadastro_pessoa_voltar["width"] = TAMANHO_BOTAO
pagina_cadastro_pessoa_voltar.place(x=WIDTH/2 - 62, y=340)

# ================ Pagina Lista das Pessoas =======================

pagina_list_pessoa.configure(bg=AZUL_CLARO)

pagina_list_pessoa_titulo = Label(
    pagina_list_pessoa, text="Selecione uma Pessoa", font=fonte_titulo)
pagina_list_pessoa_titulo.configure(bg=AZUL_CLARO)
pagina_list_pessoa_titulo.pack(side=TOP, fill=X, pady=30)

lista_pessoa = Listbox(pagina_list_pessoa, width=50)
lista_pessoa.pack(padx=150, fill=BOTH)
lista_pessoa.yview_scroll(number=2, what='units')

pagina_list_pessoa_acessar = Button(
    pagina_list_pessoa, text="Editar", font=fonte, command=lambda: direciona_editar_pessoa())
pagina_list_pessoa_acessar.pack(padx=45, ipadx=30, side=LEFT)

pagina_list_pessoa_apagar = Button(
    pagina_list_pessoa, text="Apagar", font=fonte, command=lambda: confirma_apagar_pessoa())
pagina_list_pessoa_apagar.pack(padx=45, ipadx=30, side=RIGHT)

pagina_list_pessoa_voltar = Button(
    pagina_list_pessoa, text="Voltar", font=fonte, command=lambda: show_frame(pagina_inicial))
pagina_list_pessoa_voltar.pack(padx=45, ipadx=30, side=RIGHT)

# ================ Pagina das Câmeras =======================

pagina_cameras.configure(bg=AZUL_CLARO)

pagina_cameras_titulo = Label(
    pagina_cameras, text="Selecione uma câmera", font=fonte_titulo)
pagina_cameras_titulo.configure(bg=AZUL_CLARO)
pagina_cameras_titulo.pack(side=TOP, fill=X, pady=30)

lista_cameras = Listbox(pagina_cameras, width=35)
lista_cameras['height'] = 5
lista_cameras.pack(padx=150, fill=BOTH)

"""
scrollbar_cameras = Scrollbar(
    pagina_cameras, orient='vertical', command=lista_cameras.yview)
scrollbar_cameras.pack(padx=45, ipadx=30, side=LEFT)

pagina_cameras_pesquisaLabel = Label(
    pagina_cameras, text="Pesquisa:", font=fonte)
pagina_cameras_pesquisaLabel.configure(bg=AZUL_CLARO)
pagina_cameras_pesquisaLabel.place(x=10, y=170)

pagina_cameras_pesquisa = Entry(pagina_cameras)
pagina_cameras_pesquisa['width'] = 20
pagina_cameras_pesquisa['font'] = fonte
pagina_cameras_pesquisa.place(x=200, y=100)

for line in range(100):
    lista_cameras.insert(END, f"Linha {line}")
"""

pagina_cameras_conectar = Button(
    pagina_cameras, text="Conectar", font=fonte, command=lambda: conecta_camera())
pagina_cameras_conectar.pack(padx=45, ipadx=30, side=RIGHT)

pagina_cameras_apagar = Button(
    pagina_cameras, text="Apagar", font=fonte, command=lambda: confirma_apagar_camera())
pagina_cameras_apagar.pack(padx=45, ipadx=30, side=RIGHT)

pagina_cameras_voltar = Button(
    pagina_cameras, text="Voltar", font=fonte, command=lambda: show_frame(pagina_inicial))
pagina_cameras_voltar.pack(padx=45, ipadx=30, side=RIGHT)


# ================ Pagina de Cadastro de Câmeras =======================

pagina_cadastro.configure(bg=AZUL_CLARO)

pagina_cadastro_titulo = Label(
    pagina_cadastro, text="Cadastre sua câmera", font=fonte_titulo)
pagina_cadastro_titulo.configure(bg=AZUL_CLARO)
pagina_cadastro_titulo.place(x=300 - 90, y=30)

pagina_cadastro_nomeLabel = Label(pagina_cadastro, text="Nome:", font=fonte)
pagina_cadastro_nomeLabel.configure(bg=AZUL_CLARO)
pagina_cadastro_nomeLabel.place(x=220 - 45, y=87)

pagina_cadastro_nome = Entry(pagina_cadastro)
pagina_cadastro_nome["width"] = 20
pagina_cadastro_nome["font"] = fonte
pagina_cadastro_nome.place(x=300 - 70, y=90)

pagina_cadastro_ipLabel = Label(pagina_cadastro, text="IP:", font=fonte)
pagina_cadastro_ipLabel.configure(bg=AZUL_CLARO)
pagina_cadastro_ipLabel.place(x=220 - 20, y=137)

pagina_cadastro_ip = Entry(pagina_cadastro)
pagina_cadastro_ip["width"] = 20
pagina_cadastro_ip["font"] = fonte
pagina_cadastro_ip.place(x=300 - 70, y=140)

pagina_cadastro_usuLabel = Label(pagina_cadastro, text="Usuário:", font=fonte)
pagina_cadastro_usuLabel.configure(bg=AZUL_CLARO)
pagina_cadastro_usuLabel.place(x=220 - 55, y=187)

pagina_cadastro_usuario = Entry(pagina_cadastro)
pagina_cadastro_usuario["width"] = 20
pagina_cadastro_usuario["font"] = fonte
pagina_cadastro_usuario.place(x=300 - 70, y=190)

pagina_cadastro_senhaLabel = Label(pagina_cadastro, text="Senha:", font=fonte)
pagina_cadastro_senhaLabel.configure(bg=AZUL_CLARO)
pagina_cadastro_senhaLabel.place(x=220 - 47, y=237)

pagina_cadastro_senha = Entry(pagina_cadastro)
pagina_cadastro_senha["width"] = 20
pagina_cadastro_senha["font"] = fonte
pagina_cadastro_senha["show"] = "*"
pagina_cadastro_senha.place(x=300 - 70, y=240)

pagina_cadastro_cadastrar = Button(pagina_cadastro, text="Cadastrar",
                                   font=fonte, command=lambda: cadastra_camera())
pagina_cadastro_cadastrar["width"] = TAMANHO_BOTAO
pagina_cadastro_cadastrar.place(x=WIDTH/2 - 62, y=290)

pagina_cadastro_label = Label(pagina_cadastro, text="", font=fonte)
pagina_cadastro_label.configure(bg=AZUL_CLARO)
pagina_cadastro_label.place(x=355 + 15, y=287)

pagina_cadastro_voltar = Button(pagina_cadastro, text="Voltar",
                                font=fonte, command=lambda: volta_pag_cadastro())
pagina_cadastro_voltar["width"] = TAMANHO_BOTAO
pagina_cadastro_voltar.place(x=WIDTH/2 - 62, y=340)

# ================ Pagina Edição de Pessoas =======================

pagina_edit_pessoa.configure(bg=AZUL_CLARO)

pagina_edit_pessoa_titulo = Label(
    pagina_edit_pessoa, text="Selecione uma Pessoa", font=fonte_titulo)
pagina_edit_pessoa_titulo.configure(bg=AZUL_CLARO)
pagina_edit_pessoa_titulo.place(x=300 - 90, y=20)

pagina_edit_pessoa_nomeLabel = Label(
    pagina_edit_pessoa, text="Nome:", font=fonte)
pagina_edit_pessoa_nomeLabel.configure(bg=AZUL_CLARO)
pagina_edit_pessoa_nomeLabel.place(x=220 - 41, y=67)

pagina_edit_pessoa_nome = Entry(pagina_edit_pessoa)
pagina_edit_pessoa_nome["width"] = 25
pagina_edit_pessoa_nome["font"] = fonte
pagina_edit_pessoa_nome.place(x=300 - 70, y=70)

pagina_edit_pessoa_emailLabel = Label(
    pagina_edit_pessoa, text="Email:", font=fonte)
pagina_edit_pessoa_emailLabel.configure(bg=AZUL_CLARO)
pagina_edit_pessoa_emailLabel.place(x=220 - 40, y=117)

pagina_edit_pessoa_email = Entry(pagina_edit_pessoa)
pagina_edit_pessoa_email["width"] = 25
pagina_edit_pessoa_email["font"] = fonte
pagina_edit_pessoa_email.place(x=300 - 70, y=120)

pagina_edit_pessoa_faltaLabel = Label(
    pagina_edit_pessoa, text="Faltas:", font=fonte)
pagina_edit_pessoa_faltaLabel.configure(bg=AZUL_CLARO)
pagina_edit_pessoa_faltaLabel.place(x=220 - 43, y=167)

pagina_edit_pessoa_falta = Entry(pagina_edit_pessoa)
pagina_edit_pessoa_falta["width"] = 25
pagina_edit_pessoa_falta["font"] = fonte
pagina_edit_pessoa_falta.place(x=300 - 70, y=170)

pagina_edit_pessoa_cursoLabel = Label(
    pagina_edit_pessoa, text="Curso:", font=fonte)
pagina_edit_pessoa_cursoLabel.configure(bg=AZUL_CLARO)
pagina_edit_pessoa_cursoLabel.place(x=220 - 40, y=220)

pagina_edit_pessoa_curso = ttk.Combobox(
    pagina_edit_pessoa, textvariable=lista_cursos)
pagina_edit_pessoa_curso["width"] = 26
pagina_edit_pessoa_curso['values'] = utils.listar_cursos()
pagina_edit_pessoa_curso['state'] = 'readonly'
pagina_edit_pessoa_curso.place(x=300 - 70, y=220)

pagina_edit_pessoa_voltar = Button(
    pagina_edit_pessoa, text="Voltar", font=fonte, command=lambda: volta_pag_edit_pessoa())
pagina_edit_pessoa_voltar.pack(pady=20, ipadx=30, side=BOTTOM)

pagina_edit_pessoa_salvar = Button(
    pagina_edit_pessoa, text="Salvar alterações", font=fonte, command=lambda: alterar_info(TEMP_ID))
pagina_edit_pessoa_salvar.pack(pady=5, ipadx=30 - 10, ipady=2, side=BOTTOM)

# ================ Método de inicialização =======================

# Adiciona as câmeras à lista
"""listar_cameras()
listar_pessoas()"""

# ================ Main Loop =======================
alunos()
janela.mainloop()
