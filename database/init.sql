CREATE TABLE IF NOT EXISTS Pessoa
(
  id_pessoa SERIAL NOT NULL,
  cpf CHAR(11) NOT NULL,
  nome VARCHAR(100) NOT NULL,
  data_nascimento DATE NOT NULL,
  PRIMARY KEY (id_pessoa),
  UNIQUE (cpf)
);

CREATE TABLE IF NOT EXISTS Estado
(
  uf CHAR(2) NOT NULL,
  nome_estado VARCHAR(25) NOT NULL,
  PRIMARY KEY (uf)
);

CREATE TABLE IF NOT EXISTS Municipio
(
  nome_municipio VARCHAR(50) NOT NULL,
  id_municipio SERIAL NOT NULL,
  uf CHAR(2) NOT NULL,
  PRIMARY KEY (id_municipio),
  FOREIGN KEY (uf) REFERENCES Estado(uf)
);

CREATE TABLE IF NOT EXISTS Propriedade
(
  nome_propriedade VARCHAR(100) NOT NULL,
  id_propriedade SERIAL NOT NULL,
  registro_imovel VARCHAR(20) NOT NULL,
  area_total_hectares NUMERIC(10, 2) NOT NULL,
  logradouro VARCHAR(100) NOT NULL,
  numero VARCHAR(5) NOT NULL,
  cep CHAR(8) NOT NULL,
  id_municipio INTEGER NOT NULL,
  PRIMARY KEY (id_propriedade),
  FOREIGN KEY (id_municipio) REFERENCES Municipio(id_municipio),
  UNIQUE (registro_imovel),
  CONSTRAINT chk_area_positiva CHECK (area_total_hectares > 0)
);

CREATE TABLE IF NOT EXISTS Produtor
(
  inscricao_estadual VARCHAR(13) NOT NULL,
  id_pessoa INTEGER NOT NULL,
  PRIMARY KEY (id_pessoa),
  FOREIGN KEY (id_pessoa) REFERENCES Pessoa(id_pessoa),
  UNIQUE (inscricao_estadual)
);

CREATE TABLE IF NOT EXISTS Tecnico
(
  crea VARCHAR(12) NOT NULL,
  id_pessoa INTEGER NOT NULL,
  PRIMARY KEY (id_pessoa),
  FOREIGN KEY (id_pessoa) REFERENCES Pessoa(id_pessoa),
  UNIQUE (crea)
);

CREATE TABLE IF NOT EXISTS Safra
(
  id_safra SERIAL NOT NULL,
  descricao_safra VARCHAR(100) NOT NULL,
  ano_agricola VARCHAR(9) NOT NULL,
  data_inicio DATE NOT NULL,
  data_fim DATE NOT NULL,
  PRIMARY KEY (id_safra),
  CONSTRAINT chk_datas_safra CHECK (data_fim >= data_inicio)
);

CREATE TABLE IF NOT EXISTS Cultivo
(
  id_cultivo SERIAL NOT NULL,
  nome_cultura VARCHAR(100) NOT NULL,
  descricao VARCHAR(150) NOT NULL,
  variedade VARCHAR(100) NOT NULL,
  PRIMARY KEY (id_cultivo)
);

CREATE TABLE IF NOT EXISTS Visita_tecnica
(
  id_visita SERIAL NOT NULL,
  data_visita DATE NOT NULL,
  observacoes VARCHAR(150) NOT NULL,
  anexos BYTEA,
  id_tecnico INTEGER NOT NULL,
  id_propriedade INTEGER NOT NULL,
  PRIMARY KEY (id_visita),
  FOREIGN KEY (id_tecnico) REFERENCES Tecnico(id_pessoa),
  FOREIGN KEY (id_propriedade) REFERENCES Propriedade(id_propriedade)
);

CREATE TABLE IF NOT EXISTS Alerta
(
  id_alerta SERIAL NOT NULL,
  tipo_alerta VARCHAR(50) NOT NULL,
  data_envio DATE NOT NULL,
  descricao VARCHAR(100) NOT NULL,
  PRIMARY KEY (id_alerta)
);

CREATE TABLE IF NOT EXISTS Alerta_recebido
(
  id_alerta INTEGER NOT NULL,
  id_produtor INTEGER NOT NULL,
  PRIMARY KEY (id_alerta, id_produtor),
  FOREIGN KEY (id_alerta) REFERENCES Alerta(id_alerta),
  FOREIGN KEY (id_produtor) REFERENCES Produtor(id_pessoa)
);

CREATE TABLE IF NOT EXISTS Valor_mercado
(
  data_registro DATE NOT NULL,
  valor NUMERIC(12, 2) NOT NULL,
  id_produtor INTEGER NOT NULL,
  id_cultivo INTEGER NOT NULL,
  PRIMARY KEY (data_registro, id_produtor, id_cultivo),
  FOREIGN KEY (id_produtor) REFERENCES Produtor(id_pessoa),
  FOREIGN KEY (id_cultivo) REFERENCES Cultivo(id_cultivo)
);

CREATE TABLE IF NOT EXISTS Possui_propriedade
(
  id_produtor INTEGER NOT NULL,
  id_propriedade INTEGER NOT NULL,
  PRIMARY KEY (id_produtor, id_propriedade),
  FOREIGN KEY (id_produtor) REFERENCES Produtor(id_pessoa),
  FOREIGN KEY (id_propriedade) REFERENCES Propriedade(id_propriedade)
);

