<template>
  <div class="login-wrapper">
    <div class="login-card">
      <h2>🔐 Вход в систему</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>Логин</label>
          <input v-model="username" type="text" required />
        </div>
        <div class="form-group">
          <label>Пароль</label>
          <input v-model="password" type="password" required />
        </div>
        <button type="submit" class="login-btn" :disabled="isLoading">
          {{ isLoading ? 'Проверка...' : 'Войти' }}
        </button>
        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();
const username = ref('');
const password = ref('');
const isLoading = ref(false);
const errorMsg = ref('');

const handleLogin = async () => {
  isLoading.value = true;
  errorMsg.value = '';
  try {
    await authStore.login(username.value, password.value);
  } catch (error) {
    errorMsg.value = "Неверный логин или пароль";
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.login-wrapper {
  display: flex; justify-content: center; align-items: center;
  height: 100vh; background: #2c3e50;
}
.login-card {
  background: white; padding: 40px; border-radius: 8px;
  width: 300px; box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}
h2 { text-align: center; color: #34495e; margin-top: 0; }
.form-group { margin-bottom: 15px; }
label { display: block; margin-bottom: 5px; font-weight: bold; color: #7f8c8d; }
input { width: 100%; padding: 10px; border: 1px solid #bdc3c7; border-radius: 4px; box-sizing: border-box;}
.login-btn {
  width: 100%; padding: 10px; background: #3498db; color: white;
  border: none; border-radius: 4px; font-weight: bold; cursor: pointer;
  margin-top: 10px;
}
.login-btn:hover { background: #2980b9; }
.error-msg { color: #e74c3c; text-align: center; font-size: 0.9em; margin-top: 15px; }
</style>