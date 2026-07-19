<template>
  <div 
    class="viewer-wrapper" 
    ref="viewerWorkspaceRef"
    @mousemove="drag" 
    @mouseup="stopDrag" 
    @mouseleave="stopDrag"
    :class="{ 'is-dragging': isDragging }"
  >
    <div class="pdf-pane" :style="{ width: pdfPaneWidth + '%' }">
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

    <div class="divider" @mousedown="startDrag" title="Потяните, чтобы изменить размер">
      <div class="divider-handle"></div>
    </div>

    <div class="info-pane" :style="{ width: (100 - pdfPaneWidth) + '%' }">
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
              <label class="block-sub-label">👥 Авторы (в порядке цитирования)</label>
              
              <div class="authors-badge-list">
                <span v-for="(auth, idx) in articleData.authors" :key="idx" class="author-mini-badge">
                  {{ auth.last_name }} {{ auth.initials }}
                  <span @click="articleData.authors.splice(idx, 1)" class="remove-auth-x">×</span>
                </span>
              </div>

              <div class="author-input-container">
                <div class="compact-form-row">
                  <input 
                    v-model="authorSearchQuery" 
                    @focus="isAuthorDropdownOpen = true"
                    @blur="hideAuthorDropdown" 
                    placeholder="Начните вводить фамилию..." 
                    class="auth-input-ln"
                  />
                  <input 
                    v-model="newAuthorForm.initials" 
                    placeholder="И. О." 
                    class="auth-input-init"
                  />
                  
                  <button v-if="!isAuthorEditMode" @click.prevent="handleCreateAndAddAuthor" class="auth-compact-btn green-btn" title="Создать нового автора в базе">+</button>
                  <button v-if="isAuthorEditMode" @click.prevent="handleUpdateAuthor" class="auth-compact-btn green-btn" title="Сохранить изменения">✓</button>
                  <button v-if="isAuthorEditMode" @click.prevent="cancelAuthorEdit" class="auth-compact-btn gray-btn" title="Отмена">×</button>
                </div>

                <ul v-if="isAuthorDropdownOpen && authorSearchQuery" class="author-dropdown">
                  <li v-for="a in filteredAuthors" :key="a.id" class="author-dropdown-item" @mousedown="addExistingAuthor(a)">
                    <span class="auth-name-text">👤 {{ a.last_name }} {{ a.initials }}</span>
                    <div class="auth-item-actions">
                      <button @mousedown.stop.prevent="startEditAuthor(a)" class="auth-action-mini-btn" title="Редактировать в базе">✏️</button>
                      <button @mousedown.stop.prevent="handleDeleteAuthor(a.id)" class="auth-action-mini-btn" title="Удалить из базы навсегда">🗑️</button>
                    </div>
                  </li>
                  <li v-if="filteredAuthors.length === 0 && !isAuthorEditMode" class="author-dropdown-item empty">
                    В базе нет автора "{{ authorSearchQuery }}". Нажмите "+", чтобы создать.
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

const isMetadataOpen = ref(true);
const isInfoOpen = ref(false);

const defaultArticleData = {
  type: 'Journal Article', title: '', year: new Date().getFullYear(),
  journal: '', issue: '', pages: '', edition: '', doi: '', web_link: '', abstract: '',
  pdf_path: '', authors: []
};
const articleData = ref({ ...defaultArticleData });

// --- СВОЙСТВА УПРАВЛЕНИЯ АВТОРАМИ ---
const authorSearchQuery = ref('');
const isAuthorDropdownOpen = ref(false);
const newAuthorForm = ref({ last_name: '', initials: '' });
const isAuthorEditMode = ref(false);
const editingAuthorId = ref(null);

watch(authorSearchQuery, (newVal) => {
  if (!isAuthorEditMode.value) {
    newAuthorForm.value.last_name = newVal;
  }
});

const filteredAuthors = computed(() => {
  if (!authorSearchQuery.value) return [];
  return authorsStore.list.filter(a => 
    a.last_name.toLowerCase().includes(authorSearchQuery.value.toLowerCase())
  );
});

const addExistingAuthor = (author) => {
  if (!articleData.value.authors.find(a => a.id === author.id)) {
    articleData.value.authors.push(author);
  }
  authorSearchQuery.value = '';
  newAuthorForm.value.initials = '';
  isAuthorDropdownOpen.value = false;
};

