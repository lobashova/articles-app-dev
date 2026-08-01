<template>
  <div class="draft-wrapper">
    <div v-if="draftsStore.isLoading" class="loading-overlay">
      ⏳ Загрузка черновика и библиографии...
    </div>

    <template v-else>
      <button 
        v-if="!isToolbarOpen" 
        @click="isToolbarOpen = true" 
        class="floating-toggle-btn"
        title="Открыть панель инструментов и заголовок"
      >
        👇 Показать меню
      </button>

      <div v-show="isToolbarOpen" class="draft-header">
        <input 
          v-model="draftTitle" 
          type="text" 
          placeholder="Название вашей статьи..." 
          class="title-input"
        />
        
        <div class="header-actions">
          <div class="controls">
            <button 
              v-if="isSplitView && currentViewingArticleId" 
              @click="insertCitationFromActiveView" 
              class="inline-cite-btn"
              title="Вставить ссылку на открытую статью по курсору"
            >
              ➕ Цитировать статью
            </button>

            <button @click="downloadDraft" class="export-btn" title="Скачать файл на компьютер">
              ⬇️ Скачать
            </button>

            <div class="searchable-select">
              <input 
                v-model="searchQuery"
                @focus="isDropdownOpen = true"
                @blur="hideDropdown"
                type="text"
                placeholder="🔍 Быстрый поиск статьи..."
                class="article-search-input"
              />
              
              <ul v-if="isDropdownOpen && searchQuery" class="dropdown-list">
                <li 
                  v-for="article in filteredArticles" 
                  :key="article.id"
                  @mousedown="selectArticleForView(article)"
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
              :disabled="!selectedPdfPath"
            >
              {{ isSplitView ? 'Закрыть PDF' : '📖 Открыть PDF' }}
            </button>
            
            <button @click="handleSave" class="save-btn" :disabled="draftsStore.isSaving">
              {{ draftsStore.isSaving ? '⏳ Сохранение...' : '💾 Сохранить драфт' }}
            </button>
          </div>

          <button @click="isToolbarOpen = false" class="toolbar-toggle-btn" title="Скрыть панель полностью">
            ✖️
          </button>
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
          
          <div class="editor-container" :style="{ height: isBibliographyOpen ? '65%' : '100%' }">
            <!-- Добавили v-if и сделали динамический editorId, чтобы избежать конфликтов -->
            <MdEditor 
              v-if="serverDraftId"
              v-model="draftContent" 
              language="en-US" 
              :preview="false" 
              :editorId="'draft-editor-' + serverDraftId"
              :scrollAuto="false"
              class="md-editor-custom"
            />
          </div>
          
          <div :class="['bibliography-panel', { 'is-collapsed': !isBibliographyOpen }]">
            
            <!-- ОТКРЫТОЕ СОСТОЯНИЕ (Показываем всю панель) -->
            <template v-if="isBibliographyOpen">
              <div class="panel-header" @click="isBibliographyOpen = false">
                <span class="panel-title-wrapper">
                  <span class="arrow-icon">▼</span>
                  <h4>📚 Используемая литература проекта ({{ draftsStore.citations.length }})</h4>
                </span>
                <button @click.stop="generateBibliography" class="gen-bib-btn">
                  📝 Сгенерировать APA список
                </button>
              </div>
              
              <div class="panel-content">
                <ul v-if="draftsStore.citations.length > 0" class="citation-links-list">
                  <li v-for="cit in draftsStore.citations" :key="cit.id" class="citation-link-item">
                    <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                      <div>
                        <span class="marker-badge">{{ cit.in_text_marker }}</span> — {{ getArticleTitleById(cit.article_id) }}
                      </div>
                      <button 
                        @click.stop="draftsStore.removeDraftCitation(cit.id)" 
                        class="remove-citation-btn"
                        title="Удалить из списка литературы"
                      >
                        ❌
                      </button>
                    </div>
                  </li>
                </ul>
                <div v-else class="empty-bib">Вы пока не процитировали ни одну статью в этом тексте.</div>
              </div>
            </template>

            <!-- ЗАКРЫТОЕ СОСТОЯНИЕ (Маленькая кнопка-вкладка внизу) -->
            <button 
              v-else 
              @click="isBibliographyOpen = true" 
              class="collapsed-bib-btn"
              title="Открыть список литературы"
            >
              📚 Литература ({{ draftsStore.citations.length }}) ▲
            </button>
            
          </div>
        </div>

        <div 
          v-if="isSplitView" 
          class="divider" 
          @mousedown="startDrag"
          title="Потяните, чтобы изменить размер"
        >
          <div class="divider-handle"></div>
        </div>

        <!-- ОБНОВЛЕННАЯ ПРАВАЯ ПАНЕЛЬ (С ПЕРЕКЛЮЧАТЕЛЕМ) -->
        <div v-if="isSplitView" class="reader-pane" :style="{ width: (100 - editorWidth) + '%' }">
          
          <!-- Переключатель видов (PDF / Информация) -->
          <div class="pane-switcher">
            <button @click="isInfoMode = false" :class="['switch-btn', { active: !isInfoMode }]">
              📄 Читать PDF
            </button>
            <button @click="isInfoMode = true" :class="['switch-btn', { active: isInfoMode }]">
              ℹ️ Карточка статьи
            </button>
          </div>
          
          <!-- РЕЖИМ 1: Читалка PDF -->
          <div v-if="!isInfoMode" class="pdf-container">
            <iframe 
              :src="`https://articles-app.ru/${selectedPdfPath}`" 
              width="100%" 
              height="100%" 
              frameborder="0"
            ></iframe>
          </div>

          <!-- РЕЖИМ 2: Информационная карточка -->
          <!-- РЕЖИМ 2: Информационная карточка (Точная копия ArticleViewer) -->
          <div v-else class="info-container">
            
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
              <h3 style="margin: 0; color: #2c3e50; font-size: 1.2em;">{{ currentViewingArticleTitle }}</h3>
              <button @click="saveArticleChanges" class="save-btn" :disabled="isSavingArticle" style="padding: 6px 12px;">
                {{ isSavingArticle ? '⏳...' : '💾 Сохранить' }}
              </button>
            </div>

            <!-- ВАШ КОД АККОРДЕОНА -->
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

              <div class="accordion-section">
                <div class="accordion-header" @click="isQuotesOpen = !isQuotesOpen">
                  <span>💬 Цитаты из статьи</span>
                  <span>{{ isQuotesOpen ? '▼' : '▲' }}</span>
                </div>
                
                <div v-if="isQuotesOpen" class="accordion-content">
                  <div class="new-quote-box">
                    <label>Добавить новую цитату</label>
                    <textarea 
                      v-model="newQuote.highlighted_text" 
                      rows="3" 
                      placeholder="Вставьте скопированный текст из PDF сюда..."
                    ></textarea>
                    <div class="new-quote-actions">
                      <input 
                        type="number" 
                        v-model="newQuote.page_number" 
                        placeholder="Стр. (опц.)" 
                        class="page-input"
                      />
                      <button @click="saveQuote" class="add-quote-btn" :disabled="!newQuote.highlighted_text">
                        ➕ Сохранить цитату
                      </button>
                    </div>
                  </div>

                  <div v-if="quotes.length > 0" class="quotes-list">
                    <div v-for="quote in quotes" :key="quote.id" class="quote-card">
                      <p class="quote-text">«{{ quote.highlighted_text }}»</p>
                      <div class="quote-footer">
                        <span class="quote-page">
                          <span v-if="quote.page_number">📄 Стр. {{ quote.page_number }}</span>
                        </span>
                        <button @click="deleteQuote(quote.id)" class="delete-quote-btn" title="Удалить цитату">🗑️</button>
                      </div>
                    </div>
                  </div>
                  <div v-else class="empty-quotes">
                    У этой статьи пока нет сохраненных цитат.
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>

      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { MdEditor } from 'md-editor-v3';
