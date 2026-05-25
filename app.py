from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
import random
from passlib.context import CryptContext
from plantas import Plantas 

app = Flask(__name__)
app.secret_key = "Mi_clave_luz_oscar"


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = "ubiarcomarialuz@gmail.com"
app.config['MAIL_PASSWORD'] = 'eedoefcvijoxxwoo'
app.config['MAIL_DEFAULT_SENDER'] = "ubiarcomarialuz@gmail.com"

mail = Mail(app)
db_mongo = Plantas()
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

@app.route('/')
def index():
    usuarioo = session.get("usuarioo")
    
    if not usuarioo:
        return redirect(url_for('login'))
        
    administrador = session.get('administrador', False)
    
    mis_plantas = db_mongo.db.plantas.find()
    
    return render_template('index.html', usuarioo=usuarioo, administrador=administrador, plantas=mis_plantas)


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('usuario')
        email = request.form.get('email')
        contrasena = request.form.get('contrasena')

        contrasena_segura = pwd_context.hash(contrasena)
        resultado = db_mongo.crear_usuario(nombre,email,contrasena_segura)
        
        if resultado:
            session['usuarioo'] = nombre
            flash("¡Registro exitoso!", "success")
            return redirect(url_for('login'))
        else:
            flash("El email ya está registrado.", "danger")
            return render_template('registro.html')
            
    return render_template('registro.html')


 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        contrasena = request.form.get('contrasena')
        
        usuario = db_mongo.buscar_usuario(email)
        
        if usuario:
            if pwd_context.verify(contrasena, usuario.get('password')): 
                session['usuarioo'] = usuario.get('nombre')
                session['email_usuario'] = email 
                
                flash("¡Inicio de sesión exitoso!", "success")
                return redirect(url_for('index'))
            else:
                flash("La contraseña es incorrecta.", "danger")
        else:
            flash("El correo electrónico no está registrado.", "danger")
            
    return render_template('login.html')



@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    if request.method == 'POST':
        email = request.form.get('email')
        usuario = db_mongo.buscar_usuario(email)
        
        if usuario:
            token = str(random.randint(100000, 999999))
            msg = Message(
                subject="[Invernadero Virtual] Restablecer tu contraseña",
                recipients=[email]
            )
            msg.body = f"Hola. Tu código para generar una nueva contraseña es: {token}"
            
            try:
                mail.send(msg)
                session['reset_email'] = email
                session['reset_token'] = token
                
                flash("Te enviamos un código.", "success")
                return redirect(url_for('verificar_codigo'))
            except Exception as e:

                print("Error al enviar el correo:",e)
    

    return render_template('recuperar.html')


@app.route('/verificar_codigo', methods=['GET', 'POST'])
def verificar_codigo():
    if 'reset_token' not in session:
        flash("Primero debes solicitar un código.", "warning")
        return redirect(url_for('recuperar'))

    if request.method == 'POST':
        codigo_usuario = request.form.get('codigo_input')
        
        if codigo_usuario == session.get('reset_token'):
            flash("¡Código correcto! Ya puedes cambiar tu contraseña.", "success")
            return redirect(url_for('nueva_contrasena')) 
        else:
            flash("El código es incorrecto, revísalo bien.", "danger")
            
    return render_template('verificar_codigo.html')


@app.route('/nueva_contrasena', methods=['GET', 'POST'])
def nueva_contrasena():
    if 'reset_email' not in session:
        flash("No has validado tu código aún.", "danger")
        return redirect(url_for('recuperar'))

    if request.method == 'POST':
        clave = request.form.get('nueva_contraseña')
        email = session.get('reset_email')

        tu_clave = pwd_context.hash(clave)
        se_actualizo = db_mongo.actualizar_contrasena(email, tu_clave)

        if se_actualizo:
            session.pop('reset_email', None)
            session.pop('reset_token', None)
            flash("Contraseña cambiada. Ya puedes iniciar sesión.", "success")
            return redirect(url_for('login'))
            
        flash("intenta cambiarla otra vez.", "danger")

    return render_template('nueva_contrasena.html')


@app.route("/logout")
def logout():
    session.pop('usuarioo', None)
    session.pop("email_usuario",None)
    session.pop('administrador', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
