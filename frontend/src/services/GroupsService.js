import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class GroupsService {
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

  async getUserGroups() {
    try {
      const response = await this.api.get('/groups/');
      return { success: true, groups: response.data };
    } catch (error) {
      console.error('Ошибка получения групп:', error);
      return { success: false, error: error.response?.data?.detail || 'Ошибка получения групп' };
    }
  }

  async addGroup(groupData) {
    try {
      const response = await this.api.post('/groups/', groupData);
      return { success: true, group: response.data };
    } catch (error) {
      console.error('Ошибка добавления группы:', error);
      return { success: false, error: error.response?.data?.detail || 'Ошибка добавления группы' };
    }
  }

  async updateGroup(groupId, groupData) {
    try {
      const response = await this.api.put(`/groups/${groupId}`, groupData);
      return { success: true, group: response.data };
    } catch (error) {
      console.error('Ошибка обновления группы:', error);
      return { success: false, error: error.response?.data?.detail || 'Ошибка обновления группы' };
    }
  }

  async deleteGroup(groupId) {
    try {
      await this.api.delete(`/groups/${groupId}`);
      return { success: true };
    } catch (error) {
      console.error('Ошибка удаления группы:', error);
      return { success: false, error: error.response?.data?.detail || 'Ошибка удаления группы' };
    }
  }

  async getGroupInfo(groupId) {
    try {
      const response = await this.api.get(`/groups/${groupId}`);
      return { success: true, group: response.data };
    } catch (error) {
      console.error('Ошибка получения информации о группе:', error);
      return { success: false, error: error.response?.data?.detail || 'Ошибка получения информации о группе' };
    }
  }
}

export default new GroupsService(); 