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
      path: '/forms/:category',
      name: 'forms',
      component: () => import('../pages/Forms.vue'),
    },

    {
      path: '/events/:category',
      name: 'events',
      component: () => import('../pages/EventList.vue'),
    },
    {
      path: '/result/:category',
      name: 'result',
      component: () => import('../pages/Result.vue'),
    },
    {
      path: '/chat',
      name: 'chat',
      component: () => import('../pages/ChatAI.vue'),
    },
    {
      path: '/chat-list/:personId',
      name: 'chat-list',
      component: () => import('../pages/ChatList.vue'),
    },
  ],
});

export default router;