import 'md-editor-v3/lib/style.css';
import api from '../api';
import { useArticlesStore } from '../stores/articles';
import { useTabsStore } from '../stores/tabs';
import { useDraftsStore } from '../stores/drafts';
import { useAuthorsStore } from '../stores/authors';
import { useTagsStore } from '../stores/tags';

const articlesStore = useArticlesStore();
const tabsStore = useTabsStore();
const draftsStore = useDraftsStore();
const authorsStore = useAuthorsStore();
const tagsStore = useTagsStore();

const draftTitle = ref('');
const draftContent = ref('');
const serverDraftId = ref(null);

const isSplitView = ref(false);
const selectedPdfPath = ref('');
const currentViewingArticleId = ref(null);
const currentViewingArticleTitle = ref('');

const isBibliographyOpen = ref(false);
const isToolbarOpen = ref(true);

const searchQuery = ref('');
const isDropdownOpen = ref(false);

const articleExtra = ref({ tags: [], quotes: [], notes: {} });



const availablePdfArticles = computed(() => {
  return articlesStore.list.filter(article => article.pdf_path);
});

const filteredArticles = computed(() => {
  const query = searchQuery.value.toLowerCase();
  if (!query) return availablePdfArticles.value;
  return availablePdfArticles.value.filter(a => 
    a.title.toLowerCase().includes(query) || 
    (a.journal && a.journal.toLowerCase().includes(query)) ||
    (a.year && a.year.toString().includes(query))
  );
});


