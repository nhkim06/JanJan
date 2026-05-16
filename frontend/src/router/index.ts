import { createRouter, createWebHistory } from 'vue-router';
import Home from '../pages/Home.vue';
import Login from '../pages/Login.vue';
import { useAuthStore } from '../stores/auth';

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
    {
      path: '/auth/callback',
      name: 'auth-callback',
      component: { render: () => null }, // 임시 컴포넌트
    },
  ],
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  
  // URL 쿼리 파라미터 확인
  const tokenInUrl = to.query.token as string;
  const success = to.query.success === 'True' || to.query.success === 'true';
  const hasData = to.query.hasData === 'True' || to.query.hasData === 'true';

  // 1. 로그인 콜백 처리 (토큰이 있거나, 성공했지만 데이터가 없는 경우)
  if (success) {
    if (tokenInUrl) {
      console.log('기존 유저 로그인 성공: 토큰 저장 중...');
      authStore.setToken(tokenInUrl);
    }

    // 쿼리 정리 및 리다이렉트 설정
    const query: any = { ...to.query };
    delete query.token;
    delete query.refresh;
    delete query.success;
    delete query.hasData;

    // 데이터가 없는 신규 유저라면 회원가입 모달 트리거
    if (!hasData) {
      console.log('신규 유저 발견: 회원가입 모달 트리거');
      authStore.setIsRegistering(true);
      query.isNewUser = 'true';
    }

    return next({ path: '/', query, replace: true });
  }

  // 2. 인증이 필요한 페이지 접근 제어
  const publicPages = ['login', 'auth-callback'];
  const authRequired = !publicPages.includes(to.name as string);

  if (authRequired && !authStore.isAuthenticated) {
    // 신규 유저 등록 과정인 경우 홈 페이지 접근 허용
    if (authStore.isRegistering || to.query.isNewUser === 'true') {
      return next();
    }
    return next({ name: 'login' });
  }

  // 3. 이미 로그인된 상태에서 로그인 페이지 접근 시 홈으로 이동
  if (to.name === 'login' && authStore.isAuthenticated) {
    return next({ name: 'home' });
  }

  next();
});

export default router;
