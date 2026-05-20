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

# Inicializamos Mail pasándole la app
mail = Mail(app)
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
        # Guardamos el correo que viene del formulario de recuperar.html
        correo_usuario = request.form.get('email')
        
        # Revisamos en Mongo si este correo ya está registrado
        cuenta_encontrada = db_mongo.buscar_usuario_por_correo(correo_usuario)
        
        if cuenta_encontrada:
            token_seguridad = str(random.randint(100000, 999999))
            
            # Preparamos el correo usando Flask-Mail
            correo_recuperacion = Message(
                subject="[Invernadero Virtual] Restablecer tu contraseña",
                recipients=[correo_usuario]
            )
            correo_recuperacion.body = f"Hola. Tu código para generar una nueva contraseña es: {token_seguridad}"
            
            try:
                # Despachamos el correo electrónico
                mail.send(correo_recuperacion)
                
                session['mail_verificar'] = correo_usuario
                session['token_valido'] = token_seguridad
                
                flash("Revisa tu bandeja de entrada, te enviamos un código.", "success")
                return redirect(url_for('verificar_codigo'))
                
            except Exception as error:
                print(f"Fallo en el envío: {error}")
                flash("No se pudo enviar el correo, intenta más tarde.", "danger")
        else:
            flash("Este correo no pertenece a ningún usuario.", "danger")
            
    return render_template('recuperar.html')


@app.route('/verificar_codigo', methods=['GET', 'POST'])
def verificar_codigo():
    # Si por alguna razón no hay un token en la sesión, los mandamos al inicio
    if 'token_valido' not in session:
        flash("Primero debes solicitar un código.", "warning")
        return redirect(url_for('recuperar'))

    if request.method == 'POST':
        # Cachamos el código que el usuario escribió en el cuadrito del HTML
        codigo_usuario = request.form.get('codigo_input')
        
        # Sacamos el token real que guardamos en la sesión para comparar
        token_real = session.get('token_valido')
        
        # Comparamos si lo que escribió es igual al número que le mandamos
        if codigo_usuario == token_real:
            flash("¡Código correcto! Ya puedes cambiar tu contraseña.", "success")
            # Aquí lo mandarías a la pantalla final para escribir su nueva contraseña
            return redirect(url_for('nueva_contrasena')) 
        else:
            flash("El código es incorrecto, revísalo bien.", "danger")
            
    return render_template('verificar_codigo.html')

@app.route('/nueva_contrasena', methods=['GET', 'POST'])
def nueva_contrasena():
    # Si intentan entrar directo sin pasar por el correo, los mandamos fuera
    if 'mail_verificar' not in session:
        flash("No has validado tu código aún.", "danger")
        return redirect(url_for('recuperar'))

    if request.method == 'POST':
        # Agarramos la contraseña que viene del formulario HTML
        nueva_clave = request.form.get('nueva_contraseña')
        correo_user = session.get('mail_verificar')

        # La encriptamos con passlib antes de mandarla a Mongo
        clave_cifrada = pwd_context.hash(nueva_clave)

        # Usamos tu método de plantas.py tal cual lo tienes
        se_actualizo = db_mongo.actualizar_password(correo_user, clave_cifrada)

        if se_actualizo:
            # Limpiamos los datos de la sesión para cerrar el proceso
            session.pop('mail_verificar', None)
            session.pop('token_valido', None)

            flash("Contraseña cambiada. Ya puedes iniciar sesión.", "success")
            return redirect(url_for('login'))
        else:
            flash("Hubo un problema, intenta cambiarla otra vez.", "danger")

    return render_template('nueva_contrasena.html')

@app.route("/logout")
def logout():
    # Borramos la sesión de forma limpia
    session.pop('usuarioo', None)
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)

