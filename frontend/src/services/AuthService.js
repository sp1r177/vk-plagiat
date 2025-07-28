import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class AuthService {
  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Добавляем токен к запросам
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  async vkLogin(vkId) {
    try {
      const response = await this.api.post('/auth/vk-login', { vk_id: vkId });
      
      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
        return { success: true, user: response.data.user };
      }
      
      return { success: false, error: 'Не удалось получить токен' };
    } catch (error) {
      console.error('Ошибка авторизации:', error);
      return { success: false, error: error.response?.data?.detail || 'Ошибка авторизации' };
    }
  }

  async getCurrentUser() {
    try {
      const response = await this.api.get('/auth/me');
      return { success: true, user: response.data };
    } catch (error) {
      console.error('Ошибка получения данных пользователя:', error);
      return { success: false, error: error.response?.data?.detail || 'Ошибка получения данных' };
    }
  }

  logout() {
    localStorage.removeItem('access_token');
  }

  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  }
}

export default new AuthService(); 