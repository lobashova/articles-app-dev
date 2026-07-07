<template>
  <div class="articles-container">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2>📚 База статей</h2>
      <button 
        @click="showUploadModal = true"
        style="padding: 10px 20px; background: #2ecc71; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;"
      >
        + Добавить статью
      </button>
    </div>

    <div v-if="showUploadModal" class="modal-overlay">
      <div class="modal-content">
        <h3 style="margin-top: 0;">Добавление нового источника</h3>
        <p style="color: #777; font-size: 0.9em; margin-bottom: 20px;">Заполните метаданные. Поля со звездочкой обязательны.</p>
        
        <form @submit.prevent="submitArticle" class="meta-form">
          <div class="form-group">
            <label>Файл статьи (PDF):</label>
            <input type="file" accept=".pdf" />
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
            <button type="submit" class="save-btn">Сохранить статью</button>
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
        
        <div>
          <button style="padding: 6px 12px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px;">
            Открыть статью
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

// Базовое состояние новой статьи
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
  abstract: ''
};

const newArticle = ref({ ...defaultArticleState });

const closeModal = () => {
  showUploadModal.value = false;
  newArticle.value = { ...defaultArticleState }; // Сброс формы
};

const submitArticle = async () => {
  try {
    await articlesStore.addArticle(newArticle.value);
    closeModal();
  } catch (error) {
    alert('Ошибка при сохранении статьи. Проверьте консоль.');
  }
};

onMounted(() => {
  articlesStore.fetchArticles();
});
</script>

<style scoped>
/* Стили для модального окна и формы */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 10px;
  width: 600px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.form-group {
  margin-bottom: 15px;
}
.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  font-size: 0.9em;
  color: #333;
}
.form-group input, 
.form-group select, 
.form-group textarea {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-sizing: border-box;
  font-family: inherit;
}

.form-row {
  display: flex;
  gap: 15px;
}
.half { flex: 1; }
.quarter { flex: 0.5; }

.dynamic-fields {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 15px;
  border-left: 3px solid #3498db;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.save-btn {
  background: #2ecc71;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}
.save-btn:hover { background: #27ae60; }

.cancel-btn {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
}
.cancel-btn:hover { background: #c0392b; }
</style>