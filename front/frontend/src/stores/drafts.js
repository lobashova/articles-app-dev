import { defineStore } from 'pinia';
import api from '../api';

export const useDraftsStore = defineStore('drafts', {
  state: () => ({
    currentDraft: null,
    isLoading: false,
    isSaving: false
  }),
  actions: {
    // Подгружаем драфт с сервера при открытии проекта
    async fetchDraftForProject(projectId) {
      this.isLoading = true;
      try {
        const response = await api.get(`/projects/${projectId}/draft`);
        this.currentDraft = response.data;
        return response.data;
      } catch (error) {
        console.error('Ошибка при загрузке черновика:', error);
      } finally {
        this.isLoading = false;
      }
    },
    // Отправляем измененный текст в базу данных
    async saveDraft(draftId, title, content) {
      this.isSaving = true;
      try {
        await api.put(`/drafts/${draftId}`, null, {
          params: { title, content } // Передаем параметры как query-strings согласно бэкенду
        });
      } catch (error) {
        console.error('Ошибка при сохранении черновика:', error);
      } finally {
        this.isSaving = false;
      }
    }
  }
});