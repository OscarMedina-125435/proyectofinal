from flask import Flask, render_template, session, redirect, url_for, request

app = Flask(__name__)

# IMPORTANTE: Esta clave permite que las sesiones (logins) sean seguras.
app.secret_key = 'tu_clave_secreta_aqui_123'

# --- RUTA PRINCIPAL (INDEX) ---
@app.route('/')
def index():
    # Renderiza tu archivo base o el index que ya tengas
    return render_template('index.html')

# --- RUTA DE LOGIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Aquí iría tu lógica de base de datos para validar usuario.
        # Por ahora, simulamos un inicio de sesión exitoso:
        session['user_id'] = 1
        session['nombre'] = 'Usuario Demo'
        return redirect(url_for('index'))
    
    # Si es GET, mostramos la página de login
    return render_template('login.html')

# --- RUTA DE REGISTRO ---
@app.route('/register')
def register():
    return render_template('register.html')

# --- RUTA DE PERFIL ---
@app.route('/perfil')
def perfil():
    # Protegemos la ruta: si no hay sesión, mandamos al login
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('perfil.html')

# --- RUTA DE LOGOUT (CERRAR SESIÓN) ---
@app.route('/logout')
def logout():
    # Limpiamos la sesión completa
    session.clear()
    return redirect(url_for('index'))

# --- MANEJO DE ERRORES ---
@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404: Página no encontrada</h1>", 404

if __name__ == '__main__':
    # debug=True reinicia el servidor cada vez que guardas un cambio
    app.run(debug=True)