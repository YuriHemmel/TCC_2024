import utils
import Banco
import Camera as Cam
import Pessoa as Pes
from tkinter import *  # Interface gráfica
from tkinter import messagebox # Caixa de mensagem para confirmações
#from tkinter import ttk # Combobox
import cv2

# Janela
janela = Tk()
janela.title("Sistema de chamada")
janela.rowconfigure(0, weight=1)
janela.columnconfigure(0, weight=1)
janela.geometry("600x400")
janela.resizable(False, False)

# Páginas
pagina_inicial = Frame(janela)
pagina_cameras = Frame(janela)
pagina_cadastro = Frame(janela)
pagina_pessoa = Frame(janela)
pagina_list_pessoa = Frame(janela)

# Fontes
fonte = ("Arial", 10, 'bold')
fonteTit = ("Arial", 13, 'bold')

# Adicionando as páginas
paginas = (pagina_inicial, pagina_cameras, pagina_cadastro, pagina_pessoa, pagina_list_pessoa)

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

def listar_cameras():
    cams = Cam.list_camera()

    for c in cams:
        lista_cameras.insert(c[0], f"Nome: {c[1]}       IP: {c[2]}")

def listar_pessoas():
    pessoas = Pes.list_pessoa()
    
    for p in pessoas:
        lista_pessoa.insert(0, f"RA: {p[0]} Nome: {p[1]}")

# Cadastra câmeras no banco de dados
def cadastra_camera():

    dados = [pagina_cadastro_nome.get(), pagina_cadastro_ip.get(),
             pagina_cadastro_senha.get(), pagina_cadastro_usuario.get()]

    # Verifica se os campos estão vazios
    for d in dados:
        if d == "":
            pagina_cadastro_label.config(
                text="Por favor, preencha os\ncampos corretamente.")
            return

    # Verifica se os dados inseridos pertencem à uma câmera já registrada
    try:
        camera = Cam.Camera(dados[0], dados[1], dados[2], dados[3])
        camera.insert_camera()
    except: #Exception as e:
        #print(e)
        pagina_cadastro_label.config(text="Dados duplicados.")
        return

    # Cadastro bem sucedido
    pagina_cadastro_label.config(text="Camera registrada com sucesso.")
    lista_cameras.insert(END, f"Nome: {dados[0]}  IP: {dados[1]}")

    pagina_cadastro_nome.delete(0, END)
    pagina_cadastro_ip.delete(0, END)
    pagina_cadastro_senha.delete(0, END)

    pagina_cadastro_nome.insert(index=1, string=f"Camera{Cam.conta_camera()}")

    return

# Cadastra pessoas no banco de dados
def cadastra_pessoa():

    dados = [pagina_pessoa_ra.get(), pagina_pessoa_nome.get(), pagina_pessoa_tel.get(), pagina_pessoa_email.get()]

    # Verifica se os campos estão vazios
    for d in dados:
        if d == "":
            pagina_pessoa_label.config(
                text="Por favor, preencha os\ncampos corretamente.")
            return

    fotoBin = utils.recebe_foto_binario()

    # Verifica se os dados inseridos pertencem à uma pessoa já registrada
    try:
        pessoa = Pes.Pessoa(dados[0], dados[1], dados[2], dados[3], fotoBin)
        pessoa.insert_pessoa()
    except Exception as e:
        print(e)
        pagina_pessoa_label.config(text="Dados duplicados.")
        return

    # Cadastro bem sucedido
    pagina_pessoa_label.config(text="Pessoa registrada com sucesso.")
    lista_pessoa.insert(0, f"RA: {dados[0]} Nome: {dados[1]}")

    return

# Indo para a página de cadastro (atualiza o campo de nome automáticamente)


def show_pag_cadastro():

    pagina_cadastro_nome.insert(index=1, string=f"Camera{Cam.conta_camera()}")
    show_frame(pagina_cadastro)

# Limpa os campos da página de cadastro


def volta_pag_cadastro():

    pagina_cadastro_nome.delete(0, END)
    pagina_cadastro_ip.delete(0, END)
    pagina_cadastro_senha.delete(0, END)
    pagina_cadastro_label.config(text="")

    show_frame(pagina_inicial)

