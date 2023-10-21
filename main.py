import utils
import os
import re
import Banco
import Camera as Cam
import Pessoa as Pes
from tkinter import *  # Interface gráfica
from tkinter import messagebox  # Caixa de mensagem para confirmações
import tkinter as tk
from tkinter import ttk
from datetime import *
import cv2
import sys
import pywhatkit

WIDTH = 600
HEIGHT = 400
TEMP_ID = ""
TAMANHO_BOTAO = 15

# Configuração básica para protocolo rtsp
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0"

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
pagina_pessoa = Frame(janela)
pagina_list_pessoa = Frame(janela)
pagina_edit_pessoa = Frame(janela)

# Fontes
fonte = ("Arial", 10, 'bold')
fonteTit = ("Arial", 13, 'bold')

# Adicionando as páginas
paginas = (pagina_inicial, pagina_cameras, pagina_cadastro,
           pagina_pessoa, pagina_list_pessoa, pagina_edit_pessoa)

# Adiciona os frames nas páginas
for frame in paginas:
    frame.grid(row=0, column=0, sticky='nsew')

# Lista de cursos
lista_cursos = tk.StringVar()

# Mostra o Frame que queremos


def show_frame(frame):
    frame.tkraise()


# Primeira página a aparecer
show_frame(pagina_inicial)

# Cria o banco de dados se não existir ainda
db = Banco.Banco()


def listar_cameras():
    cams = Cam.list_camera()

    for c in cams:
        lista_cameras.insert(c[0], f"Nome: {c[1]}       IP: {c[2]}")


def listar_pessoas():
    pessoas = Pes.list_pessoa()

    for p in pessoas:
        lista_pessoa.insert(0, f"ID: {p[0]} Nome: {p[1]}")

# Cadastra câmeras no banco de dados


def cadastra_camera():

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
        # print(e)
        pagina_cadastro_label.config(
            text="Câmera já cadastrada\nanteriormente.")
        return

    # Cadastro bem sucedido
    pagina_cadastro_label.config(text="Camera registrada com sucesso.")
    lista_cameras.insert(END, f"Nome: {dados[0]}  IP: {dados[1]}")

    pagina_cadastro_nome.delete(0, END)
    pagina_cadastro_ip.delete(0, END)
    pagina_cadastro_senha.delete(0, END)

    # pagina_cadastro_nome.insert(index=1, string=f"Camera{Cam.conta_camera()}")

    return

# Cadastra pessoas no banco de dados


