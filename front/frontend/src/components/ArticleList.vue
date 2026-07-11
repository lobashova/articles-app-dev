<template>
  <div class="articles-container">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2>📚 База статей</h2>
      <button 
        @click="openCreateModal"
        style="padding: 10px 20px; background: #2ecc71; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;"
      >
        + Добавить статью
      </button>
    </div>

    <div v-if="showUploadModal" class="modal-overlay">
      <div class="modal-content">
        <h3 style="margin-top: 0;">{{ isEditMode ? 'Редактирование метаданных' : 'Добавление нового источника' }}</h3>
        
        <form @submit.prevent="submitArticle" class="meta-form">
          <div v-if="!isEditMode" class="form-group">
            <label>Файл статьи (PDF):</label>
            <input type="file" accept=".pdf" @change="handleFileUpload" />
            <div v-if="isUploading" style="color: #2980b9; font-size: 0.9em; margin-top: 5px;">
              ⏳ Анализируем PDF и ищем метаданные...
            </div>
          </div>

          <div class="form-row">
            <div class="form-group half">
              <label>Тип источника (APA) *</label>
              <select v-model="newArticle.type" required>
                <option value="Journal Article">Журнальная статья</option>
                <option value="Book">Книга</option>
                <option value="Conference Paper">Материалы конференции</option>
                <option value="Website">Веб-сайт</option>
              </select>
            </div>
            <div class="form-group half">
              <label>Год издания *</label>
              <input v-model="newArticle.year" type="number" required />
            </div>
          </div>

          <div class="form-group">
            <label>Название статьи/книги *</label>
            <input v-model="newArticle.title" type="text" required placeholder="Введите полное название..." />
          </div>

          <div v-if="newArticle.type === 'Journal Article'" class="dynamic-fields">
            <div class="form-row">
              <div class="form-group half">
                <label>Название журнала</label>
                <input v-model="newArticle.journal" type="text" />
              </div>
              <div class="form-group quarter">
                <label>Выпуск (Issue)</label>
                <input v-model="newArticle.issue" type="text" />
              </div>
              <div class="form-group quarter">
                <label>Страницы</label>
                <input v-model="newArticle.pages" type="text" placeholder="10-25" />
              </div>
            </div>
          </div>

          <div v-if="newArticle.type === 'Book'" class="dynamic-fields">
            <div class="form-group">
              <label>Издание (Edition)</label>
              <input v-model="newArticle.edition" type="text" placeholder="например, 2nd ed." />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group half">
              <label>DOI</label>
              <input v-model="newArticle.doi" type="text" placeholder="10.1000/xyz123" />
            </div>
            <div class="form-group half">
              <label>Web Ссылка</label>
              <input v-model="newArticle.web_link" type="url" placeholder="https://..." />
            </div>
          </div>

          <div class="form-group">
            <label>Аннотация (Abstract)</label>
            <textarea v-model="newArticle.abstract" rows="3" placeholder="Скопируйте абстракт сюда..."></textarea>
          </div>

          <div class="modal-actions">
            <button type="submit" class="save-btn">Сохранить</button>
            <button type="button" @click="closeModal" class="cancel-btn">Отмена</button>
          </div>
        </form>
      </div>
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
            <span style="background: #eee; padding: 2px 6px; border-radius: 4px; margin-right: 10px; font-weight: bold;">{{ article.type }}</span>
            Год: {{ article.year || '—' }} | Журнал: {{ article.journal || '—' }}
          </p>
        </div>
        
        <div style="display: flex; gap: 8px;">
          <button 
            @click="openArticleFile(article.pdf_path)"
            :disabled="!article.pdf_path"
            :style="{ background: article.pdf_path ? '#3498db' : '#95a5a6' }"
            style="padding: 6px 12px; color: white; border: none; border-radius: 4px; cursor: pointer;"
          >
            {{ article.pdf_path ? 'Открыть PDF' : 'Нет файла' }}
          </button>
          
          <button 
            @click="openEditModal(article)"
            style="padding: 6px 12px; background: #f39c12; color: white; border: none; border-radius: 4px; cursor: pointer;"
          >
            Изменить
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
      В вашей базе пока нет статей. Загрузите первый источник!
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useArticlesStore } from '../stores/articles';