const handleCreateAndAddAuthor = async () => {
  if (!newAuthorForm.value.last_name || !newAuthorForm.value.initials) {
    alert("Заполните Фамилию и Инициалы!");
    return;
  }
  try {
    const created = await authorsStore.createAuthor(newAuthorForm.value);
    articleData.value.authors.push(created);
    authorSearchQuery.value = '';
    newAuthorForm.value = { last_name: '', initials: '' };
    isAuthorDropdownOpen.value = false;
  } catch (error) { alert("Ошибка при создании автора."); }
};

// Редактирование сущности автора в глобальной базе
const startEditAuthor = (author) => {
  isAuthorEditMode.value = true;
  editingAuthorId.value = author.id;
  authorSearchQuery.value = author.last_name;
  newAuthorForm.value.initials = author.initials;
  isAuthorDropdownOpen.value = false;
};
const cancelAuthorEdit = () => {
  isAuthorEditMode.value = false;
  editingAuthorId.value = null;
  authorSearchQuery.value = '';
  newAuthorForm.value = { last_name: '', initials: '' };
};
const handleUpdateAuthor = async () => {
  if (!authorSearchQuery.value || !newAuthorForm.value.initials) return;
  try {
    const updated = await authorsStore.updateAuthor(editingAuthorId.value, authorSearchQuery.value, newAuthorForm.value.initials);
    // Меняем локально у статьи, если он был привязан
    const index = articleData.value.authors.findIndex(a => a.id === editingAuthorId.value);
    if (index !== -1) articleData.value.authors[index] = updated;
    cancelAuthorEdit();
  } catch (e) { alert("Ошибка обновления автора."); }
};
const handleDeleteAuthor = async (id) => {
  if (confirm("Удалить автора из всей системы? Он пропадет из всех карточек источников!")) {
    await authorsStore.deleteAuthor(id);
    articleData.value.authors = articleData.value.authors.filter(a => a.id !== id);
  }
};

// Теги и заметки
const newTagName = ref('');
const newTagColor = ref('#3498db');
const articleTags = ref([]);
const isTagDropdownOpen = ref(false);
const notes = ref({ aims: '', methods: '', results: '', comments: '' });
const noteIds = ref({ aims: null, methods: null, results: null, comments: null });

const filteredTags = computed(() => {
  return tagsStore.list.filter(t => t.name.toLowerCase().includes(newTagName.value.toLowerCase()));
});

const isNewMode = computed(() => articleId.value === 'new' || !articleId.value);

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
    if (articlesStore.list.length === 0) await articlesStore.fetchArticles();
    const matched = articlesStore.list.find(a => a.id === articleId.value);
    if (matched) {
      articleData.value = { ...matched, authors: [] };
      const authRes = await api.get(`/articles/${articleId.value}/authors/`);
      articleData.value.authors = authRes.data;
    }
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

const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  isUploading.value = true;
  try {
    const uploadResult = await articlesStore.uploadFile(file);
    articleData.value.pdf_path = uploadResult.path;
    if (uploadResult.extracted_metadata) {
      const meta = uploadResult.extracted_metadata;
      if (meta.title) articleData.value.title = meta.title;
      if (meta.year) articleData.value.year = meta.year;
      if (meta.journal) articleData.value.journal = meta.journal;
      if (meta.doi) articleData.value.doi = meta.doi;
    }
  } catch (error) { alert("Ошибка загрузки файла."); }
  finally { isUploading.value = false; }
};

const addTagToArticle = async (tag) => {
  if (!tag || articleTags.value.find(t => t.id === tag.id)) return;
  if (!isNewMode.value) await api.post(`/articles/${articleId.value}/tags/${tag.id}`);
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
  if (!isNewMode.value) await api.delete(`/articles/${articleId.value}/tags/${tagId}`);
  articleTags.value = articleTags.value.filter(t => t.id !== tagId);
};

// --- ИЗМЕНЕНИЕ ШИРИНЫ ОКНА (DRAG) ---
const viewerWorkspaceRef = ref(null);
const pdfPaneWidth = ref(60); // По умолчанию читалка занимает 60%
const isDragging = ref(false);

const startDrag = () => { isDragging.value = true; };
const stopDrag = () => { isDragging.value = false; };
const drag = (e) => {
  if (!isDragging.value || !viewerWorkspaceRef.value) return;
  const rect = viewerWorkspaceRef.value.getBoundingClientRect();
  let newWidth = ((e.clientX - rect.left) / rect.width) * 100;
  if (newWidth > 25 && newWidth < 75) {
    pdfPaneWidth.value = newWidth;
  }
};

