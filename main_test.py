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
from customtkinter import *

# ---------------------------------------- Constantes --------------------------------------------------------
# Tamanho da janela
WIDTH = 850
HEIGHT = 620

# Cores
AZUL_CLARO = "#075EBD"
AZUL_ESCURO = "#023D71"
PRETO = "#000000"
BRANCO = "#FFFFFF"
VERDE = "#66C475"
VERMELHO = "#FF5961"

# Fontes
FONTE = ("Ivy", 16)
FONTE_TITULO = ("Ivy", 20, 'bold')
FONTE_BOTAO = ("Ivy", 13, 'bold')

# ------------------------------------------- Dotenv --------------------------------------------------------

# Lê as variáveis de ambiente presentes no arquivo .env
load_dotenv()

# =========================================== Código =========================================================

# ------------------------------------------- Configurações da janela --------------------------------------------------------
janela = CTk()
janela.title("Sistema de chamada")
janela.geometry(f"{WIDTH}x{HEIGHT}")
janela.minsize(width=WIDTH, height=HEIGHT)

set_appearance_mode("Dark")

janela.grid_columnconfigure(0, weight=2)
janela.grid_columnconfigure(1, weight=1)
janela.grid_columnconfigure(2, weight=2)

janela.grid_rowconfigure(1, weight=2)
janela.grid_rowconfigure(2, weight=1)
janela.grid_rowconfigure(3, weight=2)

# ------------------------------------------- Configurações de páginas --------------------------------------------------------
# Frames / Páginas
frame_conteudo = CTkFrame(janela)
frame_conteudo.grid(row=1, column=0, sticky='nsew', columnspan=3, rowspan=3)
frame_conteudo.configure(fg_color='transparent')

frame_conteudo.grid_columnconfigure(0, weight=1)
frame_conteudo.grid_columnconfigure(1, weight=0)
frame_conteudo.grid_columnconfigure(2, weight=1)

frame_conteudo.grid_rowconfigure(0, weight=1)
frame_conteudo.grid_rowconfigure(1, weight=0)
frame_conteudo.grid_rowconfigure(2, weight=1)

pagina_inicial = CTkFrame(frame_conteudo)
pagina_inicial.grid(row=0, column=0, sticky='nsew', columnspan=3, rowspan=3)

pagina_cadastro = CTkFrame(frame_conteudo)
pagina_cadastro.grid(row=0, column=0, sticky='nsew', columnspan=3, rowspan=3)

# ------------------------------------------- Criação de banco de dados --------------------------------------------------------

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

    if dia_semana in [0, 1, 2, 3, 4]:
        # Aulas do dia
        aulas_dia = utils.verifica_aula_dia(dia_semana)
        utils.adiciona_fotos_alunos(aulas_dia, dia_semana)
        if (os.listdir('imagensAlunos') == []):
            print('Não há nenhum aluno ou aula para este dia letivo.')
        else:
            inicia_reconhecimento()
            print("Preparação de aulas do dia concluida")


# Computa as faltas do dia
def computa_faltas():
    current_time = datetime.now()

    # Verifica se hoje é dia de semana ou fim de semana
    dia_semana = current_time.weekday()

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

    # manda_mensagens()

    # Confere presença do aluno
    utils.confere_presenca()

    computa_faltas()

# Fecha o aplicativo e seus subprocessos


def sair():
    os._exit(0)

# ========================= Schedules ================================


schedule.every(40).minutes.do(manda_mensagens)
schedule.every().day.at("00:00").do(prepara_dia)
schedule.every().day.at("23:59").do(computa_faltas)

# ------------------------------------------- Funções --------------------------------------------------------

# Mostra os frames


def show_frame(frame):
    frame.tkraise()

# Troca informações do Título


def troca_titulo(texto, nome_img):

    img = Image.open(f"images/icon_{nome_img}.png")
    img = img.resize((40, 40))
    img = ImageTk.PhotoImage(img)

    label_titulo.configure(text=texto, image=img)

# ================================================== Cabeçalho ========================================================
# --------------------------------------------------- Imagens --------------------------------------------------------


