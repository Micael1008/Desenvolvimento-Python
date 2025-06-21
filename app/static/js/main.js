// app/static/js/main.js - VERSÃO FINAL, COMPLETA E CORRIGIDA
document.addEventListener('DOMContentLoaded', () => {

    // --- LÓGICA PARA TROCA DE TEMA (CLARO/ESCURO) ---
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    if (themeToggleBtn) {
        const darkIcon = document.getElementById('theme-toggle-dark-icon');
        const lightIcon = document.getElementById('theme-toggle-light-icon');
        
        const applyTheme = (isDark) => {
            document.documentElement.classList.toggle('dark', isDark);
            if (darkIcon && lightIcon) {
                // Se for escuro, o ícone da lua (dark) se esconde, e o do sol (light) aparece.
                darkIcon.classList.toggle('hidden', isDark);
                lightIcon.classList.toggle('hidden', !isDark);
            }
        };
        
        themeToggleBtn.addEventListener('click', () => {
            const newThemeIsDark = !document.documentElement.classList.contains('dark');
            applyTheme(newThemeIsDark);
            localStorage.setItem('theme', newThemeIsDark ? 'dark' : 'light');
        });

        // Aplica o tema que estava salvo ou o padrão (escuro)
        const savedThemeIsDark = localStorage.getItem('theme') !== 'light';
        applyTheme(savedThemeIsDark);
    }

    // --- FUNÇÃO FETCHDATA MELHORADA ---
    async function fetchData(url, method = 'GET', data = null) {
        const options = { method, headers: { 'Content-Type': 'application/json' } };
        if (data) options.body = JSON.stringify(data);
        try {
            const response = await fetch(url, options);
            const result = await response.json();
            if (!response.ok) {
                showFlashMessage(result.message || 'Ocorreu um erro no servidor.', 'error');
                console.error('API Error:', result);
                return null;
            }
            return result;
        } catch (error) {
            console.error('Connection Error:', error);
            showFlashMessage('Erro de conexão. Verifique sua rede e o console.', 'error');
            return null;
        }
    }

    // --- ESTADO GLOBAL E ELEMENTOS DO DOM ---
    let appState = { isAuthenticated: false, currentUser: null, projects: [] };
    const views = document.querySelectorAll('.view');
    const navLinksContainer = document.getElementById('nav-links');
    const welcomeMessage = document.getElementById('welcome-message');
    const profileDetails = document.getElementById('profile-details');
    const projectList = document.getElementById('project-list');
    const flashMessagesContainer = document.getElementById('flash-messages');
    const modalBackdrop = document.getElementById('modal-backdrop');
    const projectModal = document.getElementById('project-modal');
    const projectForm = document.getElementById('project-form');
    const modalTitle = document.getElementById('modal-title');
    const profileModal = document.getElementById('profile-modal');
    let statusChart = null;

    // --- FUNÇÕES DE UTILITÁRIO ---
    function showFlashMessage(message, type = 'info') {
        if (!flashMessagesContainer) return;
        flashMessagesContainer.innerHTML = `<div class="flash-message ${type}">${message}</div>`;
        setTimeout(() => { flashMessagesContainer.innerHTML = ''; }, 5000);
    }

    // --- FUNÇÕES DE RENDERIZAÇÃO ---
    function renderNav() {
        if (!navLinksContainer) return;
        if (appState.isAuthenticated && appState.currentUser) {
            navLinksContainer.innerHTML = `
                <div class="flex items-center space-x-4">
                    <span class="text-slate-400">Olá, <span class="font-semibold text-white">${appState.currentUser.nome.split(' ')[0]}</span></span>
                    <button id="logout-btn" class="bg-slate-700 text-slate-300 font-semibold py-2 px-4 rounded-lg hover:bg-slate-600 transition">Sair</button>
                </div>`;
        } else {
            navLinksContainer.innerHTML = '';
        }
    }
    
    function renderProfileDetails() {
        if (!profileDetails || !appState.currentUser) return;
        profileDetails.innerHTML = `
            <p><strong>Nome:</strong> ${appState.currentUser.nome || 'Não informado'}</p>
            <p><strong>Email:</strong> ${appState.currentUser.email}</p>
            <p><strong>Contato:</strong> ${appState.currentUser.contato || 'Não informado'}</p>
            <p><strong>Tipo:</strong> ${appState.currentUser.tipoUsuario ? 'Administrador' : 'Utilizador'}</p>`;
    }

    function renderProjects() {
        if (!projectList) return;
        projectList.innerHTML = appState.projects.length === 0 ? `<div class="text-center py-12 px-6 bg-slate-800/50 rounded-lg"><h3 class="font-semibold text-white">Nenhum projeto encontrado.</h3><p class="text-slate-400 mt-1">Clique em "Novo Projeto" para começar.</p></div>` :
            appState.projects.map(p => `
            <div class="project-item border border-slate-700 p-4 rounded-lg flex justify-between items-center">
                <div><h3 class="font-bold text-lg text-white">${p.name}</h3><p class="text-slate-400 text-sm">${p.description || ''}</p></div>
                <div class="flex items-center gap-4">
                    <span class="text-sm font-medium px-3 py-1 rounded-full ${p.status === 'Concluído' ? 'bg-green-900/50 text-green-300' : p.status === 'Em Andamento' ? 'bg-yellow-900/50 text-yellow-300' : 'bg-slate-700 text-slate-300'}">${p.status}</span>
                    <button data-id="${p.id}" class="edit-project-btn text-slate-400 hover:text-indigo-400">Editar</button>
                    <button data-id="${p.id}" class="delete-project-btn text-slate-400 hover:text-red-400">Eliminar</button>
                </div>
            </div>`).join('');
    }

    function renderChart() {
        const chartCanvas = document.getElementById('project-status-chart');
        if (!chartCanvas) return;
        if (statusChart) statusChart.destroy();
        const ctx = chartCanvas.getContext('2d');
        const statusCounts = appState.projects.reduce((acc, p) => { acc[p.status] = (acc[p.status] || 0) + 1; return acc; }, {});
        const backgroundColors = {
            'A Fazer': '#4f46e5',
            'Em Andamento': '#f59e0b',
            'Concluído': '#10b981'
        };
        const data = {
            labels: Object.keys(statusCounts).length > 0 ? Object.keys(statusCounts) : ['Nenhum Projeto'],
            datasets: [{
                label: 'Projetos',
                data: Object.keys(statusCounts).length > 0 ? Object.values(statusCounts) : [1],
                backgroundColor: Object.keys(statusCounts).length > 0 ? Object.keys(statusCounts).map(status => backgroundColors[status] || '#6b7280') : ['#374151'],
                borderColor: '#1f2937', borderWidth: 2
            }]
        };
        statusChart = new Chart(ctx, {
            type: 'doughnut', data, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#d1d5db', font: { size: 14 } } } } }
        });
    }
    
    async function renderDashboard() {
        if (!appState.isAuthenticated || !welcomeMessage) return;
        welcomeMessage.textContent = `Bem-vindo(a) de volta, ${appState.currentUser.nome.split(' ')[0]}!`;
        const projectsData = await fetchData('/api/projects');
        if (projectsData) {
            appState.projects = projectsData;
            renderProjects();
            renderChart();
        }
        const profileData = await fetchData('/api/profile');
        if (profileData) {
            appState.currentUser = { ...appState.currentUser, ...profileData };
             renderProfileDetails();
        }
    }
    
    function navigate(viewId) {
        const targetView = viewId.replace('-view', '');
        views.forEach(v => v.classList.toggle('active', v.id === `${targetView}-view`));
        if (targetView === 'dashboard') {
            renderDashboard();
        }
        renderNav();
    }

    async function checkAuthStatus() {
        const result = await fetchData('/api/auth_status');
        appState.isAuthenticated = result?.isAuthenticated;
        if (appState.isAuthenticated) {
            appState.currentUser = result.user;
            navigate('dashboard');
        } else {
            navigate('landing');
        }
    }

    async function handleLogin(e) {
        e.preventDefault();
        const data = { email: e.target.elements['login-email'].value, password: e.target.elements['login-password'].value };
        const result = await fetchData('/api/login', 'POST', data);
        if (result?.isAuthenticated) {
            appState.isAuthenticated = true;
            appState.currentUser = result.user;
            showFlashMessage('Login bem-sucedido!', 'success');
            navigate('dashboard');
        }
    }

    async function handleSignup(e) {
        e.preventDefault();
        const name = e.target.elements['signup-name'].value;
        const email = e.target.elements['signup-email'].value;
        const password = e.target.elements['signup-password'].value;
        const confirmPassword = e.target.elements['signup-confirm-password'].value;
        if (password !== confirmPassword) return showFlashMessage('As senhas não coincidem.', 'error');
        
        const result = await fetchData('/api/signup', 'POST', { name, email, password });
        if (result?.isAuthenticated) {
            // Após cadastro, faz login automaticamente para pegar todos os dados do usuário
            const loginResult = await fetchData('/api/login', 'POST', { email, password });
            if (loginResult?.isAuthenticated) {
                appState.isAuthenticated = true;
                appState.currentUser = loginResult.user;
                showFlashMessage('Conta criada com sucesso!', 'success');
                navigate('dashboard');
            }
        }
    }

    async function handleLogout() {
        await fetchData('/api/logout', 'POST');
        appState.isAuthenticated = false;
        appState.currentUser = null;
        navigate('landing');
    }

    function openProjectModal(project = null) {
        if (!projectForm || !modalTitle) return;
        projectForm.reset();
        document.getElementById('project-id').value = '';
        if (project) {
            modalTitle.textContent = 'Editar Projeto';
            document.getElementById('project-id').value = project.id;
            document.getElementById('project-name').value = project.name;
            document.getElementById('project-description').value = project.description || '';
            document.getElementById('project-status').value = project.status;
        } else {
            modalTitle.textContent = 'Adicionar Novo Projeto';
        }
        if(projectModal) projectModal.style.display = 'block';
        if(modalBackdrop) modalBackdrop.style.display = 'block';
    }

    function closeProjectModal() {
        if(projectModal) projectModal.style.display = 'none';
        if(modalBackdrop) modalBackdrop.style.display = 'none';
    }

    async function handleProjectSubmit(e) {
        e.preventDefault();
        const id = document.getElementById('project-id').value;
        const projectData = {
            name: document.getElementById('project-name').value,
            description: document.getElementById('project-description').value,
            status: document.getElementById('project-status').value,
        };
        const url = id ? `/api/projects/${id}` : '/api/projects';
        const method = id ? 'PUT' : 'POST';
        const result = await fetchData(url, method, projectData);
        if (result) {
            showFlashMessage(result.message, 'success');
            closeProjectModal();
            await renderDashboard();
        }
    }

    function setupEventListeners() {
        document.body.addEventListener('click', (e) => {
            const button = e.target.closest('button');
            if (!button) return;
            if (button.dataset.target) { e.preventDefault(); navigate(button.dataset.target); }
            if (button.id === 'logout-btn') handleLogout();
            if (button.id === 'add-project-btn') openProjectModal();
            if (button.id === 'cancel-project-btn') closeProjectModal();
            if (button.classList.contains('edit-project-btn')) {
                const project = appState.projects.find(p => p.id == button.dataset.id);
                if (project) openProjectModal(project);
            }
            if (button.classList.contains('delete-project-btn')) {
                if (confirm('Tem a certeza que deseja excluir este projeto?')) {
                    fetchData(`/api/projects/${button.dataset.id}`, 'DELETE').then(r => r && renderDashboard());
                }
            }
        });
        document.getElementById('login-form')?.addEventListener('submit', handleLogin);
        document.getElementById('signup-form')?.addEventListener('submit', handleSignup);
        projectForm?.addEventListener('submit', handleProjectSubmit);
        document.getElementById('logo')?.addEventListener('click', e => { e.preventDefault(); navigate(appState.isAuthenticated ? 'dashboard' : 'landing'); });
        modalBackdrop?.addEventListener('click', closeProjectModal);
    }
    
    setupEventListeners();
    checkAuthStatus();
});