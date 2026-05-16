<template>
  <div
    class="min-h-screen bg-slate-50 flex flex-col items-center justify-start p-6 font-sans text-slate-800"
  >
    <div
      class="w-full max-w-md flex flex-col h-[calc(100vh-3rem)] relative space-y-4"
    >
      <!-- 상단 네비게이션 (진단 결과 스타일 적용) -->
      <div class="flex items-center justify-between w-full py-2 flex-shrink-0">
        <button
          @click="$router.back()"
          class="w-10 h-10 flex items-center justify-center bg-white rounded-full border border-slate-200/70 shadow-sm text-slate-600 hover:bg-slate-50 active:scale-95 transition"
          title="뒤로 가기"
        >
          <font-awesome-icon icon="fa-solid fa-chevron-left" class="h-5 w-5" />
        </button>
        <span class="text-sm font-semibold text-slate-500"
          >에티켓 AI 상담실</span
        >
        <div class="w-10"></div>
      </div>

      <!-- 채팅 메시지 영역 -->
      <div class="flex-1 w-full overflow-y-auto pr-1 space-y-6 flex flex-col">
        <div v-for="(msg, index) in messages" :key="index" class="w-full">
          <!-- 유저 메시지 -->
          <div
            v-if="msg.sender === 'user'"
            class="flex flex-col items-end pl-12"
          >
            <div
              class="flex items-center gap-1 mb-1.5 text-xs text-slate-400 font-semibold"
            >
              <span>나</span>
              <font-awesome-icon icon="fa-solid fa-user" class="w-2.5 h-2.5" />
            </div>
            <div
              class="bg-gradient-to-br from-indigo-600 to-indigo-500 text-white rounded-3xl rounded-tr-sm py-3 px-5 text-[15px] font-medium leading-relaxed shadow-sm shadow-indigo-600/10 whitespace-pre-wrap break-all"
            >
              {{ msg.text }}
            </div>
          </div>

          <!-- AI 메시지 -->
          <div v-else class="flex flex-col items-start pr-12">
            <div
              class="flex items-center gap-1.5 mb-1.5 text-xs text-indigo-600 font-bold"
            >
              <font-awesome-icon
                icon="fa-solid fa-wand-magic-sparkles"
                class="w-3.5 h-3.5 animate-pulse"
              />
              <span>에티켓 AI</span>
            </div>

            <div class="flex items-start gap-2.5 w-full">
              <div
                class="w-9 h-9 rounded-full bg-white border border-slate-200/70 shadow-sm flex-shrink-0 flex items-center justify-center text-indigo-500"
              >
                <font-awesome-icon
                  icon="fa-solid fa-wand-magic-sparkles"
                  class="w-4 h-4"
                />
              </div>
              <div class="w-full">
                <!-- 로딩 중 상태 -->
                <div
                  v-if="msg.isLoading"
                  class="inline-flex gap-1.5 items-center bg-white border border-slate-100 rounded-3xl rounded-tl-sm py-4 px-5 shadow-sm min-h-[50px]"
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
                <!-- 일반 메시지 (진단결과 카드 스타일 적용) -->
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

      <!-- 하단 입력창 영역 (둥근 모서리 및 인디고 포커스 스타일 강화) -->
      <div class="w-full pt-2 flex-shrink-0">
        <div
          class="relative flex items-center bg-white border border-slate-200/80 rounded-full shadow-md px-5 py-3 focus-within:border-indigo-500 focus-within:ring-4 focus-within:ring-indigo-50 transition-all"
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
              'absolute right-2 w-10 h-10 rounded-full flex items-center justify-center transition-all',
              inputMessage.trim()
                ? 'bg-[#0f1423] text-white shadow-md active:scale-95 cursor-pointer'
                : 'bg-slate-100 text-slate-400 cursor-not-allowed',
            ]"
          >
            <font-awesome-icon
              icon="fa-solid fa-paper-plane"
              class="w-4 h-4 transform rotate-45 -translate-x-[1px] translate-y-[0px]"
            />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const inputMessage = ref('');
const messages = ref([]);

onMounted(() => {
  const category = route.query.category || '일반';
  const targetName = route.query.targetName || '상대방';
  const cultureBase = route.query.cultureBase || '한국';

  const initialUserMessage = `지금 ${cultureBase}에서 ${category} 상황인 ${targetName}님과의 에티켓에 대해 더 자세히 알려줘.`;

  messages.value.push({
    sender: 'user',
    text: initialUserMessage,
  });

  messages.value.push({
    sender: 'ai',
    isLoading: true,
    text: '',
  });

  setTimeout(() => {
    const aiMessageIndex = messages.value.findIndex(
      (m) => m.sender === 'ai' && m.isLoading,
    );
    if (aiMessageIndex !== -1) {
      messages.value[aiMessageIndex].isLoading = false;
      messages.value[aiMessageIndex].text =
        `${targetName}님과의 ${category} 상황이시군요! ${cultureBase} 문화권을 기준으로 더 구체적인 조언을 드릴게요.\n\n어떤 점이 가장 궁금하신가요? (예: 구체적인 선물 추천, 복장, 건네면 좋은 말 등)`;
    }
  }, 1000);
});

const sendMessage = () => {
  if (!inputMessage.value.trim()) return;

  messages.value.push({
    sender: 'user',
    text: inputMessage.value,
  });

  inputMessage.value = '';

  messages.value.push({
    sender: 'ai',
    isLoading: true,
    text: '',
  });

  setTimeout(() => {
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
/* 부드러운 스크롤바 디테일 스타일링 */
.overflow-y-auto {
  scroll-behavior: smooth;
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}
.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 9999px;
}
</style>
