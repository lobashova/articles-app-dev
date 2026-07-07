<template>
  <div class="projects-container">
    <h2>Мои научные проекты</h2>
    
    <div style="background: #f5f5f5; padding: 15px; margin-bottom: 20px; border-radius: 8px;">
      <h3>Создать новый проект</h3>
      <form @submit.prevent="submitProject">
        <div style="margin-bottom: 10px;">
          <input 
            v-model="newProject.name" 
            type="text" 
            placeholder="Название проекта (например, 'Анализ данных 2026')" 
            required 
            style="width: 100%; padding: 8px;"
          />
        </div>
        <div style="margin-bottom: 10px;">
          <textarea 
            v-model="newProject.description" 
            placeholder="Краткое описание, цели..." 
            rows="3"
            style="width: 100%; padding: 8px;"
          ></textarea>
        </div>
        <button type="submit" style="padding: 8px 16px; cursor: pointer;">
          Сохранить проект
        </button>
      </form>
    </div>

    <div v-if="projectsStore.isLoading">Загрузка...</div>
    
    <ul v-else-if="projectsStore.list.length > 0" style="list-style: none; padding: 0;">
      <li 
        v-for="project in projectsStore.list" 
        :key="project.id" 
        style="background: white; border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 8px;"
      >
        <h4 style="margin: 0 0 10px 0; color: #2c3e50;">{{ project.name }}</h4>
        <p style="margin: 0 0 15px 0; color: #555;">{{ project.description || 'Описание отсутствует' }}</p>
        
        <button 
          @click="tabsStore.openTab({ 
            id: 'draft-' + project.id, 
            title: '📝 Драфт: ' + project.name, 
            componentName: 'DraftEditor'
          })"
          style="padding: 6px 12px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px;"
        >
          Открыть черновик
        </button>

        <button 
          @click="projectsStore.deleteProject(project.id)"
          style="padding: 6px 12px; background: #e74c3c; color: white; border: none; border-radius: 4px; cursor: pointer;"
        >
          Удалить
        </button>
      </li>
    </ul>
    
    <div v-else>Проектов пока нет. Создайте свой первый проект выше!</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useProjectsStore } from '../stores/projects';

import { useTabsStore } from '../stores/tabs'; // Добавьте этот импорт
const tabsStore = useTabsStore(); // Инициализируйте его

const projectsStore = useProjectsStore();

// Локальное состояние для формы
const newProject = ref({
  name: '',
  description: ''
});

// Функция отправки формы
const submitProject = async () => {
  await projectsStore.addProject(newProject.value);
  // Очищаем форму после успешного создания
  newProject.value.name = '';
  newProject.value.description = '';
};

// Загружаем проекты при открытии
onMounted(() => {
  projectsStore.fetchProjects();
});
</script>