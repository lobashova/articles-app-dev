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
        
        <div v-if="isSplitView" class="searchable-select">
          <input 
            v-model="searchQuery"
            @focus="isDropdownOpen = true"
            @blur="hideDropdown"
            type="text"
            placeholder="🔍 Поиск статьи для Split View..."
            class="article-search-input"
          />
          
          <ul v-if="isDropdownOpen" class="dropdown-list">
            <li 
              v-for="article in filteredArticles" 
              :key="article.id"
              @mousedown="selectArticle(article)"
              class="dropdown-item"
            >
              <div style="font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                {{ article.title }}
              </div>
              <div style="font-size: 0.8em; color: #7f8c8d;">
                Год: {{ article.year || 'н.д.' }} | {{ article.journal || 'Журнал не указан' }}
              </div>
            </li>
            <li v-if="filteredArticles.length === 0" class="dropdown-item empty">
              Статьи не найдены
            </li>
          </ul>
        </div>

        <button 
          @click="toggleSplitView" 
          :class="['split-btn', { active: isSplitView }]"
        >
          {{ isSplitView ? 'Закрыть PDF' : '📖 Открыть PDF' }}
        </button>
        <button class="save-btn">💾 Сохранить</button>
      </div>
    </div>

    <div 
      class="workspace" 
      ref="workspaceRef" 
      @mousemove="drag" 
      @mouseup="stopDrag" 
      @mouseleave="stopDrag"
      :class="{ 'is-dragging': isDragging }"
    >
      
      <div class="editor-pane" :style="{ width: isSplitView ? editorWidth + '%' : '100%' }">
        <MdEditor 
          v-model="draftContent" 
          language="en-US" 
          :preview="false" 
          class="md-editor-custom"
        />
      </div>

      <div 
        v-if="isSplitView" 
        class="divider" 
        @mousedown="startDrag"
        title="Потяните, чтобы изменить размер"
      >
        <div class="divider-handle"></div>
      </div>

      <div v-if="isSplitView" class="reader-pane" :style="{ width: (100 - editorWidth) + '%' }">
        <div v-if="selectedPdfPath" class="pdf-container">
          <iframe 
            :src="`https://articles-app.ru/${selectedPdfPath}`" 
            width="100%" 
            height="100%" 
            frameborder="0"
          ></iframe>
        </div>
        <div v-else class="empty-reader">
          <p>👈 Найдите и выберите статью в панели сверху.</p>
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

const draftTitle = ref('Новый черновик');
const draftContent = ref('# Введение\n\nЗдесь вы можете писать текст. А вот пример математической модели:\n\n$f(x) = \\int_{-\\infty}^{\\infty} \\hat f(\\xi)\\,e^{2 \\pi i \\xi x} \\,d\\xi$');

const isSplitView = ref(false);
const selectedPdfPath = ref('');

// --- ЛОГИКА УМНОГО ПОИСКА ---
const searchQuery = ref('');
const isDropdownOpen = ref(false);

const availablePdfArticles = computed(() => {
  return articlesStore.list.filter(article => article.pdf_path);
});

// Фильтруем статьи по названию, журналу или году
const filteredArticles = computed(() => {
  const query = searchQuery.value.toLowerCase();
  if (!query) return availablePdfArticles.value;
  
  return availablePdfArticles.value.filter(a => 
    a.title.toLowerCase().includes(query) || 
    (a.journal && a.journal.toLowerCase().includes(query)) ||
    (a.year && a.year.toString().includes(query))
  );
});

const selectArticle = (article) => {
  selectedPdfPath.value = article.pdf_path;
  searchQuery.value = article.title; // Показываем название выбранной статьи в инпуте
  isDropdownOpen.value = false;
};

// Используем таймаут, чтобы клик по списку успел сработать до того, как инпут потеряет фокус
const hideDropdown = () => {
  setTimeout(() => {
    isDropdownOpen.value = false;
  }, 200);
};
// ----------------------------

