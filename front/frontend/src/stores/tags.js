import { defineStore } from 'pinia';
import api from '../api';

export const useTagsStore = defineStore('tags', {
  state: () => ({
    list: [],
  }),
  actions: {
    async fetchTags() {
      try {
        const response = await api.get('/tags/');
        this.list = response.data;
      } catch (error) {
        console.error('Ошибка загрузки тегов:', error);
      }
    },
    async createTag(name) {
      try {
        const response = await api.post('/tags/', { name });
        this.list.push(response.data);
        return response.data;
      } catch (error) {
        console.error('Ошибка создания тега:', error);
        throw error;
      }
    }
  }
});