<template>
  <div
    class="min-h-screen bg-slate-50 flex flex-col items-center justify-start p-6 font-sans text-slate-800"
  >
    <div class="w-full max-w-md space-y-6 relative">
      <div class="flex items-center justify-between w-full py-2">
        <button
          @click="goHome"
          class="w-10 h-10 flex items-center justify-center bg-white rounded-full border border-slate-200/70 shadow-sm text-slate-600 hover:bg-slate-50 active:scale-95 transition"
          title="처음으로 이동"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
            />
          </svg>
        </button>
        <span class="text-sm font-semibold text-slate-500">진단 결과</span>
        <div class="w-10"></div>
      </div>

      <div
        class="bg-white rounded-3xl p-8 shadow-sm border border-slate-100 text-center relative overflow-hidden"
      >
        <h2 class="text-sm font-medium text-slate-400 mb-2">적정 추천 금액</h2>
        <div class="text-5xl font-black tracking-tight mb-2 text-slate-900">
          50,000<span class="text-2xl font-bold text-indigo-600 ml-1">원</span>
        </div>
        <p class="text-sm font-semibold text-slate-400 mb-6">
          최소 30,000원 이상
        </p>

        <div
          class="bg-emerald-50/50 rounded-2xl p-4 flex items-center justify-start border border-emerald-100/50"
        >
          <span class="text-emerald-500 mr-2 flex items-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clip-rule="evenodd"
              />
            </svg>
          </span>
          <p class="text-sm font-medium text-slate-600">
            안 가고 3만원 or 가고 5만원
          </p>
        </div>
      </div>

      <div class="bg-rose-50/40 rounded-3xl p-6 border border-rose-100/70">
        <div class="flex items-center text-rose-600 font-bold mb-4">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5 mr-2"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          필수 금기사항
        </div>
        <hr class="border-rose-200/60 mb-4" />
        <ul
          class="list-disc pl-5 text-sm font-medium text-rose-700/90 space-y-2"
        >
          <li>안 친한데 가족 대동</li>
        </ul>
      </div>

      <div class="bg-emerald-50/30 rounded-3xl p-6 border border-emerald-100">
        <div class="flex items-center text-emerald-700 font-bold mb-4">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5 mr-2"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5a2 2 0 10-2 2h2zm0 0h4m-4 0H8m12 3v9a2 2 0 01-2 2H6a2 2 0 01-2-2V10h16z"
            />
          </svg>
          추천 선물 & 팁
        </div>
        <hr class="border-emerald-200/50 mb-4" />
        <ul
          class="list-disc pl-5 text-sm font-medium text-emerald-800/90 space-y-2"
        >
          <li>축의금</li>
        </ul>
      </div>

      <div class="pt-2 space-y-3">
        <button
          @click="handleCreateMessage"
          class="w-full bg-white text-indigo-600 border border-indigo-200 hover:bg-indigo-50 active:scale-[0.99] transition py-4 px-6 rounded-2xl font-bold text-base flex items-center justify-center shadow-sm"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5 mr-2"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
          상황별 추천 멘트 만들기
        </button>

        <button
          @click="handleChatWithAI"
          class="w-full bg-[#0f1423] text-white hover:bg-slate-800 active:scale-[0.99] transition py-4 px-6 rounded-2xl font-bold text-base flex items-center justify-center shadow-md"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5 mr-2 text-indigo-300"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
            />
          </svg>
          AI와 더 자세히 대화하기
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const goHome = () => {
  console.log('홈 화면(첫 페이지)으로 이동합니다.');
  router.push('/');
};

const handleCreateMessage = () => {
  console.log('추천 멘트 만들기 페이지로 이동');
};

const handleChatWithAI = () => {
  console.log('AI 채팅 페이지로 이동');
};
</script>
