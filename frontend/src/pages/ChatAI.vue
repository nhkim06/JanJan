<template>
  <div
    :class="[
      'flex flex-col items-center font-sans relative w-full',
      isComponent ? 'h-full' : 'min-h-screen bg-slate-50 justify-between',
    ]"
  >
    <header
      v-if="!isComponent"
      class="w-full max-w-md md:max-w-2xl lg:max-w-3xl flex items-center px-6 py-6 border-b border-slate-100 bg-white/80 backdrop-blur-md sticky top-0 z-30"
    >
      <button
        @click="router.back()"
        class="mr-4 text-slate-400 hover:text-slate-600 transition-colors"
      >
        <font-awesome-icon icon="fa-solid fa-chevron-left" class="w-5 h-5" />
      </button>
      <h1 class="text-xl font-black text-slate-900 tracking-tight">
        AI Advisor
      </h1>
    </header>

    <div
      ref="messageContainer"
      :class="[
        'flex-1 w-full max-w-md md:max-w-2xl lg:max-w-3xl overflow-y-auto px-6 py-6 space-y-6 flex flex-col',
        isComponent ? '' : '',
      ]"
    >
      <div
        v-if="isHistoryLoading"
        class="w-full flex items-center justify-center py-10 flex-1"
      >
        <div class="animate-pulse flex flex-col items-center">
          <div
            class="w-8 h-8 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin mb-3"
          ></div>
          <p class="text-sm font-medium text-slate-400">
            Loading conversation...
          </p>
        </div>
      </div>

      <template v-else>
        <div v-for="(msg, index) in messages" :key="index" class="w-full">
          <!-- AI Message -->
          <div
            v-if="msg.sender === 'ai'"
            class="flex items-start space-x-3 max-w-[85%]"
          >
            <div
              class="w-8 h-8 rounded-xl bg-indigo-600 flex items-center justify-center text-white flex-shrink-0 shadow-lg shadow-indigo-100"
            >
              <font-awesome-icon icon="fa-solid fa-robot" class="w-4 h-4" />
            </div>
            <div
              class="bg-white px-5 py-3.5 rounded-2xl rounded-tl-none shadow-sm border border-slate-100"
            >
              <div v-if="msg.isLoading" class="flex space-x-1.5 py-1">
                <div
                  class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.3s]"
                ></div>
                <div
                  class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.15s]"
                ></div>
                <div
                  class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce"
                ></div>
              </div>
              <div v-else class="space-y-4">
                <!-- Money Recommendation Card -->
                <div
                  v-if="msg.money"
                  class="bg-indigo-50 border border-indigo-100 rounded-2xl p-4"
                >
                  <div
                    class="text-[11px] font-black text-indigo-500 uppercase tracking-widest mb-2"
                  >
                    Recommended Amount
                  </div>

                  <div class="text-xl font-black text-indigo-900">
                    {{ msg.money }}
                  </div>
                </div>

                <!-- AI Text -->
                <p
                  class="text-sm md:text-base text-slate-700 font-medium leading-relaxed whitespace-pre-wrap"
                >
                  {{ msg.text }}
                </p>
              </div>
            </div>
          </div>

          <!-- User Message -->
          <div v-else class="flex justify-end w-full">
            <div
              class="max-w-[85%] bg-slate-900 text-white px-5 py-3.5 rounded-2xl rounded-tr-none shadow-md shadow-slate-100"
            >
              <p class="text-sm md:text-base font-bold leading-relaxed">
                {{ msg.text }}
              </p>
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- Input Area -->
    <div
      class="w-full max-w-md md:max-w-2xl lg:max-w-3xl p-6 bg-white border-t border-slate-50 sticky bottom-0"
    >
      <div class="relative flex items-center">
        <input
          v-model="inputMessage"
          type="text"
          placeholder="Ask me anything..."
          class="w-full bg-slate-50 border border-slate-100 rounded-2xl py-4 pl-5 pr-14 text-sm md:text-base font-bold text-slate-800 placeholder-slate-300 focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-50 transition-all"
          @keyup.enter="sendMessage"
        />
        <button
          @click="sendMessage"
          class="absolute right-2 w-10 h-10 bg-indigo-600 text-white rounded-xl flex items-center justify-center shadow-lg shadow-indigo-100 active:scale-90 transition-all"
        >
          <font-awesome-icon icon="fa-solid fa-paper-plane" class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
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
const router = useRouter();
const messageContainer = ref<HTMLElement | null>(null);

const inputMessage = ref('');
const isHistoryLoading = ref(false);

const scrollToBottom = async () => {
  await nextTick();
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight;
  }
};

interface ChatMessage {
  sender: 'user' | 'ai';
  text?: string;
  isLoading?: boolean;

  // AI structured response
  money?: string;
  body?: string;
}

const messages = ref<ChatMessage[]>([]);

onMounted(async () => {
  await initializeChat();
});

watch(
  () => [props.roomId, route.query.roomId],
  async (newVal, oldVal) => {
    if (JSON.stringify(newVal) !== JSON.stringify(oldVal)) {
      await initializeChat();
    }
  },
);