const selectArticleForView = async (article) => {
  selectedPdfPath.value = article.pdf_path;
  currentViewingArticleId.value = article.id;
  currentViewingArticleTitle.value = article.title;
  searchQuery.value = article.title;
  isDropdownOpen.value = false;
  
  // Возвращаем режим PDF при открытии новой статьи
  isInfoMode.value = false; 
  
  // Асинхронно подгружаем теги, цитаты и заметки для Карточки
  await loadArticleExtraInfo(article.id);
};

// КНОПКА ЦИТИРОВАНИЯ ВНУТРИ СТАТЬИ (С УМНОЙ ВСТАВКОЙ ПО КУРСОРУ)
const insertCitationFromActiveView = async () => {
  if (!currentViewingArticleId.value) return;
  
  try {
    // 1. Запрашиваем короткий APA-маркер с бэкенда (например, "(Smith, 2023)")
    const res = await api.get(`/articles/${currentViewingArticleId.value}/apa-in-text`);
    const marker = res.data.in_text;
    
    // 2. Сохраняем в БД связь между драфтом и статьей
    await draftsStore.addDraftCitation(serverDraftId.value, currentViewingArticleId.value, marker);
    
    // 3. Ищем текстовое поле редактора на странице
    const textarea = document.querySelector('.md-editor-custom textarea');
    
    if (textarea) {
      // Запоминаем позицию курсора
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      
      // Разрезаем текст на "до курсора" и "после курсора", вставляя маркер между ними
      draftContent.value = draftContent.value.substring(0, start) + ` ${marker} ` + draftContent.value.substring(end);
      
      // Небольшой таймаут, чтобы Vue успел обновить DOM, возвращаем фокус на курсор
      setTimeout(() => {
        textarea.focus();
        // Сдвигаем курсор в конец вставленной цитаты
        textarea.selectionStart = textarea.selectionEnd = start + marker.length + 2; 
      }, 50);
    } else {
      // Запасной вариант (fallback), если курсор не найден
      draftContent.value += ` ${marker} `;
    }
    
    // Разворачиваем нижнюю панель
    isBibliographyOpen.value = true;
  } catch (error) {
    alert("Не удалось сгенерировать внутритекстовую цитату. Убедитесь, что сервер обновлен.");
    console.error(error);
  }
};

const getArticleTitleById = (id) => {
  const art = articlesStore.list.find(a => a.id === id);
  return art ? art.title : 'Неизвестный источник';
};

const generateBibliography = async () => {
  if (draftsStore.citations.length === 0) return;
  let bibSection = "\n\n## Список литературы / References\n\n";
  try {
    for (const citation of draftsStore.citations) {
      const res = await api.get(`/articles/${citation.article_id}/apa`);
      bibSection += `* ${res.data.citation}\n`;
    }
    draftContent.value += bibSection;
    alert("✨ Список литературы APA добавлен в конец черновика!");
    await handleSave();
  } catch (error) {
    alert("Ошибка при сборке библиографии");
  }
};

const hideDropdown = () => {
  setTimeout(() => { isDropdownOpen.value = false; }, 200);
};

// --- LOGIC DRAG ---
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

const toggleSplitView = () => {
  isSplitView.value = !isSplitView.value;
  if (!isSplitView.value) {
    selectedPdfPath.value = ''; 
    currentViewingArticleId.value = null;
    currentViewingArticleTitle.value = '';
    searchQuery.value = '';
    editorWidth.value = 50; 
  }
};

// --- СОСТОЯНИЕ КАРТОЧКИ СТАТЬИ ---
const isInfoMode = ref(false); 
const isSavingArticle = ref(false);

const isMetadataOpen = ref(false);
const isInfoOpen = ref(true);
const isQuotesOpen = ref(false);

