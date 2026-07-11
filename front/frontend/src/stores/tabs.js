import { defineStore } from 'pinia';

export const useTabsStore = defineStore('tabs', {
  state: () => {
    // 1. При инициализации проверяем, есть ли сохраненные вкладки в браузере
    const savedTabs = localStorage.getItem('openTabs');
    const savedActiveTabId = localStorage.getItem('activeTabId');

    return {
      // Если нашли сохраненные вкладки — парсим их из строки в массив, иначе ставим дефолтную
      activeTabId: savedActiveTabId ? savedActiveTabId : 'projects',
      openTabs: savedTabs ? JSON.parse(savedTabs) : [
        { id: 'projects', title: '📁 Мои проекты', componentName: 'ProjectList' }
      ]
    };
  },
  actions: {
    // Вспомогательный метод для перезаписи данных в локальной памяти браузера
    saveToLocalStorage() {
      localStorage.setItem('openTabs', JSON.stringify(this.openTabs));
      localStorage.setItem('activeTabId', this.activeTabId);
    },

    // Переключение на другую вкладку
    setActiveTab(tabId) {
      this.activeTabId = tabId;
      this.saveToLocalStorage(); // Запоминаем, какая вкладку теперь активна
    },

    // Открытие новой вкладки (или переключение на нее, если она уже открыта)
    openTab(tabData) {
      const existingTab = this.openTabs.find(tab => tab.id === tabData.id);
      if (!existingTab) {
        this.openTabs.push(tabData);
      }
      this.activeTabId = tabData.id;
      this.saveToLocalStorage(); // Сохраняем обновленный список и активную вкладку
    },

    // Закрытие вкладки
    closeTab(tabId) {
      this.openTabs = this.openTabs.filter(tab => tab.id !== tabId);
      
      // Если закрыли активную вкладку, переключаемся на последнюю доступную
      if (this.activeTabId === tabId) {
        this.activeTabId = this.openTabs.length > 0 
          ? this.openTabs[this.openTabs.length - 1].id 
          : null;
      }
      this.saveToLocalStorage(); // Сохраняем изменения после удаления вкладки
    }
  }
});