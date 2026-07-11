<template>
  <div class="draft-wrapper">
    <div class="draft-header">
      <input 
        v-model="draftTitle" 
        type="text" 
        placeholder="Название вашей статьи..." 
        class="title-input"
      />
      
      <div class="controls">
        <select 
          v-if="isSplitView" 
          v-model="selectedPdfPath" 
          class="article-select"
        >
          <option value="">-- Выберите статью для просмотра --</option>
          <option 
            v-for="article in availablePdfArticles" 
            :key="article.id" 
            :value="article.pdf_path"
          >
            {{ article.title }} ({{ article.year || 'н.д.' }})
          </option>
        </select>

        <button 
          @click="toggleSplitView" 
          :class="['split-btn', { active: isSplitView }]"
        >
          {{ isSplitView ? 'Закрыть Split View' : '📖 Открыть Split View' }}
        </button>
        <button class="save-btn">💾 Сохранить</button>
      </div>
    </div>

    <div :class="['workspace', { 'is-split': isSplitView }]">
      
      <div class="editor-pane">
        <MdEditor 
          v-model="draftContent" 
          language="en-US" 
          class="md-editor-custom"
        />
      </div>

      <div v-if="isSplitView" class="reader-pane">
        <div v-if="selectedPdfPath" class="pdf-container">
          <iframe 
            :src="`https://articles-app.ru/${selectedPdfPath}`" 
            width="100%" 
            height="100%" 
            frameborder="0"
          ></iframe>
        </div>
        <div v-else class="empty-reader">
          <p>👈 Выберите статью в верхнем меню, чтобы открыть её здесь.</p>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { MdEditor } from 'md-editor-v3';
import 'md-editor-v3/lib/style.css';
import { useArticlesStore } from '../stores/articles';

const articlesStore = useArticlesStore();

// Состояние черновика
const draftTitle = ref('Новый черновик');
const draftContent = ref('# Введение\n\nЗдесь вы можете писать текст. А вот пример математической модели:\n\n$f(x) = \\int_{-\\infty}^{\\infty} \\hat f(\\xi)\\,e^{2 \\pi i \\xi x} \\,d\\xi$');

// Состояние Split View
const isSplitView = ref(false);
const selectedPdfPath = ref('');

// Фильтруем статьи, оставляя только те, к которым физически прикреплен PDF
const availablePdfArticles = computed(() => {
  return articlesStore.list.filter(article => article.pdf_path);
});

const toggleSplitView = () => {
  isSplitView.value = !isSplitView.value;
  if (!isSplitView.value) {
    selectedPdfPath.value = ''; // Сбрасываем выбранную статью при закрытии
  }
};

onMounted(() => {
  // Убедимся, что статьи загружены в хранилище, чтобы было из чего выбирать
  if (articlesStore.list.length === 0) {
    articlesStore.fetchArticles();
  }
});
</script>

<style scoped>
.draft-wrapper {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px); /* Вычитаем высоту верхних панелей (Top-bar и Tabs) */
  margin: -20px; /* Убираем стандартные отступы main-content, чтобы редактор был на весь экран */
}

.draft-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: #fff;
  border-bottom: 1px solid #e0e0e0;
}

.title-input {
  width: 40%;
  font-size: 1.5em;
  padding: 5px;
  border: none;
  outline: none;
  background: transparent;
  font-weight: bold;
  color: #2c3e50;
}

.controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.article-select {
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ccc;
  max-width: 300px;
}

.split-btn {
  padding: 8px 15px;
  background: #ecf0f1;
  color: #2c3e50;
  border: 1px solid #bdc3c7;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.2s;
}

.split-btn.active {
  background: #34495e;
  color: white;
  border-color: #2c3e50;
}

.save-btn {
  padding: 8px 15px;
  background: #2ecc71;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.workspace {
  display: flex;
  flex-grow: 1;
  overflow: hidden;
}

.editor-pane {
  flex: 1; /* В обычном режиме занимает 100% ширины */
  transition: all 0.3s ease;
}

/* Когда включен Split View, каждый блок занимает по 50% */
.workspace.is-split .editor-pane {
  flex: 0 0 50%;
  border-right: 2px solid #ccc;
}

.reader-pane {
  flex: 0 0 50%;
  background: #ecf0f1;
  display: flex;
  flex-direction: column;
}

.pdf-container {
  flex-grow: 1;
  width: 100%;
  height: 100%;
}

.empty-reader {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #7f8c8d;
  font-size: 1.1em;
}

.md-editor-custom {
  height: 100% !important;
}
</style>