const saveEverything = async () => {
  if (!articleData.value.title) {
    alert("Заполните название статьи!");
    return;
  }
  isSaving.value = true;
  try {
    let savedArticleId = articleId.value;
    if (isNewMode.value) {
      const res = await api.post('/articles/', articleData.value);
      savedArticleId = res.data.id;
      articlesStore.list.unshift(res.data);
    } else {
      await api.put(`/articles/${articleId.value}`, articleData.value);
    }
    
    const authorIds = articleData.value.authors.map(a => a.id);
    await api.post(`/articles/${savedArticleId}/sync-authors/`, { author_ids: authorIds });
    
    if (isNewMode.value) {
      for (const tag of articleTags.value) {
        await api.post(`/articles/${savedArticleId}/tags/${tag.id}`);
      }
    }
    
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
  } catch (error) { alert("Ошибка при комплексном сохранении."); }
  finally { isSaving.value = false; }
};

watch(() => tabsStore.activeTabId, () => { initViewer(); });
onMounted(() => {
  authorsStore.fetchAuthors();
  tagsStore.fetchTags();
  initViewer();
});

const hideAuthorDropdown = () => {
  // Даем время (200мс) на то, чтобы сработал @mousedown на элементе списка
  setTimeout(() => { isAuthorDropdownOpen.value = false; }, 200);
};
</script>

