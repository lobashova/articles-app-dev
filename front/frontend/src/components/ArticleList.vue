<template>
  <div class="articles-container">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2>📚 База статей</h2>
      <button 
        @click="showUploadModal = true"
        style="padding: 10px 20px; background: #2ecc71; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;"
      >
        + Добавить статью
      </button>
    </div>

    <div v-if="showUploadModal" style="background: #fdfdfd; padding: 20px; border: 1px solid #ccc; border-radius: 8px; margin-bottom: 20px;">
      <h3>Загрузка новой статьи</h3>
      <p style="color: #777;">Здесь скоро появится форма загрузки PDF и умный парсинг метаданных.</p>
      <button @click="showUploadModal = false" style="padding: 5px 10px; cursor: pointer;">Отмена</button>
    </div>

    <div v-if="articlesStore.isLoading">Загрузка базы...</div>
    
    <ul v-else-if="articlesStore.list.length > 0" style="list-style: none; padding: 0;">
      <li 
        v-for="article in articlesStore.list" 
        :key="article.id" 
        style="background: white; border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;"
      >
        <div>
          <h4 style="margin: 0 0 5px 0; color: #2c3e50;">{{ article.title }}</h4>
          <p style="margin: 0; font-size: 0.9em; color: #7f8c8d;">
            <span style="background: #eee; padding: 2px 6px; border-radius: 4px; margin-right: 10px;">{{ article.type }}</span>
            Год: {{ article.year || '—' }} | Журнал: {{ article.journal || '—' }}
          </p>
        </div>
        
        <div>
          <button 
            style="padding: 6px 12px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px;"
          >
            Открыть статью
          </button>
          <button 
            @click="articlesStore.deleteArticle(article.id)"
            style="padding: 6px 12px; background: #e74c3c; color: white; border: none; border-radius: 4px; cursor: pointer;"
          >
            Удалить
          </button>
        </div>
      </li>
    </ul>
    
    <div v-else class="empty-state">
      В вашей базе пока нет статей. Загрузите первый PDF-файл!
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useArticlesStore } from '../stores/articles';
import { useTabsStore } from '../stores/tabs';

const articlesStore = useArticlesStore();
const tabsStore = useTabsStore();
const showUploadModal = ref(false);

onMounted(() => {
  articlesStore.fetchArticles();
});
</script>