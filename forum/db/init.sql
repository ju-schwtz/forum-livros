CREATE TABLE UsuUsuarios (
    UsuId INT PRIMARY KEY AUTO_INCREMENT,
    UsuNome VARCHAR(100) NOT NULL,
    UsuSenha VARCHAR(255) NOT NULL,
    UsuDataCadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    UsuAtivo TINYINT DEFAULT 1
);

CREATE TABLE CTLCategoriasDeLivros (
    CTLId INT PRIMARY KEY AUTO_INCREMENT,
    CTLNome VARCHAR(100) NOT NULL,
    CTLDescricao TEXT,
    CTLAtivo TINYINT DEFAULT 1
);

CREATE TABLE LivLivros (
    LivId INT PRIMARY KEY AUTO_INCREMENT,
    LivTitulo VARCHAR(150) NOT NULL,
    LivAutor VARCHAR(100) NOT NULL,
    LivEditora VARCHAR(100),
    LivAnoPublicacao SMALLINT,
    LivDescricao TEXT,
    LivCategoriaId INT,
    LivAtivo TINYINT DEFAULT 1,
    LivImagemBase64 LONGTEXT,
    FOREIGN KEY (LivCategoriaId) REFERENCES CTLCategoriasDeLivros(CTLId)
);

CREATE TABLE PosPostagens (
    PosId INT PRIMARY KEY AUTO_INCREMENT,
    PosTitulo VARCHAR(150) NOT NULL,
    PosConteudo TEXT NOT NULL,
    PosDataCriacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    PosNota DECIMAL(2,1) NOT NULL,
    PosUsuId INT,
    PosLivId INT,
    PosAtivo TINYINT DEFAULT 1,
    FOREIGN KEY (PosUsuId) REFERENCES UsuUsuarios(UsuId), 
    FOREIGN KEY (PosLivId) REFERENCES LivLivros(LivId)
);

CREATE TABLE ComComentarios (
    ComId INT PRIMARY KEY AUTO_INCREMENT,
    ComConteudo TEXT NOT NULL,
    ComDataCriacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    ComUsuId INT,
    ComPosId INT,
    ComAtivo TINYINT DEFAULT 1,
    FOREIGN KEY (ComUsuId) REFERENCES UsuUsuarios(UsuId),
    FOREIGN KEY (ComPosId) REFERENCES PosPostagens(PosId)
);