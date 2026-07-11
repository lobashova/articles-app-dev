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
          <p>👈 Выберите статью в верхнем меню.</p>
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

// --- ЛОГИКА ИЗМЕНЕНИЯ РАЗМЕРА ОКОН (DRAG & DROP) ---
const workspaceRef = ref(null);
const editorWidth = ref(50); // По умолчанию редактор занимает 50%
const isDragging = ref(false);

const startDrag = () => {
  isDragging.value = true;
};

const stopDrag = () => {
  isDragging.value = false;
};

const drag = (e) => {
  if (!isDragging.value || !workspaceRef.value) return;
  
  // Получаем координаты рабочей области
  const rect = workspaceRef.value.getBoundingClientRect();
  
  // Вычисляем новую ширину в процентах
  let newWidth = ((e.clientX - rect.left) / rect.width) * 100;
  
  // Ограничиваем, чтобы нельзя было схлопнуть окна полностью (от 20% до 80%)
  if (newWidth > 20 && newWidth < 80) {
    editorWidth.value = newWidth;
  }
};
// ----------------------------------------------------

const availablePdfArticles = computed(() => {
  return articlesStore.list.filter(article => article.pdf_path);
});

const toggleSplitView = () => {
  isSplitView.value = !isSplitView.value;
  if (!isSplitView.value) {
    selectedPdfPath.value = ''; 
    editorWidth.value = 50; // Сброс ширины при закрытии
  }
};

onMounted(() => {
  if (articlesStore.list.length === 0) {
    articlesStore.fetchArticles();
  }
});
</script>

<style scoped>
.draft-wrapper {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
  margin: -20px;
}

.draft-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 15px 20px; background: #fff; border-bottom: 1px solid #e0e0e0;
}

.title-input {
  width: 40%; font-size: 1.5em; padding: 5px; border: none;
  outline: none; background: transparent; font-weight: bold; color: #2c3e50;
}

.controls { display: flex; gap: 10px; align-items: center; }
.article-select { padding: 8px; border-radius: 4px; border: 1px solid #ccc; max-width: 300px; }

.split-btn {
  padding: 8px 15px; background: #ecf0f1; color: #2c3e50;
  border: 1px solid #bdc3c7; border-radius: 4px; cursor: pointer;
  font-weight: bold; transition: all 0.2s;
}
.split-btn.active { background: #34495e; color: white; border-color: #2c3e50; }
.save-btn { padding: 8px 15px; background: #2ecc71; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }

.workspace {
  display: flex;
  flex-grow: 1;
  overflow: hidden;
  position: relative;
}

/* Отключаем выделение текста при перетаскивании ползунка */
.workspace.is-dragging { user-select: none; }
.workspace.is-dragging iframe { pointer-events: none; }

.editor-pane {
  height: 100%;
  transition: width 0.1s; /* Плавность, но не слишком медленная для drag */
}

/* СТИЛИ РАЗДЕЛИТЕЛЯ */
.divider {
  width: 10px;
  background-color: #f1f2f6;
  cursor: col-resize;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
  border-left: 1px solid #dfe4ea;
  border-right: 1px solid #dfe4ea;
  transition: background-color 0.2s;
}
.divider:hover, .workspace.is-dragging .divider {
  background-color: #dcdde1;
}
.divider-handle {
  height: 30px;
  width: 4px;
  background-color: #a4b0be;
  border-radius: 2px;
}

.reader-pane {
  height: 100%;
  background: #ecf0f1;
  display: flex;
  flex-direction: column;
}

.pdf-container { flex-grow: 1; width: 100%; height: 100%; }
.empty-reader { display: flex; justify-content: center; align-items: center; height: 100%; color: #7f8c8d; font-size: 1.1em; }
.md-editor-custom { height: 100% !important; }
</style>