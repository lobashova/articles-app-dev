import { defineStore } from 'pinia';
import api from '../api';

export const useArticlesStore = defineStore('articles', {
  state: () => ({
    list: [],
    isLoading: false,
  }),
  actions: {
    // Получение всех статей с сервера
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
    // Удаление статьи
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