def cadastra_pessoa():
    PATTERN_RA = "^[A-z0-9]{7}$"
    PATTERN_NOME = "^(?=^.{2,60}$)^[A-ZÀÁÂĖÈÉÊÌÍÒÓÔÕÙÚÛÇ][a-zàáâãèéêìíóôõùúç]+(?:[ ](?:das?|dos?|de|e|[A-ZÀÁÂĖÈÉÊÌÍÒÓÔÕÙÚÛÇ][a-zàáâãèéêìíóôõùúç]+))*$"
    PATTERN_TELEFONE = "^\(?(?:[14689][1-9]|2[12478]|3[1234578]|5[1345]|7[134579])?\)? ?(?:[2-8]|9[0-9])[0-9]{3}\-?[0-9]{4}$"

    dados = [pagina_pessoa_id.get(), pagina_pessoa_nome.get(),
             pagina_pessoa_tel.get()]

    # Verifica se os campos estão vazios
    for d in dados:
        if d.strip() == "":
            pagina_pessoa_label.config(
                text="Por favor, preencha os\ncampos corretamente.")
            return

    # Valida os campos com regex -> RA/ID, nome e telefone
    ra_valido = re.match(PATTERN_RA, dados[0])
    if ra_valido is None:
        pagina_pessoa_label.config(
            text="ID inválido!\nPor favor, preencha o\ncampo de ID corretamente.")
        return

    nome_valido = re.match(PATTERN_NOME, dados[1])
    if nome_valido is None:
        pagina_pessoa_label.config(
            text="Nome inválido!\nPor favor, preencha o\ncampo de nome corretamente.")
        return

    telefone_valido = re.match(PATTERN_TELEFONE, dados[2])
    if telefone_valido is None:
        pagina_pessoa_label.config(
            text="Telefone inválido!\nPor favor, preencha o\ncampo de telefone corretamente.")
        return

    if pagina_pessoa_curso.get() == "Selecione um curso":
        pagina_pessoa_label.config(
            text="Por favor, selecione um curso\nválido!")
        return

    # Tira foto em analise, vai falhar
    fotoBin = utils.recebe_foto_binario()

    # Verifica se os dados inseridos pertencem à uma pessoa já registrada
    try:
        pessoa = Pes.Pessoa(dados[0], dados[1], dados[2], 0, fotoBin,
                            utils.retorna_curso_id(pagina_pessoa_curso.get()), 0)
        pessoa.insert_pessoa()
    except:  # Exception as e:
        # print(e)
        pagina_pessoa_label.config(text="Pessoa já cadastrada\nanteriomente.")
        return

    # Cadastro bem sucedido
    pagina_pessoa_label.config(text="Pessoa registrada com sucesso.")
    lista_pessoa.insert(0, f"ID: {dados[0]} Nome: {dados[1]}")

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
    # pessoa[2] = Telefone
    # pessoa[3] = faltas
    # pessoa[4] = foto
    # pessoa[5] = id do curso
    # pessoa[6] = presença no dia

    pagina_edit_pessoa_nome.insert(index=0, string=f"{pessoa[1]}")
    pagina_edit_pessoa_tel.insert(index=0, string=f"{pessoa[2]}")
    pagina_edit_pessoa_falta.insert(index=0, string=f"{pessoa[3]}")
    pagina_edit_pessoa_curso.set(f"{utils.retorna_curso_nome(pessoa[5])}")

    guarda_id(pessoa[0])

    show_frame(pagina_edit_pessoa)
# Salva novas informações no banco


