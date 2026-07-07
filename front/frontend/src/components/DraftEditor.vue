<template>
  <div class="draft-container" style="max-width: 1000px; margin: 0 auto; padding-bottom: 40px;">
    <input 
      v-model="draftTitle" 
      type="text" 
      placeholder="Название вашей статьи..." 
      style="width: 100%; font-size: 1.5em; padding: 10px; margin-bottom: 15px; border: none; border-bottom: 2px solid #ccc; outline: none; background: transparent;"
    />
    
    <MdEditor 
      v-model="draftContent" 
      language="en-US" 
      style="height: 70vh;"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';
// Импортируем сам компонент редактора и его стили
import { MdEditor } from 'md-editor-v3';
import 'md-editor-v3/lib/style.css';

const draftTitle = ref('Новый черновик');
// Добавим тестовый текст с математической формулой, чтобы сразу проверить рендер
const draftContent = ref('# Введение\n\nЗдесь вы можете писать текст. А вот пример математической модели:\n\n$f(x) = \\int_{-\\infty}^{\\infty} \\hat f(\\xi)\\,e^{2 \\pi i \\xi x} \\,d\\xi$');
</script>