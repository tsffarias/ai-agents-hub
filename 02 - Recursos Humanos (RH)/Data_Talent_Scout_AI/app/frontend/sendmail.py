import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(to_email, subject, html_message):
    # Ajuste as informações do seu serviço de e-mail:
    SENDER_EMAIL = "seu_email@example.com"
    SENDER_PASSWORD = "SUA_SENHA_AQUI"
    SMTP_SERVER = "smtp.example.com"  # Ex: smtp.gmail.com
    SMTP_PORT = 587                   # TLS (padrão)

    # Monta a mensagem
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email

    # Opcional: versão texto simples (fallback)
    text_part = "Versão de texto simples do email (fallback)."
    # Versão HTML (enviada por padrão)
    html_part = html_message

    # Constrói as duas partes
    msg.attach(MIMEText(text_part, 'plain'))
    msg.attach(MIMEText(html_part, 'html'))

    # Envia de fato
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Inicializa TLS
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        print(f"Email enviado com sucesso para {to_email}")
    except Exception as e:
        print(f"Falha ao enviar email: {str(e)}")
