from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
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
    postagens = db.relationship('Postagem', back_populates='usuario', lazy=True)
    comentarios = db.relationship('Comentario', back_populates='usuario', lazy=True)

class Livro(db.Model):
    __tablename__ = 'LivLivros'

    id = db.Column('LivId', db.Integer, primary_key=True)
    titulo = db.Column('LivTitulo', db.String(150), nullable=False)
    autor = db.Column('LivAutor', db.String(100), nullable=False)
    editora = db.Column('LivEditora', db.String(100))
    ano_publicacao = db.Column('LivAnoPublicacao', db.SmallInteger)
    descricao = db.Column('LivDescricao', db.Text)
    categoria_id = db.Column('LivCategoriaId', db.Integer, db.ForeignKey('CtlCategoriasLivros.CTLId'))
    ativo = db.Column('LivAtivo', db.Boolean, default=True)
    imagem_base64 = db.Column('LivImagemBase64', db.Text)

    categoria = db.relationship('CategoriaLivro', back_populates='livro')
    avaliacoes = db.relationship('Avaliacao', back_populates='livro')

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
    livro = db.relationship('Livro', back_populates='avaliacoes')

class CategoriaLivro(db.Model):
    __tablename__ = 'CtlCategoriasLivros'  # ou o nome real da tabela

    id = db.Column('CTLId', db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column('CTLNome', db.String(100), nullable=False)
    descricao = db.Column('CTLDescricao', db.Text)
    ativo = db.Column('CTLAtivo', db.Boolean, default=True)

    livro = db.relationship('Livro', back_populates='categoria', lazy=True)

class Postagem(db.Model):
    __tablename__ = 'PosPostagens'

    id = db.Column('PosId', db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column('PosTitulo', db.String(150), nullable=False)
    conteudo = db.Column('PosConteudo', db.Text, nullable=False)
    data_criacao = db.Column('PosDataCriacao', db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column('PosUsuId', db.Integer, db.ForeignKey('UsuUsuarios.UsuId'))
    ativo = db.Column('PosAtivo', db.Boolean, default=True)

    usuario = db.relationship('Usuario', back_populates='postagens')
    comentarios = db.relationship('Comentario', back_populates='postagem', lazy=True)

class Comentario(db.Model):
    __tablename__ = 'ComComentarios'

    id = db.Column('ComId', db.Integer, primary_key=True, autoincrement=True)
    conteudo = db.Column('ComConteudo', db.Text, nullable=False)
    data_criacao = db.Column('ComDataCriacao', db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column('ComUsuId', db.Integer, db.ForeignKey('UsuUsuarios.UsuId'))
    postagem_id = db.Column('ComPosId', db.Integer, db.ForeignKey('PosPostagens.PosId'))
    ativo = db.Column('ComAtivo', db.Boolean, default=True)

    usuario = db.relationship('Usuario', back_populates='comentarios')
    postagem = db.relationship('Postagem', back_populates='comentarios')

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

    livros_com_maior_media = db.session.query(
        Livro, 
        func.avg(Avaliacao.nota).label('media_avaliacao')
    ).join(Avaliacao, Avaliacao.id == Livro.id).filter(Livro.ativo == True, Avaliacao.ativo == 1).group_by(Livro.id).order_by(func.avg(Avaliacao.nota).desc()).limit(3).all()

    return render_template('forum.html', livros=livros_com_maior_media, usuario=usuario)

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

@app.route('/livro/<int:livro_id>')
def pagina_livro(livro_id):
    if 'usuario' in session:
        usuario = session['usuario'] 
    else:
        return redirect(url_for('login'))

    livro = Livro.query.get(livro_id)
    if not livro:
        return render_template('pages/livro/livro.html', livro=None)

    media = (
        sum([a.nota for a in livro.avaliacoes]) / len(livro.avaliacoes)
        if livro.avaliacoes else None
    )

    return render_template('livro.html', livro=livro, media_avaliacoes=media)

# ----- Inicialização -----
if __name__ == '__main__':
    app.run(debug=True)
