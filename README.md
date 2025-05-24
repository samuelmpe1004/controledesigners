# Controle Mensal de Fichas de Liberação para Designers

Este projeto é um sistema web para controle mensal de fichas de liberação para designers. Ele permite que cada designer faça login, registre suas fichas de produção (nome do cliente, tipo de tecido, metragem, data) e gere relatórios de produção por período, com um alerta sobre a natureza projetiva dos dados.

## Tecnologias Utilizadas

*   **Backend:** Python com Flask
*   **Frontend:** HTML, CSS, JavaScript (com templates Jinja2)
*   **Banco de Dados:** PostgreSQL
*   **Autenticação:** Flask-Login
*   **Formulários:** Flask-WTF
*   **ORM:** Flask-SQLAlchemy

## Configuração do Ambiente Local

Siga os passos abaixo para configurar e rodar o projeto localmente.

### 1. Pré-requisitos

*   Python 3.8 ou superior instalado.
*   `pip` (gerenciador de pacotes Python).
*   Um servidor PostgreSQL instalado e rodando (ou acesso a um serviço de PostgreSQL na nuvem para desenvolvimento).

### 2. Clonar o Repositório (Exemplo)

```bash
# git clone <URL_DO_REPOSITORIO_NO_GITHUB>
# cd nome_do_diretorio_do_projeto
```

No nosso caso, o projeto está em `/home/ubuntu/controle_fichas_designers`.

### 3. Criar e Ativar o Ambiente Virtual

É altamente recomendável usar um ambiente virtual para isolar as dependências do projeto.

```bash
cd /home/ubuntu/controle_fichas_designers
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar as Dependências

Com o ambiente virtual ativado, instale as dependências listadas no arquivo `requirements.txt`.

```bash
pip3 install -r requirements.txt
```

### 5. Configurar o Banco de Dados PostgreSQL

1.  **Crie um Banco de Dados:**
    *   Crie um novo banco de dados no seu servidor PostgreSQL. Por exemplo, nomeie-o `controle_fichas`.
    *   Crie um usuário e senha para acessar este banco de dados, ou use um usuário existente com as permissões necessárias.

2.  **Configurar Variáveis de Ambiente:**
    O arquivo `src/main.py` espera variáveis de ambiente para a configuração do banco de dados e a chave secreta do Flask. Você pode defini-las diretamente no seu terminal antes de rodar a aplicação, ou usar um arquivo `.env` com uma biblioteca como `python-dotenv` (não incluída por padrão neste projeto, mas pode ser adicionada).

    Variáveis necessárias:
    *   `FLASK_SECRET_KEY`: Uma chave secreta forte para a segurança da sessão do Flask. Exemplo: `sua_chave_secreta_super_segura`
    *   `DATABASE_URL`: A URL de conexão com o seu banco de dados PostgreSQL. O formato é `postgresql://usuario:senha@host:porta/nome_do_banco`.
        *   Exemplo para um banco local: `postgresql://postgres:admin@localhost:5432/controle_fichas`

    Para definir no terminal (Linux/macOS):
    ```bash
    export FLASK_SECRET_KEY="sua_chave_secreta_super_segura"
    export DATABASE_URL="postgresql://postgres:admin@localhost:5432/controle_fichas"
    ```

### 6. Criar as Tabelas no Banco de Dados

Ao rodar a aplicação pela primeira vez (ou se as tabelas ainda não existirem), o `main.py` tentará criar as tabelas automaticamente (`db.create_all()`). Certifique-se de que o banco de dados e o usuário configurados na `DATABASE_URL` existem e têm permissão para criar tabelas.

Alternativamente, você pode entrar no shell do Flask e criar as tabelas manualmente:
```bash
cd /home/ubuntu/controle_fichas_designers
source venv/bin/activate
# Defina as variáveis de ambiente FLASK_SECRET_KEY e DATABASE_URL aqui se ainda não o fez
python3
>>> from src.main import app, db
>>> with app.app_context():
...     db.create_all()
... 
>>> exit()
```

### 7. Rodar a Aplicação Localmente

Com o ambiente virtual ativado e as variáveis de ambiente configuradas:

```bash
cd /home/ubuntu/controle_fichas_designers
python3 src/main.py
```

A aplicação estará disponível em `http://0.0.0.0:5000/` ou `http://localhost:5000/`.

## Estrutura do Projeto

```
controle_fichas_designers/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py       # Modelo de Usuário
│   │   └── ficha.py      # Modelo da Ficha de Liberação
│   ├── routes/
│   │   ├── auth.py       # Rotas de autenticação (login, registro)
│   │   └── main.py       # Rotas principais (index, fichas, relatório)
│   ├── static/           # Arquivos estáticos (CSS, JS, imagens, templates HTML)
│   │   ├── style.css
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── index.html
│   │   ├── adicionar_ficha.html
│   │   ├── relatorio.html
│   │   ├── 404.html      # Template para erro 404
│   │   └── 500.html      # Template para erro 500
│   ├── forms.py          # Formulários WTForms
│   └── main.py           # Ponto de entrada da aplicação Flask
├── venv/                 # Ambiente virtual Python
└── requirements.txt      # Dependências do projeto
└── README.md             # Este arquivo
```

