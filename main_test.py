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
WIDTH = 1050
HEIGHT = 620

# Cores
AMARELO = '#FFEE70'
AZUL_CLARO = "#075EBD"
AZUL_ESCURO = "#023D71"
PRETO = "#000000"
BRANCO = "#FFFFFF"
VERDE = "#66C475"
VERDE_ESCURO = "#539E5E"
VERMELHO = "#FF5961"
VERMELHO_ESCURO = "#B74046"

# FONTEs
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

janela.grid_columnconfigure(0, weight=1)
janela.grid_columnconfigure(2, weight=1)

janela.grid_rowconfigure(1, weight=1)
janela.grid_rowconfigure(3, weight=1)

# ------------------------------------------- Configurações de páginas --------------------------------------------------------
# Frames / Páginas
frame_conteudo = CTkFrame(janela, fg_color='transparent', corner_radius=0)
frame_conteudo.grid(row=1, column=0, sticky='nsew', rowspan=3, columnspan=3)

frame_conteudo.grid_columnconfigure(0, weight=1)
frame_conteudo.grid_columnconfigure(4, weight=1)

frame_conteudo.grid_rowconfigure(8, weight=1)

pagina_inicial = CTkFrame(frame_conteudo, corner_radius=0)
pagina_inicial.grid(row=0, column=0, sticky='nsew', columnspan=5, rowspan=9)

pagina_cadastro = CTkFrame(frame_conteudo)
pagina_cadastro.grid(row=1, column=0, sticky='nsew', columnspan=5, rowspan=3)

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

    img = CTkImage(light_image=Image.open(f"images/icon_{nome_img}.png"),
                   dark_image=Image.open(f"images/icon_{nome_img}.png"),
                   size=(40, 40))

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

