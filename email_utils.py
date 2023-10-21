import smtplib
import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


load_dotenv()
USERNAME = os.environ['user'] # email do raspberry para login
PASS = os.environ['pass'] # senha do email do raspberry para login
REMETENTE = os.environ['email'] # email do remetente (quem vai enviar a mensagem)

# Envia um email para o aluno contabilizando que teve falta na aula e foi contabilizado em nosso sistema
def envia_email_acusando_falta(aluno, ID, destinatario):
    assunto_email = "Atenção: Você recebeu falta!"
    mensagem_email = f"Caro(a) {aluno}, de RA: {ID}:\n\nInformamos que sua presença em sala de aula não foi contabilizada e portanto foi atribuída falta!"

    enviar_email(destinatario, assunto_email, mensagem_email)


# Envia um email de alerta para o aluno caso não seja contabilizada sua presença na aula
def envia_email_alerta(aluno, ID, destinatario):
    assunto_email = "Alerta: Sua presença não foi contabilizada até o momento!" # assunto do email a ser enviado
    mensagem_email = f"Caro(a) {aluno}, de RA: {ID}:\n\nInformamos que até o presente momento, não detectamos sua presença em sala de aula. Caso se mantenha desta forma, será atribuida falta para este dia letivo. Se você está presente em sala, contate o professor responsável." # mensagem do email a ser enviado

    enviar_email(destinatario, assunto_email, mensagem_email)


# Envia um email de confirmação para o aluno, informando que ele está presente em sala
def envia_email_confirmando_presenca(aluno, ID, destinatario):
    assunto_email = "Confirmação: Sua presença foi confirmada!"
    mensagem_email = f"Caro(a) {aluno}, de RA: {ID}:\n\nInformamos que sua presença em sala de aula foi confirmada e foi contabilizada em nosso sistema!"

    enviar_email(destinatario, assunto_email, mensagem_email)


# Método generico para envio de email via raspberry pi
def enviar_email(destinatario, assunto_email, mensagem_email):
    # inicia a montagem do email usando MIMEMultipart
    mimemsg = MIMEMultipart() 
    mimemsg['From']=REMETENTE
    mimemsg['To']=destinatario
    mimemsg['Subject']=assunto_email
    mimemsg.attach(MIMEText(mensagem_email, 'plain'))

    # Abre conexão smtp para realizar o envio do email
    connection = smtplib.SMTP(host='smtp.gmail.com', port=587)
    connection.starttls()

    # login do email do remetente
    connection.login(USERNAME, PASS)

    # envio da mensagem
    connection.send_message(mimemsg)

    # fechando conexão
    connection.quit()