def volta_pag_pessoa():

    pagina_pessoa_nome.delete(0, END)
    pagina_pessoa_ra.delete(0, END)
    pagina_pessoa_tel.delete(0, END)
    pagina_pessoa_email.delete(0, END)
    pagina_pessoa_label.config(text="")

    show_frame(pagina_inicial)

# Apaga camera do banco de dados
def confirma_apagar_camera():

    camSelecionada = lista_cameras.get(ACTIVE)

    #Se não tiver câmera registrada, dá erro
    if camSelecionada == "":
        messagebox.showinfo('Erro', 'Nenhuma câmera selecionada')
        return

    camSelecionada = camSelecionada.split()[1]
    
    #Cria caixa de mensagem para confirmação
    res = messagebox.askquestion("Apagar câmera", f"Deseja apagar informações da câmera {camSelecionada}?")

    if res == 'yes':
        lista_cameras.delete(lista_cameras.curselection())    
        Cam.delete_camera(camSelecionada)
        messagebox.showinfo('Sucesso', 'Câmera apagada com sucesso')
        
    else:
        messagebox.showinfo('Cancelado', 'Ação cancelada')

# Apaga pessoa do banco de dados
def confirma_apagar_pessoa():

    selecionada = lista_pessoa.get(ACTIVE)

    #Se não tiver pessoa registrada, dá erro
    if selecionada == "":
        messagebox.showinfo('Erro', 'Nenhuma pessoa selecionada')
        return

    nomeSelecionado = selecionada.split()[3::]
    nome = ""

    for n in nomeSelecionado:
        nome = nome + " " + n

    selecionada = selecionada.split()[1]
    
    #Cria caixa de mensagem para confirmação
    res = messagebox.askquestion("Apagar pessoa", f"Deseja apagar informações de{nome}?")

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

        #os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

        url = f"rtsp://{user}:{password}@{ip}:{port}/onvif1"

        print('Conectado com ' + url)

        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)

    while True:
        ret, frame = cap.read()
        if ret == False:
            print("Sem frame")
            break
        else:
            cv2.imshow('VIDEO', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# ================ Pagina inicial =======================


pagina_inicial.configure(bg="#1FFF93")

pagina_inicial_titulo = Label(pagina_inicial, text="Bem Vindo", font=fonteTit)
pagina_inicial_titulo.configure(bg="#1FFF93")
pagina_inicial_titulo.place(x=300 - 47, y=20)


pagina_inicial_camsLabel = Label(
    pagina_inicial, text="Abrir câmera", font=fonte)
pagina_inicial_camsLabel.configure(bg="#1FFF93")
pagina_inicial_camsLabel.place(x=165, y=105)

pagina_inicial_cams = Button(pagina_inicial, text="Cameras",
                             font=fonte, command=lambda: show_frame(pagina_cameras))
pagina_inicial_cams.place(x=175, y=135)

pagina_inicial_listPesLabel = Label(
    pagina_inicial, text="Listar Pessoas", font=fonte)
pagina_inicial_listPesLabel.configure(bg="#1FFF93")
pagina_inicial_listPesLabel.place(x=350, y=105)

pagina_inicial_listPes = Button(pagina_inicial, text="Pessoas",
                             font=fonte, command=lambda: show_frame(pagina_list_pessoa))
pagina_inicial_listPes.place(x=365, y=135)

pagina_inicial_cadLabel = Label(
    pagina_inicial, text="Cadastrar câmera", font=fonte)
pagina_inicial_cadLabel.configure(bg="#1FFF93")
pagina_inicial_cadLabel.place(x=152, y=200)

pagina_inicial_cadastro = Button(
    pagina_inicial, text="Cadastrar Câmera", font=fonte, command=lambda: show_pag_cadastro())
pagina_inicial_cadastro.place(x=148, y=230)

pagina_inicial_pessoaLabel = Label(
    pagina_inicial, text="Cadastrar pessoas", font=fonte)
pagina_inicial_pessoaLabel.configure(bg="#1FFF93")
pagina_inicial_pessoaLabel.place(x=335, y=200)

pagina_inicial_pessoa = Button(
    pagina_inicial, text="Cadastrar Pessoa", font=fonte, command=lambda: show_frame(pagina_pessoa))
pagina_inicial_pessoa.place(x=335, y=230)

# ================ Pagina das Câmeras =======================

pagina_cameras.configure(bg="#1FFF93")

pagina_cameras_titulo = Label(
    pagina_cameras, text="Selecione uma câmera", font=fonteTit)
pagina_cameras_titulo.configure(bg="#1FFF93")
pagina_cameras_titulo.place(x=300 - 90, y=40)

lista_cameras = Listbox(pagina_cameras, width=35)
lista_cameras.place(x=250 - 50, y=80)
lista_cameras.yview_scroll(number=2, what='units')

pagina_cameras_conectar = Button(
    pagina_cameras, text="Conectar", font=fonte, command=lambda: conecta_camera())
pagina_cameras_conectar.place(x=300 - 80, y=270)

pagina_cameras_apagar = Button(
    pagina_cameras, text="Apagar", font=fonte, command=lambda: confirma_apagar_camera())
pagina_cameras_apagar.place(x=300 + 20, y=270)

pagina_cameras_voltar = Button(
    pagina_cameras, text="Voltar", font=fonte, command=lambda: show_frame(pagina_inicial))
pagina_cameras_voltar.place(x=300 - 25, y=320)

# ================ Pagina de Cadastro de Câmeras =======================

pagina_cadastro.configure(bg="#1FFF93")

pagina_cadastro_titulo = Label(
    pagina_cadastro, text="Cadastre sua câmera", font=fonteTit)
pagina_cadastro_titulo.configure(bg="#1FFF93")
pagina_cadastro_titulo.place(x=300 - 90, y=30)
pagina_cadastro_titulo.pack()

pagina_cadastro_nomeLabel = Label(pagina_cadastro, text="Nome:", font=fonte)
pagina_cadastro_nomeLabel.configure(bg="#1fff93")
pagina_cadastro_nomeLabel.place(x=220 - 45, y=87)

pagina_cadastro_nome = Entry(pagina_cadastro)
pagina_cadastro_nome["width"] = 20
pagina_cadastro_nome["font"] = fonte
pagina_cadastro_nome.place(x=300 - 70, y=90)

pagina_cadastro_ipLabel = Label(pagina_cadastro, text="IP:", font=fonte)
pagina_cadastro_ipLabel.configure(bg="#1fff93")
pagina_cadastro_ipLabel.place(x=220 - 20, y=137)

pagina_cadastro_ip = Entry(pagina_cadastro)
pagina_cadastro_ip["width"] = 20
pagina_cadastro_ip["font"] = fonte
pagina_cadastro_ip.place(x=300 - 70, y=140)

pagina_cadastro_usuLabel = Label(pagina_cadastro, text="Usuário:", font=fonte)
pagina_cadastro_usuLabel.configure(bg="#1fff93")
pagina_cadastro_usuLabel.place(x=220 - 55, y=187)

pagina_cadastro_usuario = Entry(pagina_cadastro)
pagina_cadastro_usuario["width"] = 20
pagina_cadastro_usuario["font"] = fonte
pagina_cadastro_usuario.insert(index=1, string="admin")
pagina_cadastro_usuario.place(x=300 - 70, y=190)

pagina_cadastro_senhaLabel = Label(pagina_cadastro, text="Senha:", font=fonte)
pagina_cadastro_senhaLabel.configure(bg="#1fff93")
pagina_cadastro_senhaLabel.place(x=220 - 47, y=237)

pagina_cadastro_senha = Entry(pagina_cadastro)
pagina_cadastro_senha["width"] = 20
pagina_cadastro_senha["font"] = fonte
pagina_cadastro_senha["show"] = "*"
pagina_cadastro_senha.place(x=300 - 70, y=240)

pagina_cadastro_cadastrar = Button(pagina_cadastro, text="Cadastrar",
                                   font=fonte, command=lambda: cadastra_camera())
pagina_cadastro_cadastrar.place(x=300 - 37, y=290)

pagina_cadastro_label = Label(pagina_cadastro, text="", font=fonte)
pagina_cadastro_label.configure(bg="#1fff93")
pagina_cadastro_label.place(x=355, y=287)

pagina_cadastro_voltar = Button(pagina_cadastro, text="Voltar",
                                font=fonte, command=lambda: volta_pag_cadastro())
pagina_cadastro_voltar.place(x=300 - 25, y=340)

# ================ Pagina de Cadastro de Pessoas =======================

pagina_pessoa.configure(bg="#1FFF93")

pagina_pessoa_titulo = Label(
    pagina_pessoa, text="Cadastre a Pessoa", font=fonteTit)
pagina_pessoa_titulo.configure(bg="#1FFF93")
pagina_pessoa_titulo.place(x=300 - 75, y=30)

pagina_pessoa_nomeLabel = Label(pagina_pessoa, text="Nome:", font=fonte)
pagina_pessoa_nomeLabel.configure(bg="#1fff93")
pagina_pessoa_nomeLabel.place(x=220 - 43, y=87)

pagina_pessoa_nome = Entry(pagina_pessoa)
pagina_pessoa_nome["width"] = 20
pagina_pessoa_nome["font"] = fonte
pagina_pessoa_nome.place(x=300 - 70, y=90)

pagina_pessoa_raLabel = Label(pagina_pessoa, text="RA:", font=fonte)
pagina_pessoa_raLabel.configure(bg="#1fff93")
pagina_pessoa_raLabel.place(x=220 - 23, y=137)

pagina_pessoa_ra = Entry(pagina_pessoa)
pagina_pessoa_ra["width"] = 20
pagina_pessoa_ra["font"] = fonte
pagina_pessoa_ra.place(x=300 - 70, y=140)

pagina_pessoa_telLabel = Label(pagina_pessoa, text="Telefone:", font=fonte)
pagina_pessoa_telLabel.configure(bg="#1fff93")
pagina_pessoa_telLabel.place(x=220 - 60, y=187)

pagina_pessoa_tel = Entry(pagina_pessoa)
pagina_pessoa_tel["width"] = 20
pagina_pessoa_tel["font"] = fonte
pagina_pessoa_tel.place(x=300 - 70, y=190)

pagina_pessoa_emailLabel = Label(pagina_pessoa, text="Email:", font=fonte)
pagina_pessoa_emailLabel.configure(bg="#1fff93")
pagina_pessoa_emailLabel.place(x=220 - 40, y=237)

pagina_pessoa_email = Entry(pagina_pessoa)
pagina_pessoa_email["width"] = 20
pagina_pessoa_email["font"] = fonte
pagina_pessoa_email.place(x=300 - 70, y=240)

pagina_pessoa_cadastrar = Button(pagina_pessoa, text="Cadastrar",
                                   font=fonte, command=lambda: cadastra_pessoa())
pagina_pessoa_cadastrar.place(x=215, y=340)

pagina_pessoa_label = Label(pagina_pessoa, text="", font=fonte)
pagina_pessoa_label.configure(bg="#1fff93")
pagina_pessoa_label.place(x=375, y=340)

pagina_pessoa_voltar = Button(pagina_pessoa, text="Voltar",
                                font=fonte, command=lambda: volta_pag_pessoa())
pagina_pessoa_voltar.place(x=310, y=340)

# ================ Pagina das Pessoas =======================

pagina_list_pessoa.configure(bg="#1FFF93")

pagina_list_pessoa_titulo = Label(
    pagina_list_pessoa, text="Selecione uma Pessoa", font=fonteTit)
pagina_list_pessoa_titulo.configure(bg="#1FFF93")
pagina_list_pessoa_titulo.place(x=300 - 90, y=40)

lista_pessoa = Listbox(pagina_list_pessoa, width=50)
lista_pessoa.place(x=150, y=80)
lista_pessoa.yview_scroll(number=2, what='units')

pagina_list_pessoa_acessar = Button(
    pagina_list_pessoa, text="Conectar", font=fonte, command=lambda: conecta_camera())
pagina_list_pessoa_acessar.place(x=300 - 80, y=270)

pagina_list_pessoa_apagar = Button(
    pagina_list_pessoa, text="Apagar", font=fonte, command=lambda: confirma_apagar_pessoa())
pagina_list_pessoa_apagar.place(x=300 + 20, y=270)

pagina_list_pessoa_voltar = Button(
    pagina_list_pessoa, text="Voltar", font=fonte, command=lambda: show_frame(pagina_inicial))
pagina_list_pessoa_voltar.place(x=300 - 25, y=320)

# ================ Método de inicialização =======================

# Adiciona as câmeras à lista
listar_cameras()
listar_pessoas()

# ================ Main Loop =======================

janela.mainloop()
