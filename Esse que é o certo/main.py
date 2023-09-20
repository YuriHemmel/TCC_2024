import Banco
import Camera as Cam
import Pessoa
import os
from tkinter import *  # Interface gráfica
from tkinter import messagebox # Caixa de mensagem para confirmações

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

# Fontes
fonte = ("Arial", 10, 'bold')
fonteTit = ("Arial", 13, 'bold')

# Adicionando as páginas
paginas = (pagina_inicial, pagina_cameras, pagina_cadastro)

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

# Cadastra câmeras
def cadastra_camera():

    dados = [pagina_cadastro_nome.get(), pagina_cadastro_ip.get(),
             pagina_cadastro_senha.get()]

    # Verifica se os campos estão vazios
    for d in dados:
        if d == "":
            pagina_cadastro_label.config(
                text="Por favor, preencha os\ncampos corretamente.")
            return

    # Verifica se os dados inseridos pertencem à uma câmera já registrada
    try:
        camera = Cam.Camera(Cam.conta_camera(), dados[0], dados[1], dados[2])
        camera.insert_camera()
    except:
        pagina_cadastro_label.config(text="Dados duplicados.")
        return

    # Cadastro bem sucedido
    pagina_cadastro_label.config(text="Camera registrada com sucesso.")
    lista_cameras.insert(END, f"Nome: {dados[0]}  IP:{dados[1]}")

    pagina_cadastro_nome.delete(0, END)
    pagina_cadastro_ip.delete(0, END)
    pagina_cadastro_senha.delete(0, END)

    pagina_cadastro_nome.insert(index=1, string=f"Camera{Cam.conta_camera()}")

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

def confirma_apagar():

    camSelecionada = lista_cameras.get(ACTIVE)
    camSelecionada = camSelecionada.split()[1]

    #Cria caixa de mensagem para confirmação
    res = messagebox.askquestion("Apagar câmera", f"Deseja apagar informações da câmera {camSelecionada}?")

    if res == 'yes':
        Cam.delete_camera(camSelecionada)
        messagebox.showinfo('Sucesso', 'Câmera apagada com sucesso')
        
    else:
        messagebox.showinfo('Cancelado', 'Ação cancelada')

# ================ Pagina inicial =======================


pagina_inicial.configure(bg="#1FFF93")

pagina_inicial_titulo = Label(pagina_inicial, text="Bem Vindo", font=fonteTit)
pagina_inicial_titulo.configure(bg="#1FFF93")
pagina_inicial_titulo.place(x=300 - 47, y=50)


pagina_inicial_camsLabel = Label(
    pagina_inicial, text="Abrir câmera", font=fonte)
pagina_inicial_camsLabel.configure(bg="#1FFF93")
pagina_inicial_camsLabel.place(x=300 - 45, y=100)

pagina_inicial_cams = Button(pagina_inicial, text="Cameras",
                             font=fonte, command=lambda: show_frame(pagina_cameras))
pagina_inicial_cams.place(x=300 - 35, y=150)

pagina_inicial_cadLabel = Label(
    pagina_inicial, text="Cadastrar câmera", font=fonte)
pagina_inicial_cadLabel.configure(bg="#1FFF93")
pagina_inicial_cadLabel.place(x=300 - 63, y=200)

pagina_inicial_cadastro = Button(
    pagina_inicial, text="Cadastrar", font=fonte, command=lambda: show_pag_cadastro())
pagina_inicial_cadastro.place(x=300 - 37, y=250)

# ================ Pagina das Câmeras =======================

pagina_cameras.configure(bg="#1FFF93")

pagina_cameras_titulo = Label(
    pagina_cameras, text="Selecione uma câmera", font=fonteTit)
pagina_cameras_titulo.configure(bg="#1FFF93")
pagina_cameras_titulo.place(x=300 - 90, y=40)

lista_cameras = Listbox(pagina_cameras, width=35)
lista_cameras.place(x=250 - 50, y=80)
lista_cameras.yview_scroll(number=2, what='units')

pagina_cameras_apagar = Button(
    pagina_cameras, text="Apagar", font=fonte, command=lambda: confirma_apagar())
pagina_cameras_apagar.place(x=300 - 30, y=270)

pagina_cameras_voltar = Button(
    pagina_cameras, text="Voltar", font=fonte, command=lambda: show_frame(pagina_inicial))
pagina_cameras_voltar.place(x=300 - 25, y=320)

# ================ Pagina de Cadastro =======================

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

# ================ Método de inicialização =======================

# Adiciona as câmeras à lista
listar_cameras()

# ================ Main Loop =======================

janela.mainloop()
