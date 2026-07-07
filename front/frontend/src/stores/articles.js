import { defineStore } from 'pinia';
import api from '../api';

export const useArticlesStore = defineStore('articles', {
  state: () => ({
    list: [],
    isLoading: false,
  }),
  actions: {
    async fetchArticles() {
      this.isLoading = true;
      try {
        const response = await api.get('/articles/');
        this.list = response.data;
      } catch (error) {
        console.error('Ошибка при загрузке статей:', error);
      } finally {
        this.isLoading = false;
      }
    },
    // --- НОВОЕ ДЕЙСТВИЕ: Создание статьи ---
    async addArticle(articleData) {
      try {
        const response = await api.post('/articles/', articleData);
        this.list.unshift(response.data); // Добавляем новую статью в начало списка
        return response.data;
      } catch (error) {
        console.error('Ошибка при сохранении статьи:', error);
        throw error;
      }
    },
    async deleteArticle(articleId) {
      try {
        await api.delete(`/articles/${articleId}`);
        this.list = this.list.filter(article => article.id !== articleId);
      } catch (error) {
        console.error('Ошибка при удалении статьи:', error);
      }
    }
  }
});