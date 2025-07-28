import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class MonitoringService {
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

  async getStatistics() {
    try {
      const response = await this.api.get('/monitoring/statistics');
      return { success: true, stats: response.data };
    } catch (error) {
      console.error('Ошибка получения статистики:', error);
      return { success: false, error: error.response?.data?.detail || 'Ошибка получения статистики' };
    }
  }

  async getStatus() {
    try {
      const response = await this.api.get('/monitoring/status');
      return { success: true, status: response.data };
    } catch (error) {
      console.error('Ошибка получения статуса мониторинга:', error);
      return { success: false, error: error.response?.data?.detail || 'Ошибка получения статуса' };
    }
  }

  async startMonitoring() {
    try {
      const response = await this.api.post('/monitoring/start');
      return { success: true, message: response.data.message };
    } catch (error) {
      console.error('Ошибка запуска мониторинга:', error);
      return { success: false, error: error.response?.data?.detail || 'Ошибка запуска мониторинга' };
    }
  }

  async checkPost(postUrl) {
    try {
      const response = await this.api.post('/monitoring/check-post', { post_url: postUrl });
      return { success: true, result: response.data };
    } catch (error) {
      console.error('Ошибка проверки поста:', error);
      return { success: false, error: error.response?.data?.detail || 'Ошибка проверки поста' };
    }
  }
}

export default new MonitoringService(); 