<style scoped>
.viewer-wrapper { display: flex; height: calc(100vh - 120px); margin: -20px; position: relative; background: #ecf0f1; }
.viewer-wrapper.is-dragging { user-select: none; }
.viewer-wrapper.is-dragging iframe { pointer-events: none; }

.pdf-pane { height: 100%; border-right: 1px solid #bdc3c7; display: flex; flex-direction: column; background: #dfe4ea; transition: width 0.05s linear; }
.pdf-container { flex-grow: 1; width: 100%; height: 100%; }

.upload-zone { display: flex; justify-content: center; align-items: center; height: 100%; }
.upload-card { background: white; padding: 40px; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1); max-width: 400px; }
.file-input-hidden { display: none; }
.upload-label-btn { display: inline-block; padding: 10px 20px; background: #3498db; color: white; border-radius: 5px; cursor: pointer; font-weight: bold; margin-top: 15px; }

/* ПОЛЗУНОК РАЗДЕЛИТЕЛЯ */
.divider { width: 10px; background-color: #f1f2f6; cursor: col-resize; display: flex; justify-content: center; align-items: center; z-index: 10; border-left: 1px solid #dfe4ea; border-right: 1px solid #dfe4ea; }
.divider-handle { height: 30px; width: 4px; background-color: #a4b0be; border-radius: 2px; }

.info-pane { 
  height: 100%; 
  background: #fff; 
  display: flex; 
  flex-direction: column; 
  box-shadow: -2px 0 10px rgba(0,0,0,0.05); 
  transition: width 0.05s linear; 
  overflow-y: auto; /* Добавили прокрутку сюда */
}

.info-header { padding: 15px 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; background: #fdfdfd; }
.save-btn { background: #2ecc71; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; }
.save-btn:disabled { background: #95a5a6; }

.accordion-container { overflow-y: visible; flex-grow: 1; }
.accordion-section { border-bottom: 1px solid #eee; }
.accordion-header { padding: 15px 20px; background: #f8f9fa; font-weight: bold; color: #2c3e50; cursor: pointer; display: flex; justify-content: space-between; user-select: none; }
.accordion-header:hover { background: #f1f2f6; }
.accordion-content { padding: 15px 20px; background: white; }

.form-group { margin-bottom: 12px; }
.form-group label { display: block; margin-bottom: 4px; font-weight: bold; font-size: 0.85em; color: #34495e; }
.form-group input, .form-group select, .form-group textarea { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-family: inherit; }
.form-row { display: flex; gap: 10px; }
.half { flex: 1; }
.quarter { flex: 0.5; }
.fields-highlight { background: #f6f8fa; padding: 10px; border-radius: 4px; margin-bottom: 10px; border-left: 3px solid #3498db; }

/* КОМПАКТНЫЙ И УЛУЧШЕННЫЙ БЛОК АВТОРОВ */
.authors-sub-block { background: #fff5e6; padding: 10px 12px; border-radius: 6px; margin-bottom: 12px; border-left: 4px solid #f39c12; }
.block-sub-label { font-weight: bold; font-size: 0.85em; display: block; margin-bottom: 6px; color: #d35400; }
.authors-badge-list { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 8px; }
.author-mini-badge { background: #f39c12; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8em; font-weight: 500; display: inline-flex; align-items: center; gap: 6px; }
.remove-auth-x { cursor: pointer; font-weight: bold; background: rgba(0,0,0,0.15); width: 14px; height: 14px; display: inline-flex; justify-content: center; align-items: center; border-radius: 50%; font-size: 10px; }
.remove-auth-x:hover { background: rgba(0,0,0,0.3); }

/* КОМПАКТНАЯ СТРОКА ВВОДА */
.compact-form-row { display: flex; gap: 4px; width: 100%; }
.auth-input-ln { flex: 1; padding: 6px 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 0.9em; box-sizing: border-box; }
.auth-input-init { width: 70px; padding: 6px 4px; border: 1px solid #ccc; border-radius: 4px; font-size: 0.9em; text-align: center; box-sizing: border-box; }
.auth-compact-btn { border: none; border-radius: 4px; width: 32px; height: 32px; font-weight: bold; cursor: pointer; color: white; display: flex; justify-content: center; align-items: center; }
.auth-compact-btn.green-btn { background: #2ecc71; }
.auth-compact-btn.gray-btn { background: #95a5a6; }

/* ВЫПАДАЮЩИЙ СПИСОК АВТОРОВ С УПРАВЛЕНИЕМ */
/* УПРАВЛЕНИЕ АВТОРАМИ И ВЫПАДАЮЩИЙ СПИСОК */
.author-input-container { 
  position: relative; 
  z-index: 1000; 
}

.author-dropdown { 
  position: absolute; 
  top: 100%; /* Список открывается вниз */
  left: 0; 
  width: 100%; 
  max-height: 180px; 
  overflow-y: auto; 
  background: white; 
  border: 1px solid #ccc; 
  border-radius: 4px; 
  z-index: 1001; 
  box-shadow: 0 4px 12px rgba(0,0,0,0.15); 
  padding: 0; 
  margin: 4px 0 0 0; 
  list-style: none; 
}

.author-dropdown-item { 
  padding: 8px 12px; 
  cursor: pointer; 
  font-size: 0.9em; 
  color: #2c3e50; 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  border-bottom: 1px solid #f5f5f5; 
}

.author-dropdown-item:hover { 
  background-color: #3498db15; 
}

.author-dropdown-item.empty { 
  color: #7f8c8d; 
  background: #fafafa; 
  cursor: default; 
  padding: 12px; 
}

.auth-name-text { 
  white-space: nowrap; 
  overflow: hidden; 
  text-overflow: ellipsis; 
  max-width: 70%; 
}

.auth-item-actions { 
  display: flex; 
  gap: 6px; 
}

.auth-action-mini-btn { 
  background: none; 
  border: none; 
  cursor: pointer; 
  font-size: 0.85em; 
  padding: 2px; 
  filter: grayscale(1); 
  transition: 0.2s; 
}

.auth-action-mini-btn:hover { 
  filter: grayscale(0); 
  transform: scale(1.15); 
}

/* ТЕГИ */
.tag-badge { color: white; padding: 4px 10px; border-radius: 15px; margin-right: 5px; display: inline-flex; align-items: center; font-size: 0.85em; font-weight: 500; }
.tag-input-wrapper { display: flex; gap: 5px; position: relative; }
.tag-dropdown { position: absolute; bottom: 100%; left: 0; width: 100%; background: white; border: 1px solid #eee; z-index: 10; padding: 0; margin: 0; list-style: none; box-shadow: 0 -4px 10px rgba(0,0,0,0.1); }
.dropdown-item { padding: 8px; cursor: pointer; }
.dropdown-item:hover { background: #f0f0f0; }
.color-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 5px; }
.color-picker { width: 35px; height: 35px; border: none; cursor: pointer; background: none; padding: 0; }
/* Увеличим приоритет выпадающего списка и добавим z-index контейнеру */
.author-input-container { 
  position: relative; 
  z-index: 100; /* Гарантирует, что список будет выше всех полей */
}

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

/* Убедитесь, что контейнер имеет относительное позиционирование */
.author-input-container { 
  position: relative; 
  z-index: 1000; /* Увеличьте z-index до достаточно большого значения */
}

/* Выпадающий список должен быть абсолютно спозиционирован относительно контейнера */
.author-dropdown {
  position: absolute;
  top: 100%; /* Позиция строго под полем ввода */
  left: 0;
  width: 100%;
  max-height: 180px;
  overflow-y: auto;
  background: white;
  border: 1px solid #ccc;
  border-radius: 4px;
  z-index: 1001; /* Должен быть выше z-index iframe */
  box-shadow: 0 4px 10px rgba(0,0,0,0.2);
  list-style: none;
  padding: 0;
  margin: 2px 0 0 0;
}

.accordion-content {
  padding: 15px 20px;
  background: white;
  overflow: visible; /* ЭТО КРИТИЧНО для отображения dropdown */
}
</style>