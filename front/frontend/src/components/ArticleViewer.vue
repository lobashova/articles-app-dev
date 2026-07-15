<!-- <!-- <template>
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

        <div class="note-group">
            <label>🏷 Теги</label>
            <div class="tags-list">
                <span v-for="tag in articleTags" :key="tag.id" class="tag-badge">
                {{ tag.name }}
                </span>
            </div>
            <div class="form-row">
                <select v-model="selectedTag" @change="addTagToArticle(selectedTag)" class="half">
                <option :value="null">-- Добавить существующий тег --</option>
                <option v-for="t in tagsStore.list" :key="t.id" :value="t">{{ t.name }}</option>
                </select>
                <input v-model="newTagName" placeholder="Новый тег..." class="quarter" />
                <button @click="createAndAddTag" class="add-tag-btn">+</button>
            </div>
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

import { useTagsStore } from '../stores/tags';

const tagsStore = useTagsStore();
const newTagName = ref('');
const articleTags = ref([]); // Теги, привязанные к этой статье

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
  tagsStore.fetchTags();
});

const addTagToArticle = async (tag) => {
  try {
    await api.post(`/articles/${articleId.value}/tags/${tag.id}`);
    articleTags.value.push(tag);
  } catch (error) {
    alert("Не удалось привязать тег");
  }
};

const createAndAddTag = async () => {
  if (!newTagName.value) return;
  const tag = await tagsStore.createTag(newTagName.value);
  await addTagToArticle(tag);
  newTagName.value = '';
};

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

.tag-badge {
  display: inline-block;
  background: #3498db;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  margin-right: 5px;
  font-size: 0.85em;
}
.add-tag-btn {
  background: #34495e;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
}
</style> -->

<!-- <template>
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
        <div style="display: flex; gap: 10px;">
          <button @click="copyApaCitation" class="apa-btn" title="Скопировать в формате APA">
            📋 APA
          </button>
          
          <button @click="saveNotes" class="save-btn" :disabled="isSaving">
            {{ isSaving ? '⏳ Сохранение...' : '💾 Сохранить' }}
          </button>
        </div>
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

        <div class="note-group">
          <label>🏷 Теги статьи</label>
          
          <div class="tags-list">
            <span 
              v-for="tag in articleTags" 
              :key="tag.id" 
              class="tag-badge" 
              :style="{ backgroundColor: tag.color }"
            >
              {{ tag.name }}
              <span @click.stop="removeTagFromArticle(tag.id)" class="remove-tag-x">×</span>
            </span>
          </div>

          <div class="tag-input-wrapper">
            <input 
              v-model="newTagName" 
              @focus="isDropdownOpen = true"
              @input="isDropdownOpen = true"
              :placeholder="isTagEditMode ? 'Редактирование тега...' : 'Начните вводить тег...'" 
              class="search-input"
            />
            
            <ul v-if="isDropdownOpen && newTagName" class="tag-dropdown">
              <li v-for="t in filteredTags" :key="t.id" class="dropdown-item" @mousedown="addTagToArticle(t)">
                <div class="tag-item-left">
                  <span class="color-dot" :style="{ background: t.color }"></span> 
                  {{ t.name }}
                </div>
                <div class="tag-item-actions">
                  <button @mousedown.stop="startEditTag(t)" class="tag-action-btn edit-t" title="Изменить">✏️</button>
                  <button @mousedown.stop="handleDeleteTag(t.id)" class="tag-action-btn delete-t" title="Удалить навсегда">🗑️</button>
                </div>
              </li>
              
              <li v-if="!filteredTags.length && !isTagEditMode" @mousedown="createAndAddTag" class="dropdown-item create-new">
                + Создать новый тег "{{ newTagName }}"
              </li>
            </ul>
            
            <input type="color" v-model="newTagColor" class="color-picker" title="Выберите цвет">
            
            <button v-if="isTagEditMode" @click="handleUpdateTag" type="button" class="tag-control-btn save-t">✓</button>
            <button v-if="isTagEditMode" @click="cancelTagEdit" type="button" class="tag-control-btn cancel-t">×</button>
          </div>
        </div>
        
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'; // <--- ДОБАВИТЬ computed СЮДА
import api from '../api';
import { useTabsStore } from '../stores/tabs';
import { useArticlesStore } from '../stores/articles';
import { useTagsStore } from '../stores/tags';

