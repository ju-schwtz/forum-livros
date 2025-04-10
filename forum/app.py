from flask import Flask, render_template, request, redirect, url_for, flash, session
import json, os

app = Flask(__name__)
app.secret_key = "chave_super_secreta"
ARQUIVO_USUARIOS = 'usuarios.json'

# ----- Funções de arquivo -----

def carregar_usuarios():
    if not os.path.exists(ARQUIVO_USUARIOS):
        return {}
    with open(ARQUIVO_USUARIOS, 'r') as f:
        return json.load(f)

def salvar_usuarios(usuarios):
    with open(ARQUIVO_USUARIOS, 'w') as f:
        json.dump(usuarios, f, indent=4)

# ----- Rotas -----

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuarios = carregar_usuarios()
        username = request.form['username']
        senha = request.form['password']
        if username in usuarios and usuarios[username]["senha"] == senha:
            session['usuario'] = username
            flash(f"Bem-vindo, {username}!", "success")
            return redirect(url_for('forum'))
        else:
            flash("Usuário ou senha incorretos.", "error")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuarios = carregar_usuarios()
        username = request.form['username']
        senha = request.form['password']
        confirmar = request.form['confirm_password']

        if username in usuarios:
            flash("Usuário já existe.", "error")
        elif senha != confirmar:
            flash("As senhas não coincidem.", "error")
        else:
            usuarios[username] = {"senha": senha}
            salvar_usuarios(usuarios)
            flash("Usuário registrado com sucesso!", "success")
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/forum')
def forum():
    if 'usuario' not in session:
        flash("Você precisa estar logado para acessar o fórum.", "error")
        return redirect(url_for('login'))
    return render_template('forum.html', usuario=session['usuario'])

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash("Logout realizado com sucesso!", "success")
    return redirect(url_for('login'))

# ----- Iniciar app -----

if __name__ == '__main__':
    app.run(debug=True)
