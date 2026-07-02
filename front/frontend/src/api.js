import axios from 'axios';

const api = axios.create({
  baseURL: 'https://articles-app.ru', // Адрес вашего рабочего API
  headers: {
    'Content-Type': 'application/json'
  }
});

export default api;