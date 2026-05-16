<template>
  <div
    :class="[
      'flex flex-col items-center font-sans relative w-full',
      isComponent ? 'h-full' : 'min-h-screen bg-slate-50 justify-between',
    ]"
  >
    <header
      v-if="!isComponent"
      class="w-full max-w-md md:max-w-2xl lg:max-w-3xl bg-white border-b border-slate-100 py-4 px-6 flex items-center justify-between sticky top-0 z-10 shadow-sm md:rounded-b-2xl"
    >
      <div class="flex items-center gap-3">
        <button
          @click="$router.back()"
          class="text-slate-600 hover:text-slate-900 transition bg-slate-50 w-8 h-8 rounded-full flex items-center justify-center"
        >
          <font-awesome-icon icon="fa-solid fa-chevron-left" class="w-4 h-4" />
        </button>
        <span class="font-bold text-slate-800 text-lg md:text-xl"
          >에티켓 AI 상담실</span
        >
      </div>
    </header>

    <div
      ref="messageContainer"
      :class="[
        'flex-1 w-full max-w-md md:max-w-2xl lg:max-w-3xl overflow-y-auto px-6 py-6 space-y-6 flex flex-col',
        isComponent ? '' : '',
      ]"
    >
      <div v-for="(msg, index) in messages" :key="index" class="w-full">
        <div
          v-if="msg.sender === 'user'"
          class="flex flex-col items-end pl-12 md:pl-24"
        >
          <div
            class="flex items-center gap-1 mb-1 text-xs text-slate-400 font-medium"
          >
            <span>나</span>
            <font-awesome-icon icon="fa-solid fa-user" class="w-3 h-3" />
          </div>
          <div
            class="bg-gradient-to-br from-indigo-600 to-indigo-500 text-white rounded-3xl rounded-tr-sm py-3 px-5 text-[15px] md:text-base font-medium leading-relaxed shadow-sm shadow-indigo-600/10 whitespace-pre-wrap break-all"
          >
            {{ msg.text }}
          </div>
        </div>

        <div v-else class="flex flex-col items-start pr-12 md:pr-24">
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
              class="w-9 h-9 md:w-10 md:h-10 rounded-full bg-white border border-slate-100 shadow-sm flex-shrink-0 flex items-center justify-center text-indigo-400"
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
                class="bg-white border border-slate-100 text-slate-800 rounded-3xl rounded-tl-sm py-3 px-5 text-[15px] md:text-base font-medium leading-relaxed shadow-sm whitespace-pre-wrap break-all"
              >
                {{ msg.text }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div
      :class="[
        'w-full max-w-md md:max-w-2xl lg:max-w-3xl bg-transparent px-6 pt-2',
        isComponent ? 'pb-4' : 'pb-8 sticky bottom-0 z-10',
      ]"
    >
      <div
        class="relative flex items-center bg-white border border-slate-200 rounded-full shadow-lg px-5 py-2.5 md:py-4 focus-within:border-indigo-500 focus-within:ring-4 focus-within:ring-indigo-50 transition-all"
      >
        <input
          v-model="inputMessage"
          type="text"
          placeholder="추가 질문을 입력하세요..."
          class="flex-1 bg-transparent text-base md:text-lg font-medium text-slate-800 placeholder-slate-400 focus:outline-none pr-12"
          @keyup.enter="sendMessage"
        />
        <button
          @click="sendMessage"
          :disabled="!inputMessage.trim()"
          :class="[
            'absolute right-2.5 md:right-4 w-10 h-10 md:w-12 md:h-12 rounded-full flex items-center justify-center transition-all',
            inputMessage.trim()
              ? 'bg-indigo-600 text-white shadow-md active:scale-95 cursor-pointer'
              : 'bg-slate-100 text-slate-400 cursor-not-allowed',
          ]"
        >
          <font-awesome-icon
            icon="fa-solid fa-paper-plane"
            class="w-5 h-5 md:w-6 md:h-6 transform rotate-45 -translate-x-[1px] translate-y-[1px]"
          />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '../utils/api';

const props = defineProps({
  isComponent: {
    type: Boolean,
    default: false,
  },
  category: String,
  targetName: String,
  cultureBase: String,
  roomId: [Number, String],
});

const route = useRoute();
const messageContainer = ref(null);

// 입력값 상태 관리
const inputMessage = ref('');

