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
            <MdEditor 
              v-model="draftContent" 
              language="en-US" 
              :preview="false" 
              class="md-editor-custom"
            />
          </div>
          
          <div :class="['bibliography-panel', { 'is-collapsed': !isBibliographyOpen }]">
            <div class="panel-header" @click="isBibliographyOpen = !isBibliographyOpen">
              <span class="panel-title-wrapper">
                <span class="arrow-icon">{{ isBibliographyOpen ? '▼' : '▲' }}</span>
                <h4>📚 Используемая литература проекта ({{ draftsStore.citations.length }})</h4>
              </span>
              <button v-if="isBibliographyOpen" @click.stop="generateBibliography" class="gen-bib-btn">
                📝 Сгенерировать APA список
              </button>
            </div>
            
            <div v-if="isBibliographyOpen" class="panel-content">
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
          <div class="reader-toolbar">
            <span class="opened-pdf-title">📋 {{ currentViewingArticleTitle }}</span>
            <button @click="insertCitationFromActiveView" class="inline-cite-btn">
              ➕ Цитировать в текст
            </button>
          </div>
          
          <div class="pdf-container">
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
const currentViewingArticleId = ref(null);
const currentViewingArticleTitle = ref('');

const isBibliographyOpen = ref(false);

const searchQuery = ref('');
const isDropdownOpen = ref(false);

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

const selectArticleForView = (article) => {
  selectedPdfPath.value = article.pdf_path;
  currentViewingArticleId.value = article.id;
  currentViewingArticleTitle.value = article.title;
  searchQuery.value = article.title;
  isDropdownOpen.value = false;
};

const insertCitationFromActiveView = async () => {
  if (!currentViewingArticleId.value) return;
  
  const citationNumber = draftsStore.citations.length + 1;
  const marker = ``;
  
  await draftsStore.addDraftCitation(serverDraftId.value, currentViewingArticleId.value, marker);
  draftContent.value += ` ${marker} `;
  isBibliographyOpen.value = true;
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

.editor-pane { display: flex; flex-direction: column; height: 100%; transition: width 0.1s; background: white; }
.editor-container { width: 100%; transition: height 0.2s ease; }
.md-editor-custom { height: 100% !important; }

.bibliography-panel { background: #f8f9fa; border-top: 2px solid #ddd; display: flex; flex-direction: column; height: 35%; transition: height 0.2s ease; }
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
.reader-toolbar { background: #fff; padding: 8px 15px; border-bottom: 1px solid #ddd; display: flex; justify-content: space-between; align-items: center; }
.opened-pdf-title { font-weight: bold; font-size: 0.9em; color: #34495e; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 65%; }
.inline-cite-btn { background: #2ecc71; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 0.85em; box-shadow: 0 2px 4px rgba(46,204,113,0.2); transition: 0.2s; }
.inline-cite-btn:hover { background: #27ae60; }
.pdf-container { flex-grow: 1; width: 100%; height: calc(100% - 40px); }
</style>