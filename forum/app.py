from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "chave_super_secreta"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/ForumLiterario'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----- Modelo -----
class Usuario(db.Model):
    __tablename__ = 'UsuUsuarios'

    id = db.Column('UsuId', db.Integer, primary_key=True)
    nome = db.Column('UsuNome', db.String(100), nullable=False)
    senha = db.Column('UsuSenha', db.String(255), nullable=False)
    data_cadastro = db.Column('UsuDataCadastro', db.DateTime, default=func.now())
    ativo = db.Column('UsuAtivo', db.Boolean, default=True)

    avaliacoes = db.relationship('Avaliacao', back_populates='usuario', lazy=True)

class Livro(db.Model):
    __tablename__ = 'LivLivros'

    id = db.Column('LivId', db.Integer, primary_key=True)
    titulo = db.Column('LivTitulo', db.String(150), nullable=False)
    autor = db.Column('LivAutor', db.String(100), nullable=False)
    editora = db.Column('LivEditora', db.String(100))
    ano_publicacao = db.Column('LivAnoPublicacao', db.SmallInteger)
    descricao = db.Column('LivDescricao', db.Text)
    categoria_id = db.Column('LivCategoriaId', db.Integer)
    ativo = db.Column('LivAtivo', db.Boolean, default=True)
    imagem_base64 = db.Column('LivImagemBase64', db.Text)

class Avaliacao(db.Model):
    __tablename__ = 'AvaAvaliacoes'

    id = db.Column('AvaId', db.Integer, primary_key=True)
    nota = db.Column('AvaNota', db.Numeric(3, 1))
    comentario = db.Column('AvaComentario', db.Text)
    data_criacao = db.Column('AvaDataCriacao', db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column('AvaUsuId', db.Integer, db.ForeignKey('UsuUsuarios.UsuId'))
    livro_id = db.Column('AvaLivId', db.Integer, db.ForeignKey('LivLivros.LivId'))
    ativo = db.Column('AvaAtivo', db.Boolean, default=True)

    usuario = db.relationship('Usuario', back_populates='avaliacoes')
    livro = db.relationship('Livro', backref='avaliacoes')

# ----- Rotas -----
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        senha = request.form['password']
        
        usuario = Usuario.query.filter_by(nome=username, senha=senha).first()
        
        if usuario:
            session['usuario'] = usuario.nome
            flash(f"Bem-vindo, {usuario.nome}!", "success")
            return redirect(url_for('forum'))
        else:
            flash("Usuário ou senha incorretos.", "error")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        senha = request.form['password']
        confirmar = request.form['confirm_password']

        if senha != confirmar:
            flash("As senhas não coincidem.", "error")
            return render_template('register.html')

        usuario_existente = Usuario.query.filter_by(nome=username).first()

        if usuario_existente:
            flash("Usuário já existe.", "error")
        else:
            novo_usuario = Usuario(nome=username, senha=senha)
            db.session.add(novo_usuario)
            db.session.commit()
            flash("Usuário registrado com sucesso!", "success")
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/forum')
def forum():
    if 'usuario' in session:
        usuario = Usuario.query.filter_by(nome=session['usuario']).first()
    else:
        usuario = None

    livro_com_maior_media = db.session.query(
        Livro, 
        func.avg(Avaliacao.nota).label('media_avaliacao')
    ).join(Avaliacao, Avaliacao.id == Livro.id).filter(Livro.ativo == True, Avaliacao.ativo == 1).group_by(Livro.id).order_by(func.avg(Avaliacao.nota).desc()).first() 

    if livro_com_maior_media:
        livro = livro_com_maior_media[0]
    else:
        livro = None

    return render_template('forum.html', livro=livro, usuario=usuario)

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash("Logout realizado com sucesso!", "success")
    return redirect(url_for('login'))

@app.route('/livros')
def listar_livros():
    livros = Livro.query.filter_by(LivAtivo=1).all()
    livros_formatados = []

    for livro in livros:
        livros_formatados.append({
            'titulo': livro.LivTitulo,
            'autor': livro.LivAutor,
            'editora': livro.LivEditora,
            'ano': livro.LivAnoPublicacao,
            'descricao': livro.LivDescricao,
            'imagem_base64': livro.LivImagemBase64
        })

    return render_template('livros.html', livros=livros_formatados)



# ----- Inicialização -----
if __name__ == '__main__':
    app.run(debug=True)