def alterar_info(varId):

    dados = [pagina_edit_pessoa_nome.get(), pagina_edit_pessoa_tel.get(),
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
    else:
        messagebox.showinfo('Cancelado', 'Ação cancelada')


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

# Limpa os campos da página de cadastro de c


def volta_pag_edit_pessoa():

    pagina_edit_pessoa_nome.delete(0, END)
    pagina_edit_pessoa_tel.delete(0, END)
    pagina_edit_pessoa_falta.delete(0, END)

    guarda_id("")

    show_frame(pagina_list_pessoa)

# Limpa os campos da página de cadastro de pessoa


def volta_pag_pessoa():

    pagina_pessoa_nome.delete(0, END)
    pagina_pessoa_id.delete(0, END)
    pagina_pessoa_tel.delete(0, END)
    pagina_pessoa_label.config(text="")

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
        messagebox.showinfo('Sucesso', 'Câmera apagada com sucesso')

    else:
        messagebox.showinfo('Cancelado', 'Ação cancelada')

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
        messagebox.showinfo('Sucesso', 'Pessoa apagada com sucesso')

    else:
        messagebox.showinfo('Cancelado', 'Ação cancelada')


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

# Manda mensagem por whatsapp


def inicia_app():

    nao_chegaram = Pes.verifica_chegada()

    for item in nao_chegaram:
        telefone = Pes.load_pessoa_telefone(item[0])
        pywhatkit.sendwhatmsg(
            f"+55{telefone}", "Teste", datetime, 15, 7, True, 5)

    return

# ================ Pagina inicial =======================


pagina_inicial.configure(bg="#71BAFF")

pagina_inicial_titulo = Label(
    pagina_inicial, text="Menu Inicial", font=fonteTit)
pagina_inicial_titulo.configure(bg="#71BAFF")
pagina_inicial_titulo.place(x=WIDTH/2 - 45, y=20)


pagina_inicial_camsLabel = Label(
    pagina_inicial, text="Lista de câmera", font=fonte)
pagina_inicial_camsLabel.configure(bg="#71BAFF")
pagina_inicial_camsLabel.place(x=60 - 10, y=105)

pagina_inicial_cams = Button(pagina_inicial, text="Lista de cameras",
                             font=fonte, command=lambda: show_frame(pagina_cameras))
pagina_inicial_cams['width'] = TAMANHO_BOTAO
pagina_inicial_cams.place(x=50 - 10, y=135)

pagina_inicial_listPesLabel = Label(
    pagina_inicial, text="Listar Pessoas", font=fonte)
pagina_inicial_listPesLabel.configure(bg="#71BAFF")
pagina_inicial_listPesLabel.place(x=65 - 10, y=210)

pagina_inicial_listPes = Button(pagina_inicial, text="Lista de pessoas",
                                font=fonte, command=lambda: show_frame(pagina_list_pessoa))
pagina_inicial_listPes['width'] = TAMANHO_BOTAO
pagina_inicial_listPes.place(x=50 - 10, y=240)

pagina_inicial_iniciaLabel = Label(
    pagina_inicial, text="Inicia app", font=fonte)
pagina_inicial_iniciaLabel.configure(bg="#71BAFF")
pagina_inicial_iniciaLabel.place(x=280 - 10, y=105)

pagina_inicial_inicia = Button(pagina_inicial, text="Iniciar",
                               font=fonte, command=lambda: inicia_app())
pagina_inicial_inicia['width'] = TAMANHO_BOTAO
pagina_inicial_inicia.place(x=250 - 10, y=135)

pagina_inicial_sairLabel = Label(
    pagina_inicial, text="Sair do app", font=fonte)
pagina_inicial_sairLabel.configure(bg="#71BAFF")
pagina_inicial_sairLabel.place(x=265, y=210)

pagina_inicial_sair = Button(
    pagina_inicial, text="Sair", font=fonte, command=lambda: sys.exit())
pagina_inicial_sair['width'] = TAMANHO_BOTAO
pagina_inicial_sair.place(x=240, y=240)

pagina_inicial_cadLabel = Label(
    pagina_inicial, text="Cadastrar câmeras", font=fonte)
pagina_inicial_cadLabel.configure(bg="#71BAFF")
pagina_inicial_cadLabel.place(x=330 + 111, y=105)

pagina_inicial_cadastro = Button(
    pagina_inicial, text="Cadastrar Câmera", font=fonte, command=lambda: show_pag_cadastro())
pagina_inicial_cadastro['width'] = TAMANHO_BOTAO
pagina_inicial_cadastro.place(x=330 + 108, y=135)

pagina_inicial_pessoaLabel = Label(
    pagina_inicial, text="Cadastrar pessoas", font=fonte)
pagina_inicial_pessoaLabel.configure(bg="#71BAFF")
pagina_inicial_pessoaLabel.place(x=330 + 112, y=210)

pagina_inicial_pessoa = Button(
    pagina_inicial, text="Cadastrar Pessoa", font=fonte, command=lambda: show_frame(pagina_pessoa))
pagina_inicial_pessoa['width'] = TAMANHO_BOTAO
pagina_inicial_pessoa.place(x=330 + 108, y=240)

# ================ Pagina das Câmeras =======================

pagina_cameras.configure(bg="#71BAFF")

pagina_cameras_titulo = Label(
    pagina_cameras, text="Selecione uma câmera", font=fonteTit)
pagina_cameras_titulo.configure(bg="#71BAFF")
pagina_cameras_titulo.pack(side=TOP, fill=X, pady=30)

lista_cameras = Listbox(pagina_cameras, width=35)
lista_cameras.pack(padx=150, fill=BOTH)
lista_cameras.yview_scroll(number=2, what='units')

pagina_cameras_conectar = Button(
    pagina_cameras, text="Conectar", font=fonte, command=lambda: conecta_camera())
pagina_cameras_conectar.pack(padx=35, ipadx=30, side=LEFT)

pagina_cameras_apagar = Button(
    pagina_cameras, text="Apagar", font=fonte, command=lambda: confirma_apagar_camera())
pagina_cameras_apagar.pack(padx=35, ipadx=30, side=RIGHT)

pagina_cameras_voltar = Button(
    pagina_cameras, text="Voltar", font=fonte, command=lambda: show_frame(pagina_inicial))
pagina_cameras_voltar.pack(padx=45, ipadx=30, side=RIGHT)

# ================ Pagina de Cadastro de Câmeras =======================

pagina_cadastro.configure(bg="#71BAFF")

pagina_cadastro_titulo = Label(
    pagina_cadastro, text="Cadastre sua câmera", font=fonteTit)
pagina_cadastro_titulo.configure(bg="#71BAFF")
pagina_cadastro_titulo.place(x=300 - 90, y=30)

pagina_cadastro_nomeLabel = Label(pagina_cadastro, text="Nome:", font=fonte)
pagina_cadastro_nomeLabel.configure(bg="#71BAFF")
pagina_cadastro_nomeLabel.place(x=220 - 45, y=87)

pagina_cadastro_nome = Entry(pagina_cadastro)
pagina_cadastro_nome["width"] = 20
pagina_cadastro_nome["font"] = fonte
pagina_cadastro_nome.place(x=300 - 70, y=90)

pagina_cadastro_ipLabel = Label(pagina_cadastro, text="IP:", font=fonte)
pagina_cadastro_ipLabel.configure(bg="#71BAFF")
pagina_cadastro_ipLabel.place(x=220 - 20, y=137)

pagina_cadastro_ip = Entry(pagina_cadastro)
pagina_cadastro_ip["width"] = 20
pagina_cadastro_ip["font"] = fonte
pagina_cadastro_ip.place(x=300 - 70, y=140)

pagina_cadastro_usuLabel = Label(pagina_cadastro, text="Usuário:", font=fonte)
pagina_cadastro_usuLabel.configure(bg="#71BAFF")
pagina_cadastro_usuLabel.place(x=220 - 55, y=187)

pagina_cadastro_usuario = Entry(pagina_cadastro)
pagina_cadastro_usuario["width"] = 20
pagina_cadastro_usuario["font"] = fonte
# pagina_cadastro_usuario.insert(index=1, string="admin")
pagina_cadastro_usuario.place(x=300 - 70, y=190)

pagina_cadastro_senhaLabel = Label(pagina_cadastro, text="Senha:", font=fonte)
pagina_cadastro_senhaLabel.configure(bg="#71BAFF")
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
pagina_cadastro_label.configure(bg="#71BAFF")
pagina_cadastro_label.place(x=355 + 15, y=287)

pagina_cadastro_voltar = Button(pagina_cadastro, text="Voltar",
                                font=fonte, command=lambda: volta_pag_cadastro())
pagina_cadastro_voltar["width"] = TAMANHO_BOTAO
pagina_cadastro_voltar.place(x=WIDTH/2 - 62, y=340)

# ================ Pagina de Cadastro de Pessoas =======================

pagina_pessoa.configure(bg="#71BAFF")

pagina_pessoa_titulo = Label(
    pagina_pessoa, text="Cadastre a Pessoa", font=fonteTit)
pagina_pessoa_titulo.configure(bg="#71BAFF")
pagina_pessoa_titulo.place(x=300 - 75, y=30)

pagina_pessoa_nomeLabel = Label(pagina_pessoa, text="Nome:", font=fonte)
pagina_pessoa_nomeLabel.configure(bg="#71BAFF")
pagina_pessoa_nomeLabel.place(x=220 - 43, y=87)

pagina_pessoa_nome = Entry(pagina_pessoa)
pagina_pessoa_nome["width"] = 20
pagina_pessoa_nome["font"] = fonte
pagina_pessoa_nome.place(x=300 - 70, y=90)

pagina_pessoa_idLabel = Label(pagina_pessoa, text="ID:", font=fonte)
pagina_pessoa_idLabel.configure(bg="#71BAFF")
pagina_pessoa_idLabel.place(x=220 - 20, y=137)

pagina_pessoa_id = Entry(pagina_pessoa)
pagina_pessoa_id["width"] = 20
pagina_pessoa_id["font"] = fonte
pagina_pessoa_id.place(x=300 - 70, y=140)

pagina_pessoa_telLabel = Label(pagina_pessoa, text="Telefone:", font=fonte)
pagina_pessoa_telLabel.configure(bg="#71BAFF")
pagina_pessoa_telLabel.place(x=220 - 60, y=187)

pagina_pessoa_tel = Entry(pagina_pessoa)
pagina_pessoa_tel["width"] = 20
pagina_pessoa_tel["font"] = fonte
pagina_pessoa_tel.place(x=300 - 70, y=190)

pagina_pessoa_cursoLabel = Label(pagina_pessoa, text="Curso:", font=fonte)
pagina_pessoa_cursoLabel.configure(bg="#71BAFF")
pagina_pessoa_cursoLabel.place(x=220 - 40, y=237)

pagina_pessoa_curso = ttk.Combobox(pagina_pessoa, textvariable=lista_cursos)
pagina_pessoa_curso['values'] = utils.listar_cursos()
pagina_pessoa_curso['state'] = 'readonly'
pagina_pessoa_curso.set(value="Selecione um curso")
pagina_pessoa_curso.place(x=300 - 70, y=240)

pagina_pessoa_cadastrar = Button(pagina_pessoa, text="Cadastrar",
                                 font=fonte, command=lambda: cadastra_pessoa())
pagina_pessoa_cadastrar["width"] = TAMANHO_BOTAO
pagina_pessoa_cadastrar.place(x=WIDTH/2 - 62, y=300)

pagina_pessoa_label = Label(pagina_pessoa, text="", font=fonte)
pagina_pessoa_label.configure(bg="#71BAFF")
pagina_pessoa_label.place(x=375, y=300)

pagina_pessoa_voltar = Button(pagina_pessoa, text="Voltar",
                              font=fonte, command=lambda: volta_pag_pessoa())
pagina_pessoa_voltar["width"] = TAMANHO_BOTAO
pagina_pessoa_voltar.place(x=WIDTH/2 - 62, y=340)

# ================ Pagina Lista das Pessoas =======================

pagina_list_pessoa.configure(bg="#71BAFF")

pagina_list_pessoa_titulo = Label(
    pagina_list_pessoa, text="Selecione uma Pessoa", font=fonteTit)
pagina_list_pessoa_titulo.configure(bg="#71BAFF")
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

# ================ Pagina Edição de Pessoas =======================

pagina_edit_pessoa.configure(bg="#71BAFF")

pagina_edit_pessoa_titulo = Label(
    pagina_edit_pessoa, text="Selecione uma Pessoa", font=fonteTit)
pagina_edit_pessoa_titulo.configure(bg="#71BAFF")
pagina_edit_pessoa_titulo.place(x=300 - 90, y=20)

pagina_edit_pessoa_nomeLabel = Label(
    pagina_edit_pessoa, text="Nome:", font=fonte)
pagina_edit_pessoa_nomeLabel.configure(bg="#71BAFF")
pagina_edit_pessoa_nomeLabel.place(x=220 - 41, y=67)

pagina_edit_pessoa_nome = Entry(pagina_edit_pessoa)
pagina_edit_pessoa_nome["width"] = 25
pagina_edit_pessoa_nome["font"] = fonte
pagina_edit_pessoa_nome.place(x=300 - 70, y=70)

pagina_edit_pessoa_telLabel = Label(
    pagina_edit_pessoa, text="Telefone:", font=fonte)
pagina_edit_pessoa_telLabel.configure(bg="#71BAFF")
pagina_edit_pessoa_telLabel.place(x=220 - 60, y=117)

pagina_edit_pessoa_tel = Entry(pagina_edit_pessoa)
pagina_edit_pessoa_tel["width"] = 25
pagina_edit_pessoa_tel["font"] = fonte
pagina_edit_pessoa_tel.place(x=300 - 70, y=120)

pagina_edit_pessoa_faltaLabel = Label(
    pagina_edit_pessoa, text="Faltas:", font=fonte)
pagina_edit_pessoa_faltaLabel.configure(bg="#71BAFF")
pagina_edit_pessoa_faltaLabel.place(x=220 - 43, y=167)

pagina_edit_pessoa_falta = Entry(pagina_edit_pessoa)
pagina_edit_pessoa_falta["width"] = 25
pagina_edit_pessoa_falta["font"] = fonte
pagina_edit_pessoa_falta.place(x=300 - 70, y=170)

pagina_edit_pessoa_cursoLabel = Label(
    pagina_edit_pessoa, text="Curso:", font=fonte)
pagina_edit_pessoa_cursoLabel.configure(bg="#71BAFF")
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
listar_cameras()
listar_pessoas()

# ================ Main Loop =======================

janela.mainloop()
