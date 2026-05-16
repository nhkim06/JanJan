import { createRouter, createWebHistory } from 'vue-router';
import Home from '../pages/Home.vue';
import Login from '../pages/Login.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
    },
    {
      path: '/chats',
      name: 'chats',
      component: import('../pages/Chats.vue'),
    },
    {
      path: '/forms/:category',
      name: 'forms',
      component: () => import('../pages/Forms.vue'),
    },
    {
      path: '/events/:category',
      name: 'events',
      component: () => import('../pages/EventList.vue'),
    },
  ],
});

export default router;
