import { defineStore } from 'pinia';
import api from '../api';

export const useAuthorsStore = defineStore('authors', {
  state: () => ({
    list: [],
  }),
  actions: {
    async fetchAuthors() {
      try {
        const response = await api.get('/authors/');
        this.list = response.data;
      } catch (error) {
        console.error('Ошибка при загрузке авторов:', error);
      }
    },
    async createAuthor(authorData) {
      try {
        const response = await api.post('/authors/', authorData);
        this.list.push(response.data);
        return response.data;
      } catch (error) {
        console.error('Ошибка при создании автора:', error);
        throw error;
      }
    }
  }
});