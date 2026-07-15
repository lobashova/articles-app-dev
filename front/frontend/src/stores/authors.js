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
    },
    // --- НОВЫЕ МЕТОДЫ: Редактирование и удаление авторов ---
    async updateAuthor(authorId, last_name, initials) {
      try {
        const response = await api.put(`/authors/${authorId}`, { last_name, initials });
        const index = this.list.findIndex(a => a.id === authorId);
        if (index !== -1) this.list[index] = response.data;
        return response.data;
      } catch (error) {
        console.error('Ошибка обновления автора:', error);
        throw error;
      }
    },
    async deleteAuthor(authorId) {
      try {
        await api.delete(`/authors/${authorId}`);
        this.list = this.list.filter(a => a.id !== authorId);
      } catch (error) {
        console.error('Ошибка удаления автора:', error);
        throw error;
      }
    }
  }
});