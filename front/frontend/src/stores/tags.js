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
    async createTag(name, color) {
      try {
        const response = await api.post('/tags/', { name, color });
        this.list.push(response.data);
        return response.data;
      } catch (error) {
        console.error('Ошибка создания тега:', error);
        throw error;
      }
    },
    // --- НОВОЕ ДЕЙСТВИЕ: Обновление тега ---
    async updateTag(tagId, name, color) {
      try {
        const response = await api.put(`/tags/${tagId}`, { name, color });
        const index = this.list.findIndex(t => t.id === tagId);
        if (index !== -1) this.list[index] = response.data;
        return response.data;
      } catch (error) {
        console.error('Ошибка обновления тега:', error);
        throw error;
      }
    },
    // --- НОВОЕ ДЕЙСТВИЕ: Глобальное удаление тега ---
    async deleteTag(tagId) {
      try {
        await api.delete(`/tags/${tagId}`);
        this.list = this.list.filter(t => t.id !== tagId);
      } catch (error) {
        console.error('Ошибка удаления тега:', error);
        throw error;
      }
    }
  }
});