const articleData = ref({ type: 'Journal Article', title: '', year: null, journal: '', issue: '', pages: '', edition: '', doi: '', web_link: '', abstract: '', authors: [] });
const articleTags = ref([]);
const notes = ref({ aims: '', methods: '', results: '', comments: '' });
const noteIds = ref({ aims: null, methods: null, results: null, comments: null });
const quotes = ref([]);
const newQuote = ref({ highlighted_text: '', page_number: null });

// Теги
const newTagName = ref('');
const newTagColor = ref('#3498db');
const isTagDropdownOpen = ref(false);
const filteredTags = computed(() => tagsStore.list.filter(t => t.name.toLowerCase().includes(newTagName.value.toLowerCase())));

// Авторы
const authorSearchQuery = ref('');
const isAuthorDropdownOpen = ref(false);
const newAuthorForm = ref({ last_name: '', initials: '' });
const isAuthorEditMode = ref(false);
const editingAuthorId = ref(null);

watch(authorSearchQuery, (newVal) => {
  if (!isAuthorEditMode.value) newAuthorForm.value.last_name = newVal;
});
const filteredAuthors = computed(() => {
  if (!authorSearchQuery.value) return [];
  return authorsStore.list.filter(a => a.last_name.toLowerCase().includes(authorSearchQuery.value.toLowerCase()));
});

// --- ФУНКЦИИ КАРТОЧКИ СТАТЬИ ---

// Загрузка данных при выборе статьи
const loadArticleExtraInfo = async (id) => {
  try {
    const art = articlesStore.list.find(a => a.id === id);
    if (art) articleData.value = { ...art, authors: [] };

    const [authorsRes, tagsRes, quotesRes, notesRes] = await Promise.all([
      api.get(`/articles/${id}/authors/`),
      api.get(`/articles/${id}/tags/`),
      api.get(`/articles/${id}/quotes/`),
      api.get(`/articles/${id}/notes/`)
    ]);
    
    articleData.value.authors = authorsRes.data;
    articleTags.value = tagsRes.data;
    quotes.value = quotesRes.data;
    
    notes.value = { aims: '', methods: '', results: '', comments: '' };
    noteIds.value = { aims: null, methods: null, results: null, comments: null };
    notesRes.data.forEach(note => {
      notes.value[note.field_type] = note.content;
      noteIds.value[note.field_type] = note.id;
    });
  } catch (e) { console.error("Ошибка загрузки:", e); }
};

// Сохранение изменений статьи
const saveArticleChanges = async () => {
  if (!currentViewingArticleId.value) return;
  isSavingArticle.value = true;
  try {
    const id = currentViewingArticleId.value;
    await api.put(`/articles/${id}`, articleData.value);
    
    const authorIds = articleData.value.authors.map(a => a.id);
    await api.post(`/articles/${id}/sync-authors/`, { author_ids: authorIds });
    
    for (const field of Object.keys(notes.value)) {
      const content = notes.value[field];
      const noteId = noteIds.value[field];
      if (noteId) {
        await api.put(`/notes/${noteId}`, { field_type: field, content: content });
      } else if (content.trim() !== '') {
        const res = await api.post(`/articles/${id}/notes/`, { field_type: field, content: content });
        noteIds.value[field] = res.data.id;
      }
    }
    
    // Обновляем список статей в сторе, чтобы изменения отобразились сразу
    const index = articlesStore.list.findIndex(a => a.id === id);
    if (index !== -1) articlesStore.list[index] = { ...articlesStore.list[index], ...articleData.value };
    currentViewingArticleTitle.value = articleData.value.title;
    
    alert("Изменения статьи успешно сохранены!");
  } catch (error) { alert("Ошибка при сохранении статьи."); }
  finally { isSavingArticle.value = false; }
};

