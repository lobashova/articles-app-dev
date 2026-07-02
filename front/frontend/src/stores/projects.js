import { defineStore } from 'pinia';
import api from '../api';

export const useProjectsStore = defineStore('projects', {
  state: () => ({
    list: [],
    isLoading: false,
  }),
  actions: {
    async fetchProjects() {
      this.isLoading = true;
      try {
        // Делаем GET-запрос к нашему эндпоинту FastAPI
        const response = await api.get('/projects/');
        this.list = response.data;
      } catch (error) {
        console.error('Ошибка при загрузке проектов:', error);
      } finally {
        this.isLoading = false;
      }
    }
  }
});