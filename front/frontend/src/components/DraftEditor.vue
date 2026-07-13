<template>
  <div class="draft-wrapper">
    <div v-if="draftsStore.isLoading" class="loading-overlay">
      ⏳ Загрузка черновика и библиографии...
    </div>

    <template v-else>
      <div class="draft-header">
        <input 
          v-model="draftTitle" 
          type="text" 
          placeholder="Название вашей статьи..." 
          class="title-input"
        />
        
        <div class="controls">
          <div class="searchable-select">
            <input 
              v-model="searchQuery"
              @focus="isDropdownOpen = true"
              @blur="hideDropdown"
              type="text"
              placeholder="🔍 Найти статью для цитирования/Split View..."
              class="article-search-input"
            />
            
            <ul v-if="isDropdownOpen && searchQuery" class="dropdown-list">
              <li 
                v-for="article in filteredArticles" 
                :key="article.id"
                @mousedown="handleArticleSelect(article)"
                class="dropdown-item"
              >
                <div class="dropdown-row">
                  <span class="title-text">{{ article.title }}</span>
                  <div class="item-actions">
                    <button @click.prevent.stop="insertCitation(article)" class="cite-action-btn" title="Вставить цитату в текст">➕ Цитата</button>
                    <button @click.prevent.stop="openInSplitView(article)" class="view-action-btn" title="Открыть в Split View">📖 Просмотр</button>
                  </div>
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
          
          <div class="bibliography-panel">
            <div class="panel-header">
              <h4>📚 Используемая литература проекта (Цитируемые источники)</h4>
              <button @click="generateBibliography" class="gen-bib-btn">📝 Сгенерировать APA список</button>
            </div>
            <ul v-if="draftsStore.citations.length > 0" class="citation-links-list">
              <li v-for="cit in draftsStore.citations" :key="cit.id" class="citation-link-item">
                <span class="marker-badge">{{ cit.in_text_marker }}</span> — {{ getArticleTitleById(cit.article_id) }}
              </li>
            </ul>
            <div v-else class="empty-bib">Вы пока не процитировали ни одну статью в этом тексте. Используйте поиск сверху.</div>
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

        <div v-if="isSplitView" class="reader-pane" :style="{ width: (100 - editorWidth) + '%' }">
          <div v-if="selectedPdfPath" class="pdf-container">
            <iframe 
              :src="`https://articles-app.ru/${selectedPdfPath}`" 
              width="100%" 
              height="100%" 
              frameborder="0"
            ></iframe>
          </div>
        </div>

      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { MdEditor } from 'md-editor-v3';
import 'md-editor-v3/lib/style.css';
import api from '../api';
import { useArticlesStore } from '../stores/articles';
import { useTabsStore } from '../stores/tabs';
import { useDraftsStore } from '../stores/drafts';

const articlesStore = useArticlesStore();
const tabsStore = useTabsStore();
const draftsStore = useDraftsStore();

const draftTitle = ref('');
const draftContent = ref('');
const serverDraftId = ref(null);

const isSplitView = ref(false);
const selectedPdfPath = ref('');

// --- ЛОГИКА УМНОГО ПОИСКА И ЦИТИРОВАНИЯ ---
const searchQuery = ref('');
const isDropdownOpen = ref(false);

const filteredArticles = computed(() => {
  const query = searchQuery.value.toLowerCase();
  if (!query) return articlesStore.list;
  return articlesStore.list.filter(a => 
    a.title.toLowerCase().includes(query) || 
    (a.journal && a.journal.toLowerCase().includes(query)) ||
    (a.year && a.year.toString().includes(query))
  );
});

const handleArticleSelect = (article) => {
  searchQuery.value = article.title;
};

// Функция вставки ссылки-маркера в текст и сохранения связи на бэкенде
const insertCitation = async (article) => {
  // Вычисляем порядковый номер для нового маркера
  const citationNumber = draftsStore.citations.length + 1;
  const marker = ``;
  
  // 1. Сохраняем связь в таблицу draft_citations через API
  await draftsStore.addDraftCitation(serverDraftId.value, article.id, marker);
  
  // 2. Вставляем маркер прямо в текст на позицию курсора (или просто в конец для простоты)
  draftContent.value += ` ${marker} `;
  isDropdownOpen.value = false;
  searchQuery.value = '';
};

const openInSplitView = (article) => {
  selectedPdfPath.value = article.pdf_path;
  searchQuery.value = article.title;
  isSplitView.value = true;
  isDropdownOpen.value = false;
};

const getArticleTitleById = (id) => {
  const art = articlesStore.list.find(a => a.id === id);
  return art ? art.title : 'Неизвестный источник';
};