// Управление авторами
const hideAuthorDropdown = () => { setTimeout(() => { isAuthorDropdownOpen.value = false; }, 200); };
const addExistingAuthor = (author) => {
  if (!articleData.value.authors.find(a => a.id === author.id)) articleData.value.authors.push(author);
  authorSearchQuery.value = ''; newAuthorForm.value.initials = ''; isAuthorDropdownOpen.value = false;
};
const handleCreateAndAddAuthor = async () => {
  if (!newAuthorForm.value.last_name || !newAuthorForm.value.initials) return;
  try {
    const created = await authorsStore.createAuthor(newAuthorForm.value);
    articleData.value.authors.push(created);
    authorSearchQuery.value = ''; newAuthorForm.value = { last_name: '', initials: '' }; isAuthorDropdownOpen.value = false;
  } catch (error) { alert("Ошибка при создании автора."); }
};
const startEditAuthor = (author) => {
  isAuthorEditMode.value = true; editingAuthorId.value = author.id;
  authorSearchQuery.value = author.last_name; newAuthorForm.value.initials = author.initials; isAuthorDropdownOpen.value = false;
};
const cancelAuthorEdit = () => {
  isAuthorEditMode.value = false; editingAuthorId.value = null; authorSearchQuery.value = ''; newAuthorForm.value = { last_name: '', initials: '' };
};
const handleUpdateAuthor = async () => {
  if (!authorSearchQuery.value || !newAuthorForm.value.initials) return;
  try {
    const updated = await authorsStore.updateAuthor(editingAuthorId.value, authorSearchQuery.value, newAuthorForm.value.initials);
    const index = articleData.value.authors.findIndex(a => a.id === editingAuthorId.value);
    if (index !== -1) articleData.value.authors[index] = updated;
    cancelAuthorEdit();
  } catch (e) { alert("Ошибка обновления автора."); }
};
const handleDeleteAuthor = async (id) => {
  if (confirm("Удалить автора из всей системы?")) {
    await authorsStore.deleteAuthor(id);
    articleData.value.authors = articleData.value.authors.filter(a => a.id !== id);
  }
};

// Управление тегами
const addTagToArticle = async (tag) => {
  if (!tag || articleTags.value.find(t => t.id === tag.id)) return;
  await api.post(`/articles/${currentViewingArticleId.value}/tags/${tag.id}`);
  articleTags.value.push(tag); newTagName.value = ''; isTagDropdownOpen.value = false;
};
const createAndAddTag = async () => {
  if (!newTagName.value) return;
  const res = await api.post('/tags/', { name: newTagName.value, color: newTagColor.value });
  tagsStore.list.push(res.data);
  await addTagToArticle(res.data);
};
const removeTagFromArticle = async (tagId) => {
  await api.delete(`/articles/${currentViewingArticleId.value}/tags/${tagId}`);
  articleTags.value = articleTags.value.filter(t => t.id !== tagId);
};

// Управление цитатами
const saveQuote = async () => {
  if (!newQuote.value.highlighted_text) return;
  try {
    const payload = { article_id: currentViewingArticleId.value, highlighted_text: newQuote.value.highlighted_text, page_number: newQuote.value.page_number || null };
    const res = await api.post('/quotes/', payload);
    quotes.value.unshift(res.data);
    newQuote.value.highlighted_text = ''; newQuote.value.page_number = null;
  } catch (error) { alert("Ошибка при сохранении цитаты."); }
};
const deleteQuote = async (id) => {
  if (!confirm("Удалить цитату?")) return;
  try { await api.delete(`/quotes/${id}`); quotes.value = quotes.value.filter(q => q.id !== id); } catch (error) {}
};

onMounted(async () => {
  if (authorsStore.list.length === 0) authorsStore.fetchAuthors();
  if (tagsStore.list.length === 0) tagsStore.fetchTags();
  if (articlesStore.list.length === 0) {
    articlesStore.fetchArticles();
  }
  const activeTabId = tabsStore.activeTabId;
  if (activeTabId && activeTabId.startsWith('draft-')) {
    const projectId = activeTabId.split('-')[1];
    const data = await draftsStore.fetchDraftForProject(projectId);
    if (data) {
      serverDraftId.value = data.id;
      draftTitle.value = data.title;
      draftContent.value = data.content || '';
    }
  }
});

const handleSave = async () => {
  if (serverDraftId.value) {
    await draftsStore.saveDraft(serverDraftId.value, draftTitle.value, draftContent.value);
    const activeTab = tabsStore.openTabs.find(t => t.id === tabsStore.activeTabId);
    if (activeTab) {
      activeTab.title = '📝 Драфт: ' + draftTitle.value;
    }
  }
};