CREATE TABLE IF NOT EXISTS Plantio
(
  id_plantio SERIAL NOT NULL,
  data_plantio DATE NOT NULL,
  area_plantada_hectares NUMERIC(10, 2) NOT NULL,
  id_propriedade INTEGER NOT NULL,
  id_safra INTEGER NOT NULL,
  id_cultivo INTEGER NOT NULL,
  PRIMARY KEY (id_plantio),
  FOREIGN KEY (id_propriedade) REFERENCES Propriedade(id_propriedade),
  FOREIGN KEY (id_safra) REFERENCES Safra(id_safra),
  FOREIGN KEY (id_cultivo) REFERENCES Cultivo(id_cultivo),
  CONSTRAINT chk_area_plantada_positiva CHECK (area_plantada_hectares > 0)
);

CREATE TABLE IF NOT EXISTS Ocorrencia
(
  id_ocorrencia SERIAL NOT NULL,
  tipo_problema VARCHAR(100) NOT NULL,
  descricao VARCHAR(100) NOT NULL,
  data_ocorrencia DATE NOT NULL,
  id_plantio INTEGER NOT NULL,
  PRIMARY KEY (id_ocorrencia, id_plantio),
  FOREIGN KEY (id_plantio) REFERENCES Plantio(id_plantio)
  ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Colheita
(
  id_colheita SERIAL NOT NULL,
  data_colheita DATE NOT NULL,
  quantidade_colheita INTEGER NOT NULL,
  unidade_medida VARCHAR(20) NOT NULL,
  id_plantio INTEGER NOT NULL,
  PRIMARY KEY (id_colheita, id_plantio),
  FOREIGN KEY (id_plantio) REFERENCES Plantio(id_plantio)
  ON DELETE CASCADE,
  CONSTRAINT chk_qtd_colhida_positiva CHECK (quantidade_colheita > 0)
);

CREATE TABLE IF NOT EXISTS Telefone
(
  numero VARCHAR(15) NOT NULL,
  tipo VARCHAR(15) NOT NULL,
  id_pessoa INTEGER NOT NULL,
  PRIMARY KEY (id_pessoa, numero),
  FOREIGN KEY (id_pessoa) REFERENCES Pessoa(id_pessoa)
);

-- Índices para FKs (melhora o desempenho de JOINs e WHERE clauses)
CREATE INDEX IF NOT EXISTS idx_produtor_pessoa ON Produtor(id_pessoa);
CREATE INDEX IF NOT EXISTS idx_tecnico_pessoa ON Tecnico(id_pessoa);
CREATE INDEX IF NOT EXISTS idx_municipio_uf ON Municipio(uf);
CREATE INDEX IF NOT EXISTS idx_propriedade_municipio ON Propriedade(id_municipio);
CREATE INDEX IF NOT EXISTS idx_visita_tecnico ON Visita_tecnica(id_tecnico);
CREATE INDEX IF NOT EXISTS idx_visita_propriedade ON Visita_tecnica(id_propriedade);
CREATE INDEX IF NOT EXISTS idx_alerta_recebido_produtor ON Alerta_recebido(id_produtor);
CREATE INDEX IF NOT EXISTS idx_valor_mercado_produtor ON Valor_mercado(id_produtor);
CREATE INDEX IF NOT EXISTS idx_valor_mercado_cultivo ON Valor_mercado(id_cultivo);
CREATE INDEX IF NOT EXISTS idx_possui_propriedade_produtor ON Possui_propriedade(id_produtor);
CREATE INDEX IF NOT EXISTS idx_possui_propriedade_propriedade ON Possui_propriedade(id_propriedade);
CREATE INDEX IF NOT EXISTS idx_plantio_propriedade ON Plantio(id_propriedade);
CREATE INDEX IF NOT EXISTS idx_plantio_safra ON Plantio(id_safra);
CREATE INDEX IF NOT EXISTS idx_plantio_cultivo ON Plantio(id_cultivo);
CREATE INDEX IF NOT EXISTS idx_telefone_pessoa ON Telefone(id_pessoa);

-- Inserindo TODOS os Estados (UF) do Brasil
INSERT INTO Estado (uf, nome_estado) VALUES 
('AC', 'Acre'),
('AL', 'Alagoas'),
('AP', 'Amapá'),
('AM', 'Amazonas'),
('BA', 'Bahia'),
('CE', 'Ceará'),
('DF', 'Distrito Federal'),
('ES', 'Espírito Santo'),
('GO', 'Goiás'),
('MA', 'Maranhão'),
('MT', 'Mato Grosso'),
('MS', 'Mato Grosso do Sul'),
('MG', 'Minas Gerais'),
('PA', 'Pará'),
('PB', 'Paraíba'),
('PR', 'Paraná'),
('PE', 'Pernambuco'),
('PI', 'Piauí'),
('RJ', 'Rio de Janeiro'),
('RN', 'Rio Grande do Norte'),
('RS', 'Rio Grande do Sul'),
('RO', 'Rondônia'),
('RR', 'Roraima'),
('SC', 'Santa Catarina'),
('SP', 'São Paulo'),
('SE', 'Sergipe'),
('TO', 'Tocantins');