// Функция автоматической сборки списка литературы на базе эндпоинта /apa
const generateBibliography = async () => {
  if (draftsStore.citations.length === 0) {
    alert("Нет цитируемых источников для сборки списка!");
    return;
  }
  
  let bibSection = "\n\n## Список литературы / References\n\n";
  
  try {
    for (const citation of draftsStore.citations) {
      const res = await api.get(`/articles/${citation.article_id}/apa`);
      bibSection += `* ${res.data.citation}\n`;
    }
    
    // Прикрепляем сгенерированный блок в самый конец вашего черновика!
    draftContent.value += bibSection;
    alert("✨ Список литературы по стандарту APA успешно сгенерирован и добавлен в конец статьи!");
    await handleSave(); // Сразу сохраняем изменения
  } catch (error) {
    alert("Ошибка при сборке библиографии");
  }
};

const hideDropdown = () => {
  setTimeout(() => { isDropdownOpen.value = false; }, 250);
};

// --- ЛОГИКА ИЗМЕНЕНИЯ РАЗМЕРА ОКОН (DRAG) ---
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
    searchQuery.value = '';
    editorWidth.value = 50; 
  }
};

// Синхронизация данных драфта при открытии
onMounted(async () => {
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
</script>

<style scoped>
.draft-wrapper { display: flex; flex-direction: column; height: calc(100vh - 120px); margin: -20px; position: relative; }
.loading-overlay { display: flex; justify-content: center; align-items: center; height: 100%; font-size: 1.2em; color: #34495e; background: #fff; }
.draft-header { display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; background: #fff; border-bottom: 1px solid #e0e0e0; }
.title-input { width: 30%; font-size: 1.5em; padding: 5px; border: none; outline: none; background: transparent; font-weight: bold; color: #2c3e50; }
.controls { display: flex; gap: 10px; align-items: center; }

.searchable-select { position: relative; width: 400px; }
.article-search-input { width: 100%; padding: 8px 12px; border-radius: 4px; border: 1px solid #ccc; outline: none; }
.dropdown-list { position: absolute; top: 100%; left: 0; width: 100%; max-height: 250px; overflow-y: auto; background: white; border: 1px solid #ccc; margin: 0; padding: 0; list-style: none; z-index: 100; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.dropdown-item { padding: 10px 12px; border-bottom: 1px solid #eee; }
.dropdown-row { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
.title-text { font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 60%; }
.item-actions { display: flex; gap: 5px; }

.cite-action-btn { background: #2ecc71; color: white; border: none; padding: 4px 8px; border-radius: 3px; cursor: pointer; font-size: 0.85em; }
.view-action-btn { background: #3498db; color: white; border: none; padding: 4px 8px; border-radius: 3px; cursor: pointer; font-size: 0.85em; }

.split-btn { padding: 8px 15px; background: #ecf0f1; color: #2c3e50; border: 1px solid #bdc3c7; border-radius: 4px; cursor: pointer; font-weight: bold; }
.split-btn.active { background: #34495e; color: white; }
.split-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.save-btn { padding: 8px 15px; background: #2ecc71; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }

.workspace { display: flex; flex-grow: 1; overflow: hidden; position: relative; }
.workspace.is-dragging { user-select: none; }
.workspace.is-dragging iframe { pointer-events: none; }

.editor-pane { display: flex; flex-direction: column; height: 100%; transition: width 0.1s; }
.md-editor-custom { flex-grow: 1; min-height: 60% !important; }

/* ПАНЕЛЬ БИБЛИОГРАФИИ */
.bibliography-panel { background: #f8f9fa; border-top: 2px solid #ddd; padding: 15px 20px; overflow-y: auto; height: 35%; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.panel-header h4 { margin: 0; color: #2c3e50; }
.gen-bib-btn { background: #9b59b6; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; }
.citation-links-list { padding-left: 20px; margin: 0; }
.citation-link-item { margin-bottom: 6px; font-size: 0.95em; }
.marker-badge { background: #e67e22; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-family: monospace; }
.empty-bib { color: #7f8c8d; font-size: 0.9em; text-align: center; margin-top: 15px; }

.divider { width: 10px; background-color: #f1f2f6; cursor: col-resize; display: flex; justify-content: center; align-items: center; z-index: 10; border-left: 1px solid #dfe4ea; border-right: 1px solid #dfe4ea; }
.divider-handle { height: 30px; width: 4px; background-color: #a4b0be; border-radius: 2px; }
.reader-pane { height: 100%; background: #ecf0f1; display: flex; flex-direction: column; }
.pdf-container { flex-grow: 1; width: 100%; height: 100%; }
</style>