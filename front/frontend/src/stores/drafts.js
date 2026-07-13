import { defineStore } from 'pinia';
import api from '../api';

export const useDraftsStore = defineStore('drafts', {
  state: () => ({
    currentDraft: null,
    citations: [], // Список привязанных статей к текущему драфту
    isLoading: false,
    isSaving: false
  }),
  actions: {
    async fetchDraftForProject(projectId) {
      this.isLoading = true;
      try {
        const response = await api.get(`/projects/${projectId}/draft`);
        this.currentDraft = response.data;
        
        // Сразу подгружаем цитаты для этого драфта
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
    
    // --- НОВЫЕ ДЕЙСТВИЯ ДЛЯ РАБОТЫ С ЦИТАТАМИ ---
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
    }
  }
});