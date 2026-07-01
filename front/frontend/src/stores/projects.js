import { defineStore } from 'pinia';
import api from '../api';

export const useProjectStore = defineStore('projects', {
  state: () => ({
    projects: []
  }),
  actions: {
    async fetchProjects() {
      const response = await api.get('/projects/');
      this.projects = response.data;
    }
  }
});