const tabsStore = useTabsStore();
const articlesStore = useArticlesStore();
const tagsStore = useTagsStore();

const articleId = ref(null);
const pdfPath = ref('');
const isSaving = ref(false);
const selectedTag = ref(null); 
const newTagName = ref('');
const newTagColor = ref('#3498db'); // Инициализируем цвет
const articleTags = ref([]);
const isDropdownOpen = ref(false); // Инициализируем состояние дропдауна

const notes = ref({ aims: '', methods: '', results: '', comments: '' });
const noteIds = ref({ aims: null, methods: null, results: null, comments: null });

// Переменные состояния для редактирования тегов
const isTagEditMode = ref(false);
const editingTagId = ref(null);

const loadArticleData = async () => {
  const activeTabId = tabsStore.activeTabId;
  if (!activeTabId || !activeTabId.startsWith('viewer-')) return;
  
  articleId.value = parseInt(activeTabId.split('-')[1]);
  
  // Ищем статью. Если список еще грузится, watch подхватит её позже
  const article = articlesStore.list.find(a => a.id === articleId.value);
  if (article) {
    pdfPath.value = article.pdf_path;
  }

  // Загружаем заметки
  try {
    const response = await api.get(`/articles/${articleId.value}/notes/`);
    response.data.forEach(note => {
      if (notes.value[note.field_type] !== undefined) {
        notes.value[note.field_type] = note.content;
        noteIds.value[note.field_type] = note.id;
      }
    });
  } catch (e) { console.error("Ошибка загрузки заметок:", e); }

  // ЗАГРУЖАЕМ ТЕГИ, УЖЕ ПРИВЯЗАННЫЕ К СТАТЬЕ
  try {
    const tagsRes = await api.get(`/articles/${articleId.value}/tags/`);
    articleTags.value = tagsRes.data;
  } catch (e) { console.error("Ошибка загрузки тегов:", e); }
};

watch(() => articlesStore.list, () => {
  if (!pdfPath.value) loadArticleData();
}, { deep: true });

onMounted(async () => {
  // РЕШЕНИЕ ПРОБЛЕМЫ ПУСТОГО PDF: Если список статей пуст (нажали F5), грузим его!
  if (articlesStore.list.length === 0) {
    await articlesStore.fetchArticles();
  }
  
  await loadArticleData();
  tagsStore.fetchTags();
});

const addTagToArticle = async (tag) => {
  if (!tag) return;
  
  // Проверяем, не привязан ли уже этот тег (чтобы не было ошибок на сервере)
  if (articleTags.value.find(t => t.id === tag.id)) {
    selectedTag.value = null; // просто сбрасываем выпадающий список
    return;
  }
  
  try {
    await api.post(`/articles/${articleId.value}/tags/${tag.id}`);
    articleTags.value.push(tag);
    selectedTag.value = null; // Очищаем выбор после успешного добавления
  } catch (error) {
    alert("Не удалось привязать тег");
  }
};

// УМНЫЙ ПОИСК ТЕГОВ
const filteredTags = computed(() => {
  return tagsStore.list.filter(t => 
    t.name.toLowerCase().includes(newTagName.value.toLowerCase())
  );
});

const createAndAddTag = async () => {
  if (!newTagName.value) return;
  try {
    // Отправляем запрос на создание
    const response = await api.post('/tags/', { 
      name: newTagName.value, 
      color: newTagColor.value 
    });
    
    const newTag = response.data;
    
    // Добавляем созданный тег в общий справочник хранилища
    tagsStore.list.push(newTag);
    
    // Привязываем тег к текущей статье
    await addTagToArticle(newTag);
    
    // Очищаем инпут
    newTagName.value = '';
  } catch (e) { 
    alert("Ошибка создания тега"); 
  }
};

const saveNotes = async () => {
  isSaving.value = true;
  try {
    for (const field of Object.keys(notes.value)) {
      const content = notes.value[field];
      const id = noteIds.value[field];

      if (id) {
        await api.put(`/notes/${id}`, { field_type: field, content: content });
      } else if (content.trim() !== '') {
        const res = await api.post(`/articles/${articleId.value}/notes/`, { 
          field_type: field, 
          content: content 
        });
        noteIds.value[field] = res.data.id;
      }
    }
  } catch (error) {
    alert("Ошибка при сохранении заметок!");
  } finally {
    isSaving.value = false;
  }
};

