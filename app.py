from flask import Flask, render_template, request, redirect, url_for, session,flash
from plantas import Plantas 
from seguridad import enviar_codigo_recuperacion, encriptar_password, verificar_password


app = Flask(__name__)
app.secret_key = "clave_secreta_provisional"

db_mongo = Plantas()

@app.route('/')
def index():
    usuarioo = session.get("usuarioo")
    if not usuarioo:
        return redirect(url_for('login'))
    return render_template('index.html', usuario=usuarioo)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
    


        password_segura = encriptar_password(password)
        resultado_registro = db_mongo.crear_usuario(nombre, email, password_segura)
        
        if resultado_registro:
           
            session['usuarioo'] = nombre
            return redirect(url_for('login'))
        else:
            return "El email ya está registrado en la base de datos."



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Buscamos y verificamos las credenciales en Atlas
        usuario = db_mongo.verificar_login(email, password)
        
        if usuario:
            # Guardamos el identificador del usuario en la sesión de Flask
            session['usuarioo'] = usuario['_id']
            print(f"✅ Sesión iniciada para: {usuario['nombre']}")
            return redirect(url_for('index'))
            
    return render_template('login.html')



@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    if request.method == 'POST':
        correo = request.form.get('email')
       
        usuario_existe = db_mongo.buscar_usuario_por_correo(correo) 
        
        if usuario_existe:
            
            codigo = enviar_codigo_recuperacion(correo)
            
            if codigo:
                session['correo_recuperacion'] = correo
                session['codigo_verificacion'] = codigo
                
                flash("¡Código enviado! Revisa tu bandeja de entrada.", "success")
                # Lo mandamos a la página donde meterá el código
                return redirect(url_for('verificar_codigo')) 
            else:
                flash("Hubo un problema al enviar el correo. Inténtalo de nuevo.", "danger")
        else:
            flash("Ese correo no está registrado en el sistema.", "danger")
            
   
    return render_template('recuperar.html')



@app.route("/logout")
def logout():
    # Borramos la sesión de forma limpia
    session.pop('usuarioo', None)
    return redirect(url_for('login'))

@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # Aquí irá tu lógica para buscar el correo en Atlas y enviar el token/correo
        return f"Enlace enviado a {email}"
    return render_template('recuperar.html')

if __name__ == '__main__':
    app.run(debug=True)