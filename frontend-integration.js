/**
 * CursoHub Frontend Integration
 * JavaScript para integrar o frontend HTML com o backend Flask
 */

class CursoHubAPI {
    constructor(baseURL = 'http://localhost:5000/api') {
        this.baseURL = baseURL;
        this.token = localStorage.getItem('cursohub_token');
    }

    // ==================== UTILITÁRIOS ====================
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        // Adicionar token se disponível
        if (this.token) {
            config.headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Erro na requisição');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('cursohub_token', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('cursohub_token');
    }

    // ==================== AUTENTICAÇÃO ====================

    async login(email, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });

        if (data.access_token) {
            this.setToken(data.access_token);
        }

        return data;
    }

    async register(userData) {
        const data = await this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });

        if (data.access_token) {
            this.setToken(data.access_token);
        }

        return data;
    }

    async getProfile() {
        return await this.request('/auth/profile');
    }

    async updateProfile(userData) {
        return await this.request('/auth/profile', {
            method: 'PUT',
            body: JSON.stringify(userData)
        });
    }

    logout() {
        this.clearToken();
        window.location.href = '/telas/index.html';
    }

    // ==================== CURSOS ====================

    async getCourses(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = `/courses${queryString ? '?' + queryString : ''}`;
        return await this.request(endpoint);
    }

    async getCourse(courseUuid) {
        return await this.request(`/courses/${courseUuid}`);
    }

    async createCourse(courseData) {
        return await this.request('/courses', {
            method: 'POST',
            body: JSON.stringify(courseData)
        });
    }

    async updateCourse(courseUuid, courseData) {
        return await this.request(`/courses/${courseUuid}`, {
            method: 'PUT',
            body: JSON.stringify(courseData)
        });
    }

    async enrollCourse(courseUuid) {
        return await this.request(`/courses/${courseUuid}/enroll`, {
            method: 'POST'
        });
    }

    async publishCourse(courseUuid) {
        return await this.request(`/courses/${courseUuid}/publish`, {
            method: 'POST'
        });
    }

    // ==================== AULAS ====================

    async getLessons(courseUuid) {
        return await this.request(`/courses/${courseUuid}/lessons`);
    }

    async getLesson(lessonUuid) {
        return await this.request(`/lessons/${lessonUuid}`);
    }

    async createLesson(courseUuid, lessonData) {
        return await this.request(`/courses/${courseUuid}/lessons`, {
            method: 'POST',
            body: JSON.stringify(lessonData)
        });
    }

    async completeLesson(lessonUuid) {
        return await this.request(`/lessons/${lessonUuid}/complete`, {
            method: 'POST'
        });
    }

    // ==================== COMENTÁRIOS ====================

    async getComments(courseUuid) {
        return await this.request(`/courses/${courseUuid}/comments`);
    }

    async createComment(courseUuid, content, parentId = null) {
        return await this.request(`/courses/${courseUuid}/comments`, {
            method: 'POST',
            body: JSON.stringify({ content, parent_id: parentId })
        });
    }

    // ==================== AVALIAÇÕES ====================

    async rateCourse(courseUuid, rating, comment = '') {
        return await this.request(`/courses/${courseUuid}/rating`, {
            method: 'POST',
            body: JSON.stringify({ rating, comment })
        });
    }

    // ==================== PROGRESSO ====================

    async getCourseProgress(courseUuid) {
        return await this.request(`/courses/${courseUuid}/progress`);
    }

    // ==================== ANALYTICS ====================

    async getAnalyticsDashboard() {
        return await this.request('/analytics/dashboard');
    }

    // ==================== UPLOAD ====================

    async uploadFile(file, type = 'materials') {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('type', type);

        return await this.request('/upload', {
            method: 'POST',
            headers: {
                // Não definir Content-Type para FormData
                ...(this.token && { 'Authorization': `Bearer ${this.token}` })
            },
            body: formData
        });
    }
}

// ==================== FUNÇÕES UTILITÁRIAS ====================

class CursoHubUI {
    constructor() {
        this.api = new CursoHubAPI();
        this.init();
    }

    init() {
        // Verificar se usuário está logado
        this.checkAuth();
        
        // Configurar eventos globais
        this.setupGlobalEvents();
    }

    checkAuth() {
        const token = localStorage.getItem('cursohub_token');
        const currentPage = window.location.pathname;
        
        // Páginas que requerem autenticação
        const protectedPages = ['/telas/painel.html', '/telas/salinhadoaluno.html'];
        
        if (protectedPages.includes(currentPage) && !token) {
            window.location.href = '/telas/index.html';
        }
    }

    setupGlobalEvents() {
        // Event listeners globais
        document.addEventListener('DOMContentLoaded', () => {
            this.setupLoginForm();
            this.setupLogoutButtons();
            this.setupCourseCards();
        });
    }

