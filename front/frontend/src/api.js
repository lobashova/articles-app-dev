import axios from 'axios';

const api = axios.create({
  baseURL: 'https://articles-app.ru', // или http://localhost:8000
});

// Добавляем токен ко всем запросам
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Если получаем ошибку 401 (токен устарел или отсутствует) - выбрасываем на логин
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      window.location.reload(); // Перезагрузит страницу и покажет форму входа
    }
    return Promise.reject(error);
  }
);

export default api;