// 메시지 데이터
const messages = ref([]);

const scrollToBottom = async () => {
  await nextTick();
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight;
  }
};

onMounted(() => {
  const roomId =
    props.roomId || (route.query.roomId ? parseInt(route.query.roomId) : null);

  if (roomId) {
    fetchChatHistory(roomId);
  } else {
    // 결과 페이지에서 넘어왔을 때 초기 메시지 설정
    const category = props.category || route.query.category || '일반';
    const targetName = props.targetName || route.query.targetName || '상대방';
    const cultureBase = props.cultureBase || route.query.cultureBase || '한국';

    const initialUserMessage = `지금 ${cultureBase}에서 ${category} 상황인 ${targetName}님과의 에티켓에 대해 더 자세히 알려줘.`;
    
    // UI에만 표시하거나, 첫 질문으로 서버에 보낼 수 있음
    messages.value.push({ sender: 'user', text: initialUserMessage });
    // 서버 응답 기다리는 시늉
    messages.value.push({ sender: 'ai', isLoading: true, text: '' });
    
    // 만약 formId가 나중에 생기면 그때 보낼 수도 있지만, 지금은 mock으로 응답만 보여줌
    setTimeout(() => {
      const aiMessageIndex = messages.value.findIndex(m => m.sender === 'ai' && m.isLoading);
      if (aiMessageIndex !== -1) {
        messages.value[aiMessageIndex].isLoading = false;
        messages.value[aiMessageIndex].text = `${targetName}님과의 ${category} 상황이시군요! ${cultureBase} 문화권을 기준으로 더 구체적인 조언을 드릴게요.\n\n어떤 점이 가장 궁금하신가요?`;
        scrollToBottom();
      }
    }, 1000);
  }
});

const fetchChatHistory = async (roomId) => {
  try {
    const response = await apiClient.get(`/chat/list?formId=${roomId}`);
    if (response.data.success) {
      messages.value = response.data.chatItems.flatMap(item => [
        { sender: 'user', text: item.question },
        { sender: 'ai', text: item.answer }
      ]);
      scrollToBottom();
    }
  } catch (error) {
    console.error('채팅 내역 조회 에러:', error);
  }
};

// 메시지 전송 로직
const sendMessage = async () => {
  if (!inputMessage.value.trim()) return;

  const userText = inputMessage.value;
  const roomId = props.roomId || (route.query.roomId ? parseInt(route.query.roomId) : null);

  // 1. 유저 메시지 추가
  messages.value.push({
    sender: 'user',
    text: userText,
  });

  inputMessage.value = '';
  scrollToBottom();

  // 2. AI 대기 상태 메시지 추가
  messages.value.push({
    sender: 'ai',
    isLoading: true,
    text: '',
  });

  scrollToBottom();

  try {
    if (roomId) {
      const response = await apiClient.post('/chat/new', {
        formId: roomId,
        question: userText
      });

      const aiMessageIndex = messages.value.findIndex(m => m.sender === 'ai' && m.isLoading);
      if (aiMessageIndex !== -1) {
        messages.value[aiMessageIndex].isLoading = false;
        messages.value[aiMessageIndex].text = response.data.answer;
        scrollToBottom();
      }
    } else {
      // roomId가 없는 경우 (임시 대응)
      setTimeout(() => {
        const aiMessageIndex = messages.value.findIndex(m => m.sender === 'ai' && m.isLoading);
        if (aiMessageIndex !== -1) {
          messages.value[aiMessageIndex].isLoading = false;
          messages.value[aiMessageIndex].text = "질문을 저장하려면 먼저 설문을 완료해주세요.";
          scrollToBottom();
        }
      }, 1000);
    }
  } catch (error) {
    console.error('메시지 전송 에러:', error);
    const aiMessageIndex = messages.value.findIndex(m => m.sender === 'ai' && m.isLoading);
    if (aiMessageIndex !== -1) {
      messages.value[aiMessageIndex].isLoading = false;
      messages.value[aiMessageIndex].text = "오류가 발생했습니다. 다시 시도해주세요.";
      scrollToBottom();
    }
  }
};

// watch messages to scroll bottom
watch(
  messages,
  () => {
    scrollToBottom();
  },
  { deep: true },
);
</script>

<style scoped>
/* 부드러운 스크롤을 원할 경우 */
.overflow-y-auto {
  scroll-behavior: smooth;
}
</style>
