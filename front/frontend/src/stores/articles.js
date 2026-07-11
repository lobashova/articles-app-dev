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
    async uploadFile(file) {
      const formData = new FormData();
      formData.append('file', file);
      try {
        const response = await api.post('/upload-article/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        return response.data;
      } catch (error) {
        console.error('Ошибка при загрузке PDF:', error);
        throw error;
      }
    },
    async addArticle(articleData) {
      try {
        const response = await api.post('/articles/', articleData);
        this.list.unshift(response.data);
        return response.data;
      } catch (error) {
        console.error('Ошибка при сохранении статьи:', error);
        throw error;
      }
    },
    
    // --- НОВОЕ ДЕЙСТВИЕ: Редактирование статьи ---
    async updateArticle(articleId, articleData) {
      try {
        const response = await api.put(`/articles/${articleId}`, articleData);
        // Находим измененную статью в массиве на фронтенде и обновляем её данные
        const index = this.list.findIndex(article => article.id === articleId);
        if (index !== -1) {
          this.list[index] = response.data;
        }
        return response.data;
      } catch (error) {
        console.error('Ошибка при обновлении статьи:', error);
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