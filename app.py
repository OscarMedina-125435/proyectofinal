from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
import random
from passlib.context import CryptContext
from plantas import Plantas 

app = Flask(__name__)
app.secret_key = "Mi_clave_luz_oscar"

# Configuración de Mail
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME="ubiarcomarialuz@gmail.com",
    MAIL_PASSWORD='eedoefcvijoxxwoo',
    MAIL_DEFAULT_SENDER="ubiarcomarialuz@gmail.com"
)

mail = Mail(app)
db_mongo = Plantas()
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


### Rutas Principales

@app.route('/')
def index():
    if not session.get("usuarioo"):
        return redirect(url_for('login'))
        
    query = request.args.get('q', '')
    if query:
        mis_plantas = db_mongo.db.plantas.find({"nombre": {"$regex": query, "$options": "i"}})
    else:
        mis_plantas = db_mongo.db.plantas.find()

    return render_template('index.html',
                            usuarioo=session.get('usuarioo'), 
                            administrador=session.get('administrador'), 
                            plantas=mis_plantas)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        contrasena = request.form.get('contrasena')
        usuario = db_mongo.buscar_usuario(email)
        
        if usuario and pwd_context.verify(contrasena, usuario.get('password')):
            session['usuarioo'] = usuario.get('nombre')
            session['email_usuario'] = email 
            session['administrador'] = (usuario.get('rol') == 'administrador')
            
            flash("¡Bienvenido de nuevo!", "success")
            return redirect(url_for('index'))
        
        flash("Credenciales incorrectas", "danger")
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('usuario')
        email = request.form.get('email')
        contrasena = request.form.get('contrasena')
        
        if db_mongo.crear_usuario(nombre, email, pwd_context.hash(contrasena)):
            flash("Registro exitoso. Inicia sesión.", "success")
            return redirect(url_for('login'))
        flash("El email ya existe.", "danger")
    return render_template('registro.html')


### Rutas de Recuperación (Añadidas para solucionar el BuildError)

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
                flash("Te enviamos un código a tu correo.", "success")
                return redirect(url_for('verificar_codigo'))
            except Exception as e:
                print("Error al enviar el correo:", e)
                flash("Error al enviar el correo. Intenta más tarde.", "danger")
        else:
            flash("Ese correo no está registrado.", "danger")

    return render_template('recuperar.html')

@app.route('/verificar_codigo', methods=['GET', 'POST'])
def verificar_codigo():
    if 'reset_token' not in session:
        return redirect(url_for('recuperar'))

    if request.method == 'POST':
        codigo_usuario = request.form.get('codigo_input')
        if codigo_usuario == session.get('reset_token'):
            flash("¡Código correcto!", "success")
            return redirect(url_for('nueva_contrasena')) 
        else:
            flash("El código es incorrecto.", "danger")
            
    return render_template('verificar_codigo.html')

@app.route('/nueva_contrasena', methods=['GET', 'POST'])
def nueva_contrasena():
    if 'reset_email' not in session:
        return redirect(url_for('recuperar'))

    if request.method == 'POST':
        clave = request.form.get('nueva_contraseña')
        email = session.get('reset_email')
        tu_clave = pwd_context.hash(clave)
        
        if db_mongo.actualizar_contrasena(email, tu_clave):
            session.pop('reset_email', None)
            session.pop('reset_token', None)
            flash("Contraseña cambiada exitosamente.", "success")
            return redirect(url_for('login'))
            
    return render_template('nueva_contrasena.html')


### Gestión de Catálogo y Sesión

@app.route('/agregar_planta', methods=['GET', 'POST'])
def agregar_planta():
    if not session.get('administrador'):
        flash("Acceso denegado", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        nueva_planta = {
            "nombre": request.form.get('nombre'),
            "descripcion": request.form.get('descripcion'),
            "imagen": request.form.get('imagen'),
            "dificultad": request.form.get('dificultad'),
            "riego": request.form.get('riego'),
            "frecuencia": request.form.get('frecuencia')
        }
        db_mongo.db.plantas.insert_one(nueva_planta)
        flash("¡Planta añadida con éxito!", "success")
        return redirect(url_for('index'))

    return render_template('agregar_planta.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)