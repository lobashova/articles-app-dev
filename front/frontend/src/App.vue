<template>
  <div class="app-layout">
    <GlobalSearch />
    <header class="top-bar">
      <div class="logo">📚 Приложение для статей</div>
      <button 
          @click="tabsStore.openTab({ id: 'library', title: '🗄️ База статей', componentName: 'ArticleList' })"
          style="background: transparent; color: white; border: 1px solid white; padding: 5px 15px; border-radius: 4px; cursor: pointer;"
        >
          Открыть библиотеку
        </button>
      <div class="search-container">
        <input type="text" placeholder="Умный поиск по базе..." class="global-search" />
      </div>
    </header>

    <nav class="tabs-bar" v-if="tabsStore.openTabs.length > 0">
      <div 
        v-for="tab in tabsStore.openTabs" 
        :key="tab.id"
        :class="['tab-item', { active: tabsStore.activeTabId === tab.id }]"
        @click="tabsStore.setActiveTab(tab.id)"
      >
        {{ tab.title }}
        <span 
          v-if="tab.id !== 'projects'" 
          class="close-btn" 
          @click.stop="tabsStore.closeTab(tab.id)"
        >
          ×
        </span>
      </div>
    </nav>

    <main class="main-content">
      <KeepAlive>
        <component :is="activeComponent" />
      </KeepAlive>
      
      <div v-if="!tabsStore.activeTabId" class="empty-state">
        Нет открытых вкладок. Воспользуйтесь поиском или откройте проекты.
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTabsStore } from './stores/tabs';
import ProjectList from './components/ProjectList.vue';
import DraftEditor from './components/DraftEditor.vue'; // 1. Проверьте наличие импорта!
import ArticleList from './components/ArticleList.vue';
import ArticleViewer from './components/ArticleViewer.vue';
import GlobalSearch from './components/GlobalSearch.vue';

const tabsStore = useTabsStore();

// Карта доступных компонентов
const componentsMap = {
  ProjectList,
  DraftEditor,
  ArticleList,
  ArticleViewer
};

const activeComponent = computed(() => {
  const activeTab = tabsStore.openTabs.find(t => t.id === tabsStore.activeTabId);
  return activeTab ? componentsMap[activeTab.componentName] : null;
});
</script>

<style>
/* Базовые стили для каркаса */
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  background-color: #fafafa;
}
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}
.top-bar {
  background: #2c3e50;
  color: white;
  padding: 10px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.logo {
  font-weight: bold;
  font-size: 1.2em;
}
.search-container {
  width: 400px;
}
.global-search {
  width: 100%;
  padding: 8px 12px;
  border-radius: 20px;
  border: none;
  outline: none;
}
.tabs-bar {
  display: flex;
  background: #e0e0e0;
  padding: 5px 10px 0 10px;
  border-bottom: 1px solid #ccc;
}
.tab-item {
  padding: 8px 15px;
  background: #f5f5f5;
  margin-right: 5px;
  border-radius: 5px 5px 0 0;
  cursor: pointer;
  border: 1px solid transparent;
  border-bottom: none;
  display: flex;
  align-items: center;
  gap: 8px;
}
.tab-item.active {
  background: #fff;
  border-color: #ccc;
  font-weight: bold;
}
.close-btn {
  color: #888;
  font-weight: bold;
}
.close-btn:hover {
  color: red;
}
.main-content {
  flex-grow: 1;
  padding: 20px;
  overflow-y: auto;
}
.empty-state {
  text-align: center;
  color: #777;
  margin-top: 50px;
}
</style>