img_titulo = CTkImage(light_image=Image.open("images/icon_casa.png"),
                      dark_image=Image.open("images/icon_casa.png"),
                      size=(40, 40))

# --------------------------------------------------- Título --------------------------------------------------------

frame_decorativo = CTkFrame(
    janela, fg_color=AZUL_ESCURO, corner_radius=0, height=60)
frame_decorativo.grid(row=0, column=0, sticky="ew", columnspan=3)

frame_titulo = CTkFrame(janela, fg_color=AZUL_CLARO, corner_radius=0)
frame_titulo.grid(row=0, column=0, sticky="ew", columnspan=3)

label_titulo = CTkLabel(frame_titulo, text="  Menu Inicial", fg_color="transparent",
                        compound=LEFT, anchor=W, font=FONTE_TITULO, image=img_titulo)
label_titulo.grid(row=0, column=0, padx=20, pady=5, sticky="ew")

# ================================================== Página Inicial ========================================================
# --------------------------------------------------- Imagens --------------------------------------------------------

# Imagem do botão de Cadastro
img_cadastro = CTkImage(light_image=Image.open("images/icon_cadastro.png"),
                        dark_image=Image.open("images/icon_cadastro.png"),
                        size=(50, 50))

# Imagem do botão de Iniciar
img_iniciar = CTkImage(light_image=Image.open("images/icon_iniciar.png"),
                       dark_image=Image.open("images/icon_iniciar.png"),
                       size=(50, 50))

# Imagem do botão de Sair
img_sair = CTkImage(light_image=Image.open("images/icon_saida.png"),
                    dark_image=Image.open("images/icon_saida.png"),
                    size=(50, 50))

# ---------------------------------------- Configuração de Janela / Grid --------------------------------------------------------
# Colunas
pagina_inicial.grid_columnconfigure(0, weight=1)
pagina_inicial.grid_columnconfigure(2, weight=1)

# Linhas
pagina_inicial.grid_rowconfigure(0, weight=1)
pagina_inicial.grid_rowconfigure(2, weight=1)
pagina_inicial.grid_rowconfigure(4, weight=1)
pagina_inicial.grid_rowconfigure(6, weight=1)

# Tornar frame transparente
pagina_inicial.configure(fg_color='transparent')

# (row=2, column=1, sticky='nsew')

# ---------------------------------------- Botões --------------------------------------------------------
# Botão de Cadastro
btn_cadastro = CTkButton(pagina_inicial, text="Cadastro", command=lambda: show_frame(pagina_cadastro), image=img_cadastro,
                         corner_radius=45, width=250, height=60, compound=LEFT, font=FONTE_TITULO)
btn_cadastro.grid(row=1, column=1, sticky="ew")

# Botão de Iniciar
btn_inicia = CTkButton(pagina_inicial, text="Iniciar", command=inicia_app, image=img_iniciar,
                       corner_radius=45, width=250, height=60, compound=LEFT, font=FONTE_TITULO)
btn_inicia.grid(row=3, column=1, sticky="ew")

# Botão de Sair
btn_sair = CTkButton(pagina_inicial, text="Sair", command=sair, image=img_sair,
                     corner_radius=45, width=250, height=60, compound=LEFT, font=FONTE_TITULO)
btn_sair.grid(row=5, column=1, sticky="ew")

# ================================================== Página de Cadastro ========================================================
# --------------------------------------------------- Imagens --------------------------------------------------------

# Imagem da aba de
img_alunos = CTkImage(light_image=Image.open("images/icon_aluno_2.png"),
                      dark_image=Image.open("images/icon_aluno_2.png"),
                      size=(20, 20))

# Imagem da aba de
img_cursos = CTkImage(light_image=Image.open("images/icon_cursos.png"),
                      dark_image=Image.open("images/icon_cursos.png"),
                      size=(20, 20))

# Imagem da aba de
img_aulas = CTkImage(light_image=Image.open("images/icon_aula.png"),
                     dark_image=Image.open("images/icon_aula.png"),
                     size=(20, 20))

# Imagem da aba de
img_faltas = CTkImage(light_image=Image.open("images/icon_falta.png"),
                      dark_image=Image.open("images/icon_falta.png"),
                      size=(20, 20))

