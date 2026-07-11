<template>
  <div class="viewer-wrapper">
    <div class="pdf-pane">
      <div v-if="pdfPath" class="pdf-container">
        <iframe 
          :src="`https://articles-app.ru/${pdfPath}`" 
          width="100%" 
          height="100%" 
          frameborder="0"
        ></iframe>
      </div>
      <div v-else class="empty-pdf">
        <p>У этой статьи пока нет загруженного PDF-файла.</p>
      </div>
    </div>

    <div class="info-pane">
      <div class="info-header">
        <h3>📝 Анализ статьи</h3>
        <button @click="saveNotes" class="save-btn" :disabled="isSaving">
          {{ isSaving ? '⏳ Сохранение...' : '💾 Сохранить' }}
        </button>
      </div>

      <div class="notes-container">
        <div class="note-group">
          <label>🎯 Цели исследования (Aims)</label>
          <textarea 
            v-model="notes.aims" 
            placeholder="Какую проблему решает автор?..."
            rows="3"
          ></textarea>
        </div>

        <div class="note-group">
          <label>🛠 Методы (Methods)</label>
          <textarea 
            v-model="notes.methods" 
            placeholder="Какие данные и алгоритмы использовались?..."
            rows="4"
          ></textarea>
        </div>

        <div class="note-group">
          <label>📊 Главные результаты (Results)</label>
          <textarea 
            v-model="notes.results" 
            placeholder="Ключевые выводы, цифры, инсайты..."
            rows="5"
          ></textarea>
        </div>

        <div class="note-group">
          <label>💡 Мои комментарии и идеи</label>
          <textarea 
            v-model="notes.comments" 
            placeholder="Как это можно применить в моем проекте? С чем я не согласна?..."
            rows="4"
          ></textarea>
        </div>
        
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api';
import { useTabsStore } from '../stores/tabs';
import { useArticlesStore } from '../stores/articles';

const tabsStore = useTabsStore();
const articlesStore = useArticlesStore();

const articleId = ref(null);
const pdfPath = ref('');
const isSaving = ref(false);

// Состояние полей ввода
const notes = ref({
  aims: '',
  methods: '',
  results: '',
  comments: ''
});

// Храним ID существующих заметок, чтобы знать: обновлять (PUT) их или создавать новые (POST)
const noteIds = ref({
  aims: null,
  methods: null,
  results: null,
  comments: null
});

onMounted(async () => {
  // Вытаскиваем ID статьи из названия вкладки (формат: viewer-ID)
  const activeTabId = tabsStore.activeTabId;
  if (activeTabId && activeTabId.startsWith('viewer-')) {
    articleId.value = parseInt(activeTabId.split('-')[1]);
    
    // Ищем статью в хранилище, чтобы получить путь к PDF
    const article = articlesStore.list.find(a => a.id === articleId.value);
    if (article) {
      pdfPath.value = article.pdf_path;
    }

    // Загружаем уже существующие заметки с бэкенда
    try {
      const response = await api.get(`/articles/${articleId.value}/notes/`);
      response.data.forEach(note => {
        // Раскладываем полученные заметки по нашим полям
        if (notes.value[note.field_type] !== undefined) {
          notes.value[note.field_type] = note.content;
          noteIds.value[note.field_type] = note.id; // Сохраняем ID для будущего обновления
        }
      });
    } catch (error) {
      console.error("Ошибка при загрузке заметок", error);
    }
  }
});

const saveNotes = async () => {
  isSaving.value = true;
  try {
    // Проходим по каждому полю (aims, methods, results, comments)
    for (const field of Object.keys(notes.value)) {
      const content = notes.value[field];
      const id = noteIds.value[field];

      if (id) {
        // Если заметка уже была в базе — обновляем её (PUT)
        await api.put(`/notes/${id}`, { field_type: field, content: content });
      } else if (content.trim() !== '') {
        // Если заметки не было, но текст появился — создаем новую (POST)
        const res = await api.post(`/articles/${articleId.value}/notes/`, { 
          field_type: field, 
          content: content 
        });
        noteIds.value[field] = res.data.id; // Запоминаем новый ID
      }
    }
  } catch (error) {
    alert("Ошибка при сохранении заметок!");
  } finally {
    isSaving.value = false;
  }
};
</script>

<style scoped>
.viewer-wrapper {
  display: flex;
  height: calc(100vh - 120px);
  margin: -20px;
  background: #ecf0f1;
}

/* Левая часть - PDF */
.pdf-pane {
  flex: 1;
  border-right: 2px solid #bdc3c7;
  display: flex;
  flex-direction: column;
}
.pdf-container {
  flex-grow: 1;
  width: 100%;
}
.empty-pdf {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #7f8c8d;
  font-size: 1.2em;
}

/* Правая часть - Рабочая тетрадь */
.info-pane {
  width: 450px;
  background: #fff;
  display: flex;
  flex-direction: column;
  box-shadow: -2px 0 10px rgba(0,0,0,0.05);
}

.info-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fdfdfd;
}
.info-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.2em;
}

.save-btn {
  background: #2ecc71;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  transition: 0.2s;
}
.save-btn:hover { background: #27ae60; }
.save-btn:disabled { background: #95a5a6; cursor: not-allowed; }

.notes-container {
  padding: 20px;
  overflow-y: auto;
  flex-grow: 1;
}

.note-group {
  margin-bottom: 20px;
}
.note-group label {
  display: block;
  font-weight: bold;
  margin-bottom: 8px;
  color: #34495e;
}
.note-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-sizing: border-box;
  font-family: inherit;
  resize: vertical;
  background: #fafafa;
}
.note-group textarea:focus {
  outline: none;
  border-color: #3498db;
  background: #fff;
}
</style>