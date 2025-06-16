

## GestorPro

Consiste em desenvolver uma plataforma para gerenciar e acompanhar projetos, focada em metodologias ágeis como RAD (Rapid Application Development). Desenvolvida como uma Aplicação de Página Única (SPA), ela permite que utilizadores organizem suas tarefas, acompanhem o progresso e colaborem eficientemente em seus projetos.

### 🔧 Requisitos:

Python 3.x

Flask
Banco de dados: SQLite

### 🗃️ Tabela 'usuarios' com os seguintes campos:

```
id: Integer (primary key, autoincrement)
email: String(50) (unique, not nullable)
senha: String(255) (not nullable)
tipoUsuario: Boolean (default False)
mudaSenha: Boolean (default False)
liberacao: Boolean (default True)
reset_token: String(100) (unique, nullable)
reset_expiration: DateTime (nullable)
```

**Tabela 'Profile' (perfil do usuário, ligada a 'User'):**
```
id: Integer (primary key, autoincrement)
userID: Integer (foreign key para 'User.id', unique, not nullable)
nome: String(50) (nullable)
contato: String(11) (nullable)
foto: String(255) (nullable, default 'default.jpg')
```

**Tabela 'Project' (projetos, ligada a 'User'):**
```
id: Integer (primary key, autoincrement)
user_id: Integer (foreign key para 'User.id', not nullable)
name: String(100) (not nullable)
description: Text (nullable)
status: String(20) (default 'A Fazer', not nullable)
created_at: DateTime (default datetime.utcnow)
```

### 🔐 Configuração de acesso ao banco de dados

```
DATABASE_URL=sqlite:///gestorprojetos.db
DATABASE_KEY=N/A (SQLite é baseado em arquivo, não usa chave de acesso como um serviço externo)
```

### 📁 Estrutura do projeto:

```
projeto/
├── venv/                   # Ambiente virtual Python (ignorada pelo Git)
├── app.py                  # Backend: API Flask, modelos de dados, lógica de autenticação e CRUD
├── gestorprojetos.db       # Base de dados SQLite (criada em runtime, ignorada pelo Git via .gitignore)
├── .gitignore              # Ficheiros e pastas a serem ignorados pelo Git
└── static/                 # Ficheiros estáticos servidos pelo Flask (pelo navegador)
    └── index.html          # Frontend: O único ficheiro HTML da SPA (contém HTML, CSS embutido e JavaScript)
    └── css/                # Ficheiro CSS externo (separe o CSS inline para cá para melhor organização)
        └── styles.css
    └── img/                # Pasta para fotos de perfil
        └── profile_pics/
            └── default.jpg # Imagem padrão de perfil
```

### 📦 Instale os requisitos do projeto:

```bash
python -m venv venv
```

```bash
pip install -r requirements.txt
```

### 🚀 Execute o projeto:

```bash
python app.py
```