    setupLoginForm() {
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleLogin(e);
            });
        }
    }

    setupLogoutButtons() {
        const logoutButtons = document.querySelectorAll('[data-action="logout"]');
        logoutButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.api.logout();
            });
        });
    }

    setupCourseCards() {
        const courseCards = document.querySelectorAll('[data-course-uuid]');
        courseCards.forEach(card => {
            const enrollButton = card.querySelector('[data-action="enroll"]');
            if (enrollButton) {
                enrollButton.addEventListener('click', async (e) => {
                    const courseUuid = card.dataset.courseUuid;
                    await this.handleEnrollment(courseUuid, e.target);
                });
            }
        });
    }

    async handleLogin(event) {
        const formData = new FormData(event.target);
        const email = formData.get('email');
        const password = formData.get('password');

        try {
            this.showLoading(event.target.querySelector('button[type="submit"]'));
            
            const response = await this.api.login(email, password);
            
            this.showSuccess('Login realizado com sucesso!');
            
            // Redirecionar baseado no papel do usuário
            const user = response.user;
            if (user.role === 'teacher' || user.role === 'admin') {
                window.location.href = '/telas/painel.html';
            } else {
                window.location.href = '/telas/salinhadoaluno.html';
            }
            
        } catch (error) {
            this.showError(error.message);
        } finally {
            this.hideLoading(event.target.querySelector('button[type="submit"]'));
        }
    }

    async handleEnrollment(courseUuid, button) {
        try {
            this.showLoading(button);
            
            await this.api.enrollCourse(courseUuid);
            
            this.showSuccess('Matrícula realizada com sucesso!');
            button.textContent = 'Matriculado';
            button.disabled = true;
            button.classList.add('btn-secondary');
            button.classList.remove('btn-primary');
            
        } catch (error) {
            this.showError(error.message);
        } finally {
            this.hideLoading(button);
        }
    }

    async loadCourses(containerId = 'courses-container', filters = {}) {
        try {
            const container = document.getElementById(containerId);
            if (!container) return;

            this.showLoading(container);
            
            const response = await this.api.getCourses(filters);
            const courses = response.courses;

            if (courses.length === 0) {
                container.innerHTML = '<p class="text-center text-neutral-500">Nenhum curso encontrado.</p>';
                return;
            }

            container.innerHTML = courses.map(course => this.createCourseCard(course)).join('');
            
        } catch (error) {
            this.showError('Erro ao carregar cursos: ' + error.message);
        }
    }

    createCourseCard(course) {
        return `
            <div class="card" data-course-uuid="${course.uuid}">
                <div class="aspect-video bg-gradient-to-br from-primary-400 to-primary-600 rounded-lg mb-4 flex items-center justify-center">
                    <i class="fas fa-play text-white text-4xl"></i>
                </div>
                <h3 class="font-semibold text-lg mb-2">${course.title}</h3>
                <p class="text-neutral-600 text-sm mb-4">${course.description.substring(0, 100)}...</p>
                <div class="flex items-center justify-between text-sm mb-4">
                    <span class="text-primary-600 font-medium">${course.stats?.total_students || 0} alunos</span>
                    <span class="text-neutral-500">${course.level}</span>
                </div>
                <div class="flex space-x-2">
                    <button class="btn btn-primary text-sm flex-1" data-action="enroll">
                        <i class="fas fa-user-plus mr-1"></i>
                        Matricular
                    </button>
                    <a href="/telas/salinhadoaluno.html?course=${course.uuid}" class="btn btn-ghost text-sm flex-1">
                        <i class="fas fa-eye mr-1"></i>
                        Ver
                    </a>
                </div>
            </div>
        `;
    }

    // Utilitários de UI
    showLoading(element) {
        if (element.tagName === 'BUTTON') {
            element.disabled = true;
            element.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Carregando...';
        } else {
            element.innerHTML = '<div class="text-center p-8"><i class="fas fa-spinner fa-spin text-primary-600 text-2xl"></i></div>';
        }
    }

    hideLoading(element) {
        if (element.tagName === 'BUTTON') {
            element.disabled = false;
            // Restaurar texto original do botão
        }
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
            type === 'success' ? 'bg-success text-white' : 
            type === 'error' ? 'bg-error text-white' : 
            'bg-info text-white'
        }`;
        
        notification.innerHTML = `
            <div class="flex items-center space-x-2">
                <i class="fas ${
                    type === 'success' ? 'fa-check-circle' : 
                    type === 'error' ? 'fa-exclamation-circle' : 
                    'fa-info-circle'
                }"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Remover após 5 segundos
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// ==================== INICIALIZAÇÃO ====================

// Instanciar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    window.cursoHub = new CursoHubUI();
});

// Exportar para uso global
window.CursoHubAPI = CursoHubAPI;
window.CursoHubUI = CursoHubUI;