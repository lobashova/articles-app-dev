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
        const response = await api.get('/projects/');
        this.list = response.data;
      } catch (error) {
        console.error('Ошибка при загрузке проектов:', error);
      } finally {
        this.isLoading = false;
      }
    },
    async addProject(projectData) {
      try {
        const response = await api.post('/projects/', projectData);
        this.list.push(response.data); 
      } catch (error) {
        console.error('Ошибка при создании проекта:', error);
      }
    },
    // --- НОВОЕ ДЕЙСТВИЕ: Удаление проекта ---
    async deleteProject(projectId) {
      try {
        await api.delete(`/projects/${projectId}`);
        // Фильтруем список, оставляя только те проекты, id которых не совпадает с удаленным
        this.list = this.list.filter(project => project.id !== projectId);
      } catch (error) {
        console.error('Ошибка при удалении проекта:', error);
      }
    }
  }
});