import { defineStore } from 'pinia';
import api from '../api';

export const useDraftsStore = defineStore('drafts', {
  state: () => ({
    currentDraft: null,
    citations: [],
    isLoading: false,
    isSaving: false
  }),
  actions: {
    async fetchDraftForProject(projectId) {
      this.isLoading = true;
      try {
        const response = await api.get(`/projects/${projectId}/draft`);
        this.currentDraft = response.data;
        await this.fetchDraftCitations(response.data.id);
        return response.data;
      } catch (error) {
        console.error('Ошибка при загрузке черновика:', error);
      } finally {
        this.isLoading = false;
      }
    },
    async saveDraft(draftId, title, content) {
      this.isSaving = true;
      try {
        await api.put(`/drafts/${draftId}`, null, {
          params: { title, content }
        });
      } catch (error) {
        console.error('Ошибка при сохранении черновика:', error);
      } finally {
        this.isSaving = false;
      }
    },
    async fetchDraftCitations(draftId) {
      try {
        const response = await api.get(`/drafts/${draftId}/citations/`);
        this.citations = response.data;
      } catch (error) {
        console.error('Ошибка загрузки цитат драфта:', error);
      }
    },
    async addDraftCitation(draftId, articleId, marker) {
      try {
        const response = await api.post('/draft-citations/', {
          draft_id: draftId,
          article_id: articleId,
          in_text_marker: marker
        });
        this.citations.push(response.data);
        return response.data;
      } catch (error) {
        console.error('Ошибка привязки цитаты:', error);
      }
    },

    // --- НОВОЕ ДЕЙСТВИЕ: Удаление цитаты из базы данных ---
    async removeDraftCitation(citationId) {
      try {
        await api.delete(`/draft-citations/${citationId}`);
        // Удаляем из локального состояния массива на фронтенде
        this.citations = this.citations.filter(c => c.id !== citationId);
      } catch (error) {
        console.error('Ошибка при удалении цитаты:', error);
        alert('Не удалось удалить статью из списка литературы.');
      }
    }
  }
});