// Кнопка отвязки тега от конкретной статьи (с сохранением в базе данных)
const removeTagFromArticle = async (tagId) => {
  try {
    // 1. Отправляем запрос на бэкенд для удаления связи в БД
    await api.delete(`/articles/${articleId.value}/tags/${tagId}`);
    
    // 2. Только после успешного ответа сервера удаляем тег из локального интерфейса
    articleTags.value = articleTags.value.filter(t => t.id !== tagId);
  } catch (error) {
    console.error("Не удалось отвязать тег:", error);
    alert("Ошибка на сервере при попытке отвязать тег.");
  }
};

// Вход в режим редактирования тега из выпадающего списка
const startEditTag = (tag) => {
  isTagEditMode.value = true;
  editingTagId.value = tag.id;
  newTagName.value = tag.name;
  newTagColor.value = tag.color;
  isDropdownOpen.value = false;
};

// Отмена редактирования
const cancelTagEdit = () => {
  isTagEditMode.value = false;
  editingTagId.value = null;
  newTagName.value = '';
  newTagColor.value = '#3498db';
};

// Сохранение изменений тега (PUT)
const handleUpdateTag = async () => {
  if (!newTagName.value || !editingTagId.value) return;
  try {
    const updatedTag = await tagsStore.updateTag(editingTagId.value, newTagName.value, newTagColor.value);
    
    // Обновляем тег в локальном списке статьи, если он там был привязан
    const index = articleTags.value.findIndex(t => t.id === editingTagId.value);
    if (index !== -1) {
      articleTags.value[index] = updatedTag;
    }
    
    cancelTagEdit();
  } catch (e) {
    alert("Ошибка при обновлении тега");
  }
};

// Удаление тега навсегда (DELETE)
const handleDeleteTag = async (tagId) => {
  if (confirm("Вы уверены, что хотите удалить этот тег из всей системы? Он пропадет у всех статей!")) {
    try {
      await tagsStore.deleteTag(tagId);
      // Убираем из текущей статьи
      articleTags.value = articleTags.value.filter(t => t.id !== tagId);
    } catch (e) {
      alert("Не удалось удалить тег");
    }
  }
};

