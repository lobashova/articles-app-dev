import { defineStore } from 'pinia';

export const useTabsStore = defineStore('tabs', {
  state: () => ({
    activeTabId: 'projects', // По умолчанию активна вкладка проектов
    openTabs: [
      { id: 'projects', title: '📁 Мои проекты', componentName: 'ProjectList' }
    ]
  }),
  actions: {
    // Открытие новой вкладки (или переключение на нее, если она уже открыта)
    openTab(tabData) {
      const existingTab = this.openTabs.find(tab => tab.id === tabData.id);
      if (!existingTab) {
        this.openTabs.push(tabData);
      }
      this.activeTabId = tabData.id;
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
    }
  }
});