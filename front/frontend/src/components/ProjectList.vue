<template>
  <div class="projects-container">
    <h2>Мои научные проекты</h2>
    <div v-if="projectsStore.isLoading">Загрузка...</div>
    
    <ul v-else-if="projectsStore.list.length > 0">
      <li v-for="project in projectsStore.list" :key="project.id" style="margin-bottom: 15px;">
        <strong>{{ project.name }}</strong>
        <p style="margin: 5px 0;">{{ project.description }}</p>
      </li>
    </ul>
    
    <div v-else>Проектов пока нет.</div>
    
    <button @click="projectsStore.fetchProjects">Обновить список</button>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useProjectsStore } from '../stores/projects';

const projectsStore = useProjectsStore();

// Загружаем проекты сразу при открытии компонента
onMounted(() => {
  projectsStore.fetchProjects();
});
</script>