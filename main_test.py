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
btn_cadastro = CTkButton(pagina_inicial, text="Cadastro", command=lambda:direciona_cadastro(), image=img_cadastro,
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
                      size=(25, 25))

# Imagem da aba de
img_cursos = CTkImage(light_image=Image.open("images/icon_cursos.png"),
                      dark_image=Image.open("images/icon_cursos.png"),
                      size=(25, 25))

# Imagem da aba de
img_aulas = CTkImage(light_image=Image.open("images/icon_aula.png"),
                     dark_image=Image.open("images/icon_aula.png"),
                     size=(25, 25))

# Imagem da aba de
img_faltas = CTkImage(light_image=Image.open("images/icon_falta.png"),
                      dark_image=Image.open("images/icon_falta.png"),
                      size=(25, 25))

# Imagem da aba de
img_cameras = CTkImage(light_image=Image.open("images/icon_camera.png"),
                       dark_image=Image.open("images/icon_camera.png"),
                       size=(25, 25))

# Imagem da aba de
img_voltar = CTkImage(light_image=Image.open("images/icon_voltar.png"),
                      dark_image=Image.open("images/icon_voltar.png"),
                      size=(25, 25))

# ---------------------------------------- Configuração de Grid da Página de cadastro --------------------------------------------------------
# Colunas
pagina_cadastro.grid_columnconfigure(0, weight=1)
pagina_cadastro.grid_columnconfigure(6, weight=1)

# Linhas
pagina_cadastro.grid_rowconfigure(1, weight=1)
pagina_cadastro.grid_rowconfigure(9, weight=1)

# Tornar frame transparente
pagina_cadastro.configure(fg_color='transparent')

# ---------------------------------------- Frames da pagina de cadastro --------------------------------------------------------

# ---------------------------------------- Frame das Abas --------------------------------------------------------

# Frame das abas (Botões)
frame_abas = CTkFrame(pagina_cadastro, fg_color=AZUL_ESCURO,
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

btn_voltar = CTkButton(frame_abas, text="Alunos", image=img_voltar, command=lambda:voltar(),
                       corner_radius=45, width=50, height=30, compound=LEFT, font=FONTE_BOTAO)
btn_voltar.pack(after=btn_camera, side=LEFT, expand=True,
                fill=X, padx=(20, 20), pady=(0, 5))

# ---------------------------------------- Frame do conteúdo --------------------------------------------------------



# ---------------------------------------- Alunos ---------------------------------------------------------------
# Função de cadastro de alunos


def alunos():
    # Titulo da página
    troca_titulo('Cadastro de Alunos', 'aluno')

'''
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
                botao_undo = Button(frame_info, command=undo_atualiza, anchor=CENTER, text='DESFAZER', width=10, height=2,
                                    overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
                botao_undo.place(x=726, y=70)

            # Botão salvar alterações do aluno
            botao_salvar = Button(frame_info, command=atualiza, anchor=CENTER, text='SALVAR\nALTERAÇÕES', width=10, height=2,
                                  overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
            botao_salvar.place(x=726, y=125)

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
            botao_desfazer = Button(frame_info, command=undo_apaga, anchor=CENTER, text='DESFAZER', width=10, height=2,
                                    overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
            botao_desfazer.place(x=726, y=70)

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
                botao_undo = Button(frame_info, command=undo_atualiza, anchor=CENTER, text='DESFAZER', width=10, height=2,
                                    overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
                botao_undo.place(x=726, y=70)

            # Botão salvar alterações do aluno
            botao_salvar = Button(frame_info, command=atualiza, anchor=CENTER, text='SALVAR\nALTERAÇÕES', width=10, height=2,
                                  overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
            botao_salvar.place(x=726, y=125)

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
    botao_undo.place(x=726, y=70)

    botao_undo.destroy()

    canvas_rect = Canvas(frame_info, width=130, height=130, background=AZUL_CLARO)
    canvas_rect.place(x=300,y=10)

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

    botao_procurar = Button(frame_info, command=pesquisa_aluno, text="PESQUISAR",
                            font=fonte_botao, compound=LEFT, overrelief=RIDGE, bg=AZUL_ESCURO, fg=BRANCO)
    botao_procurar.place(x=757, y=33)

    # ------------------------------------ Botões ---------------------------------

    # Botão adicionar aluno
    botao_adicionar = Button(frame_info, command=novo_aluno, anchor=CENTER, text='ADICIONAR', width=10, height=2,
                             overrelief=RIDGE, font=fonte_botao, bg=VERDE, foreground=BRANCO)
    botao_adicionar.place(x=617, y=70)

    # Botão alterar aluno
    botao_alterar = Button(frame_info, command=carregar_aluno, anchor=CENTER, text='ALTERAR', width=10, height=2,
                           overrelief=RIDGE, font=fonte_botao, bg=AZUL_ESCURO, foreground=BRANCO)
    botao_alterar.place(x=617, y=125)

    # Botão deletar aluno
    botao_deletar = Button(frame_info, command=apagar_aluno, anchor=CENTER, text='DELETAR', width=10, height=2,
                           overrelief=RIDGE, font=fonte_botao, bg=VERMELHO, foreground=BRANCO)
    botao_deletar.place(x=617, y=180)

    # Botão informações do aluno
    botao_mostrar = Button(frame_info, command=info_aluno, anchor=CENTER, text='INFO', width=10, height=2,
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

    mostra_alunos()'''

# ---------------------------------------- Cursos/Turmas --------------------------------------------------------
# Função de cadastro de alunos


def cursos_turmas():
    # Titulo da página
    troca_titulo('Cadastro de Cursos e Turmas', 'cursos')

# ---------------------------------------- Aulas ----------------------------------------------------------------
# Função de cadastro de alunos


def aulas():
    # Titulo da página
    troca_titulo('Cadastro de Aulas', 'aula')

# ---------------------------------------- Faltas ---------------------------------------------------------------
# Função de cadastro de alunos


def faltas():
    # Titulo da página
    troca_titulo('Faltas', 'falta')

# ---------------------------------------- Câmeras --------------------------------------------------------------
# Função de cadastro de alunos


def cameras():
    # Titulo da página
    troca_titulo('Cadastro de Câmeras', 'camera')

# ---------------------------------------- Ir e voltar da Página Inicial --------------------------------------------------------------

def direciona_cadastro():
   # Mostra aba de cadastro de aluno
   alunos()

   # Direciona para a página de cadastro
   show_frame(pagina_cadastro)

def voltar():
    # Titulo da página
    troca_titulo('  Menu Inicial', 'casa')

    # Direciona para a página inicial
    show_frame(pagina_inicial)

# ---------------------------------------- Troca de janelas --------------------------------------------------------------

# Função de troca de janelas
def controle(comando_botao):
    '''
    for widget in frame_tabela.winfo_children():
        widget.destroy()
    '''

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
janela.mainloop()
