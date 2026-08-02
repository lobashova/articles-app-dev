<template>
  <div class="articles-container">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2>📚 База источников</h2>
      <button 
        @click="openCreateTab"
        style="padding: 10px 20px; background: #2ecc71; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;"
      >
        + Добавить статью
      </button>
    </div>

    <div class="filters-panel">
      <div class="filters-grid">
        <div class="filter-item">
          <label>Поиск по названию</label>
          <input v-model="filters.title" placeholder="Введите название..." />
        </div>
        <div class="filter-item">
          <label>Автор</label>
          <input v-model="filters.author" placeholder="Фамилия или инициалы..." />
        </div>
        <div class="filter-item">
          <label>Журнал</label>
          <input v-model="filters.journal" placeholder="Название журнала..." />
        </div>
        <div class="filter-item">
          <label>Год</label>
          <input v-model="filters.year" type="number" placeholder="Например, 2023" />
        </div>
        <div class="filter-item">
          <label>Тег</label>
          <input v-model="filters.tag" placeholder="Название тега..." />
        </div>
        <div class="filter-item">
          <label>Сортировка</label>
          <select v-model="sortBy">
            <option value="newest">Сначала новые (по году)</option>
            <option value="oldest">Сначала старые (по году)</option>
            <option value="alpha">По алфавиту (А-Я)</option>
          </select>
        </div>
      </div>
      <div class="filters-actions">
        <button @click="resetFilters" class="reset-btn">Сбросить фильтры</button>
      </div>
    </div>

    <div v-if="articlesStore.isLoading">Загрузка базы...</div>
    
    <ul v-else-if="filteredAndSortedArticles.length > 0" style="list-style: none; padding: 0;">
      <li 
        v-for="article in filteredAndSortedArticles" 
        :key="article.id" 
        style="background: white; border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;"
      >
        <div>
          <h4 style="margin: 0 0 5px 0; color: #2c3e50;">{{ article.title }}</h4>
          <p style="margin: 0; font-size: 0.9em; color: #7f8c8d;">
            <span style="background: #eee; padding: 2px 6px; border-radius: 4px; margin-right: 10px; font-weight: bold;">{{ article.type }}</span>
            Год: {{ article.year || '—' }} | Журнал: {{ article.journal || '—' }}
          </p>
          
          <div v-if="article.authors && article.authors.length > 0" style="margin-top: 5px; font-size: 0.85em; color: #34495e;">
            👥 Авторы: {{ article.authors.map(a => `${a.last_name} ${a.initials}`).join(', ') }}
          </div>
          <div v-if="article.tags && article.tags.length > 0" style="margin-top: 5px;">
            <span v-for="tag in article.tags" :key="tag.id" style="background: #3498db; color: white; padding: 2px 6px; border-radius: 4px; margin-right: 5px; font-size: 0.8em;">
              {{ tag.name }}
            </span>
          </div>
        </div>
        
        <div style="display: flex; gap: 8px;">
          <button 
            @click="openArticleTab(article)"
            style="padding: 8px 16px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;"
          >
            Открыть и анализировать
          </button>
          
          <button 
            @click="articlesStore.deleteArticle(article.id)"
            style="padding: 8px 16px; background: #e74c3c; color: white; border: none; border-radius: 4px; cursor: pointer;"
          >
            Удалить
          </button>
        </div>
      </li>
    </ul>
    
    <div v-else class="empty-state">
      По вашему запросу ничего не найдено или база пуста.
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useArticlesStore } from '../stores/articles';
import { useTabsStore } from '../stores/tabs';

const articlesStore = useArticlesStore();
const tabsStore = useTabsStore();

// --- СОСТОЯНИЕ ФИЛЬТРОВ И СОРТИРОВКИ ---
const filters = ref({
  title: '',
  author: '',
  journal: '',
  year: '',
  tag: ''
});
const sortBy = ref('newest'); // 'newest', 'oldest', 'alpha'