// --- ГЕНЕРАЦИЯ И КОПИРОВАНИЕ APA ---
const copyApaCitation = async () => {
  try {
    const response = await api.get(`/articles/${articleId.value}/apa`);
    const citationText = response.data.citation;
    
    // Копируем текст в буфер обмена браузера
    await navigator.clipboard.writeText(citationText);
    
    alert("✅ Цитата скопирована:\n\n" + citationText);
  } catch (error) {
    console.error(error);
    alert("Не удалось сгенерировать цитату. Проверьте консоль.");
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

.tag-badge {
  display: inline-block;
  background: #3498db;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  margin-right: 5px;
  font-size: 0.85em;
}
.add-tag-btn {
  background: #34495e;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.tag-input-wrapper { display: flex; gap: 5px; position: relative; margin-top: 5px; }
.search-input { flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
.color-picker { width: 40px; height: 40px; border: none; cursor: pointer; background: none; }
.tag-dropdown { position: absolute; top: 100%; left: 0; width: 100%; background: white; border: 1px solid #eee; z-index: 10; border-radius: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.dropdown-item { padding: 8px; cursor: pointer; display: flex; align-items: center; }
.dropdown-item:hover { background: #f0f0f0; }
.color-dot { width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; }
.tag-badge { color: white; padding: 4px 10px; border-radius: 15px; margin-right: 5px; display: inline-block; }
.tag-badge {
  color: white;
  padding: 4px 10px;
  border-radius: 15px;
  margin-right: 5px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}
.remove-tag-x {
  cursor: pointer;
  background: rgba(0,0,0,0.2);
  border-radius: 50%;
  width: 14px;
  height: 14px;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  font-size: 11px;
}
.remove-tag-x:hover { background: rgba(0,0,0,0.4); }

.dropdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
}
.tag-item-left { display: flex; align-items: center; }

.tag-item-actions { display: flex; gap: 4px; }
.tag-action-btn {
  background: none; border: none; cursor: pointer; padding: 2px; font-size: 0.9em; filter: grayscale(1); transition: 0.2s;
}
.tag-action-btn:hover { filter: grayscale(0); transform: scale(1.1); }

.tag-control-btn {
  border: none; border-radius: 4px; width: 35px; height: 35px; font-weight: bold; cursor: pointer; color: white;
}
.tag-control-btn.save-t { background: #2ecc71; }
.tag-control-btn.cancel-t { background: #95a5a6; }
.apa-btn {
  background: #f39c12;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  transition: 0.2s;
}
.apa-btn:hover {
  background: #e67e22;
} 
</style>  -->

<template>
  <div class="viewer-wrapper">
    <div class="pdf-pane">
      <div v-if="articleData.pdf_path" class="pdf-container">
        <iframe 
          :src="`https://articles-app.ru/${articleData.pdf_path}`" 
          width="100%" 
          height="100%" 
          frameborder="0"
        ></iframe>
      </div>
      
      <div v-else class="upload-zone">
        <div class="upload-card">
          <span style="font-size: 3em;">📁</span>
          <h4>Загрузите PDF-файл статьи</h4>
          <p>Система автоматически откроет его и попытается извлечь метаданные</p>
          <input type="file" accept=".pdf" @change="handleFileUpload" class="file-input-hidden" id="pdf-initializer" />
          <label for="pdf-initializer" class="upload-label-btn">
            {{ isUploading ? '⏳ Анализируем PDF...' : 'Выбрать файл' }}
          </label>
        </div>
      </div>
    </div>

    <div class="info-pane">
      <div class="info-header">
        <h3>{{ isNewMode ? '✨ Добавление источника' : '📝 Анализ статьи' }}</h3>
        <button @click="saveEverything" class="save-btn" :disabled="isSaving">
          {{ isSaving ? '⏳ Сохранение...' : '💾 Сохранить всё' }}
        </button>
      </div>

      <div class="accordion-container">
        
        <div class="accordion-section">
          <div class="accordion-header" @click="isMetadataOpen = !isMetadataOpen">
            <span>📋 Метаданные статьи</span>
            <span>{{ isMetadataOpen ? '▼' : '▲' }}</span>
          </div>
          
          <div v-if="isMetadataOpen" class="accordion-content">
            <div class="form-row">
              <div class="form-group half">
                <label>Тип источника *</label>
                <select v-model="articleData.type" required>
                  <option value="Journal Article">Журнальная статья</option>
                  <option value="Book">Книга</option>
                  <option value="Conference Paper">Материалы конференции</option>
                  <option value="Website">Веб-сайт</option>
                </select>
              </div>
              <div class="form-group half">
                <label>Год издания *</label>
                <input v-model="articleData.year" type="number" required />
              </div>
            </div>

            <div class="form-group">
              <label>Название статьи/книги *</label>
              <input v-model="articleData.title" type="text" required placeholder="Введите название..." />
            </div>

            <div class="authors-sub-block">
              <label style="font-weight: bold; font-size: 0.85em; display: block; margin-bottom: 5px;">
                👥 Авторы (в порядке цитирования)
              </label>
              
              <div class="authors-badge-list">
                <span v-for="(auth, idx) in articleData.authors" :key="idx" class="author-mini-badge">
                  {{ auth.last_name }} {{ auth.initials }}
                  <span @click="articleData.authors.splice(idx, 1)" style="cursor:pointer; font-weight:bold; margin-left:5px;">×</span>
                </span>
              </div>

              <div class="author-input-container" style="position: relative; margin-top: 8px;">
                <div class="form-row" style="gap: 5px;">
                  <input 
                    v-model="authorSearchQuery" 
                    @focus="isAuthorDropdownOpen = true"
                    placeholder="Начните вводить фамилию..." 
                    class="half"
                    style="padding:6px; border: 1px solid #ccc; border-radius: 4px;"
                  />
                  <input 
                    v-model="newAuthorForm.initials" 
                    placeholder="И. О." 
                    class="quarter" 
                    style="padding:6px; border: 1px solid #ccc; border-radius: 4px;"
                  />
                  <button @click.prevent="handleCreateAndAddAuthor" class="author-add-btn">
                    + Создать и добавить
                  </button>
                </div>

                <ul v-if="isAuthorDropdownOpen && authorSearchQuery" class="author-dropdown">
                  <li 
                    v-for="a in filteredAuthors" 
                    :key="a.id" 
                    @mousedown="addExistingAuthor(a)"
                    class="author-dropdown-item"
                  >
                    👤 {{ a.last_name }} {{ a.initials }}
                  </li>
                  <li v-if="filteredAuthors.length === 0" class="author-dropdown-item empty">
                    В базе нет автора "{{ authorSearchQuery }}". Заполните "И.О." и нажмите Создать.
                  </li>
                </ul>
              </div>
            </div>

            <div v-if="articleData.type === 'Journal Article'" class="fields-highlight">
              <div class="form-row">
                <div class="form-group half"><label>Журнал</label><input v-model="articleData.journal" type="text" /></div>
                <div class="form-group quarter"><label>Выпуск</label><input v-model="articleData.issue" type="text" /></div>
                <div class="form-group quarter"><label>Страницы</label><input v-model="articleData.pages" type="text" /></div>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group half"><label>DOI</label><input v-model="articleData.doi" type="text" /></div>
              <div class="form-group half"><label>Web Ссылка</label><input v-model="articleData.web_link" type="url" /></div>
            </div>
            <div class="form-group">
              <label>Аннотация (Abstract)</label>
              <textarea v-model="articleData.abstract" rows="2"></textarea>
            </div>
          </div>
        </div>

        <div class="accordion-section">
          <div class="accordion-header" @click="isInfoOpen = !isInfoOpen">
            <span>📝 Информация о статье и теги</span>
            <span>{{ isInfoOpen ? '▼' : '▲' }}</span>
          </div>
          
          <div v-if="isInfoOpen" class="accordion-content">
            <div class="form-group">
              <label>🏷 Теги статьи</label>
              <div class="tags-list" style="margin-bottom: 8px;">
                <span v-for="tag in articleTags" :key="tag.id" class="tag-badge" :style="{ backgroundColor: tag.color }">
                  {{ tag.name }} <span @click.stop="removeTagFromArticle(tag.id)" style="cursor:pointer; margin-left:4px;">×</span>
                </span>
              </div>
              <div class="tag-input-wrapper">
                <input v-model="newTagName" @focus="isTagDropdownOpen = true" placeholder="Поиск/создание тега..." class="search-input" />
                <ul v-if="isTagDropdownOpen && newTagName" class="tag-dropdown">
                  <li v-for="t in filteredTags" :key="t.id" @mousedown="addTagToArticle(t)" class="dropdown-item">
                    <span class="color-dot" :style="{ background: t.color }"></span> {{ t.name }}
                  </li>
                  <li v-if="!filteredTags.length" @mousedown="createAndAddTag" class="dropdown-item create-new">
                    + Создать тег "{{ newTagName }}"
                  </li>
                </ul>
                <input type="color" v-model="newTagColor" class="color-picker" title="Цвет тега">
              </div>
            </div>

            <div class="form-group">
              <label>🎯 Цели исследования (Aims)</label>
              <textarea v-model="notes.aims" rows="3" placeholder="Какую проблему решает автор?..."></textarea>
            </div>
            <div class="form-group">
              <label>🛠 Методы (Methods)</label>
              <textarea v-model="notes.methods" rows="3" placeholder="Алгоритмы, выборка, данные..."></textarea>
            </div>
            <div class="form-group">
              <label>📊 Главные результаты (Results)</label>
              <textarea v-model="notes.results" rows="3" placeholder="Ключевые выводы..."></textarea>
            </div>
            <div class="form-group">
              <label>💡 Мои комментарии и идеи</label>
              <textarea v-model="notes.comments" rows="3" placeholder="Как это использовать в проекте?..."></textarea>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import api from '../api';
import { useTabsStore } from '../stores/tabs';
import { useArticlesStore } from '../stores/articles';
import { useAuthorsStore } from '../stores/authors';
import { useTagsStore } from '../stores/tags';

const tabsStore = useTabsStore();
const articlesStore = useArticlesStore();
const authorsStore = useAuthorsStore();
const tagsStore = useTagsStore();

const articleId = ref(null);
const isSaving = ref(false);
const isUploading = ref(false);

// Состояния раскрытия блоков (По умолчанию метаданные открыты, инфо закрыта)
const isMetadataOpen = ref(true);
const isInfoOpen = ref(false);

// Режим создания новой статьи
const isNewMode = computed(() => articleId.value === 'new' || !articleId.value);

// Единое реактивное состояние метаданных статьи
const defaultArticleData = {
  type: 'Journal Article', title: '', year: new Date().getFullYear(),
  journal: '', issue: '', pages: '', edition: '', doi: '', web_link: '', abstract: '',
  pdf_path: '', authors: []
};
const articleData = ref({ ...defaultArticleData });

// Состояние авторов и тегов
const selectedAuthor = ref(null);
const authorSearchQuery = ref('');
const isAuthorDropdownOpen = ref(false);
const newAuthorForm = ref({ last_name: '', initials: '' });
const selectedTag = ref(null);
const newTagName = ref('');
const newTagColor = ref('#3498db');
const articleTags = ref([]);
const isTagDropdownOpen = ref(false);

// Заметки
const notes = ref({ aims: '', methods: '', results: '', comments: '' });
const noteIds = ref({ aims: null, methods: null, results: null, comments: null });

// Умная фильтрация тегов
const filteredTags = computed(() => {
  return tagsStore.list.filter(t => t.name.toLowerCase().includes(newTagName.value.toLowerCase()));
});

// Загрузка/инициализация компонента
const initViewer = async () => {
  const activeTabId = tabsStore.activeTabId;
  if (!activeTabId || !activeTabId.startsWith('viewer-')) return;
  
  const rawId = activeTabId.split('-')[1];
  
  if (rawId === 'new') {
    articleId.value = 'new';
    articleData.value = { ...defaultArticleData, authors: [] };
    articleTags.value = [];
    notes.value = { aims: '', methods: '', results: '', comments: '' };
    noteIds.value = { aims: null, methods: null, results: null, comments: null };
  } else {
    articleId.value = parseInt(rawId);
    
    // Убедимся, что база статей загружена, если зашли по прямой ссылке
    if (articlesStore.list.length === 0) {
      await articlesStore.fetchArticles();
    }
    
    const matched = articlesStore.list.find(a => a.id === articleId.value);
    if (matched) {
      articleData.value = { ...matched, authors: [] };
      // Качаем привязанных авторов
      const authRes = await api.get(`/articles/${articleId.value}/authors/`);
      articleData.value.authors = authRes.data;
    }
    
    // Качаем заметки и теги
    loadNotesAndTags();
  }
};

const loadNotesAndTags = async () => {
  if (isNewMode.value) return;
  try {
    const response = await api.get(`/articles/${articleId.value}/notes/`);
    response.data.forEach(note => {
      if (notes.value[note.field_type] !== undefined) {
        notes.value[note.field_type] = note.content;
        noteIds.value[note.field_type] = note.id;
      }
    });
    const tagsRes = await api.get(`/articles/${articleId.value}/tags/`);
    articleTags.value = tagsRes.data;
  } catch (e) { console.error(e); }
};

// Загрузка PDF файла прямо во вкладке
const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  isUploading.value = true;
  try {
    const uploadResult = await articlesStore.uploadFile(file);
    articleData.value.pdf_path = uploadResult.path;
    
    // Если бэкенд распарсил PDF, предзаполняем форму на лету
    if (uploadResult.extracted_metadata) {
      const meta = uploadResult.extracted_metadata;
      if (meta.title) articleData.value.title = meta.title;
      if (meta.year) articleData.value.year = meta.year;
      if (meta.journal) articleData.value.journal = meta.journal;
      if (meta.doi) articleData.value.doi = meta.doi;
    }
  } catch (error) {
    alert("Ошибка загрузки файла.");
  } finally { isUploading.value = false; }
};

// Синхронизируем ввод фамилии с формой создания нового автора
watch(authorSearchQuery, (newVal) => {
  newAuthorForm.value.last_name = newVal;
});

// Фильтруем глобальный список авторов по введенным буквам
const filteredAuthors = computed(() => {
  if (!authorSearchQuery.value) return [];
  return authorsStore.list.filter(a => 
    a.last_name.toLowerCase().includes(authorSearchQuery.value.toLowerCase())
  );
});

// Добавление автора, который УЖЕ есть в базе данных (клик из списка)
const addExistingAuthor = (author) => {
  if (!articleData.value.authors.find(a => a.id === author.id)) {
    articleData.value.authors.push(author);
  }
  // Сбрасываем поля ввода
  authorSearchQuery.value = '';
  newAuthorForm.value.initials = '';
  isAuthorDropdownOpen.value = false;
};

// Создание АБСОЛЮТНО НОВОГО автора на сервере и добавление его к статье
const handleCreateAndAddAuthor = async () => {
  if (!newAuthorForm.value.last_name || !newAuthorForm.value.initials) {
    alert("Заполните Фамилию и Инициалы для создания нового автора!");
    return;
  }
  try {
    const created = await authorsStore.createAuthor(newAuthorForm.value);
    articleData.value.authors.push(created);
    
    // Очищаем поля
    authorSearchQuery.value = '';
    newAuthorForm.value = { last_name: '', initials: '' };
    isAuthorDropdownOpen.value = false;
  } catch (error) {
    alert("Ошибка при сохранении автора в справочник.");
  }
};

// const createNewAuthor = async () => {
//   if (newAuthorForm.value.last_name && newAuthorForm.value.initials) {
//     const created = await authorsStore.createAuthor(newAuthorForm.value);
//     articleData.value.authors.push(created);
//     newAuthorForm.value = { last_name: '', initials: '' };
//   }
// };

// Логика управления тегами
const addTagToArticle = async (tag) => {
  if (!tag) return;
  if (articleTags.value.find(t => t.id === tag.id)) return;
  
  if (!isNewMode.value) {
    await api.post(`/articles/${articleId.value}/tags/${tag.id}`);
  }
  articleTags.value.push(tag);
  newTagName.value = '';
  isTagDropdownOpen.value = false;
};
const createAndAddTag = async () => {
  if (!newTagName.value) return;
  const res = await api.post('/tags/', { name: newTagName.value, color: newTagColor.value });
  tagsStore.list.push(res.data);
  await addTagToArticle(res.data);
};
const removeTagFromArticle = async (tagId) => {
  if (!isNewMode.value) {
    await api.delete(`/articles/${articleId.value}/tags/${tagId}`);
  }
  articleTags.value = articleTags.value.filter(t => t.id !== tagId);
};

// --- ЕДИНАЯ ФУНКЦИЯ СОХРАНЕНИЯ ВСЕГО КОНТЕКСТА СТАТЬИ ---
const saveEverything = async () => {
  if (!articleData.value.title) {
    alert("Заполните название статьи!");
    return;
  }
  isSaving.value = true;
  try {
    let savedArticleId = articleId.value;
    
    // 1. Сохраняем/обновляем саму статью
    if (isNewMode.value) {
      const res = await api.post('/articles/', articleData.value);
      savedArticleId = res.data.id;
      articlesStore.list.unshift(res.data); // добавляем в общий список
    } else {
      await api.put(`/articles/${articleId.value}`, articleData.value);
    }
    
    // 2. Синхронизируем авторов
    const authorIds = articleData.value.authors.map(a => a.id);
    await api.post(`/articles/${savedArticleId}/sync-authors/`, { author_ids: authorIds });
    
    // 3. Сохраняем теги (если это был режим создания, сохраняем накопленные теги в БД)
    if (isNewMode.value) {
      for (const tag of articleTags.value) {
        await api.post(`/articles/${savedArticleId}/tags/${tag.id}`);
      }
    }
    
    // 4. Сохраняем заметки
    for (const field of Object.keys(notes.value)) {
      const content = notes.value[field];
      const id = noteIds.value[field];
      if (id) {
        await api.put(`/notes/${id}`, { field_type: field, content: content });
      } else if (content.trim() !== '') {
        const res = await api.post(`/articles/${savedArticleId}/notes/`, { field_type: field, content: content });
        noteIds.value[field] = res.data.id;
      }
    }
    
    // Если это была новая статья — трансформируем вкладку в обычный режим просмотра этой статьи
    if (isNewMode.value) {
      const currentTab = tabsStore.openTabs.find(t => t.id === 'viewer-new');
      if (currentTab) {
        currentTab.id = 'viewer-' + savedArticleId;
        currentTab.title = '📖 ' + articleData.value.title.substring(0, 15) + '...';
        tabsStore.activeTabId = 'viewer-' + savedArticleId;
      }
      articleId.value = savedArticleId;
    }
    
    alert("✨ Всё успешно сохранено в базу данных!");
  } catch (error) {
    alert("Ошибка при комплексном сохранении.");
  } finally { isSaving.value = false; }
};

watch(() => tabsStore.activeTabId, () => { initViewer(); });
onMounted(() => {
  authorsStore.fetchAuthors();
  tagsStore.fetchTags();
  initViewer();
});
</script>

<style scoped>
.viewer-wrapper { display: flex; height: calc(100vh - 120px); margin: -20px; background: #ecf0f1; }
.pdf-pane { flex: 1; border-right: 2px solid #bdc3c7; display: flex; flex-direction: column; background: #dfe4ea; }
.pdf-container { flex-grow: 1; width: 100%; }

/* Стильная зона загрузки вместо пустого iframe */
.upload-zone { display: flex; justify-content: center; align-items: center; height: 100%; }
.upload-card { background: white; padding: 40px; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1); max-width: 400px; }
.file-input-hidden { display: none; }
.upload-label-btn { display: inline-block; padding: 10px 20px; background: #3498db; color: white; border-radius: 5px; cursor: pointer; font-weight: bold; margin-top: 15px; }

.info-pane { width: 450px; background: #fff; display: flex; flex-direction: column; box-shadow: -2px 0 10px rgba(0,0,0,0.05); }
.info-header { padding: 15px 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; background: #fdfdfd; }
.save-btn { background: #2ecc71; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; }
.save-btn:disabled { background: #95a5a6; }

/* АККОРДЕОНЫ */
.accordion-container { overflow-y: auto; flex-grow: 1; }
.accordion-section { border-bottom: 1px solid #eee; }
.accordion-header { padding: 15px 20px; background: #f8f9fa; font-weight: bold; color: #2c3e50; cursor: pointer; display: flex; justify-content: space-between; }
.accordion-header:hover { background: #f1f2f6; }
.accordion-content { padding: 20px; background: white; }

.form-group { margin-bottom: 12px; }
.form-group label { display: block; margin-bottom: 4px; font-weight: bold; font-size: 0.85em; color: #34495e; }
.form-group input, .form-group select, .form-group textarea { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
.form-row { display: flex; gap: 10px; }
.half { flex: 1; }
.quarter { flex: 0.5; }
.fields-highlight { background: #f6f8fa; padding: 10px; border-radius: 4px; margin-bottom: 10px; border-left: 3px solid #3498db; }

/* Авторы и теги */
.authors-sub-block { background: #fff5e6; padding: 10px; border-radius: 4px; margin-bottom: 12px; border-left: 3px solid #f39c12; }
.authors-badge-list { display: flex; flex-wrap: wrap; gap: 4px; }
.author-mini-badge { background: #f39c12; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; }
.author-add-btn { padding: 4px 10px; background: #34495e; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.85em; }

.tag-badge { color: white; padding: 4px 10px; border-radius: 15px; margin-right: 5px; display: inline-flex; align-items: center; font-size: 0.85em; font-weight: 500; }
.tag-input-wrapper { display: flex; gap: 5px; position: relative; }
.tag-dropdown { position: absolute; bottom: 100%; left: 0; width: 100%; background: white; border: 1px solid #eee; z-index: 10; padding: 0; margin: 0; list-style: none; box-shadow: 0 -4px 10px rgba(0,0,0,0.1); }
.dropdown-item { padding: 8px; cursor: pointer; }
.dropdown-item:hover { background: #f0f0f0; }
.color-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 5px; }
.color-picker { width: 35px; height: 35px; border: none; cursor: pointer; background: none; padding: 0; }
/* Стили для умного автокомплита авторов */
.author-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  max-height: 180px;
  overflow-y: auto;
  background: white;
  border: 1px solid #ccc;
  border-radius: 4px;
  z-index: 99;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  padding: 0;
  margin: 2px 0 0 0;
  list-style: none;
}
.author-dropdown-item {
  padding: 8px 12px;
  cursor: pointer;
  font-size: 0.9em;
  color: #2c3e50;
}
.author-dropdown-item:hover {
  background-color: #3498db15;
}
.author-dropdown-item.empty {
  color: #7f8c8d;
  background: #fafafa;
  cursor: default;
}
</style>