const initializeChat = async () => {
  const roomId =
    props.roomId ||
    (route.query.roomId ? parseInt(route.query.roomId as string) : null);

  if (roomId) {
    isHistoryLoading.value = true;
    await fetchChatHistory(roomId);
    isHistoryLoading.value = false;

    // If still no messages after fetching, show initial welcome
    if (messages.value.length === 0) {
      showInitialMessage();
    }
  } else {
    showInitialMessage();
  }
};

const showInitialMessage = () => {
  messages.value = [];
  const category = props.category || route.query.category || 'General';
  const targetName = props.targetName || route.query.targetName || 'Person';
  const cultureBase = props.cultureBase || route.query.cultureBase || 'Global';

  const initialUserMessage = `Tell me more about etiquette for ${targetName} in a ${category} situation (Base: ${cultureBase}).`;

  messages.value.push({ sender: 'user', text: initialUserMessage });
  messages.value.push({ sender: 'ai', isLoading: true, text: '' });

  setTimeout(() => {
    const aiMessageIndex = messages.value.findIndex(
      (m) => m.sender === 'ai' && m.isLoading,
    );
    if (aiMessageIndex !== -1) {
      messages.value[aiMessageIndex].isLoading = false;
      messages.value[aiMessageIndex].text = `Of course! I can help you with ${targetName}'s ${category} event based on ${cultureBase} customs.\n\nWhat would you like to know specifically?`;
      scrollToBottom();
    }
  }, 1000);
};

const parseAIAnswer = (raw: string) => {
  if (!raw) return { body: '' };

  try {
    const parsed = JSON.parse(raw);

    return {
      money: parsed.money || '',
      body:
        parsed.text ||
        parsed.message ||
        parsed.fullReport ||
        parsed.summary ||
        parsed.analysis ||
        parsed.intro ||
        raw,
    };
  } catch {
    // Handle 2-line plain text format (intro \n amount)
    const lines = raw.split('\n').filter((l) => l.trim());
    if (lines.length >= 2) {
      const amountLine = lines[lines.length - 1];
      const amountMatch = amountLine.match(/(\d+)\s*(\w+)/);

      if (amountMatch) {
        return {
          money: amountLine.trim(),
          body: lines.slice(0, -1).join('\n').trim(),
        };
      }
    }
    return {
      body: raw,
    };
  }
};

const fetchChatHistory = async (roomId: any) => {
  try {
    const response = await apiClient.get(`/chat/list?formId=${roomId}`);
    if (response.data.success) {
      const chatItems = response.data.chatItems || [];

      messages.value = chatItems
        .filter((item: any) => {
          // Filter out automated analysis items (they start with { or are __CHAT_ITEM__)
          const q = item.question.trim();
          return q !== '__CHAT_ITEM__' && !q.startsWith('{');
        })
        .flatMap((item: any) => {
          const parsed = parseAIAnswer(item.answer);

          return [
            {
              sender: 'user',
              text: item.question,
            },
            {
              sender: 'ai',
              text: parsed.body,
              money: parsed.money,
            },
          ];
        });
      scrollToBottom();
    }
  } catch (error) {
    console.error('Error fetching chat history:', error);
  }
};

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return;

  const userText = inputMessage.value;
  const roomId =
    props.roomId ||
    (route.query.roomId ? parseInt(route.query.roomId as string) : null);

  messages.value.push({
    sender: 'user',
    text: userText,
  });

  inputMessage.value = '';
  scrollToBottom();

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
        question: userText,
      });

      const aiMessageIndex = messages.value.findIndex(
        (m) => m.sender === 'ai' && m.isLoading,
      );
      if (aiMessageIndex !== -1) {
        const parsed = parseAIAnswer(response.data.answer);

        messages.value[aiMessageIndex].isLoading = false;
        messages.value[aiMessageIndex].text = parsed.body;
        messages.value[aiMessageIndex].money = parsed.money;
        scrollToBottom();
      }
    } else {
      setTimeout(() => {
        const aiMessageIndex = messages.value.findIndex(
          (m) => m.sender === 'ai' && m.isLoading,
        );
        if (aiMessageIndex !== -1) {
          messages.value[aiMessageIndex].isLoading = false;
          messages.value[aiMessageIndex].text =
            'Please complete the survey first to save your questions.';
          scrollToBottom();
        }
      }, 1000);
    }
  } catch (error) {
    console.error('Error sending message:', error);
    const aiMessageIndex = messages.value.findIndex(
      (m) => m.sender === 'ai' && m.isLoading,
    );
    if (aiMessageIndex !== -1) {
      messages.value[aiMessageIndex].isLoading = false;
      messages.value[aiMessageIndex].text =
        'An error occurred. Please try again.';
      scrollToBottom();
    }
  }
};

watch(
  messages,
  () => {
    scrollToBottom();
  },
  { deep: true },
);
</script>

<style scoped>
.overflow-y-auto {
  scroll-behavior: smooth;
}
</style>
