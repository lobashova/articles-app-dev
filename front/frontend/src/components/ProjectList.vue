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
        <button type="submit" style="padding: 8px 16px; cursor: pointer; background: #2ecc71; color: white; border: none; border-radius: 4px; font-weight: bold;">
          + Создать проект
        </button>
      </form>
    </div>

    <div v-if="projectsStore.isLoading">Загрузка...</div>
    
    <ul v-else-if="projectsStore.list.length > 0" style="list-style: none; padding: 0;">
      <li 
        v-for="project in projectsStore.list" 
        :key="project.id" 
        style="background: white; border: 1px solid #ddd; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);"
      >
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px;">
          <div>
            <h3 style="margin: 0 0 5px 0; color: #2c3e50;">{{ project.name }}</h3>
            <p style="margin: 0; color: #7f8c8d; font-size: 0.9em;">{{ project.description || 'Описание отсутствует' }}</p>
          </div>
          <button 
            @click="projectsStore.deleteProject(project.id)"
            style="padding: 6px 12px; background: #e74c3c; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.8em;"
            title="Удалить проект целиком"
          >
            🗑️ Удалить проект
          </button>
        </div>

        <div style="background: #f8f9fa; padding: 15px; border-radius: 6px; border-left: 3px solid #3498db;">
          <h4 style="margin: 0 0 10px 0; color: #34495e;">📄 Черновики проекта:</h4>
          
          <ul style="list-style: none; padding: 0; margin: 0 0 15px 0;" v-if="draftsByProject[project.id] && draftsByProject[project.id].length > 0">
            <li 
              v-for="draft in draftsByProject[project.id]" 
              :key="draft.id"
              style="display: flex; align-items: center; justify-content: space-between; padding: 8px; background: white; margin-bottom: 5px; border-radius: 4px; border: 1px solid #eee;"
            >
              <span style="font-weight: 500; color: #2c3e50;">📝 {{ draft.title }}</span>
              <div>
                <button 
                  @click="tabsStore.openTab({ 
                    id: 'draft-' + draft.id, 
                    title: '📝 ' + draft.title.substring(0, 15) + (draft.title.length > 15 ? '...' : ''), 
                    componentName: 'DraftEditor'
                  })"
                  style="padding: 4px 10px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 5px; font-size: 0.85em;"
                >
                  Редактировать
                </button>
                <button 
                  @click="deleteDraft(project.id, draft.id)"
                  style="padding: 4px 8px; background: transparent; color: #e74c3c; border: 1px solid #e74c3c; border-radius: 4px; cursor: pointer; font-size: 0.85em;"
                  title="Удалить черновик"
                >
                  ✕
                </button>
              </div>
            </li>
          </ul>
          
          <div v-else style="color: #95a5a6; margin-bottom: 15px; font-size: 0.9em;">
            Пока нет черновиков.
          </div>

          <button 
            @click="createNewDraft(project.id, project.name)"
            style="padding: 6px 12px; background: #fff; color: #3498db; border: 1px dashed #3498db; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 0.85em;"
          >
            + Создать новый черновик
          </button>
        </div>

      </li>
    </ul>
    
    <div v-else>Проектов пока нет. Создайте свой первый проект выше!</div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useProjectsStore } from '../stores/projects';
import { useTabsStore } from '../stores/tabs';
import api from '../api'; // Нужен для прямых запросов к API черновиков

const tabsStore = useTabsStore();
const projectsStore = useProjectsStore();

const newProject = ref({
  name: '',
  description: ''
});

// Объект для хранения черновиков, сгруппированных по ID проекта
const draftsByProject = ref({});

const submitProject = async () => {
  await projectsStore.addProject(newProject.value);
  newProject.value.name = '';
  newProject.value.description = '';
};

// Загрузка черновиков для конкретного проекта
const loadDraftsForProject = async (projectId) => {
  try {
    const response = await api.get(`/projects/${projectId}/drafts/`);
    draftsByProject.value[projectId] = response.data;
  } catch (error) {
    console.error(`Ошибка при загрузке черновиков для проекта ${projectId}:`, error);
  }
};

// Создание нового черновика
const createNewDraft = async (projectId, projectName) => {
  const customTitle = prompt("Введите название нового черновика:", `Часть 1: ${projectName}`);
  if (!customTitle) return; // Если пользователь нажал "Отмена"

  try {
    // Внимание: В FastAPI мы определили параметры в query string, поэтому передаем params
    const response = await api.post('/drafts/', null, { 
      params: { 
        project_id: projectId, 
        title: customTitle 
      } 
    });
    
    // Обновляем список локально
    if (!draftsByProject.value[projectId]) {
      draftsByProject.value[projectId] = [];
    }
    draftsByProject.value[projectId].push(response.data);
    
    // Сразу открываем созданный черновик во вкладке
    tabsStore.openTab({ 
      id: 'draft-' + response.data.id, 
      title: '📝 ' + response.data.title.substring(0, 15) + '...', 
      componentName: 'DraftEditor'
    });

  } catch (error) {
    alert("Ошибка при создании черновика");
    console.error(error);
  }
};

// Удаление черновика
const deleteDraft = async (projectId, draftId) => {
  if (!confirm("Вы уверены, что хотите удалить этот черновик? Текст будет потерян навсегда.")) return;
  
  try {
    await api.delete(`/drafts/${draftId}`);
    // Удаляем из локального списка
    draftsByProject.value[projectId] = draftsByProject.value[projectId].filter(d => d.id !== draftId);
    
    // Если вкладка с этим черновиком была открыта, закрываем её
    tabsStore.closeTab('draft-' + draftId);
  } catch (error) {
    alert("Ошибка при удалении черновика");
    console.error(error);
  }
};

// Когда загружаются проекты, автоматически подгружаем черновики для каждого из них
watch(() => projectsStore.list, (newProjects) => {
  newProjects.forEach(project => {
    if (!draftsByProject.value[project.id]) {
      loadDraftsForProject(project.id);
    }
  });
}, { immediate: true, deep: true });

onMounted(() => {
  projectsStore.fetchProjects();
});
</script>