<template>
  <div v-if="isOpen" class="search-overlay" @click.self="closeSearch">
    <div class="search-modal">
      <div class="search-input-wrapper">
        <span class="search-icon">🔍</span>
        <input 
          id="global-search-input"
          v-model="query" 
          @input="handleSearch"
          @keydown.esc="closeSearch"
          type="text" 
          placeholder="Поиск по статьям, черновикам и тегам... (Esc для выхода)" 
          autocomplete="off"
        />
      </div>

      <div class="search-results">
        <div v-if="isLoading" class="search-state">⏳ Ищем в базе...</div>
        <div v-else-if="!query" class="search-state">Введите запрос для поиска</div>
        <div v-else-if="isEmpty" class="search-state">Ничего не найдено 😔</div>

        <template v-else>
          <div v-if="results.articles.length > 0" class="result-group">
            <h4 class="group-title">📄 Статьи</h4>
            <ul>
              <li v-for="art in results.articles" :key="'art-'+art.id" @click="openArticle(art)">
                <span class="res-title">{{ art.title }}</span>
                <span class="res-meta">{{ art.year || 'н.д.' }}</span>
              </li>
            </ul>
          </div>

          <div v-if="results.drafts.length > 0" class="result-group">
            <h4 class="group-title">📝 Черновики проектов</h4>
            <ul>
              <li v-for="draft in results.drafts" :key="'draft-'+draft.id" @click="openDraft(draft)">
                <span class="res-title">{{ draft.title }}</span>
              </li>
            </ul>
          </div>

          <div v-if="results.tags.length > 0" class="result-group">
            <h4 class="group-title">🏷 Теги</h4>
            <div class="tags-row">
              <span 
                v-for="tag in results.tags" 
                :key="'tag-'+tag.id" 
                class="tag-badge" 
                :style="{ backgroundColor: tag.color }"
              >
                {{ tag.name }}
              </span>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import api from '../api';
import { useTabsStore } from '../stores/tabs';

const tabsStore = useTabsStore();
const isOpen = ref(false);
const query = ref('');
const isLoading = ref(false);
const results = ref({ articles: [], drafts: [], tags: [] });
let debounceTimer = null;

// Слушатель горячих клавиш (Ctrl+K или Cmd+K)
const handleKeydown = (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    isOpen.value = true;
    setTimeout(() => {
      const input = document.getElementById('global-search-input');
      if (input) input.focus();
    }, 100);
  }
};

onMounted(() => {
  window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown);
});

const closeSearch = () => {
  isOpen.value = false;
  query.value = '';
  results.value = { articles: [], drafts: [], tags: [] };
};

// Запрос на сервер с задержкой (чтобы не спамить API на каждую букву)
const handleSearch = () => {
  clearTimeout(debounceTimer);
  if (query.value.length < 2) {
    results.value = { articles: [], drafts: [], tags: [] };
    return;
  }
  
  isLoading.value = true;
  debounceTimer = setTimeout(async () => {
    try {
      const response = await api.get(`/search/?q=${query.value}`);
      results.value = response.data;
    } catch (error) {
      console.error("Ошибка поиска", error);
    } finally {
      isLoading.value = false;
    }
  }, 300); // 300 мс задержки
};

const isEmpty = computed(() => {
  return results.value.articles.length === 0 && 
         results.value.drafts.length === 0 && 
         results.value.tags.length === 0;
});

// Открытие статьи во вьювере
const openArticle = (art) => {
  tabsStore.openTab({
    id: 'viewer-' + art.id,
    title: '📖 ' + art.title.substring(0, 15) + '...',
    componentName: 'ArticleViewer'
  });
  closeSearch();
};

// Открытие черновика
const openDraft = (draft) => {
  tabsStore.openTab({
    id: 'draft-' + draft.project_id,
    title: '📝 Драфт: ' + draft.title.substring(0, 15),
    componentName: 'DraftEditor'
  });
  closeSearch();
};
</script>

<style scoped>
.search-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(0,0,0,0.4); backdrop-filter: blur(3px);
  display: flex; justify-content: center; padding-top: 10vh; z-index: 9999;
}
.search-modal {
  background: white; width: 600px; max-width: 90%; border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2); overflow: hidden; display: flex; flex-direction: column; max-height: 70vh;
}
.search-input-wrapper { display: flex; align-items: center; padding: 15px 20px; border-bottom: 1px solid #eee; }
.search-icon { font-size: 1.2em; margin-right: 15px; opacity: 0.5; }
.search-input-wrapper input {
  flex-grow: 1; border: none; outline: none; font-size: 1.2em; color: #2c3e50; font-family: inherit;
}
.search-results { padding: 0; overflow-y: auto; background: #fdfdfd; }
.search-state { padding: 30px; text-align: center; color: #7f8c8d; font-size: 1.1em; }
.result-group { border-bottom: 1px solid #eee; }
.result-group:last-child { border-bottom: none; }
.group-title { margin: 0; padding: 10px 20px; background: #f8f9fa; font-size: 0.85em; color: #7f8c8d; text-transform: uppercase; letter-spacing: 1px; }
.result-group ul { list-style: none; margin: 0; padding: 0; }
.result-group li {
  padding: 12px 20px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: background 0.1s;
}
.result-group li:hover { background: #3498db15; }
.res-title { font-weight: 500; color: #2c3e50; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 80%; }
.res-meta { font-size: 0.85em; color: #95a5a6; }
.tags-row { padding: 12px 20px; display: flex; flex-wrap: wrap; gap: 8px; }
.tag-badge { color: white; padding: 4px 10px; border-radius: 15px; font-size: 0.85em; font-weight: bold; }
</style>