from flask import Flask, render_template, request, redirect, url_for, session, flash
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from passlib.context import CryptContext
from plantas import Plantas 

app = Flask(__name__)
app.secret_key = "clave_secreta_provisional"

db_mongo = Plantas()

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


@app.route('/')
def index():
    # 1. Verificamos si el usuario inició sesión
    usuarioo = session.get("usuarioo")
    
    if not usuarioo:
        return redirect(url_for('login'))
        
    # 2. Llamamos al método de tu archivo plantas.py a través de db_mongo
    mis_plantas = db_mongo.db.plantas.find()
    # 3. Mandamos los datos limpios a tu plantilla HTML
    return render_template('index.html', usuario=usuarioo, plantas=mis_plantas)


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        # 1. Encriptamos la contraseña aquí mismo usando passlib
        password_segura = pwd_context.hash(password)
        
        # 2. Guardamos en MongoDB pasando los datos en el orden de tu plantas.py
        resultado_registro = db_mongo.crear_usuario(nombre, email, password_segura)
        
        if resultado_registro:
            session['usuarioo'] = nombre
            flash("¡Registro exitoso!", "success")
            return redirect(url_for('login'))
        else:
            return "El email ya está registrado en la base de datos."
            
    return render_template('registro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password_plano = request.form.get('password')
        
       
        usuario = db_mongo.buscar_usuario_por_correo(email)
        
        if usuario:

            password_encriptada_db = usuario.get('password')
            
        # Busca esta línea y déjala configurada exactamente así:

            if pwd_context.verify(password_plano, password_encriptada_db):
                session['usuarioo'] = usuario.get('nombre')
                flash("¡Inicio de sesión exitoso!", "success")
                return redirect(url_for('index'))
            else:
                flash("Contraseña incorrecta.", "danger")
        else:
            flash("El correo no está registrado.", "danger")
            
    return render_template('login.html')


@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    if request.method == 'POST':
        correo = request.form.get('email')
        
       
        usuario_existe = db_mongo.buscar_usuario_por_correo(correo)
        
        if usuario_existe:
            # 2. Generamos el código de 6 dígitos aquí mismo
            codigo_guardado = str(random.randint(100000, 999999))
            
            
            GMAIL_USER = "tu_correo@gmail.com"
            GMAIL_PASSWORD = "abcd efgh ijkl mnop" 
            
            mensaje = MIMEMultipart()
            mensaje["From"] = GMAIL_USER
            mensaje["To"] = correo
            mensaje["Subject"] = "Código de Recuperación - Invernadero Virtual"
            
            cuerpo = f"Tu código de verificación para cambiar tu contraseña es: {codigo_guardado}"
            mensaje.attach(MIMEText(cuerpo, "plain"))
            
            try:
                
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(GMAIL_USER, GMAIL_PASSWORD)
                server.sendmail(GMAIL_USER, correo, mensaje.as_string())
                server.quit()
                
               
                session['correo_recuperacion'] = correo
                session['codigo_verificacion'] = codigo_guardado
                
                flash("¡Código enviado con éxito! Revisa tu correo.", "success")
                return redirect(url_for('verificar_codigo'))
                
            except Exception as e:
                print(f"Error al enviar correo: {e}")
                flash("Hubo un error al enviar el correo.", "danger")
        else:
            flash("Ese correo no está registrado.", "danger")
            
    return render_template('recuperar.html')


@app.route("/logout")
def logout():
    # Borramos la sesión de forma limpia
    session.pop('usuarioo', None)
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)

