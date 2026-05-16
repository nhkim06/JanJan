<template>
  <div class="flex justify-center bg-gray-50 min-h-screen">
    <div
      class="w-full max-w-md md:max-w-xl bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-50/30 via-white to-white flex flex-col px-8 pt-24 pb-12 min-h-screen relative select-none items-center"
    >
      <div class="flex flex-col items-center w-full max-w-sm">
        <!-- 로고 및 서비스 이름 -->
        <div
          class="w-20 h-20 md:w-24 md:h-24 bg-gradient-to-tr from-indigo-600 to-violet-500 rounded-3xl flex items-center justify-center text-white shadow-xl shadow-indigo-200 mb-8 animate-bounce-subtle"
        >
          <font-awesome-icon
            icon="fa-solid fa-wand-magic-sparkles"
            class="w-10 h-10 md:w-12 md:h-12"
          />
        </div>

        <header class="text-center mb-12">
          <h1 class="text-3xl md:text-4xl font-black text-slate-900 tracking-tight mb-3">
            잔잔 (JanJan)
          </h1>
          <p class="text-sm md:text-base font-medium text-slate-500 leading-relaxed">
            당신의 일상 속 예의를 더 가볍게,<br />
            AI와 함께하는 스마트한 에티켓 가이드
          </p>
        </header>

        <!-- 로그인 섹션 -->
        <div class="w-full space-y-4">
          <button
            @click="handleGoogleLogin"
            class="w-full flex items-center justify-center gap-3 bg-white border border-slate-200 rounded-2xl py-4 px-6 shadow-sm hover:shadow-md hover:border-slate-300 active:scale-[0.98] transition-all duration-200 group"
          >
            <svg
              class="w-6 h-6"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                fill="#4285F4"
              />
              <path
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                fill="#34A853"
              />
              <path
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"
                fill="#FBBC05"
              />
              <path
                d="M12 5.38c1.62 0 3.06.56 4.21 1.66l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                fill="#EA4335"
              />
            </svg>
            <span class="text-slate-700 font-bold text-base md:text-lg">Google 계정으로 시작하기</span>
          </button>
        </div>

        <!-- 하단 문구 -->
        <footer class="mt-auto pt-12 text-center">
          <p class="text-xs text-slate-400 font-medium leading-relaxed">
            로그인 시 서비스 <span class="underline decoration-slate-200">이용약관</span> 및
            <span class="underline decoration-slate-200">개인정보처리방침</span>에<br />
            동의하는 것으로 간주됩니다.
          </p>
        </footer>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const handleGoogleLogin = () => {
  // 실제 로그인 로직은 백엔드 구현 시 연동
  console.log('Google 로그인 시도...');
  // 데모를 위해 바로 홈으로 이동
  router.push('/');
};
</script>

<style scoped>
@keyframes bounce-subtle {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

.animate-bounce-subtle {
  animation: bounce-subtle 3s infinite ease-in-out;
}
</style>
