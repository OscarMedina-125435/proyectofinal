from flask import Flask, render_template, request, redirect, url_for
from plantas import Plantas 

app = Flask(__name__)
app.secret_key = "clave_secreta_provisional"

db_mongo = Plantas()

@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        
        user_id = db_mongo.crear_usuario(nombre, email, password)
        
        if user_id:
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
            print(f"✅ Sesión iniciada para: {usuario['nombre']}")
            return redirect(url_for('index'))
        else:
            # Si no coinciden los datos en la nube
            return "Credenciales incorrectas. Intenta de nuevo."

    # GET: Muestra el formulario de inicio de sesión
    return render_template('login.html')

if __name__ == '__main__':
    # debug=True permite que la app se reinicie sola cuando hagas cambios
    app.run(debug=True)