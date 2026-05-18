from flask import Flask, render_template, request, redirect, url_for,session
from plantas import Plantas 

app = Flask(__name__)
app.secret_key = "clave_secreta_provisional"

db_mongo = Plantas()

@app.route('/')
def index():
    user = session.get("usuarioo")
    if usuarioo:
        return f"Bienvenido,"
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        

        usuarioo= db_mongo.crear_usuario(nombre,password,email)
        
        if usuarioo:
            return redirect(url_for('login'))
        else:
            return "El email ya está registrado en la base de datos."
            
    # GET: Muestra el formulario de registro
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Buscamos el usuario en Atlas
        usuario = db_mongo.verificar_login(email, password)
        
        if usuario:
            # Si las credenciales son correctas, entramos al index
            session['usuarioo'] = usuario['_id']
            print(f"✅ Sesión iniciada para: {usuario['nombre']}")
            return redirect(url_for('index'))
        else:
            # Si no coinciden los datos en la nube
            return "Credenciales incorrectas. Intenta de nuevo."

    # GET: Muestra el formulario de inicio de sesión
    return render_template('login.html')


@app.route("/logout")

def logout():
    session.pop('usuarioo', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)