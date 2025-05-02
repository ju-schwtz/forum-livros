from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from dotenv import load_dotenv
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "chave_super_secreta"

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{3306}/{os.getenv('MYSQL_DB')}?charset=utf8mb4"
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

    postagens = db.relationship('Postagem', back_populates='usuario')
    comentarios = db.relationship('Comentario', back_populates='usuario')

class CategoriaLivro(db.Model):
    __tablename__ = 'CTLCategoriasDeLivros'

    id = db.Column('CTLId', db.Integer, primary_key=True)
    nome = db.Column('CTLNome', db.String(100), nullable=False)
    descricao = db.Column('CTLDescricao', db.Text)
    ativo = db.Column('CTLAtivo', db.Boolean, default=True)

    livros = db.relationship('Livro', back_populates='categoria')

class Livro(db.Model):
    __tablename__ = 'LivLivros'

    id = db.Column('LivId', db.Integer, primary_key=True)
    titulo = db.Column('LivTitulo', db.String(150), nullable=False)
    autor = db.Column('LivAutor', db.String(100), nullable=False)
    editora = db.Column('LivEditora', db.String(100))
    ano_publicacao = db.Column('LivAnoPublicacao', db.SmallInteger)
    descricao = db.Column('LivDescricao', db.Text)
    categoria_id = db.Column('LivCategoriaId', db.Integer, db.ForeignKey('CTLCategoriasDeLivros.CTLId'))
    ativo = db.Column('LivAtivo', db.Boolean, default=True)
    imagem_base64 = db.Column('LivImagemBase64', db.Text)

    categoria = db.relationship('CategoriaLivro', back_populates='livros')
    postagens = db.relationship('Postagem', back_populates='livro')

class Postagem(db.Model):
    __tablename__ = 'PosPostagens'

    id = db.Column('PosId', db.Integer, primary_key=True)
    titulo = db.Column('PosTitulo', db.String(150), nullable=False)
    conteudo = db.Column('PosConteudo', db.Text, nullable=False)
    data_criacao = db.Column('PosDataCriacao', db.DateTime, default=func.now())
    nota = db.Column('PosNota', db.Numeric(2, 1))
    usuario_id = db.Column('PosUsuId', db.Integer, db.ForeignKey('UsuUsuarios.UsuId'))
    livro_id = db.Column('PosLivId', db.Integer, db.ForeignKey('LivLivros.LivId'))
    ativo = db.Column('PosAtivo', db.Boolean, default=True)

    usuario = db.relationship('Usuario', back_populates='postagens')
    livro = db.relationship('Livro', back_populates='postagens')
    comentarios = db.relationship('Comentario', back_populates='postagem')


class Comentario(db.Model):
    __tablename__ = 'ComComentarios'

    id = db.Column('ComId', db.Integer, primary_key=True)
    conteudo = db.Column('ComConteudo', db.Text, nullable=False)
    data_criacao = db.Column('ComDataCriacao', db.DateTime, default=func.now())
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

    livros_com_maior_media = (
        db.session.query(Livro, func.avg(Postagem.nota).label('media_postagens'))
            .join(Livro.postagens)
            .filter(Livro.ativo == True, Postagem.ativo == True, Postagem.nota != None)
            .group_by(Livro.id)
            .order_by(func.avg(Postagem.nota).desc())
            .limit(3)
            .all()
    )

    return render_template('forum.html', livros=livros_com_maior_media, usuario=usuario)

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash("Logout realizado com sucesso!", "success")
    return redirect(url_for('login'))

@app.route('/livro/<int:livro_id>')
def pagina_livro(livro_id):
    if 'usuario' in session:
        usuario = Usuario.query.filter_by(nome=session['usuario']).first()
    else:
        return redirect(url_for('login'))

    livro = Livro.query.get(livro_id)
    
    if not livro:
        return render_template('forum.html')

    postagens = Postagem.query.filter_by(livro_id=livro.id, ativo=True).order_by(Postagem.data_criacao.desc()).all()

    notas = [p.nota for p in postagens if p.nota is not None]

    if not notas:
        media = 0.0
    else:
        media = round((sum(notas) / len(notas) if notas else None), 2)

    return render_template('livro.html', livro=livro, media_avaliacoes=media, postagens=postagens, usuario=usuario)

@app.route('/livro/<int:livro_id>/postar', methods=['POST'])
def cadastrar_postagem(livro_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))  # ou outra lógica para usuários não logados

    usuario = Usuario.query.filter_by(nome=session['usuario']).first()

    titulo = request.form.get('titulo')
    conteudo = request.form.get('conteudo')
    nota = request.form.get('nota')

    postagem = Postagem(
        titulo=titulo,
        conteudo=conteudo,
        nota=nota,
        usuario_id=usuario.id,
        livro_id=livro_id
    )

    db.session.add(postagem)
    db.session.commit()

    return redirect(url_for('pagina_livro', livro_id=livro_id))

@app.route('/postagem/<int:id>/excluir', methods=['POST'])
def excluir_postagem(id):
    postagem = Postagem.query.get_or_404(id)

    if 'usuario' in session:
        usuario = Usuario.query.filter_by(nome=session['usuario']).first()
    else:
        return redirect(url_for('login'))

    livro_id = postagem.livro_id

    db.session.delete(postagem)
    db.session.commit()

    return redirect(url_for('pagina_livro', livro_id=livro_id))

@app.route('/livros')
def listar_livros():
    if 'usuario' in session:
        usuario = Usuario.query.filter_by(nome=session['usuario']).first()
    else:
        return redirect(url_for('login'))

    titulo = request.args.get('titulo', type=str)
    categoria_id = request.args.get('categoria_id', type=int)
    data_publicacao = request.args.get('data_publicacao', type=str)

    query = (
        db.session.query(Livro, func.coalesce(func.avg(Postagem.nota), 0).label('media_nota'))
        .outerjoin(Livro.postagens)
        .filter(Livro.ativo == True)
    )

    if titulo:
        query = query.filter(Livro.titulo.ilike(f'%{titulo}%'))
    if categoria_id:
        query = query.filter(Livro.categoria_id == categoria_id)
    if data_publicacao:
        query = query.filter(Livro.data_publicacao == data_publicacao)

    livros = query.group_by(Livro.id).all()
    categorias = CategoriaLivro.query.all()

    return render_template('livros.html', livros=livros, categorias=categorias)

# ----- Inicialização -----
if __name__ == '__main__':
    app.run(debug=True)
