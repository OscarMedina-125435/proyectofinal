import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from passlib.context import CryptContext

# Configuración de Passlib para encriptar contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def encriptar_password(password):
    """Convierte la contraseña en un hash seguro para Mongo"""
    return pwd_context.hash(password)

def verificar_password(password_plana, password_encriptada):
    """Compara la contraseña del login con la de la base de datos"""
    return pwd_context.verify(password_plana, password_encriptada)

def enviar_codigo_recuperacion(correo_destino):
    """Genera un código de 6 dígitos y lo envía por Gmail"""
    codigo = str(random.randint(100000, 999999))
    
    # RECUERDA: Configura tus datos de Gmail aquí
    GMAIL_USER = "tu_correo@gmail.com"
    GMAIL_PASSWORD = "abcd efgh ijkl mnop" # Tus 16 letras de Google
    
    mensaje = MIMEMultipart()
    mensaje["From"] = GMAIL_USER
    mensaje["To"] = correo_destino
    mensaje["Subject"] = "Código de Recuperación - Invernadero Virtual"
    
    cuerpo = f"""
    Hola,
    
    Has solicitado restablecer tu contraseña para el Invernadero Virtual.
    Tu código de verificación es: {codigo}
    
    Si no solicitaste esto, puedes ignorar este correo.
    """
    mensaje.attach(MIMEText(cuerpo, "plain"))
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, correo_destino, mensaje.as_string())
        server.quit()
        return codigo  # Regresamos el código para guardarlo en la sesión
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return None