// --- ЭКСПОРТ ЧЕРНОВИКА (СКАЧИВАНИЕ ФАЙЛА) ---
const downloadDraft = () => {
  if (!draftContent.value) {
    alert("Черновик пуст! Нечего скачивать.");
    return;
  }

  // Создаем "виртуальный" файл из текста
  const blob = new Blob([draftContent.value], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  
  // Создаем невидимую ссылку и "кликаем" по ней
  const a = document.createElement('a');
  a.href = url;
  
  // Очищаем название от спецсимволов для безопасного имени файла
  const safeTitle = (draftTitle.value || 'draft').replace(/[^a-z0-9а-яё]/gi, '_').toLowerCase();
  a.download = `${safeTitle}.md`; // Формат файла
  
  document.body.appendChild(a);
  a.click();
  
  // Убираем за собой
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};
</script>

<style scoped>
.draft-wrapper { display: flex; flex-direction: column; height: calc(100vh - 120px); margin: -20px; position: relative; }
.loading-overlay { display: flex; justify-content: center; align-items: center; height: 100%; font-size: 1.2em; color: #34495e; background: #fff; }

.draft-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 15px 20px; 
  background: #fff; 
  border-bottom: 1px solid #e0e0e0; 
}
.title-input { width: 30%; font-size: 1.5em; padding: 5px; border: none; outline: none; background: transparent; font-weight: bold; color: #2c3e50; }

/* ИСПРАВЛЕННЫЕ СТИЛИ КОНТРОЛЛЕРОВ (ДОБАВИЛИ GAP ДЛЯ ИСКЛЮЧЕНИЯ НАЛОЖЕНИЯ) */
.controls { 
  display: flex; 
  gap: 15px; /* Задали безопасное расстояние между поиском и кнопками */
  align-items: center; 
}

.searchable-select { position: relative; width: 350px; }
.article-search-input { width: 100%; padding: 8px 12px; border-radius: 4px; border: 1px solid #ccc; outline: none; box-sizing: border-box; }
.dropdown-list { position: absolute; top: 100%; left: 0; width: 100%; max-height: 250px; overflow-y: auto; background: white; border: 1px solid #ccc; margin: 0; padding: 0; list-style: none; z-index: 100; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.dropdown-item { padding: 10px 12px; border-bottom: 1px solid #eee; cursor: pointer; }
.dropdown-item:hover { background: #f8f9fa; }

.split-btn { padding: 8px 15px; background: #ecf0f1; color: #2c3e50; border: 1px solid #bdc3c7; border-radius: 4px; cursor: pointer; font-weight: bold; white-space: nowrap; }
.split-btn.active { background: #34495e; color: white; }
.split-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.save-btn { padding: 8px 15px; background: #2ecc71; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; white-space: nowrap; }

.workspace { display: flex; flex-grow: 1; overflow: hidden; position: relative; }
.workspace.is-dragging { user-select: none; }
.workspace.is-dragging iframe { pointer-events: none; }

.editor-container { width: 100%; transition: height 0.2s ease; }
.md-editor-custom { height: 100% !important; }


.bibliography-panel.is-collapsed { height: 45px; overflow: hidden; }
.panel-header { display: flex; justify-content: space-between; align-items: center; padding: 10px 20px; background: #f1f2f6; cursor: pointer; user-select: none; border-bottom: 1px solid #ddd; }
.panel-title-wrapper { display: flex; align-items: center; gap: 10px; }
.panel-header h4 { margin: 0; color: #2c3e50; }
.arrow-icon { font-size: 0.8em; color: #7f8c8d; transition: transform 0.2s; }
.gen-bib-btn { background: #9b59b6; color: white; border: none; padding: 5px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 0.85em; }
.panel-content { padding: 15px 20px; overflow-y: auto; flex-grow: 1; }
.citation-links-list { padding-left: 20px; margin: 0; list-style-type: none; }
.citation-link-item { margin-bottom: 8px; font-size: 0.95em; display: flex; align-items: center; }
.marker-badge { background: #e67e22; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-family: monospace; }
.empty-bib { color: #7f8c8d; font-size: 0.9em; text-align: center; margin-top: 10px; }

/* СТИЛИ ДЛЯ КНОПКИ УДАЛЕНИЯ ЦИТАТЫ */
.remove-citation-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.85em;
  padding: 2px 6px;
  border-radius: 50%;
  transition: background-color 0.2s;
}
.remove-citation-btn:hover {
  background-color: #ffeaea;
}

.divider { width: 10px; background-color: #f1f2f6; cursor: col-resize; display: flex; justify-content: center; align-items: center; z-index: 10; border-left: 1px solid #dfe4ea; border-right: 1px solid #dfe4ea; }
.divider-handle { height: 30px; width: 4px; background-color: #a4b0be; border-radius: 2px; }
.reader-pane { height: 100%; background: #ecf0f1; display: flex; flex-direction: column; }
.inline-cite-btn { background: #2ecc71; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 0.85em; box-shadow: 0 2px 4px rgba(46,204,113,0.2); transition: 0.2s; }
.inline-cite-btn:hover { background: #27ae60; }

.export-btn { 
  padding: 8px 15px; 
  background: #34495e; 
  color: white; 
  border: none; 
  border-radius: 4px; 
  cursor: pointer; 
  font-weight: bold; 
  white-space: nowrap;
  transition: background 0.2s;
}
.export-btn:hover {
  background: #2c3e50;
}

/* Обертка для кнопок в шапке */
.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

/* Кнопка-переключатель видимости панели */
.toolbar-toggle-btn {
  background: #f1f2f6;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 6px 12px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: bold;
  color: #2c3e50;
  transition: 0.2s;
  white-space: nowrap;
}
.toolbar-toggle-btn:hover {
  background: #dfe4ea;
}

/* Обновленная кнопка цитирования (сделал её синей, чтобы отличалась от сохранения) */
.inline-cite-btn { 
  background: #3498db; 
  color: white; 
  border: none; 
  padding: 8px 15px; 
  border-radius: 4px; 
  cursor: pointer; 
  font-weight: bold; 
  font-size: 0.9em; 
  transition: 0.2s; 
  white-space: nowrap;
}
.inline-cite-btn:hover { background: #2980b9; }

/* PDF контейнер теперь на всю высоту без вычетов */
.pdf-container { 
  flex-grow: 1; 
  width: 100%; 
  height: 100%; 
}

/* ПЛАВАЮЩАЯ КНОПКА ВОЗВРАТА МЕНЮ */
.floating-toggle-btn {
  position: absolute;
  top: 10px;
  right: 20px;
  z-index: 1000;
  background: rgba(52, 73, 94, 0.8);
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 20px;
  cursor: pointer;
  font-weight: bold;
  font-size: 0.85em;
  backdrop-filter: blur(5px);
  transition: all 0.2s ease;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.floating-toggle-btn:hover {
  background: rgba(44, 62, 80, 1);
  transform: translateY(2px);
}

/* Добавляем position: relative, чтобы вкладка позиционировалась строго внутри редактора */
.editor-pane { display: flex; flex-direction: column; height: 100%; transition: width 0.1s; background: white; position: relative; }

/* Основная панель */
.bibliography-panel { background: #f8f9fa; border-top: 2px solid #ddd; display: flex; flex-direction: column; height: 35%; transition: height 0.2s ease; z-index: 10; }

/* В закрытом состоянии панель схлопывается до 0 пикселей */
.bibliography-panel.is-collapsed { 
  height: 0; 
  border-top: none; 
  overflow: visible; /* Разрешаем кнопке "торчать" из нулевой высоты */
}

/* Стили для маленькой кнопки-язычка внизу */
.collapsed-bib-btn {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  background: #f8f9fa;
  color: #34495e;
  border: 1px solid #ddd;
  border-bottom: none;
  padding: 4px 20px;
  border-radius: 8px 8px 0 0; /* Делает форму вкладки (закруглена только сверху) */
  cursor: pointer;
  font-size: 0.85em;
  font-weight: bold;
  box-shadow: 0 -2px 5px rgba(0,0,0,0.05);
  z-index: 100;
  transition: all 0.2s ease;
}

.collapsed-bib-btn:hover {
  background: #eef2f5;
  padding-bottom: 8px; /* Прикольный эффект: вкладка чуть "вытягивается" вверх при наведении */
}

/* ПЕРЕКЛЮЧАТЕЛЬ PDF / КАРТОЧКА */
.pane-switcher {
  display: flex;
  background: #f1f2f6;
  border-bottom: 1px solid #ddd;
}
.switch-btn {
  flex: 1;
  padding: 10px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-weight: bold;
  color: #7f8c8d;
  transition: all 0.2s ease;
  font-size: 0.9em;
}
.switch-btn:hover {
  background: #eef2f5;
}
.switch-btn.active {
  background: #fff;
  color: #3498db;
  border-bottom: 3px solid #3498db;
}

/* КОНТЕЙНЕР КАРТОЧКИ СТАТЬИ */
.info-container {
  flex-grow: 1;
  background: #fff;
  padding: 25px;
  overflow-y: auto;
}
.info-title {
  margin-top: 0;
  color: #2c3e50;
  border-bottom: 2px solid #ecf0f1;
  padding-bottom: 12px;
  margin-bottom: 20px;
  font-size: 1.3em;
}
.info-block {
  margin-bottom: 25px;
}
.info-block h4 {
  margin: 0 0 12px 0;
  color: #34495e;
  font-size: 0.95em;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* ТЕГИ */
.tags-list { display: flex; flex-wrap: wrap; gap: 8px; }
.tag-badge {
  color: white;
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 0.85em;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* ЦИТАТЫ */
.quotes-list { display: flex; flex-direction: column; gap: 12px; }
.quote-card {
  background: #f8f9fa;
  border-left: 4px solid #9b59b6;
  padding: 12px;
  border-radius: 0 6px 6px 0;
}
.quote-text {
  font-style: italic;
  margin: 0 0 8px 0;
  font-size: 0.95em;
  line-height: 1.5;
  color: #2c3e50;
}
.quote-page { font-size: 0.8em; color: #7f8c8d; font-weight: bold; }

/* ЗАМЕТКИ */
.note-item {
  background: #f1f2f6;
  padding: 10px 12px;
  border-radius: 6px;
  font-size: 0.9em;
  margin-bottom: 10px;
  line-height: 1.5;
  color: #2c3e50;
}
.note-item strong { color: #e67e22; margin-right: 5px; }
.empty-text { color: #95a5a6; font-size: 0.9em; font-style: italic; }

/* КОМПАКТНЫЙ И УЛУЧШЕННЫЙ БЛОК АВТОРОВ */
.authors-sub-block { background: #fff5e6; padding: 10px 12px; border-radius: 6px; margin-bottom: 12px; border-left: 4px solid #f39c12; }
.block-sub-label { font-weight: bold; font-size: 0.85em; display: block; margin-bottom: 6px; color: #d35400; }
.authors-badge-list { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 8px; }
.author-mini-badge { background: #f39c12; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8em; font-weight: 500; display: inline-flex; align-items: center; gap: 6px; }
.remove-auth-x { cursor: pointer; font-weight: bold; background: rgba(0,0,0,0.15); width: 14px; height: 14px; display: inline-flex; justify-content: center; align-items: center; border-radius: 50%; font-size: 10px; }
.remove-auth-x:hover { background: rgba(0,0,0,0.3); }

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

/* --- ЦИТАТЫ --- */
.new-quote-box {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  border: 1px dashed #bdc3c7;
  margin-bottom: 20px;
}
.new-quote-box label {
  font-size: 0.85em;
  color: #7f8c8d;
  margin-bottom: 8px;
  display: block;
}
.new-quote-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}
.page-input {
  width: 90px;
  padding: 6px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.add-quote-btn {
  flex-grow: 1;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}
.add-quote-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.quotes-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.quote-card {
  background: #fff;
  border-left: 4px solid #9b59b6;
  padding: 12px;
  border-radius: 0 6px 6px 0;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}
.quote-text {
  font-style: italic;
  color: #2c3e50;
  margin: 0 0 10px 0;
  font-size: 0.95em;
  line-height: 1.4;
}
.quote-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #f1f2f6;
  padding-top: 8px;
}
.quote-page {
  font-size: 0.8em;
  color: #7f8c8d;
  font-weight: bold;
}
.delete-quote-btn {
  background: none;
  border: none;
  cursor: pointer;
  filter: grayscale(1);
  opacity: 0.6;
}
.delete-quote-btn:hover {
  filter: grayscale(0);
  opacity: 1;
  transform: scale(1.1);
}
.empty-quotes {
  text-align: center;
  color: #95a5a6;
  font-style: italic;
  padding: 20px;
}

.accordion-container { overflow-y: visible; flex-grow: 1; }
.accordion-section { border-bottom: 1px solid #eee; }
.accordion-header { padding: 15px 20px; background: #f8f9fa; font-weight: bold; color: #2c3e50; cursor: pointer; display: flex; justify-content: space-between; user-select: none; }
.accordion-header:hover { background: #f1f2f6; }
.accordion-content { padding: 15px 20px; background: white; }

/* --- СТИЛИ ФОРМ И ПОЛЕЙ ВВОДА (Восстановленные) --- */
.form-group { margin-bottom: 12px; }
.form-group label { display: block; margin-bottom: 4px; font-weight: bold; font-size: 0.85em; color: #34495e; }
.form-group input, .form-group select, .form-group textarea { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-family: inherit; }
.form-row { display: flex; gap: 10px; }
.half { flex: 1; }
.quarter { flex: 0.5; }
.fields-highlight { background: #f6f8fa; padding: 10px; border-radius: 4px; margin-bottom: 10px; border-left: 3px solid #3498db; }

</style>