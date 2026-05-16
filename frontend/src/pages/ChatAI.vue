<template>
  <div
    class="min-h-screen bg-slate-50 flex flex-col items-center justify-between font-sans relative"
  >
    <header
      class="w-full max-w-md bg-white border-b border-slate-100 py-4 px-6 flex items-center justify-between sticky top-0 z-10 shadow-sm"
    >
      <div class="flex items-center gap-3">
        <button
          @click="$router.back()"
          class="text-slate-600 hover:text-slate-900 transition"
        >
          <font-awesome-icon icon="fa-solid fa-chevron-left" class="w-5 h-5" />
        </button>
        <span class="font-bold text-slate-800 text-lg">에티켓 AI 상담실</span>
      </div>
    </header>

    <div
      class="flex-1 w-full max-w-md overflow-y-auto px-6 py-6 space-y-6 flex flex-col"
    >
      <div v-for="(msg, index) in messages" :key="index" class="w-full">
        <div v-if="msg.sender === 'user'" class="flex flex-col items-end pl-12">
          <div
            class="flex items-center gap-1 mb-1 text-xs text-slate-400 font-medium"
          >
            <span>나</span>
            <font-awesome-icon icon="fa-solid fa-user" class="w-3 h-3" />
          </div>
          <div
            class="bg-gradient-to-br from-indigo-600 to-indigo-500 text-white rounded-3xl rounded-tr-sm py-3 px-5 text-[15px] font-medium leading-relaxed shadow-sm shadow-indigo-600/10 whitespace-pre-wrap break-all"
          >
            {{ msg.text }}
          </div>
        </div>

        <div v-else class="flex flex-col items-start pr-12">
          <div
            class="flex items-center gap-1.5 mb-1.5 text-xs text-indigo-600 font-bold"
          >
            <font-awesome-icon icon="fa-solid fa-wand-magic-sparkles" class="w-3.5 h-3.5 animate-pulse" />
            <span>에티켓 AI</span>
          </div>

          <div class="flex items-start gap-2.5 w-full">
            <div
              class="w-9 h-9 rounded-full bg-white border border-slate-100 shadow-sm flex-shrink-0 flex items-center justify-center text-indigo-400"
            >
              <font-awesome-icon icon="fa-solid fa-wand-magic-sparkles" />
            </div>
            <div class="w-full">
              <div
                v-if="msg.isLoading"
                class="flex gap-1.5 items-center bg-white border border-slate-100 rounded-3xl rounded-tl-sm py-4 px-5 shadow-sm min-h-[50px]"
              >
                <span
                  class="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                  style="animation-delay: 0ms"
                ></span>
                <span
                  class="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                  style="animation-delay: 150ms"
                ></span>
                <span
                  class="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                  style="animation-delay: 300ms"
                ></span>
              </div>
              <div
                v-else
                class="bg-white border border-slate-100 text-slate-800 rounded-3xl rounded-tl-sm py-3 px-5 text-[15px] font-medium leading-relaxed shadow-sm whitespace-pre-wrap break-all"
              >
                {{ msg.text }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div
      class="w-full max-w-md bg-transparent px-6 pb-8 pt-2 sticky bottom-0 z-10"
    >
      <div
        class="relative flex items-center bg-white border border-slate-200 rounded-full shadow-lg px-5 py-2.5 focus-within:border-indigo-500 focus-within:ring-4 focus-within:ring-indigo-50 transition-all"
      >
        <input
          v-model="inputMessage"
          type="text"
          placeholder="추가 질문을 입력하세요..."
          class="flex-1 bg-transparent text-base font-medium text-slate-800 placeholder-slate-400 focus:outline-none pr-12"
          @keyup.enter="sendMessage"
        />
        <button
          @click="sendMessage"
          :disabled="!inputMessage.trim()"
          :class="[
            'absolute right-2.5 w-10 h-10 rounded-full flex items-center justify-center transition-all',
            inputMessage.trim()
              ? 'bg-indigo-600 text-white shadow-md active:scale-95 cursor-pointer'
              : 'bg-slate-100 text-slate-400 cursor-not-allowed',
          ]"
        >
          <font-awesome-icon icon="fa-solid fa-paper-plane" class="w-5 h-5 transform rotate-45 -translate-x-[1px] translate-y-[1px]" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// 입력값 상태 관리
const inputMessage = ref('');

// 더미 메시지 데이터 데이터 구조 (초기 세팅)
const messages = ref([
  {
    sender: 'user',
    text: '지금 한국에서 결혼식 에티켓에 대해 더 자세히 알려줘. 내 관계는 지인이야.',
  },
  {
    sender: 'ai',
    isLoading: true, // 이미지처럼 AI가 로딩 중(점 세개)인 상태 표현을 위한 플래그
    text: '',
  },
  {
    sender: 'user',
    text: '지금 한국에서 결혼식 에티켓에 대해 더 자세히 알려줘. 내 관계는 지인이야.',
  },
  {
    sender: 'ai',
    isLoading: true,
    text: '',
  },
]);

// 메시지 전송 로직
const sendMessage = () => {
  if (!inputMessage.value.trim()) return;

  // 1. 유저 메시지 추가
  messages.value.push({
    sender: 'user',
    text: inputMessage.value,
  });

  const tempUserText = inputMessage.value;
  inputMessage.value = '';

  // 2. AI 대기 상태 메시지 추가
  messages.value.push({
    sender: 'ai',
    isLoading: true,
    text: '',
  });

  // 3. 실제 API 연동을 흉내 낸 타이밍 처리 (2초 후 답변)
  setTimeout(() => {
    // 가장 최근의 대기 중인 AI 인덱스 찾아서 업데이트
    const aiMessageIndex = messages.value.findIndex(
      (m) => m.sender === 'ai' && m.isLoading,
    );
    if (aiMessageIndex !== -1) {
      messages.value[aiMessageIndex].isLoading = false;
      messages.value[aiMessageIndex].text =
        `지인 관계이시군요! 한국의 일반적인 지인 결혼식 축의금 가이드라인은 다음과 같습니다.\n\n• 기본 축의금: 5만 원 ~ 7만 원 (식사를 하지 않는 경우 5만 원 권장)\n• 식사 동반 시: 10만 원\n• 복장 에티켓: 하얀색 원피스나 옷은 피하시고 단정한 셔츠나 슬랙스, 정장 차림을 추천해 드립니다.`;
    }
  }, 1500);
};
</script>

<style scoped>
/* 부드러운 스크롤을 원할 경우 */
.overflow-y-auto {
  scroll-behavior: smooth;
}
</style>