## Deploy

### 1. GitHub

1.  Crie um novo repositório no GitHub.
2.  Inicialize um repositório Git no diretório do seu projeto local, se ainda não o fez:
    ```bash
    cd /home/ubuntu/controle_fichas_designers
    git init
    git add .
    git commit -m "Commit inicial do projeto Controle de Fichas"
    ```
3.  Adicione o repositório remoto do GitHub e envie o código:
    ```bash
    git remote add origin <URL_DO_SEU_REPOSITORIO_NO_GITHUB.git>
    git branch -M main
    git push -u origin main
    ```
    Certifique-se de adicionar um arquivo `.gitignore` para ignorar arquivos desnecessários (como `venv/`, `__pycache__/`, arquivos `.env` locais, etc.) antes do primeiro commit.

    Exemplo de `.gitignore`:
    ```
    venv/
    __pycache__/
    *.pyc
    .env
    instance/
    ```

### 2. Render

O Render é uma plataforma que oferece hospedagem gratuita para aplicações web e bancos de dados PostgreSQL.

1.  **Crie uma Conta no Render:** Se ainda não tiver, crie uma conta em [render.com](https://render.com).

2.  **Crie um Banco de Dados PostgreSQL no Render:**
    *   No dashboard do Render, clique em "New" -> "PostgreSQL".
    *   Escolha um nome para o seu banco de dados, selecione a região e o plano (o plano gratuito é suficiente para este projeto).
    *   Após a criação, o Render fornecerá os detalhes de conexão, incluindo uma "Internal Connection String" ou "External Connection String". Você usará essa string como `DATABASE_URL`.

3.  **Crie um Web Service para a Aplicação Flask:**
    *   No dashboard do Render, clique em "New" -> "Web Service".
    *   Conecte sua conta do GitHub e selecione o repositório do projeto.
    *   Configure o serviço:
        *   **Name:** Escolha um nome para sua aplicação (ex: `controle-fichas`).
        *   **Region:** Escolha a região mais próxima de seus usuários.
        *   **Branch:** `main` (ou a branch que você usa para produção).
        *   **Root Directory:** Deixe em branco se `requirements.txt` e `src/main.py` estão na raiz do repositório (ou ajuste se sua estrutura for diferente e o Render não detectar automaticamente).
        *   **Runtime:** Python 3
        *   **Build Command:** `pip install -r requirements.txt` (o Render geralmente detecta isso automaticamente).
        *   **Start Command:** `gunicorn src.main:app` (Gunicorn é um servidor WSGI recomendado para produção. Adicione `gunicorn` ao seu `requirements.txt`).
            *   Para usar Gunicorn, primeiro instale-o no seu ambiente virtual e atualize `requirements.txt`:
                ```bash
                pip3 install gunicorn
                pip3 freeze > requirements.txt
                ```
                Depois, faça commit e push dessas alterações para o GitHub.
        *   **Environment Variables:**
            *   `FLASK_SECRET_KEY`: Defina uma chave secreta forte.
            *   `DATABASE_URL`: Use a "Internal Connection String" do seu banco de dados PostgreSQL criado no Render. É importante usar a URL interna para comunicação entre serviços dentro do Render para evitar latência e custos.
            *   `PYTHON_VERSION`: Especifique a versão do Python que você usou no desenvolvimento (ex: `3.11.0`).

4.  **Deploy:**
    *   Clique em "Create Web Service". O Render irá clonar seu repositório, instalar as dependências, e iniciar sua aplicação.
    *   O Render fornecerá uma URL pública para sua aplicação (ex: `https://nome-da-sua-app.onrender.com`).

5.  **Migrações/Criação de Tabelas no Deploy:**
    O `db.create_all()` no `main.py` tentará criar as tabelas quando a aplicação iniciar. Se você precisar de um controle mais robusto sobre migrações de banco de dados em produção, considere usar Flask-Migrate com Alembic.

### Alternativas Gratuitas para Hospedagem (se Render não for ideal):

*   **PythonAnywhere:** Oferece um plano gratuito com limitações, mas bom para projetos menores em Python/Flask e suporta MySQL/PostgreSQL.
*   **Fly.io:** Possui um nível gratuito que pode acomodar aplicações Flask e bancos de dados PostgreSQL.
*   **Railway:** Similar ao Render, oferece hospedagem para aplicações e bancos de dados com um plano gratuito inicial.

Lembre-se de adaptar as instruções de deploy para a plataforma escolhida, especialmente em relação à configuração de variáveis de ambiente e comandos de build/start.