# Imagem da aba de
img_cameras = CTkImage(light_image=Image.open("images/icon_camera.png"),
                       dark_image=Image.open("images/icon_camera.png"),
                       size=(20, 20))

# Imagem da aba de
img_voltar = CTkImage(light_image=Image.open("images/icon_voltar.png"),
                      dark_image=Image.open("images/icon_voltar.png"),
                      size=(20, 20))

# ---------------------------------------- Configuração de Grid --------------------------------------------------------
# Colunas
pagina_cadastro.grid_columnconfigure(0, weight=1)
pagina_cadastro.grid_columnconfigure(6, weight=1)

# Linhas
pagina_cadastro.grid_rowconfigure(1, weight=1)
pagina_cadastro.grid_rowconfigure(9, weight=1)

# Tornar frame transparente
pagina_cadastro.configure(fg_color='transparent')

# ---------------------------------------- Frame dos ícones --------------------------------------------------------
frame_icones = CTkFrame(pagina_cadastro, fg_color='transparent', height=30)
frame_icones.grid(row=0, column=0, columnspan=7, rowspan=1, sticky='nsew')

frame_icones.grid_columnconfigure(0, weight=3)
frame_icones.grid_columnconfigure(1, weight=2)
frame_icones.grid_columnconfigure(2, weight=1)
frame_icones.grid_columnconfigure(3, weight=1)
frame_icones.grid_columnconfigure(4, weight=1)
frame_icones.grid_columnconfigure(5, weight=1)
frame_icones.grid_columnconfigure(6, weight=1)
frame_icones.grid_columnconfigure(7, weight=1)
frame_icones.grid_columnconfigure(8, weight=2)
frame_icones.grid_columnconfigure(9, weight=3)

label_img_aluno = CTkLabel(frame_icones, text="",
                           image=img_alunos, fg_color='transparent')
label_img_aluno.grid(row=0, column=2, sticky='nsew')

label_img_cursos = CTkLabel(frame_icones, text="",
                            image=img_cursos, fg_color='transparent')
label_img_cursos.grid(row=0, column=3, sticky='nsew')

label_img_aulas = CTkLabel(frame_icones, text="",
                           image=img_aulas, fg_color='transparent')
label_img_aulas.grid(row=0, column=4, sticky='nsew')

label_img_faltas = CTkLabel(frame_icones, text="",
                            image=img_faltas, fg_color='transparent')
label_img_faltas.grid(row=0, column=5, sticky='nsew')

label_img_cameras = CTkLabel(frame_icones, text="",
                             image=img_cameras, fg_color='transparent')
label_img_cameras.grid(row=0, column=6, sticky='nsew')

label_img_voltar = CTkLabel(frame_icones, text="",
                            image=img_voltar, fg_color='transparent')
label_img_voltar.grid(row=0, column=7, sticky='nsew')

# ---------------------------------------- TabView (#abas) --------------------------------------------------------


def voltar():
    if abas.get() == "Voltar":
        show_frame(pagina_inicial)
        abas.set("Alunos")


abas = CTkTabview(pagina_cadastro, command=voltar)
abas.grid(row=1, column=0, padx=5, pady=(0, 5),
          sticky="nsew", columnspan=7, rowspan=10)

abas.add("Alunos")
abas.add("Cursos/Turmas")
abas.add("Aulas")
abas.add("Faltas")
abas.add("Câmeras")
abas.add("Voltar")

# ---------------------------------------- Aba Alunos --------------------------------------------------------
# ---------------------------------------- Aba Cursos / Turmas --------------------------------------------------------
# ---------------------------------------- Aba Aulas --------------------------------------------------------
# ---------------------------------------- Aba Faltas --------------------------------------------------------
# ---------------------------------------- Aba Câmeras --------------------------------------------------------

# ---------------------------------------- Funções --------------------------------------------------------


# ---------------------------------------- Métodos de inicialização --------------------------------------------------------

# Fecha processos no "X" da janela
janela.protocol("WM_DELETE_WINDOW", sair)

# Primeira página a aparecer
show_frame(pagina_inicial)

# Main loop
janela.mainloop()