# ---------------------------------------- Botões --------------------------------------------------------
# Botão de Cadastro
btn_cadastro = CTkButton(pagina_inicial, text="Cadastro", command=lambda: direciona_cadastro(), image=img_cadastro,
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

# Imagem da aba de Alunos
img_alunos = CTkImage(light_image=Image.open("images/icon_aluno_2.png"),
                      dark_image=Image.open("images/icon_aluno_2.png"),
                      size=(25, 25))

# Imagem da aba de Cursos e Turmas
img_cursos = CTkImage(light_image=Image.open("images/icon_cursos.png"),
                      dark_image=Image.open("images/icon_cursos.png"),
                      size=(25, 25))

# Imagem da aba de Aulas
img_aulas = CTkImage(light_image=Image.open("images/icon_aula.png"),
                     dark_image=Image.open("images/icon_aula.png"),
                     size=(25, 25))

# Imagem da aba de Faltas
img_faltas = CTkImage(light_image=Image.open("images/icon_falta.png"),
                      dark_image=Image.open("images/icon_falta.png"),
                      size=(25, 25))

# Imagem da aba de Câmeras
img_cameras = CTkImage(light_image=Image.open("images/icon_camera.png"),
                       dark_image=Image.open("images/icon_camera.png"),
                       size=(25, 25))

# Imagem de Voltar
img_voltar = CTkImage(light_image=Image.open("images/icon_voltar.png"),
                      dark_image=Image.open("images/icon_voltar.png"),
                      size=(25, 25))

# Imagem de Pesquisa
img_pesquisa = CTkImage(light_image=Image.open("images/icon_lupa_lightmode.png"),
                        dark_image=Image.open("images/icon_lupa_darkmode.png"),
                        size=(25, 25))

# ---------------------------------------- Frame das Abas --------------------------------------------------------

# Frame das abas (Botões)
frame_abas = CTkFrame(frame_conteudo, fg_color=AZUL_ESCURO,
                      corner_radius=0, height=60)
frame_abas.grid(row=0, column=0, sticky="ew", columnspan=7)

btn_aluno = CTkButton(frame_abas, text="Alunos", image=img_alunos, command=lambda: controle('alunos'),
                      corner_radius=45, width=50, height=30, compound=LEFT, font=FONTE_BOTAO)
btn_aluno.pack(side=LEFT, expand=True, fill=X, padx=(20, 0), pady=(0, 5))

btn_cursos = CTkButton(frame_abas, text="Cursos/Turmas", image=img_cursos, command=lambda: controle('cursos'),
                       corner_radius=45, width=50, height=30, compound=LEFT, font=FONTE_BOTAO)
btn_cursos.pack(after=btn_aluno, side=LEFT, expand=True,
                fill=X, padx=(20, 0), pady=(0, 5))

btn_aulas = CTkButton(frame_abas, text="Aulas", image=img_aulas, command=lambda: controle('aulas'),
                      corner_radius=45, width=50, height=30, compound=LEFT, font=FONTE_BOTAO)
btn_aulas.pack(after=btn_cursos, side=LEFT, expand=True,
               fill=X, padx=(20, 0), pady=(0, 5))

btn_faltas = CTkButton(frame_abas, text="Faltas", image=img_faltas, command=lambda: controle('faltas'),
                       corner_radius=45, width=50, height=30, compound=LEFT, font=FONTE_BOTAO)
btn_faltas.pack(after=btn_aulas, side=LEFT, expand=True,
                fill=X, padx=(20, 0), pady=(0, 5))

btn_camera = CTkButton(frame_abas, text="Câmeras", image=img_cameras, command=lambda: controle('cameras'),
                       corner_radius=45, width=50, height=30, compound=LEFT, font=FONTE_BOTAO)
btn_camera.pack(after=btn_faltas, side=LEFT, expand=True,
                fill=X, padx=(20, 0), pady=(0, 5))

btn_voltar = CTkButton(frame_abas, text="Alunos", image=img_voltar, command=lambda: voltar(),
                       corner_radius=45, width=50, height=30, compound=LEFT, font=FONTE_BOTAO)
btn_voltar.pack(after=btn_camera, side=LEFT, expand=True,
                fill=X, padx=(20, 20), pady=(0, 5))

# ---------------------------------------- Frame das Tabelas --------------------------------------------------------

frame_tabela = CTkFrame(frame_conteudo)
frame_tabela.grid(row=4, column=0, sticky='nsew', columnspan=5,
                  rowspan=5, ipadx=5, ipady=10)

frame_tabela.grid_columnconfigure(0, weight=1)
frame_tabela.grid_columnconfigure(4, weight=1)

frame_tabela.grid_rowconfigure(0, weight=1)
frame_tabela.grid_rowconfigure(4, weight=1)

# ---------------------------------------- Configuração da Página de cadastro --------------------------------------------------------
# Colunas
pagina_cadastro.grid_columnconfigure(0, weight=2)
pagina_cadastro.grid_columnconfigure(1, weight=1)
pagina_cadastro.grid_columnconfigure(2, weight=2)
pagina_cadastro.grid_columnconfigure(3, weight=2)
pagina_cadastro.grid_columnconfigure(5, weight=1)

# Tornar frame transparente
pagina_cadastro.configure(fg_color='transparent')

# ---------------------------------------- Alunos ---------------------------------------------------------------
# Função de cadastro de alunos


def alunos():
    # Titulo da página
    troca_titulo('  Cadastro de Alunos', 'aluno')

# ---------------------------------------- Configuração da pagina de cadastro --------------------------------------------------------

    pagina_cadastro.grid_columnconfigure(0, weight=2)
    pagina_cadastro.grid_columnconfigure(1, weight=1)
    pagina_cadastro.grid_columnconfigure(2, weight=2)
    pagina_cadastro.grid_columnconfigure(3, weight=2)
    pagina_cadastro.grid_columnconfigure(4, weight=0)
    pagina_cadastro.grid_columnconfigure(5, weight=1)

# ---------------------------------------- Configuração do frame de tabela --------------------------------------------------------

    frame_tabela.grid_columnconfigure(0, weight=1)
    frame_tabela.grid_columnconfigure(3, weight=0)
    frame_tabela.grid_columnconfigure(4, weight=1)

    frame_tabela.grid_rowconfigure(0, weight=0)
    frame_tabela.grid_rowconfigure(1, weight=0)
    frame_tabela.grid_rowconfigure(4, weight=1)

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

            alunos()

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

            label_foto = CTkLabel(frame_foto, text="",
                                  image=aluno_foto, fg_color='transparent')
            label_foto.grid(row=0, column=0, sticky='nsew', rowspan=5)

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
                botao_undo = CTkButton(pagina_cadastro, command=undo_atualiza, anchor=CENTER, text='DESFAZER',
                                       font=FONTE_BOTAO, fg_color=VERMELHO, hover_color=VERMELHO_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
                botao_undo.grid(row=2, column=6, sticky='ew')

            # Botão salvar alterações do aluno
            botao_salvar = CTkButton(pagina_cadastro, command=atualiza, anchor=CENTER, text='SALVAR\nALTERAÇÕES',
                                     font=FONTE_BOTAO, fg_color=VERDE, hover_color=VERDE_ESCURO, border_color=AMARELO, border_width=2, corner_radius=58)
            botao_salvar.grid(row=4, column=6, sticky='ew')

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
            botao_desfazer = CTkButton(pagina_cadastro, command=undo_apaga, anchor=CENTER, text='DESFAZER',
                                       font=FONTE_BOTAO, fg_color='transparent', border_color=AMARELO, border_width=2, corner_radius=32)
            botao_desfazer.grid(row=2, column=6, sticky='ew')

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
            aluno_foto = aluno_foto.resize((130, 150))
            aluno_foto = ImageTk.PhotoImage(aluno_foto)

            label_foto = CTkLabel(frame_foto, text="",
                                  image=aluno_foto, fg_color='transparent')
            label_foto.grid(row=0, column=0, sticky='nsew', rowspan=5)

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
                botao_undo = CTkButton(pagina_cadastro, command=undo_atualiza, anchor=CENTER, text='DESFAZER', font=FONTE_BOTAO,
                                       fg_color='transparent', border_color=AMARELO, border_width=2, corner_radius=32)
                botao_undo.grid(row=2, column=6, sticky='ew')

            # Botão salvar alterações do aluno
            botao_salvar = CTkButton(pagina_cadastro, command=atualiza, anchor=CENTER, text='SALVAR\nALTERAÇÕES',
                                     font=FONTE_BOTAO, fg_color='transparent', border_color=AMARELO, border_width=2, corner_radius=58)
            botao_salvar.grid(row=4, column=6, sticky='ew')

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
            aluno_foto = aluno_foto.resize((130, 150))
            aluno_foto = ImageTk.PhotoImage(aluno_foto)

            label_foto = CTkLabel(frame_foto, text="",
                                  image=aluno_foto, fg_color='transparent')
            label_foto.grid(row=0, column=0, sticky='nsew', rowspan=5)

        except IndexError:
            messagebox.showerror("Erro", "Selecione um aluno na tabela.")

    # Label e entry do Nome do aluno
    label_nome = CTkLabel(pagina_cadastro, text="Nome *",
                          anchor=NW, font=FONTE, fg_color='transparent')
    label_nome.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 5))

    entry_nome_aluno = CTkEntry(
        pagina_cadastro, placeholder_text='Nome do Aluno')
    entry_nome_aluno.grid(row=1, column=0, sticky='ew',
                          columnspan=2, padx=10, pady=(0, 5))

    # Label e entry do email
    label_email = CTkLabel(pagina_cadastro, text="Email *",
                           compound=LEFT, anchor=NW, font=FONTE, fg_color='transparent')
    label_email.grid(row=2, column=0, sticky='ew', padx=10, pady=(10, 5))

    entry_email = CTkEntry(pagina_cadastro, placeholder_text='Email do Aluno')
    entry_email.grid(row=3, column=0, sticky='ew',
                     columnspan=2, padx=10, pady=(0, 5))

    # Label e entry do Telefone
    label_telefone = CTkLabel(pagina_cadastro, text="Telefone *",
                              compound=LEFT, anchor=NW, font=FONTE, fg_color='transparent')
    label_telefone.grid(row=4, column=0, sticky='ew', padx=10, pady=(10, 5))

    entry_telefone = CTkEntry(
        pagina_cadastro, placeholder_text='Telefone do Aluno')
    entry_telefone.grid(row=5, column=0, sticky='ew', padx=10, pady=(0, 5))

    # Label e combobox do Sexo
    label_sexo = CTkLabel(pagina_cadastro, text="Sexo *", compound=LEFT,
                          anchor=NW, font=FONTE, fg_color='transparent')
    label_sexo.grid(row=4, column=1, sticky='ew', padx=10, pady=(10, 5))

    combobox_sexo = CTkComboBox(pagina_cadastro, font=FONTE_BOTAO, values=[
                                'Masculino', 'Feminino'], state='readonly')
    combobox_sexo.grid(row=5, column=1, sticky='ew', padx=10, pady=(0, 5))

    # Label e entry do RA
    label_ra = CTkLabel(pagina_cadastro, text="RA *", compound=LEFT,
                        anchor=NW, font=FONTE, fg_color='transparent')
    label_ra.grid(row=2, column=3, sticky='ew', padx=5, pady=(10, 5))

    entry_ra = CTkEntry(pagina_cadastro, placeholder_text='RA do Aluno')
    entry_ra.grid(row=3, column=3, sticky='ew', padx=5, pady=(0, 5))

    # Pegando as Turmas
    turmas = utils.mostra_turma()
    turma = []

    for item in turmas:
        turma.append(item[1])

    # Label e combobox do Curso
    label_turma = CTkLabel(pagina_cadastro, text="Turma *",
                           compound=LEFT, anchor=NW, font=FONTE, fg_color='transparent')
    label_turma.grid(row=4, column=3, sticky='ew', padx=5, pady=(10, 5))

    combobox_turma = CTkComboBox(
        pagina_cadastro, font=FONTE_BOTAO, values=turma, state='readonly')
    combobox_turma.grid(row=5, column=3, sticky='ew', padx=5, pady=(0, 5))

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

            label_foto = CTkLabel(frame_foto, text="",
                                  image=aluno_foto, fg_color='transparent')
            label_foto.grid(row=0, column=0, sticky='ns', rowspan=5)

            botao_carregar.configure(text="TROCAR DE FOTO")
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

            label_foto = CTkLabel(frame_foto, text="",
                                  image=aluno_foto, fg_color='transparent')
            label_foto.grid(row=0, column=0, sticky='ns', rowspan=5)
        except:
            messagebox.showerror('Erro', 'Não foi possível processar a foto corretamente.\nPor favor tente novamente')

    # Desfaz a ação de atualizar o aluno

    def undo_atualiza():
        global undo_list, botao_undo, undo_falta
        utils.atualiza_aluno(undo_list)
        mostra_alunos()
        botao_undo.destroy()
        utils.atualiza_falta(undo_falta)

    # Botão desfazer alteração do aluno
    botao_undo = CTkButton(pagina_cadastro, command=undo_atualiza,
                           anchor=CENTER, text='DESFAZER', font=FONTE_BOTAO, fg_color=VERDE, hover_color=VERDE_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
    botao_undo.grid(row=2, column=5, sticky='ew')

    botao_undo.destroy()

    frame_foto = CTkFrame(pagina_cadastro, fg_color='transparent',
                          border_width=2, width=130, height=150, border_color=BRANCO)
    frame_foto.grid(row=0, column=2, pady=(10, 0), rowspan=5)

    # Botão Tira foto
    botao_foto = CTkButton(pagina_cadastro, command=tira_foto, text='Tirar foto'.upper(
    ), anchor=CENTER, font=FONTE_BOTAO, fg_color='transparent', border_color=AMARELO, border_width=2, corner_radius=45)
    botao_foto.grid(row=5, column=2, sticky='ew', padx=5, pady=(5, 0))

    # Botão Carregar Foto
    botao_carregar = CTkButton(pagina_cadastro, command=escolhe_imagem, text='Carregar\nfoto'.upper(
    ), anchor=CENTER, font=FONTE_BOTAO, fg_color='transparent', border_color=AMARELO, border_width=2, corner_radius=58)
    botao_carregar.grid(row=6, column=2, sticky='ew', padx=5, pady=(5, 0))

    linha_separacao = CTkFrame(
        pagina_cadastro, width=5, fg_color=BRANCO, corner_radius=100)
    linha_separacao.grid(row=0, column=4, sticky='ns', rowspan=7)

    # Procura Aluno
    label_procura_nome = CTkLabel(
        pagina_cadastro, text="Procurar Aluno", anchor=NW, font=FONTE, fg_color='transparent')
    label_procura_nome.grid(row=0, column=5, sticky='ew',
                            columnspan=2, padx=(10, 0), pady=(10, 0))

    entry_procura = CTkEntry(pagina_cadastro, placeholder_text='RA do Aluno')
    entry_procura.grid(row=1, column=5, sticky='ew', padx=(10, 5), pady=5)

    botao_procurar = CTkButton(pagina_cadastro, command=pesquisa_aluno, text="", image=img_pesquisa,
                               font=FONTE_BOTAO, fg_color='transparent', border_color=AMARELO, border_width=2, corner_radius=32)
    botao_procurar.grid(row=1, column=6, sticky='ew', padx=5)

    # ------------------------------------ Botões ---------------------------------

    # Botão adicionar aluno
    botao_adicionar = CTkButton(pagina_cadastro, command=novo_aluno, anchor=CENTER, text='ADICIONAR',
                                font=FONTE_BOTAO, fg_color=VERDE, hover_color=VERDE_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
    botao_adicionar.grid(row=2, column=5, sticky='ew', padx=5, pady=(10, 0))

    # Botão alterar aluno
    botao_alterar = CTkButton(pagina_cadastro, command=carregar_aluno, anchor=CENTER, text='ALTERAR',
                              font=FONTE_BOTAO, fg_color=AZUL_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
    botao_alterar.grid(row=4, column=5, sticky='ew', padx=5)

    # Botão deletar aluno
    botao_deletar = CTkButton(pagina_cadastro, command=apagar_aluno, anchor=CENTER, text='DELETAR',
                              font=FONTE_BOTAO, fg_color=VERMELHO, hover_color=VERMELHO_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
    botao_deletar.grid(row=6, column=5, sticky='ew', padx=5)

    # Botão informações do aluno
    botao_mostrar = CTkButton(pagina_cadastro, command=info_aluno, anchor=CENTER, text='INFO',
                              font=FONTE_BOTAO, fg_color='transparent', border_color=AMARELO, border_width=2, corner_radius=32)
    botao_mostrar.grid(row=6, column=6, sticky='ew', padx=5)

    # Mostra a tabela com os alunos

    def mostra_alunos():
        tabela_alunos_label = CTkLabel(
            pagina_cadastro, text="Tabela de alunos", anchor=SW, font=FONTE, fg_color='transparent')
        tabela_alunos_label.grid(row=6, column=0, sticky='ew', padx=5)

        lista_cabecalho = ['RA', 'Nome', 'Email',
                           'Telefone', 'Sexo', 'Foto', 'Turma']

        lista_itens = utils.mostra_aluno()

        global tree_alunos

        tree_alunos = ttk.Treeview(
            frame_tabela, selectmode="extended", columns=lista_cabecalho, show='headings')
        tree_alunos.grid(row=0, column=0, columnspan=6,
                         rowspan=6, padx=5, sticky='nsew')

        # Scrollbars
        scroll_vertical = CTkScrollbar(
            frame_tabela, orientation='vertical', command=tree_alunos.yview, corner_radius=32)
        scroll_vertical.grid(row=0, column=6, rowspan=5, sticky='ns')

        scroll_horizontal = CTkScrollbar(
            frame_tabela, orientation="horizontal", command=tree_alunos.xview, corner_radius=32)
        scroll_horizontal.grid(row=6, column=0, columnspan=6, sticky='ew')

        tree_alunos.configure(yscrollcommand=scroll_vertical.set,
                              xscrollcommand=scroll_horizontal.set)

        posicao_coluna = ["nw", "nw", "nw", "center",
                          "center", "center", "center"]
        largura_coluna = [60, 150, 150, 100, 60, 70, 60]
        cont = 0

        for coluna in lista_cabecalho:
            tree_alunos.heading(coluna, text=coluna.title(), anchor=NW)
            tree_alunos.column(
                coluna, width=largura_coluna[cont], anchor=posicao_coluna[cont])

            cont += 1

        for item in lista_itens:
            tree_alunos.insert('', 'end', values=item)

    mostra_alunos()

# ---------------------------------------- Cursos/Turmas --------------------------------------------------------
# Função de cadastro de alunos


def cursos_turmas():
    # Titulo da página
    troca_titulo('  Cadastro de Cursos e Turmas', 'cursos')

# ---------------------------------------- Configuração da pagina de cadastro --------------------------------------------------------

    pagina_cadastro.grid_columnconfigure(0, weight=2)
    pagina_cadastro.grid_columnconfigure(1, weight=1)
    pagina_cadastro.grid_columnconfigure(2, weight=2)
    pagina_cadastro.grid_columnconfigure(3, weight=2)
    pagina_cadastro.grid_columnconfigure(4, weight=0)
    pagina_cadastro.grid_columnconfigure(5, weight=1)

# ---------------------------------------- Configuração do frame de tabela --------------------------------------------------------

    frame_tabela.grid_columnconfigure(1, weight=1)
    frame_tabela.grid_columnconfigure(4, weight=1)

    frame_tabela.grid_rowconfigure(0, weight=0)
    frame_tabela.grid_rowconfigure(1, weight=0)
    frame_tabela.grid_rowconfigure(3, weight=1)

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
                botao_undo_curso = CTkButton(pagina_cadastro, command=undo_atualiza_curso, anchor=CENTER, text='DESFAZER',
                                             font=FONTE_BOTAO, fg_color=VERMELHO, hover_color=VERMELHO_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
                botao_undo_curso.grid(
                    row=4, column=2, sticky='ew', padx=5, pady=(10, 5))

            botao_salvar = CTkButton(pagina_cadastro, command=atualiza, anchor=CENTER, text="Salvar\nalterações".upper(
            ), font=FONTE_BOTAO, fg_color=VERDE, hover=VERDE_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
            botao_salvar.grid(row=4, column=1, sticky='ew',
                              padx=5, pady=(10, 5))
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
            botao_desfazer = CTkButton(pagina_cadastro, command=undo_apaga, anchor=CENTER, text='DESFAZER',
                                       font=FONTE_BOTAO, fg_color=VERMELHO, hover_color=VERMELHO_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
            botao_desfazer.grid(
                row=4, column=2, sticky='ew', padx=5, pady=(10, 5))

        except IndexError:
            messagebox.showerror("Erro", "Selecione um curso na tabela.")

    # Label e entry do Nome do curso
    label_nome = CTkLabel(pagina_cadastro, text="Nome do Curso *",
                          anchor=NW, font=FONTE, fg_color='transparent')
    label_nome.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 5))

    entry_nome_curso = CTkEntry(
        pagina_cadastro, placeholder_text="Nome do Curso")
    entry_nome_curso.grid(row=1, column=0, sticky='ew',
                          columnspan=2, padx=10, pady=(0, 5))

    # Label e entry da Duração do curso
    label_duracao = CTkLabel(
        pagina_cadastro, text="Duração *", anchor=NW, font=FONTE, fg_color='transparent')
    label_duracao.grid(row=2, column=0, sticky='ew', padx=10, pady=(10, 5))

    entry_duracao = CTkEntry(
        pagina_cadastro, placeholder_text="Duração do curso")
    entry_duracao.grid(row=3, column=0, sticky='ew', padx=10, pady=(0, 5))

    # Botão salvar curso
    botao_curso_adicionar = CTkButton(pagina_cadastro, command=novo_curso, anchor=CENTER, text='ADICIONAR',
                                      font=FONTE_BOTAO, fg_color=VERDE, hover_color=VERDE_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
    botao_curso_adicionar.grid(
        row=5, column=0, sticky='ew', padx=(10, 5), pady=(10, 5))

    # Botão atualizar curso
    botao_curso_alterar = CTkButton(pagina_cadastro, command=carregar_curso, anchor=CENTER, text='ALTERAR',
                                    font=FONTE_BOTAO, fg_color='transparent', border_color=AMARELO, border_width=2, corner_radius=32)
    botao_curso_alterar.grid(
        row=5, column=1, sticky='ew', padx=5, pady=(10, 5))

    # Botão deletar curso
    botao_curso_deletar = CTkButton(pagina_cadastro, command=apagar_curso, anchor=CENTER, text='DELETAR',
                                    font=FONTE_BOTAO, fg_color=VERMELHO, hover_color=VERMELHO_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
    botao_curso_deletar.grid(
        row=5, column=2, sticky='ew', padx=5, pady=(10, 5))

    # Mostra Tabela Cursos
    def mostra_cursos():
        tabela_cursos_label = CTkLabel(
            pagina_cadastro, text="Tabela de cursos", anchor=SW, font=FONTE, fg_color='transparent')
        tabela_cursos_label.grid(
            row=6, column=0, sticky='ew', padx=10, pady=(10, 5))

        lista_cabecalho = ['ID', 'Curso', 'Duração']

        lista_itens = utils.mostra_curso()

        global tree_cursos

        tree_cursos = ttk.Treeview(
            frame_tabela, selectmode="extended", columns=lista_cabecalho, show='headings')
        tree_cursos.grid(row=0, column=0, sticky='nsew', padx=5,
                         columnspan=2, rowspan=5)

        # Scrollbars
        scroll_vertical = CTkScrollbar(
            frame_tabela, orientation='vertical', command=tree_cursos.yview, corner_radius=32)
        scroll_vertical.grid(row=0, column=2, sticky='ns', rowspan=5)

        scroll_horizontal = CTkScrollbar(
            frame_tabela, orientation="horizontal", command=tree_cursos.xview, corner_radius=32)
        scroll_horizontal.grid(row=5, column=0, sticky='ew', columnspan=2)

        tree_cursos.configure(yscrollcommand=scroll_vertical,
                              xscrollcommand=scroll_horizontal)

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
    botao_undo_curso = CTkButton(pagina_cadastro, command=undo_atualiza_curso, anchor=CENTER, text='DESFAZER',
                                 font=FONTE_BOTAO, fg_color=VERMELHO, hover_color=VERMELHO_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
    botao_undo_curso.grid(row=4, column=2, sticky='ew', padx=10, pady=10)

    botao_undo_curso.destroy()

    mostra_cursos()

    # ------------------------------- Linha Separatória ---------------------------------------

    linha_separacao = CTkFrame(
        pagina_cadastro, width=5, fg_color=BRANCO, corner_radius=220)
    linha_separacao.grid(row=0, column=3, sticky='ns', rowspan=7)

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
            combobox_curso.set('')
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
                combobox_curso.set('')
                data_inicio.delete(0, END)

                # atualiza os dados da tabela
                mostra_turmas()

                botao_salvar.destroy()

                # Botão desfazer alteração do aluno
                botao_undo_turma = CTkButton(pagina_cadastro, command=undo_atualiza_turma, anchor=CENTER, text='DESFAZER',
                                             font=FONTE_BOTAO, fg_color=VERMELHO, hover_color=VERMELHO_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
                botao_undo_turma.grid(
                    row=4, column=7, sticky='ew', padx=(0, 5), pady=(10, 5))

            botao_salvar = CTkButton(pagina_cadastro, command=atualiza, anchor=CENTER, text="Salvar\nalterações".upper(
            ), font=FONTE_BOTAO, fg_color=VERDE, hover_color=VERDE_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
            botao_salvar.grid(row=4, column=6, sticky='ew',
                              padx=(10, 5), pady=(10, 5))
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
            botao_desfazer = CTkButton(pagina_cadastro, command=undo_atualiza_turma, anchor=CENTER, text='DESFAZER',
                                       font=FONTE_BOTAO, fg_color=VERMELHO, hover_color=VERMELHO_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
            botao_desfazer.grid(row=4, column=7, sticky='ew',
                                padx=(0, 5), pady=(10, 5))

        except IndexError:
            messagebox.showerror("Erro", "Selecione um turma na tabela.")

    label_nome = CTkLabel(pagina_cadastro, text="Nome Turma *",
                          anchor=NW, font=FONTE, fg_color='transparent')
    label_nome.grid(row=0, column=4, sticky='ew',
                    padx=5, pady=(10, 5), columnspan=2)

    entry_nome_turma = CTkEntry(
        pagina_cadastro, placeholder_text="Nome da Turma")
    entry_nome_turma.grid(row=1, column=4, sticky='ew', padx=5, pady=(0, 5))

    label_curso_turma = CTkLabel(
        pagina_cadastro, text="Curso *", anchor=NW, font=FONTE, fg_color='transparent')
    label_curso_turma.grid(row=2, column=4, sticky='ew', padx=5, pady=(10, 5))

    # Pegando os cursos
    cursos = utils.mostra_curso()
    curso = []

    for item in cursos:
        curso.append(item[1])

    combobox_curso = CTkComboBox(
        pagina_cadastro, values=curso, state='readonly')
    combobox_curso.grid(row=3, column=4, sticky='ew', padx=5, pady=(0, 5))

    label_data_inicio = CTkLabel(pagina_cadastro, text="Data de início *",
                                 anchor=NW, font=FONTE, fg_color='transparent')
    label_data_inicio.grid(row=4, column=4, sticky='ew', padx=5, pady=(10, 5))

    data_inicio = DateEntry(pagina_cadastro, background=AZUL_ESCURO,
                            foreground=BRANCO, borderwidth=2, year=2023)
    data_inicio.grid(row=5, column=4, sticky='ew', padx=5, pady=(10, 5))

    # Botão adicionar turma
    botao_turma_adicionar = CTkButton(pagina_cadastro, command=nova_turma, anchor=CENTER, text='ADICIONAR',
                                      font=FONTE_BOTAO, fg_color=VERDE, hover_color=VERDE_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
    botao_turma_adicionar.grid(
        row=5, column=5, sticky='ew', padx=(0, 5), pady=(10, 5))

    # Botão alterar turma
    botao_turma_alterar = CTkButton(pagina_cadastro, command=carregar_turma, anchor=CENTER, text='ALTERAR',
                                    font=FONTE_BOTAO, fg_color='transparent', border_color=AMARELO, border_width=2, corner_radius=32)
    botao_turma_alterar.grid(
        row=5, column=6, sticky='ew', padx=(0, 5), pady=(10, 5))

    # Botão deletar turma
    botao_turma_deletar = CTkButton(pagina_cadastro, command=apagar_turma, anchor=CENTER, text='DELETAR',
                                    font=FONTE_BOTAO, fg_color=VERMELHO, hover_color=VERMELHO_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
    botao_turma_deletar.grid(
        row=5, column=7, sticky='ew', padx=(0, 5), pady=(10, 5))

    def mostra_turmas():
        global combobox_curso

        combobox_curso.destroy()

        # Atualiza o combobox dos cursos
        # Pegando os cursos
        cursos = utils.mostra_curso()
        curso = []

        for item in cursos:
            curso.append(item[1])

        combobox_curso = CTkComboBox(
            pagina_cadastro, values=curso, state='readonly')
        combobox_curso.grid(row=3, column=4, sticky='ew', padx=5, pady=(0, 5))

        tabela_turma_label = CTkLabel(pagina_cadastro, text="Tabela de turmas",
                                      anchor=SW, font=FONTE, fg_color='transparent')
        tabela_turma_label.grid(row=6, column=4, sticky='ew', padx=5)

        lista_cabecalho = ['ID', 'Nome da Turma', 'Curso', 'Inicio']

        lista_itens = utils.mostra_turma()

        global tree_turma

        tree_turma = ttk.Treeview(
            frame_tabela, selectmode="extended", columns=lista_cabecalho, show='headings')
        tree_turma.grid(row=0, column=4, sticky='nsew', padx=5,
                        columnspan=2, rowspan=5)

        # Scrollbars
        scroll_vertical = CTkScrollbar(
            frame_tabela, orientation='vertical', command=tree_turma.yview, corner_radius=32)
        scroll_vertical.grid(row=0, column=6, sticky='ns', rowspan=5)

        scroll_horizontal = CTkScrollbar(
            frame_tabela, orientation="horizontal", command=tree_turma.xview, corner_radius=32)
        scroll_horizontal.grid(row=5, column=4, sticky='ew', columnspan=2)

        tree_turma.configure(yscrollcommand=scroll_vertical,
                             xscrollcommand=scroll_horizontal)

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
    botao_undo_turma = CTkButton(pagina_cadastro, command=undo_atualiza_turma, anchor=CENTER, text='DESFAZER',
                                 font=FONTE_BOTAO, fg_color=VERMELHO, hover_color=VERMELHO_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
    botao_undo_turma.grid(row=4, column=7, sticky='ew',
                          padx=(0, 5), pady=(10, 5))

    botao_undo_turma.destroy()

    mostra_turmas()

# ---------------------------------------- Aulas ----------------------------------------------------------------
# Função de cadastro de alunos


def aulas():
    # Titulo da página
    troca_titulo('  Cadastro de Aulas', 'aula')

# ---------------------------------------- Configuração da pagina de cadastro --------------------------------------------------------
    
    pagina_cadastro.grid_columnconfigure(0, weight=1)
    pagina_cadastro.grid_columnconfigure(1, weight=1)
    pagina_cadastro.grid_columnconfigure(2, weight=1)
    pagina_cadastro.grid_columnconfigure(3, weight=1)
    pagina_cadastro.grid_columnconfigure(4, weight=1)
    pagina_cadastro.grid_columnconfigure(5, weight=1)

# ---------------------------------------- Detalhes das Aulas --------------------------------------------------------
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
                botao_undo = CTkButton(pagina_cadastro, command=undo_atualiza, anchor=CENTER, text='DESFAZER', font=FONTE_BOTAO,
                                       fg_color=VERMELHO, hover_color=VERMELHO_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
                botao_undo.grid(row=3, column=5, sticky='ew', padx=10, pady=5)

                botao_salvar.destroy()

            botao_salvar = CTkButton(pagina_cadastro, command=atualiza, anchor=CENTER, text="Salvar\nalterações".upper(
            ), font=FONTE_BOTAO, fg_color=VERDE, hover_color=VERDE_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
            botao_salvar.grid(row=2, column=5, sticky='ew',
                              padx=10, pady=(10, 5))
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
            botao_desfazer = CTkButton(pagina_cadastro, command=undo_apaga, anchor=CENTER, text='DESFAZER',
                                       font=FONTE_BOTAO, fg_color=VERMELHO, hover_color=VERMELHO_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
            botao_desfazer.grid(row=3, column=5, sticky='ew', padx=10, pady=5)

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
                botao_undo = CTkButton(pagina_cadastro, command=undo_atualiza, anchor=CENTER, text='DESFAZER',
                                       font=FONTE_BOTAO, fg_color=VERMELHO, hover_color=VERMELHO_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
                botao_undo.grid(row=3, column=5, sticky='ew', padx=10, pady=5)

            # Botão salvar alterações da aula
            botao_salvar = CTkButton(pagina_cadastro, command=atualiza, anchor=CENTER, text='Salvar\nalterações'.upper(
            ), font=FONTE_BOTAO, fg_color=VERDE, hover_color=VERDE_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
            botao_salvar.grid(row=2, column=5, sticky='ew',
                              padx=10, pady=(10, 5))

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
    label_nome = CTkLabel(pagina_cadastro, text="Nome *",
                          anchor=NW, font=FONTE, fg_color='transparent')
    label_nome.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 5))

    entry_nome_aula = CTkEntry(
        pagina_cadastro, placeholder_text='Nome da Aula')
    entry_nome_aula.grid(row=1, column=0, sticky='ew',
                         columnspan=2, padx=10, pady=(0, 5))

    # Label e entry do dia
    label_dia = CTkLabel(pagina_cadastro, text="Dia da Semana *",
                         anchor=NW, font=FONTE, fg_color='transparent')
    label_dia.grid(row=2, column=0, sticky='ew', padx=10, pady=(10, 5))

    # Dias da semana
    dia_semana = ['Segunda-feira', 'Terça-feira',
                  'Quarta-feira', 'Quinta-feira', 'Sexta-feira']

    combobox_dia = CTkComboBox(
        pagina_cadastro, values=dia_semana, state='readonly')
    combobox_dia.grid(row=3, column=0, sticky='ew', padx=10, pady=(0, 5))

    # Pegando as Turmas
    turmas = utils.mostra_turma()
    turma = []

    for item in turmas:
        turma.append(item[1])

    # Label e combobox do Sexo
    label_turma = CTkLabel(pagina_cadastro, text="Turma *",
                           anchor=NW, font=FONTE, fg_color='transparent')
    label_turma.grid(row=0, column=2, sticky='ew', padx=15, pady=(10, 5))

    combobox_turma = CTkComboBox(
        pagina_cadastro, values=turma, state='readonly')
    combobox_turma.grid(row=1, column=2, sticky='ew', padx=15, pady=(0, 5))

    # Label e entry da hora de inicio
    label_hora = CTkLabel(pagina_cadastro, text="Hora de inicio *",
                          anchor=NW, font=FONTE, fg_color='transparent')
    label_hora.grid(row=2, column=2, sticky='ew', padx=15, pady=(10, 5))

    # Frame que fica o relógio de cadastro de hora
    frame_hora = CTkFrame(
        pagina_cadastro, fg_color=AZUL_CLARO, corner_radius=32)
    frame_hora.grid(row=3, column=2, sticky='ew', padx=0, pady=(0, 5))

    frame_hora.columnconfigure(0, weight=1)
    frame_hora.columnconfigure(2, weight=1)

    entry_hora = SpinTimePickerModern(frame_hora)
    entry_hora.addAll(constants.HOURS24)
    entry_hora.configureAll(bg=AZUL_CLARO, fg=BRANCO, font=FONTE_TITULO, hoverbg=AZUL_CLARO,
                            hovercolor=AZUL_ESCURO, clickedbg=AZUL_ESCURO, clickedcolor=BRANCO)
    entry_hora.configure_separator(bg=AZUL_CLARO, fg=BRANCO)
    entry_hora.grid(row=0, column=0, sticky='ew', padx=15, columnspan=3)

    linha_separacao = CTkFrame(
        pagina_cadastro, width=5, fg_color=BRANCO, corner_radius=100)
    linha_separacao.grid(row=0, column=3, sticky='ns', rowspan=6)

    # Procura aula
    label_procura_nome = CTkLabel(pagina_cadastro, text="Procurar aula",
                                  anchor=NW, font=FONTE, fg_color='transparent')
    label_procura_nome.grid(
        row=0, column=4, sticky='ew', padx=10, pady=(10, 5))

    entry_procura = CTkEntry(pagina_cadastro, placeholder_text='Nome da aula')
    entry_procura.grid(row=1, column=4, sticky='ew',
                       padx=10, pady=(0, 5), columnspan=2)

    # ------------------------------------ Botões ---------------------------------

    # Botão adicionar aula
    botao_adicionar = CTkButton(pagina_cadastro, command=nova_aula, anchor=CENTER, text='ADICIONAR',
                                font=FONTE_BOTAO, fg_color=VERDE, hover_color=VERDE_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
    botao_adicionar.grid(row=2, column=4, sticky='ew', padx=10, pady=(10, 5))

    # Botão alterar aula
    botao_alterar = CTkButton(pagina_cadastro, command=carregar_aula, anchor=CENTER, text='ALTERAR',
                              font=FONTE_BOTAO, fg_color='transparent', border_color=AMARELO, border_width=2, corner_radius=32)
    botao_alterar.grid(row=3, column=4, sticky='ew', padx=10, pady=5)

    # Botão deletar aula
    botao_deletar = CTkButton(pagina_cadastro, command=apagar_aula, anchor=CENTER, text='DELETAR',
                              font=FONTE_BOTAO, fg_color=VERMELHO, hover_color=VERMELHO_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
    botao_deletar.grid(row=4, column=4, sticky='ew', padx=10, pady=(5, 10))

    # Botão informações do aula
    botao_mostrar = CTkButton(pagina_cadastro, command=info_aula, anchor=CENTER, text='INFO',
                              font=FONTE_BOTAO, fg_color='transparent', border_color=AMARELO, border_width=2, corner_radius=32)
    botao_mostrar.grid(row=4, column=5, sticky='ew', padx=10, pady=(5, 10))

    # Botão pesquisa aula
    botao_procurar = CTkButton(pagina_cadastro, command=pesquisa_aula, text="", image=img_pesquisa,
                               font=FONTE_BOTAO, fg_color='transparent', border_color=AMARELO, border_width=2, corner_radius=32)
    botao_procurar.grid(row=1, column=6, sticky='ew', padx=(0, 5), pady=(0, 5))
    # ---------------------------------- Tabela das aulas -------------------------------------

    def mostra_aula():
        tabela_aula_label = CTkLabel(
            pagina_cadastro, text="Tabela de aulas", anchor=NW, font=FONTE, fg_color='transparent')
        tabela_aula_label.grid(row=5, column=0, sticky='ew', padx=10)

        lista_cabecalho = ['ID', 'Nome', 'Dia', 'Hora', 'ID Turma']

        lista_itens = utils.mostra_aula()

        global tree_aulas

        tree_aulas = ttk.Treeview(
            frame_tabela, selectmode="extended", columns=lista_cabecalho, show='headings')
        tree_aulas.grid(row=0, column=0, sticky='nsew',
                        padx=5, columnspan=5, rowspan=5)

        # Scrollbars
        scroll_vertical = CTkScrollbar(
            frame_tabela, orientation='vertical', command=tree_aulas.yview)
        scroll_vertical.grid(row=0, column=5, sticky='ns', rowspan=5)

        scroll_horizontal = CTkScrollbar(
            frame_tabela, orientation="horizontal", command=tree_aulas.xview)
        scroll_horizontal.grid(row=5, column=0, sticky='ew', columnspan=5)

        tree_aulas.configure(yscrollcommand=scroll_vertical,
                             xscrollcommand=scroll_horizontal)

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
    botao_undo = CTkButton(pagina_cadastro, command=undo_atualiza, anchor=CENTER, text='DESFAZER',
                           font=FONTE_BOTAO, fg_color=VERMELHO, hover_color=VERMELHO_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
    botao_undo.grid(row=3, column=5, sticky='ew', padx=20, pady=10)

    botao_undo.destroy()

    mostra_aula()

# ---------------------------------------- Faltas ---------------------------------------------------------------
# Função de cadastro de alunos


def faltas():
    # Titulo da página
    troca_titulo('  Faltas', 'falta')

    # ---------------------------------------- Configuração da pagina de cadastro --------------------------------------------------------

    pagina_cadastro.grid_columnconfigure(0, weight=1)
    pagina_cadastro.grid_columnconfigure(1, weight=0)
    pagina_cadastro.grid_columnconfigure(2, weight=2)
    pagina_cadastro.grid_columnconfigure(3, weight=1)
    pagina_cadastro.grid_columnconfigure(4, weight=0)
    pagina_cadastro.grid_columnconfigure(5, weight=2)

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
    label_procura_aluno = CTkLabel(pagina_cadastro, text="Procurar aluno",
                                   anchor=NW, font=FONTE, fg_color='transparent')
    label_procura_aluno.grid(
        row=0, column=0, sticky='ew', padx=10, pady=(10, 5))

    entry_procura_aluno = CTkEntry(
        pagina_cadastro, placeholder_text='RA do Aluno')
    entry_procura_aluno.grid(
        row=1, column=0, sticky='ew', padx=(10, 5), pady=(0, 5))

    # Botão pesquisa aluno
    botao_procura_aluno = CTkButton(pagina_cadastro, command=pesquisa_faltas_aluno, text="", image=img_pesquisa,
                                    font=FONTE_BOTAO, fg_color='transparent', border_color=AMARELO, border_width=2, corner_radius=32)
    botao_procura_aluno.grid(
        row=1, column=1, sticky='ew', padx=(0, 5), pady=(0, 5))

    # Procura por aula
    label_procura_aula = CTkLabel(pagina_cadastro, text="Procurar aula",
                                  anchor=NW, font=FONTE, fg_color='transparent')
    label_procura_aula.grid(
        row=0, column=3, sticky='ew', padx=10, pady=(10, 5))

    entry_procura_aula = CTkEntry(
        pagina_cadastro, placeholder_text='Nome da aula')
    entry_procura_aula.grid(row=1, column=3, sticky='ew',
                            padx=(10, 5), pady=(0, 5))

    # Botão pesquisa aula
    botao_procurar_aula = CTkButton(pagina_cadastro, command=pesquisa_faltas_aula, text="", image=img_pesquisa,
                                    font=FONTE_BOTAO, fg_color='transparent', border_color=AMARELO, border_width=2, corner_radius=32)
    botao_procurar_aula.grid(
        row=1, column=4, sticky='ew', padx=(0, 5), pady=(0, 5))

    # Botão mostra tabela de faltas, sem pesquisa
    botao_procurar_aula = CTkButton(pagina_cadastro, command=lambda: mostra_falta(""), text="CANCELAR\nPROCURA",
                                    font=FONTE_BOTAO, fg_color='transparent', border_color=AMARELO, border_width=2, corner_radius=32)
    botao_procurar_aula.grid(
        row=1, column=6, sticky='ew', padx=15, pady=(0, 5))

    # ---------------------------------- Tabela das faltas -------------------------------------

    def mostra_falta(tipo):
        global dados_falta

        lista_cabecalho = ['ID', 'RA',
                           'Nome do Aluno', 'Aula', 'Turma', 'Faltas']

        if tipo == "":
            lista_itens = utils.mostra_falta()
        elif tipo == "aluno" or tipo == "aula":
            lista_itens = dados_falta
            dados_falta = []

        tree_faltas = ttk.Treeview(
            frame_tabela, selectmode="extended", columns=lista_cabecalho, show='headings')
        tree_faltas.grid(row=0, column=0, sticky='nsew',
                         columnspan=5, rowspan=5, padx=5)

        # Scrollbars
        scroll_vertical = CTkScrollbar(
            frame_tabela, orientation='vertical', command=tree_faltas.yview)
        scroll_vertical.grid(row=0, column=5, sticky='ns', rowspan=5)

        scroll_horizontal = CTkScrollbar(
            frame_tabela, orientation="horizontal", command=tree_faltas.xview)
        scroll_horizontal.grid(row=5, column=0, sticky='ew', columnspan=5)

        tree_faltas.configure(yscrollcommand=scroll_vertical,
                              xscrollcommand=scroll_horizontal)

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
# ---------------------------------------- Câmeras --------------------------------------------------------------
# Função de cadastro de alunos


def cameras():
    # Titulo da página
    troca_titulo('  Cadastro de Câmeras', 'camera')

# ---------------------------------------- Configuração da pagina de cadastro --------------------------------------------------------
    
    pagina_cadastro.grid_columnconfigure(0, weight=1)
    pagina_cadastro.grid_columnconfigure(1, weight=0)
    pagina_cadastro.grid_columnconfigure(2, weight=0)
    pagina_cadastro.grid_columnconfigure(3, weight=0)
    pagina_cadastro.grid_columnconfigure(4, weight=0)
    pagina_cadastro.grid_columnconfigure(5, weight=0)
    pagina_cadastro.grid_columnconfigure(6, weight=0)

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
                botao_undo = CTkButton(pagina_cadastro, command=undo_atualiza, anchor=CENTER, text='DESFAZER',
                                        font=FONTE_BOTAO, fg_color=VERMELHO, hover_color=VERMELHO_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
                botao_undo.grid(row=3, column=5, sticky='ew', padx=(0,5), pady=(0,5))

            botao_salvar = Button(pagina_cadastro, command=atualiza, anchor=CENTER, text="SALVAR\nALTERAÇÕES",
                                        font=FONTE_BOTAO, fg_color=VERDE, hover_color=VERDE_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
            botao_salvar.grid(row=3, column=4, sticky='ew', padx=(0,5), pady=(0,5))

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
            botao_desfazer = CTkButton(pagina_cadastro, command=undo_apaga, anchor=CENTER, text='DESFAZER',
                                        font=FONTE_BOTAO, fg_color=VERMELHO, hover_color=VERMELHO_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
            botao_desfazer.grid(row=3, column=5, sticky='ew', padx=(0,5), pady=(0,5))

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
                botao_undo = CTkButton(pagina_cadastro, command=undo_atualiza, anchor=CENTER, text='DESFAZER',
                                        font=FONTE_BOTAO, fg_color=VERMELHO, hover_color=VERMELHO_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
                botao_undo.grid(row=3, column=5, sticky='ew', padx=(0,5), pady=(0,5))

            # Botão salvar alterações da camera
            botao_salvar = CTkButton(pagina_cadastro, command=atualiza, anchor=CENTER, text='SALVAR\nALTERAÇÕES',
                                        font=FONTE_BOTAO, fg_color=VERDE, hover_color=VERDE_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
            botao_salvar.grid(row=3, column=4, sticky='ew', padx=(0,5), pady=(0,5))

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
    label_nome = CTkLabel(pagina_cadastro, text="Nome *",
                       anchor=NW, font=FONTE, fg_color='transparent')
    label_nome.grid(row=0, column=0, sticky='ew', padx=10, pady=(10,5))

    entry_nome_camera = CTkEntry(pagina_cadastro, placeholder_text='Nome da câmera')
    entry_nome_camera.grid(row=1, column=0, sticky='ew', padx=10, pady=(0,5))

    # Label e entry do ip
    label_ip = CTkLabel(pagina_cadastro, text="IP *",
                     anchor=NW, font=FONTE, fg_color='transparent')
    label_ip.grid(row=2, column=0, sticky='ew', padx=10, pady=(10,5))

    entry_ip = CTkEntry(pagina_cadastro, placeholder_text='IP da câmera')
    entry_ip.grid(row=3, column=0, sticky='ew', padx=10, pady=(0,5))

    # Label e entry do usuario
    label_usuario = CTkLabel(pagina_cadastro, text="Usuario *",
                            anchor=NW, font=FONTE, fg_color='transparent')
    label_usuario.grid(row=0, column=1, sticky='ew', padx=10, pady=(10,5))

    entry_usuario = CTkEntry(pagina_cadastro, placeholder_text='Nome de usuário')
    entry_usuario.grid(row=1, column=1, sticky='ew', padx=10, pady=(0,5))

    # Label e combobox do Sexo
    label_senha = CTkLabel(pagina_cadastro, text="Senha *",
                        anchor=NW, font=FONTE, fg_color='transparent')
    label_senha.grid(row=2, column=1, sticky='ew', padx=10, pady=(10,5))

    entry_senha = CTkEntry(pagina_cadastro, placeholder_text='Senha')
    entry_senha['show'] = "*"
    entry_senha.grid(row=3, column=1, sticky='ew', padx=10, pady=(0,5))

    # Linha de separação
    linha_separacao = CTkFrame(pagina_cadastro, width=5, fg_color=BRANCO, corner_radius=100)
    linha_separacao.grid(row=0, column=2, sticky='ns', rowspan=5)

    # Procura Aluno
    label_procura_nome = CTkLabel(pagina_cadastro, text="Procurar camera",
                               anchor=NW, font=FONTE, fg_color='transparent')
    label_procura_nome.grid(row=0, column=3, sticky='ew', padx=10, pady=(10,5))

    entry_procura = CTkEntry(pagina_cadastro, placeholder_text='IP da câmera')
    entry_procura.grid(row=1, column=3, sticky='ew', padx=10, pady=(0,5))

    # ------------------------------------ Botões ---------------------------------

    # Botão adicionar camera
    botao_adicionar = CTkButton(pagina_cadastro, command=nova_camera, anchor=CENTER, text='ADICIONAR',
                            font=FONTE_BOTAO, fg_color=VERDE, hover_color=VERDE_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
    botao_adicionar.grid(row=2, column=3, sticky='ew', padx=(10,5), pady=(10,5))

    # Botão alterar camera
    botao_alterar = CTkButton(pagina_cadastro, command=carregar_camera, anchor=CENTER, text='ALTERAR',
                            font=FONTE_BOTAO, fg_color='transparent', border_color=AMARELO, border_width=2, corner_radius=32)
    botao_alterar.grid(row=2, column=4, sticky='ew', padx=(0,5), pady=(10,5))

    # Botão deletar camera
    botao_deletar = CTkButton(pagina_cadastro, command=apagar_camera, anchor=CENTER, text='DELETAR',
                            font=FONTE_BOTAO, fg_color=VERMELHO, hover_color=VERMELHO_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
    botao_deletar.grid(row=2, column=5, sticky='ew', padx=(0,5), pady=(10,5))

    # Botão informações do camera
    botao_mostrar = CTkButton(pagina_cadastro, command=info_camera, anchor=CENTER, text='INFO',
                            font=FONTE_BOTAO, fg_color='transparent', border_color=AMARELO, border_width=2, corner_radius=32)
    botao_mostrar.grid(row=2, column=6, sticky='ew', padx=(0,5), pady=(10,5))

    # Botão pesquisa camera
    botao_procurar = CTkButton(pagina_cadastro, command=pesquisa_camera, text="", image=img_pesquisa,
                            font=FONTE_BOTAO, fg_color='transparent', border_color=AMARELO, border_width=2, corner_radius=32)
    botao_procurar.grid(row=1, column=4, sticky='ew', padx=10, pady=(0,5))

    # Botão mostra visão da camera
    botao_imagem = CTkButton(pagina_cadastro, command=mostra_imagem, anchor=CENTER, text='MOSTRAR\nVÍDEO',
                            font=FONTE_BOTAO, fg_color='transparent', border_color=AMARELO, border_width=2, corner_radius=32)
    botao_imagem.grid(row=3, column=3, sticky='ew', padx=(10,5), pady=(0,5))

    # ---------------------------------- Tabela das cameras -------------------------------------

    def mostra_camera():
        tabela_camera_label = CTkLabel(pagina_cadastro, text="Tabela de cameras",
                                anchor=NW, font=FONTE, fg_color='transparent')
        tabela_camera_label.grid(row=4, column=0, sticky='ew', padx=10)
        lista_cabecalho = ['ID', 'Nome', 'IP', 'Usuario']

        lista_itens = utils.mostra_camera()

        global tree_cameras

        tree_cameras = ttk.Treeview(
            frame_tabela, selectmode="extended", columns=lista_cabecalho, show='headings')
        tree_cameras.grid(row=0, column=0, sticky="nsew", columnspan=5, rowspan=5, padx=5)

        # Scrollbars
        scroll_vertical = CTkScrollbar(
            frame_tabela, orientation='vertical', command=tree_cameras.yview)
        scroll_vertical.grid(row=0, column=5, sticky='ns', rowspan=5)
        
        scroll_horizontal = CTkScrollbar(
            frame_tabela, orientation="horizontal", command=tree_cameras.xview)
        scroll_horizontal.grid(row=5, column=0, sticky='ew', columnspan=5)

        tree_cameras.configure(yscrollcommand=scroll_vertical,
                               xscrollcommand=scroll_horizontal)

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
    botao_undo = CTkButton(pagina_cadastro, command=undo_atualiza, anchor=CENTER, text='DESFAZER',
                        font=FONTE_BOTAO, fg_color=VERMELHO, hover_color=VERMELHO_ESCURO, border_color=AMARELO, border_width=2, corner_radius=32)
    botao_undo.grid(row=3, column=4, sticky='ew', padx=(0,5), pady=(0,5))

    botao_undo.destroy()

    mostra_camera()

# ---------------------------------------- Ir e voltar da Página Inicial --------------------------------------------------------------


def direciona_cadastro():
    # Mostra aba de cadastro de aluno
    alunos()

    # Direciona para a página de cadastro
    show_frame(frame_abas)
    show_frame(pagina_cadastro)
    show_frame(frame_tabela)


def voltar():
    # Titulo da página
    troca_titulo('  Menu Inicial', 'casa')

    # Direciona para a página inicial
    show_frame(pagina_inicial)

# ---------------------------------------- Troca de janelas --------------------------------------------------------------

# Função de troca de janelas


def controle(comando_botao):

    for widget in pagina_cadastro.winfo_children():
        widget.destroy()

    for widget in frame_tabela.winfo_children():
        widget.destroy()

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


# ---------------------------------------- Métodos de inicialização --------------------------------------------------------

# Fecha processos no "X" da janela
janela.protocol("WM_DELETE_WINDOW", sair)

# Primeira página a aparecer
show_frame(pagina_inicial)

# Main loop
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
