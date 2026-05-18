from flask import Flask, render_template, request, redirect, url_for, session
from plantas import Plantas 

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
        password = request.form.get('password')
        email = request.form.get('email')
        
        # Guardamos el usuario directamente en MongoDB Atlas
        usuarioo = db_mongo.crear_usuario(nombre, email, password)
        
        if usuarioo:
            # Redirigimos al login para que inicie sesión formalmente
            return redirect(url_for('login'))
        else:
            return "El email ya está registrado en la base de datos."
            
    return render_template('registro.html')


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