🚀 GestorPro - Gerenciador de Projetos RAD
GestorPro é uma plataforma web moderna e intuitiva para gerenciamento e acompanhamento de projetos, focada em metodologias ágeis como RAD (Rapid Application Development). Desenvolvida como uma Aplicação de Página Única (SPA), ela permite que utilizadores organizem suas tarefas, acompanhem o progresso e colaborem eficientemente em seus projetos.

🧠 Visão Geral
A proposta do GestorPro é oferecer uma solução unificada para o ciclo de vida do projeto, onde:

Utilizadores gerenciam o seu próprio perfil com dados adicionais (nome, contato, foto).

Utilizadores criam, visualizam, editam e excluem projetos (implementando um ciclo CRUD completo).

A plataforma visualiza o status dos projetos através de gráficos dinâmicos.

Garante a segurança e integridade dos dados através de autenticação robusta e validações no backend.

Figma do projeto (anterior, para referência visual do design): https://www.figma.com/design/XIuqlSS2bx04yJaOv6VWEP/Figma-basics?node-id=603-2

🖥️ Tecnologias Utilizadas
✅ Frontend (Aplicação de Página Única - SPA):

HTML5: Estrutura base da SPA.

CSS3 (Tailwind CSS via CDN): Estilização utilitária e responsiva.

JavaScript Vanilla: Lógica principal da SPA, gestão de estado, navegação entre vistas, e todas as interações dinâmicas.

Chart.js: Biblioteca JavaScript para criação de gráficos dinâmicos (ex: gráfico de status de projetos).

Google Fonts (Inter): Tipografia moderna e legível.

✅ Backend (API REST):

Python & Flask: Framework web leve, atuando como o servidor de API para a lógica de negócio, autenticação e operações CRUD.

SQLAlchemy & SQLite: ORM (Object-Relational Mapper) e base de dados relacional leve para persistência de dados.

Werkzeug.security: Para hashing seguro de senhas.

Flask-Login: Para gestão de sessões de utilizador.

Secrets & Datetime: Para geração e gestão de tokens de redefinição de senha.

Re (Regex): Para validações de formato de dados (e-mail, contato).

✅ Estrutura modular e responsiva, com foco em usabilidade.

📂 Estrutura do Projeto
📁 Gestorpro/
├── venv/                   # Ambiente virtual Python (ignorada pelo Git)
├── app.py                  # Backend: API Flask, modelos de dados, lógica de autenticação e CRUD
├── gestorprojetos.db       # Base de dados SQLite (criada em runtime, ignorada pelo Git via .gitignore)
├── .gitignore              # Ficheiros e pastas a serem ignorados pelo Git
└── static/                 # Ficheiros estáticos servidos pelo Flask (pelo navegador)
    └── index.html          # Frontend: O único ficheiro HTML da SPA (contém HTML, CSS embutido e JavaScript)
    └── css/
        └── styles.css      # Ficheiro CSS externo (separe o CSS inline para cá para melhor organização)
    └── img/
        └── profile_pics/   # Pasta para fotos de perfil
            └── default.jpg # Imagem padrão de perfil

🎯 Funcionalidades Essenciais
🔒 Autenticação e Gestão de Utilizadores
Registo de Novos Utilizadores: Criação de conta com validação de nome completo (min. 2 caracteres), e-mail (formato válido e único) e senha (obrigatória, min. 6 caracteres).

Login: Acesso seguro com e-mail e senha. Verifica credenciais, estado da conta (ativa/inativa) e se a senha precisa ser alterada.

Perfil do Utilizador: Gestão de dados adicionais como nome, contato (11 dígitos numéricos) e uma URL para foto de perfil.

Alteração de Senha: Requer a senha atual correta, uma nova senha e a sua confirmação (devem ser idênticas e ter no mínimo 6 caracteres).

Recuperação de Senha: Geração e validação de um token seguro (com expiração de 1 hora) enviado por e-mail (para depuração, o link aparece na consola). Permite a redefinição da senha.

Logout: Encerramento seguro da sessão do utilizador.

📊 Gestão de Projetos (CRUD Completo)
Visualização de Projetos: Lista e exibe detalhes de todos os projetos do utilizador autenticado.

Criação de Projetos: Adição de novos projetos com nome (obrigatório, min. 3 caracteres), descrição (opcional, min. 5 caracteres se fornecida) e status (A Fazer, Em Andamento, Concluído).

Edição de Projetos: Atualização de nome, descrição e status de projetos existentes. Apenas o proprietário do projeto pode editar.

Eliminação de Projetos: Remoção de projetos. Apenas o proprietário pode eliminar.

Gráfico de Status de Projetos: Uma representação visual dinâmica (gráfico de donut Chart.js) da distribuição dos projetos por status, exibida no painel de controlo.

🚧 Funcionalidades Futuras
Gestão de Perfil Avançada: Implementação de upload real de ficheiros para fotos de perfil.

Colaboração em Projetos: Adicionar funcionalidades para que múltiplos utilizadores possam trabalhar no mesmo projeto.

Sistema de Chat: Integração de um sistema de comunicação em tempo real entre utilizadores.

Painel Administrativo: Desenvolvimento de uma interface para que utilizadores com tipoUsuario=True (admins) possam gerir outros utilizadores e projetos da plataforma.

Notificações: Implementação de alertas automáticos por e-mail ou diretamente na aplicação.

📄 Licença
Este projeto está sob a licença MIT. Sinta-se livre para usar, modificar e contribuir!

🛠 Feito com 💙 por Equipe GestorPro
