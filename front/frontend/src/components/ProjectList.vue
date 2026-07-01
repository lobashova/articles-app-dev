<template>
  <div>
    <h1>Мои проекты</h1>
    <ul>
      <li v-for="project in projectStore.projects" :key="project.id">
        {{ project.name }} - {{ project.description }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useProjectStore } from '../stores/projects';

const projectStore = useProjectStore();
onMounted(() => {
  projectStore.fetchProjects();
});
</script>