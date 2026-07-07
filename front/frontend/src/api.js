import axios from 'axios';

const api = axios.create({
  // Замените на ваш реальный домен, если он отличается
  baseURL: 'https://articles-app.ru', 
  headers: {
    'Content-Type': 'application/json'
  }
});

export default api;