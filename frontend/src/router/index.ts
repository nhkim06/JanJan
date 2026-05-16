import { createRouter, createWebHistory } from 'vue-router'
import Home from '../pages/Home.vue'
import Login from '../pages/Login.vue'
import Chats from '../pages/Chats.vue'
import Forms from '../pages/Forms.vue'

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
      component: Chats,
    },
    {
      path: '/forms',
      name: 'forms',
      component: Forms,
    },
  ],
})

export default router