const articlesStore = useArticlesStore();
const showUploadModal = ref(false);
const isUploading = ref(false);

// Флаги для режима редактирования
const isEditMode = ref(false);
const editingArticleId = ref(null);

const defaultArticleState = {
  type: 'Journal Article',
  title: '',
  year: new Date().getFullYear(),
  journal: '',
  issue: '',
  edition: '',
  pages: '',
  doi: '',
  web_link: '',
  abstract: '',
  pdf_path: ''
};

const newArticle = ref({ ...defaultArticleState });
const selectedFile = ref(null);

// Открытие для создания
const openCreateModal = () => {
  isEditMode.value = false;
  editingArticleId.value = null;
  newArticle.value = { ...defaultArticleState };
  showUploadModal.value = true;
};

// Открытие для редактирования
const openEditModal = (article) => {
  isEditMode.value = true;
  editingArticleId.value = article.id;
  // Копируем текущие данные статьи в форму
  newArticle.value = { ...article };
  showUploadModal.value = true;
};

const closeModal = () => {
  showUploadModal.value = false;
  newArticle.value = { ...defaultArticleState };
  selectedFile.value = null;
  isEditMode.value = false;
  editingArticleId.value = null;
};

const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  isUploading.value = true;
  try {
    const uploadResult = await articlesStore.uploadFile(file);
    newArticle.value.pdf_path = uploadResult.path;
    
    if (uploadResult.extracted_metadata) {
      const meta = uploadResult.extracted_metadata;
      if (meta.title) newArticle.value.title = meta.title;
      if (meta.year) newArticle.value.year = meta.year;
      if (meta.journal) newArticle.value.journal = meta.journal;
      if (meta.doi) newArticle.value.doi = meta.doi;
      alert("✨ Метаданные успешно извлечены из PDF!");
    }
  } catch (error) {
    alert("Ошибка при загрузке или анализе файла.");
  } finally {
    isUploading.value = false;
  }
};

const submitArticle = async () => {
  try {
    if (isEditMode.value) {
      // Если мы редактируем — вызываем PUT эндпоинт
      await articlesStore.updateArticle(editingArticleId.value, newArticle.value);
    } else {
      // Если создаем новую — вызывем POST эндпоинт
      await articlesStore.addArticle(newArticle.value);
    }
    closeModal();
  } catch (error) {
    alert('Ошибка при сохранении изменений.');
  }
};

// Функция открытия PDF файла в новой вкладке браузера
const openArticleFile = (pdfPath) => {
  if (!pdfPath) return;
  // Формируем прямую ссылку на примонтированную бэкендом папку
  const fileUrl = `https://articles-app.ru/${pdfPath}`;
  window.open(fileUrl, '_blank');
};

onMounted(() => {
  articlesStore.fetchArticles();
});
</script>

<style scoped>
/* Стили остаются прежними */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex; justify-content: center; align-items: center; z-index: 1000;
}
.modal-content {
  background: white; padding: 30px; border-radius: 10px;
  width: 600px; max-width: 90%; max-height: 90vh; overflow-y: auto;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.form-group { margin-bottom: 15px; }
.form-group label { display: block; margin-bottom: 5px; font-weight: bold; font-size: 0.9em; color: #333; }
.form-group input, .form-group select, .form-group textarea {
  width: 100%; padding: 8px 10px; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box;
}
.form-row { display: flex; gap: 15px; }
.half { flex: 1; }
.quarter { flex: 0.5; }
.dynamic-fields { background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 15px; border-left: 3px solid #3498db; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.save-btn { background: #2ecc71; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; }
.cancel-btn { background: #e74c3c; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
</style>