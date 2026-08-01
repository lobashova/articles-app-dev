import { defineStore } from 'pinia';
import api from '../api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(username, password) {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      
      const res = await api.post('/login', formData);
      this.token = res.data.access_token;
      localStorage.setItem('token', this.token);
    },
    logout() {
      this.token = null;
      localStorage.removeItem('token');
      window.location.reload();
    }
  }
});