// --- ЛОГИКА ИЗМЕНЕНИЯ РАЗМЕРА ОКОН ---
const workspaceRef = ref(null);
const editorWidth = ref(50);
const isDragging = ref(false);

const startDrag = () => { isDragging.value = true; };
const stopDrag = () => { isDragging.value = false; };

const drag = (e) => {
  if (!isDragging.value || !workspaceRef.value) return;
  const rect = workspaceRef.value.getBoundingClientRect();
  let newWidth = ((e.clientX - rect.left) / rect.width) * 100;
  if (newWidth > 20 && newWidth < 80) {
    editorWidth.value = newWidth;
  }
};
// -------------------------------------

const toggleSplitView = () => {
  isSplitView.value = !isSplitView.value;
  if (!isSplitView.value) {
    selectedPdfPath.value = ''; 
    searchQuery.value = '';
    editorWidth.value = 50; 
  }
};

onMounted(() => {
  if (articlesStore.list.length === 0) {
    articlesStore.fetchArticles();
  }
});
</script>

<style scoped>
.draft-wrapper { display: flex; flex-direction: column; height: calc(100vh - 120px); margin: -20px; }
.draft-header { display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; background: #fff; border-bottom: 1px solid #e0e0e0; }
.title-input { width: 40%; font-size: 1.5em; padding: 5px; border: none; outline: none; background: transparent; font-weight: bold; color: #2c3e50; }
.controls { display: flex; gap: 10px; align-items: center; }

/* СТИЛИ ДЛЯ УМНОГО ПОИСКА */
.searchable-select {
  position: relative;
  width: 350px;
}
.article-search-input {
  width: 100%;
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #ccc;
  outline: none;
  font-family: inherit;
}
.article-search-input:focus {
  border-color: #3498db;
}
.dropdown-list {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  max-height: 300px;
  overflow-y: auto;
  background: white;
  border: 1px solid #ccc;
  border-top: none;
  border-radius: 0 0 4px 4px;
  margin: 0;
  padding: 0;
  list-style: none;
  z-index: 100;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.dropdown-item {
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
}
.dropdown-item:last-child {
  border-bottom: none;
}
.dropdown-item:hover {
  background-color: #f8f9fa;
}
.dropdown-item.empty {
  color: #7f8c8d;
  text-align: center;
  cursor: default;
}
.dropdown-item.empty:hover {
  background-color: white;
}

.split-btn { padding: 8px 15px; background: #ecf0f1; color: #2c3e50; border: 1px solid #bdc3c7; border-radius: 4px; cursor: pointer; font-weight: bold; transition: all 0.2s; }
.split-btn.active { background: #34495e; color: white; border-color: #2c3e50; }
.save-btn { padding: 8px 15px; background: #2ecc71; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
.workspace { display: flex; flex-grow: 1; overflow: hidden; position: relative; }
.workspace.is-dragging { user-select: none; }
.workspace.is-dragging iframe { pointer-events: none; }
.editor-pane { height: 100%; transition: width 0.1s; }
.divider { width: 10px; background-color: #f1f2f6; cursor: col-resize; display: flex; justify-content: center; align-items: center; z-index: 10; border-left: 1px solid #dfe4ea; border-right: 1px solid #dfe4ea; transition: background-color 0.2s; }
.divider:hover, .workspace.is-dragging .divider { background-color: #dcdde1; }
.divider-handle { height: 30px; width: 4px; background-color: #a4b0be; border-radius: 2px; }
.reader-pane { height: 100%; background: #ecf0f1; display: flex; flex-direction: column; }
.pdf-container { flex-grow: 1; width: 100%; height: 100%; }
.empty-reader { display: flex; justify-content: center; align-items: center; height: 100%; color: #7f8c8d; font-size: 1.1em; }
.md-editor-custom { height: 100% !important; }
</style>