// Сброс фильтров
const resetFilters = () => {
  filters.value = { title: '', author: '', journal: '', year: '', tag: '' };
  sortBy.value = 'newest';
};

// Вычисляемое свойство: фильтрует и сортирует список статей
const filteredAndSortedArticles = computed(() => {
  // Получаем исходный список
  let result = articlesStore.list;

  // 1. Фильтрация
  if (filters.value.title) {
    const q = filters.value.title.toLowerCase();
    result = result.filter(a => a.title && a.title.toLowerCase().includes(q));
  }
  
  if (filters.value.year) {
    result = result.filter(a => a.year && a.year.toString() === filters.value.year.toString());
  }
  
  if (filters.value.journal) {
    const q = filters.value.journal.toLowerCase();
    result = result.filter(a => a.journal && a.journal.toLowerCase().includes(q));
  }
  
  if (filters.value.author) {
    const q = filters.value.author.toLowerCase();
    result = result.filter(a => {
      if (!a.authors || !Array.isArray(a.authors)) return false; // Защита, если авторы не подгружены
      return a.authors.some(auth => 
        (auth.last_name && auth.last_name.toLowerCase().includes(q)) || 
        (auth.initials && auth.initials.toLowerCase().includes(q))
      );
    });
  }
  
  if (filters.value.tag) {
    const q = filters.value.tag.toLowerCase();
    result = result.filter(a => {
      if (!a.tags || !Array.isArray(a.tags)) return false; // Защита, если теги не подгружены
      return a.tags.some(tag => tag.name && tag.name.toLowerCase().includes(q));
    });
  }

  // 2. Сортировка
  // Создаем копию массива, чтобы не мутировать стейт при вызове .sort()
  result = [...result];
  
  if (sortBy.value === 'alpha') {
    result.sort((a, b) => {
      const titleA = a.title || '';
      const titleB = b.title || '';
      return titleA.localeCompare(titleB);
    });
  } else if (sortBy.value === 'newest') {
    result.sort((a, b) => (b.year || 0) - (a.year || 0));
  } else if (sortBy.value === 'oldest') {
    result.sort((a, b) => (a.year || 0) - (b.year || 0));
  }

  return result;
});

// Открытие вкладки для создания новой статьи
const openCreateTab = () => {
  tabsStore.openTab({
    id: 'viewer-new',
    title: '➕ Новая статья',
    componentName: 'ArticleViewer'
  });
};

// Открытие существующей статьи
const openArticleTab = (article) => {
  tabsStore.openTab({
    id: 'viewer-' + article.id,
    title: '📖 ' + (article.title ? article.title.substring(0, 15) + '...' : 'Статья'),
    componentName: 'ArticleViewer'
  });
};

onMounted(() => {
  articlesStore.fetchArticles();
});
</script>

<style scoped>
/* Стили для панели фильтров */
.filters-panel {
  background: white;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 20px;
  border: 1px solid #e1e8ed;
  box-shadow: 0 2px 10px rgba(0,0,0,0.02);
}
.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 15px;
  margin-bottom: 15px;
}
.filter-item {
  display: flex;
  flex-direction: column;
}
.filter-item label {
  font-size: 0.85em;
  font-weight: bold;
  color: #34495e;
  margin-bottom: 6px;
}
.filter-item input, .filter-item select {
  padding: 8px 10px;
  border: 1px solid #bdc3c7;
  border-radius: 6px;
  font-size: 0.9em;
  outline: none;
  transition: border-color 0.2s;
}
.filter-item input:focus, .filter-item select:focus {
  border-color: #3498db;
}
.filters-actions {
  display: flex;
  justify-content: flex-end;
}
.reset-btn {
  padding: 8px 16px;
  background: #95a5a6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: bold;
  transition: background 0.2s;
}
.reset-btn:hover {
  background: #7f8c8d;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #7f8c8d;
  background: white;
  border-radius: 8px;
  border: 1px dashed #bdc3c7;
  font-size: 1.1em;
}
</style>