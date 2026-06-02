from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
import random
from passlib.context import CryptContext
from plantas import Plantas 

app = Flask(__name__)
app.secret_key = "Mi_clave_luz_oscar"



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


@app.route('/')
def index():
    if not session.get("usuarioo"):
        return redirect(url_for('login'))
        
    query = request.args.get('q', '')
    mis_plantas = db_mongo.obtener_plantas(query)

    email_actual = session.get('email_usuario')
    mis_favoritos = db_mongo.obtener_favoritos_usuario(email_actual)
    
    usuario_data = db_mongo.buscar_usuario(email_actual)
    lista_ids_favoritos = usuario_data.get('favoritos', []) if usuario_data else []

    return render_template('index.html',
                            usuarioo=session.get('usuarioo'), 
                            administrador=session.get('administrador'), 
                            plantas=mis_plantas,
                            favoritos=mis_favoritos,         
                            lista_ids_favoritos=lista_ids_favoritos)


@app.route('/favorito', methods=['POST'])
def favorito():
    if not session.get("usuarioo"):
        return redirect(url_for('login'))
        
    planta_id = request.form.get('planta_id')
    email_usuario = session.get('email_usuario')
    
    if planta_id and email_usuario:
        db_mongo.alternar_favorito(email_usuario, planta_id)
        
    
    return redirect(request.referrer or url_for('index'))


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
        
        flash("icorrectas", "danger")
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

@app.route('/agregar_planta', methods=['GET', 'POST'])
def agregar_planta():
    if not session.get('administrador'):
        flash( "Denegado","danger")
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
        
        db_mongo.insertar_planta(nueva_planta)
        flash("¡Planta añadida con éxito!", "success")
        return redirect(url_for('index'))

    return render_template('agregar_planta.html')

@app.route('/eliminar_planta/<id>')
def eliminar_planta(id):
    
    if not session.get('administrador'):
        flash("Acceso denegado: Se requieren permisos de administrador.")
        return redirect(url_for('index'))

    if db_mongo.eliminar_planta(id):
        flash("La planta ha sido eliminada del sistema.")
    else:
        flash("Error: No se pudo encontrar o eliminar la planta.")
        
    return redirect(url_for('index'))

@app.route('/editar_planta/<id>', methods=['GET', 'POST'])
def editar_planta(id):
    
    variables_globales = globals()
    instancia_plantas = None
    
    for nombre_var, valor in variables_globales.items():
        if valor.__class__.__name__ == 'Plantas':
            instancia_plantas = valor
            break

    if not instancia_plantas:
        if 'plantas' in variables_globales:
            instancia_plantas = variables_globales['plantas']
        else:
            return "Error: No se encontró la conexión a la base de datos en app.py", 500

    if request.method == 'POST':
        datos_actualizados = {
            "nombre": request.form.get('nombre'),
            "descripcion": request.form.get('descripcion'),
            "imagen": request.form.get('imagen'),
            "dificultad": request.form.get('dificultad'),
            "frecuencia": request.form.get('frecuencia'),
            "riego": request.form.get('riego')
        }

        instancia_plantas.actualizar_planta(id, datos_actualizados)
        return redirect(url_for('index')) 

    planta_encontrada = instancia_plantas.obtener_planta_por_id(id)
    if not planta_encontrada:
        return "La planta que intentas editar no existe.", 404
        
    return render_template('editar_planta.html', planta=planta_encontrada)

@app.route('/comentarios')
def comentario():
    return render_template('comentarios.html')


@app.route('/sugerencia', methods=['POST'])
def sugerencias():
    nombre = request.form.get('nombre_planta')
    if nombre:
        # Usamos el método correcto de tu clase asignado a db_mongo
        db_mongo.insertar_sugerencia(nombre)
        flash("¡Sugerencia enviada!", "success")
    return redirect('/comentarios')

@app.route('/sugerencia/procesar/<id>', methods=['POST']) 
def procesar_sugerencia(id):
    accion = request.form.get('accion') 
    
    # Intentamos buscar la sugerencia usando el método de tu clase plantas.py
    sugerencia = db_mongo.buscar_sugerencia_por_id(id)
    
    if not sugerencia:
        flash("Sugerencia inválida o no encontrada.", "error")
        return redirect('/comentarios')

    if accion == 'aceptar':
        # 1. Insertamos la planta en el catálogo usando tu método insertar_planta
        nueva_planta = {
            "nombre": sugerencia["nombre_planta"],
            "descripcion": "Descripción pendiente de actualizar.",
            "imagen": "",
            "dificultad": "Media",
            "riego": "Moderado",
            "frecuencia": "Semanal"
        }
        db_mongo.insertar_planta(nueva_planta)
        
        # 2. Actualizamos el estado de la sugerencia usando tu método
        db_mongo.actualizar_estado_sugerencia(id, "aprobado")
        flash("¡Aceptada y añadida al catálogo!", "success")

    elif accion == 'rechazar':
        # 3. Actualizamos el estado a rechazado usando tu método
        db_mongo.actualizar_estado_sugerencia(id, "rechazado")
        flash("Sugerencia rechazada.", "info")
        
    return redirect('/comentarios')



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)