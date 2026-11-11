# Sistema de Gestão da Festa do IFC Campus Blumenau

Este projeto é uma aplicação web desenvolvida com Streamlit para organizar a festa estudantil do IFC Campus Blumenau. O sistema centraliza as informações sobre os alimentos a serem vendidos, os fornecedores dos insumos, as pessoas que participarão da organização e o preço de venda de cada item.

## Funcionalidades

- Cadastro e gestão de alimentos
- Cadastro e gestão de fornecedores
- Cadastro e gestão de pessoas envolvidas na festa
- Cadastro e gestão da festa/evento
- Visualização resumida dos dados para tomada de decisão
- Suporte a banco SQLite para testes locais e MySQL para produção

## Tecnologias utilizadas

- Python
- Streamlit
- SQLAlchemy
- SQLite
- MySQL
- uv

## Estrutura do projeto

```text
.
├── README.md
├── .gitignore
├── .env.example
├── pyproject.toml
├── src/
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   └── models.py
└── data/
```

## Requisitos

- Python 3.11+
- uv instalado

## Como executar

1. Abra o terminal na raiz do projeto.
2. Instale as dependências:

```bash
uv sync
```

3. Configure as variáveis de ambiente. Para ambiente local, pode usar o banco SQLite automaticamente. Para produção, crie um arquivo `.env` com a URL do MySQL:

```bash
cp .env.example .env
```

Depois edite o arquivo `.env` com sua conexão MySQL:

```env
APP_ENV=production
MYSQL_URL=mysql+pymysql://usuario:senha@host:3306/festa_ifc
```

4. Inicie a aplicação:

```bash
uv run streamlit run src/app.py
```

A aplicação ficará disponível no navegador em `http://localhost:8501`.

## Banco de dados

- SQLite: usado para testes locais e desenvolvimento
- MySQL: usado em produção
- A variável de ambiente `MYSQL_URL` controla a conexão do ambiente de produção

## Observações

- Os insumos podem ser doados ou adquiridos, e essa informação fica registrada no sistema.
- O sistema foi pensado para apoiar a organização de uma festa estudantil com pessoas envolvidas em diferentes papéis, como alunos, pais e servidores.
- O deploy do Streamlit pode ser feito no ambiente recomendado, como o Streamlit Community Cloud.
