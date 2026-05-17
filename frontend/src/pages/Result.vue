<template>
  <div
    class="min-h-screen bg-slate-50 flex flex-col items-center p-6 pb-24 font-sans text-slate-800"
  >
    <!-- Global Data Loading -->
    <div
      v-if="isLoading"
      class="flex-1 flex flex-col items-center justify-center"
    >
      <div
        class="w-12 h-12 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin mb-4"
      ></div>
      <p class="text-slate-500 font-medium text-lg">
        Initializing your custom guide...
      </p>
    </div>

    <div
      v-else-if="!formDetail"
      class="flex-1 flex flex-col items-center justify-center"
    >
      <p class="text-slate-400 font-medium">Data not found.</p>
      <button
        @click="goHome"
        class="mt-4 text-indigo-600 font-bold hover:underline"
      >
        Go Home
      </button>
    </div>

    <div v-else class="w-full max-w-md md:max-w-2xl lg:max-w-3xl space-y-6">
      <!-- Top Navigation -->
      <div class="flex items-center justify-between w-full py-2">
        <button
          @click="goHome"
          class="w-10 h-10 flex items-center justify-center bg-white rounded-full border border-slate-200 shadow-sm text-slate-600 hover:bg-slate-50 active:scale-95 transition"
        >
          <font-awesome-icon icon="fa-solid fa-house" class="h-4 w-4" />
        </button>
        <span
          class="text-sm font-extrabold text-slate-400 tracking-widest uppercase"
          >Analysis Result</span
        >
        <div class="w-10"></div>
      </div>

      <!-- 1. Welcome Greeting Card -->
      <div
        class="bg-white rounded-[32px] p-8 shadow-sm border border-slate-100 overflow-hidden relative group h-[160px] flex flex-col justify-center"
      >
        <div
          class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 to-violet-500"
        ></div>
        <div class="flex items-center space-x-3 mb-2">
          <span
            class="px-3 py-1 bg-indigo-50 text-indigo-600 rounded-lg text-[10px] font-black tracking-wider uppercase"
          >
            {{ categoryName }}
          </span>
          <span class="text-[10px] font-bold text-slate-300"
            >Base: {{ formDetail.cultureBase }}</span
          >
        </div>
        <div v-if="loadingSteps.amount" class="space-y-2 animate-pulse">
          <div class="h-8 bg-slate-100 rounded-lg w-3/4"></div>
        </div>
        <div v-else class="overflow-y-auto custom-scrollbar pr-2">
          <h1
            class="text-2xl md:text-3xl font-black text-slate-900 leading-tight"
          >
            {{
              aiReport.intro ||
              `Hello! Here is your custom guide for ${formDetail.targetName}.`
            }}
          </h1>
        </div>
      </div>

      <!-- 2. Recommended Amount Box -->
      <div
        class="bg-indigo-600 rounded-[32px] p-10 shadow-xl shadow-indigo-100 flex flex-col items-center justify-center text-center text-white relative overflow-hidden h-[200px]"
      >
        <div
          class="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_30%_20%,_rgba(255,255,255,0.1),_transparent)]"
        ></div>
        <h2 class="text-sm font-bold opacity-80 mb-2 uppercase tracking-widest">
          Recommended Amount
        </h2>

        <div
          v-if="loadingSteps.amount"
          class="flex flex-col items-center animate-pulse"
        >
          <div class="h-16 bg-white/20 rounded-2xl w-48 mb-4"></div>
        </div>
        <div v-else class="flex items-baseline space-x-2">
          <span class="text-6xl md:text-7xl font-black tracking-tighter">
            {{ (aiReport.amount || 0).toLocaleString() }}
          </span>
          <span class="text-2xl font-bold opacity-90">{{
            aiReport.currency || 'KRW'
          }}</span>
        </div>
      </div>

      <!-- [ADD] Outfit Recommendation Ad Card -->
      <div
        class="bg-gradient-to-br from-slate-900 to-slate-800 rounded-[32px] p-8 shadow-xl text-white relative overflow-hidden group cursor-pointer hover:scale-[1.01] transition-transform duration-300"
      >
        <div
          class="absolute top-0 right-0 w-32 h-32 bg-indigo-500/20 blur-3xl rounded-full -mr-10 -mt-10 group-hover:bg-indigo-500/30 transition-colors"
        ></div>
        <div class="relative flex items-center justify-between">
          <div class="space-y-2 max-w-[70%]">
            <span
              class="px-2 py-0.5 bg-amber-400 text-slate-900 rounded text-[9px] font-black uppercase tracking-wider"
              >Sponsored</span
            >
            <h3 class="text-xl md:text-2xl font-black leading-tight">
              Struggling with what to wear?
            </h3>
            <p class="text-xs md:text-sm font-medium text-slate-300">
              Get 1:1 premium styling advice for your upcoming
              {{ categoryName }} event.
            </p>
          </div>
          <div class="flex-shrink-0 ml-4">
            <div
              class="w-16 h-16 md:w-20 md:h-20 bg-white/10 backdrop-blur-md rounded-2xl flex items-center justify-center border border-white/20 group-hover:rotate-6 transition-transform"
            >
              <font-awesome-icon
                icon="fa-solid fa-shirt"
                class="text-3xl text-indigo-400"
              />
            </div>
          </div>
        </div>
        <button
          class="mt-6 w-full py-3 bg-white text-slate-900 rounded-2xl font-black text-sm hover:bg-slate-100 transition-colors flex items-center justify-center"
        >
          View Outfit Recommendations
          <font-awesome-icon
            icon="fa-solid fa-arrow-right"
            class="ml-2 text-xs"
          />
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- 3. Etiquette Summary Box -->
        <div
          class="bg-rose-50/50 rounded-[32px] p-7 border border-rose-100 flex flex-col h-[300px]"
        >
          <div
            class="flex items-center text-rose-600 font-black text-sm mb-4 tracking-tight uppercase flex-shrink-0"
          >
            <font-awesome-icon icon="fa-solid fa-shield-halved" class="mr-2" />
            Etiquette Summary
          </div>

          <div v-if="loadingSteps.etiquette" class="space-y-3 animate-pulse">
            <div v-for="i in 4" :key="i" class="flex items-center">
              <div class="w-2 h-2 bg-rose-200 rounded-full mr-2"></div>
              <div class="h-4 bg-rose-100 rounded w-full"></div>
            </div>
          </div>
          <div
            v-else
            class="space-y-3 flex-1 overflow-y-auto custom-scrollbar pr-2"
          >
            <div
              v-for="(tip, idx) in parsedVillainTips"
              :key="idx"
              class="flex items-start"
            >
              <span class="text-rose-400 mt-1 mr-2 flex-shrink-0">•</span>
              <p
                class="text-sm md:text-base font-bold text-rose-900 leading-snug"
              >
                {{ tip }}
              </p>
            </div>
            <p
              v-if="!parsedVillainTips.length && !loadingSteps.etiquette"
              class="text-xs text-rose-300 italic"
            >
              No specific summary available.
            </p>
          </div>
        </div>

        <!-- 4. Message Guide Box -->
        <div
          class="bg-emerald-50/50 rounded-[32px] p-7 border border-emerald-100 flex flex-col h-[300px]"
        >
          <div
            class="flex items-center text-emerald-700 font-black text-sm mb-4 tracking-tight uppercase flex-shrink-0"
          >
            <font-awesome-icon icon="fa-solid fa-pen-nib" class="mr-2" />
            Message Guide
          </div>

          <div v-if="loadingSteps.message" class="space-y-4 animate-pulse">
            <div
              v-for="i in 2"
              :key="i"
              class="p-4 bg-white/50 rounded-2xl h-16"
            ></div>
          </div>
          <div
            v-else
            class="space-y-4 flex-1 overflow-y-auto custom-scrollbar pr-2"
          >
            <div
              v-for="(msg, idx) in parsedMessages"
              :key="idx"
              class="bg-white/80 rounded-2xl p-4 border border-emerald-100/50 shadow-sm relative group cursor-pointer hover:border-emerald-300 transition-all active:scale-95"
              @click="copyToClipboard(msg)"
            >
              <p
                class="text-xs md:text-sm font-bold text-emerald-900 italic leading-relaxed"
              >
                "{{ msg }}"
              </p>
              <div
                class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <font-awesome-icon
                  icon="fa-solid fa-copy"
                  class="text-emerald-400 text-[10px]"
                />
              </div>
            </div>
            <p
              v-if="!parsedMessages.length && !loadingSteps.message"
              class="text-xs text-emerald-300 italic"
            >
              No templates available.
            </p>
          </div>
        </div>
      </div>

      <!-- 5. Full Analysis Report -->
      <div
        class="bg-white rounded-[32px] p-8 shadow-sm border border-slate-100 space-y-6 flex flex-col h-[500px]"
      >
        <div
          class="flex items-center justify-between border-b border-slate-50 pb-5 flex-shrink-0"
        >
          <div
            class="flex items-center text-slate-900 font-black text-sm tracking-tight uppercase"
          >
            <font-awesome-icon
              icon="fa-solid fa-file-invoice"
              class="mr-2 text-indigo-500"
            />
            AI Full Analysis Report
          </div>
        </div>

        <div
          v-if="loadingSteps.amount || loadingSteps.etiquette"
          class="space-y-3 animate-pulse"
        >
          <div class="h-4 bg-slate-100 rounded w-full"></div>
          <div class="h-4 bg-slate-100 rounded w-5/6"></div>
          <div class="h-4 bg-slate-100 rounded w-4/6"></div>
        </div>
        <div
          v-else
          class="flex-1 overflow-y-auto custom-scrollbar pr-4 space-y-8"
        >
          <!-- Report Section: Amount Analysis -->
          <div class="space-y-3">
            <h3
              class="text-xs font-black text-indigo-500 uppercase tracking-widest flex items-center sticky top-0 bg-white py-2 z-10"
            >
              <span class="w-6 h-px bg-indigo-100 mr-2"></span>
              Money & Gift Analysis
            </h3>
            <div
              class="text-sm md:text-base leading-relaxed text-slate-600 font-medium whitespace-pre-wrap p-5 bg-slate-50/50 rounded-2xl border border-slate-100/50"
            >
              {{ aiReport.amountProse || 'Waiting for amount analysis...' }}
            </div>
          </div>

          <!-- Report Section: Etiquette Analysis -->
          <div class="space-y-3">
            <h3
              class="text-xs font-black text-rose-500 uppercase tracking-widest flex items-center sticky top-0 bg-white py-2 z-10"
            >
              <span class="w-6 h-px bg-rose-100 mr-2"></span>
              Etiquette & Manners Analysis
            </h3>
            <div
              class="text-sm md:text-base leading-relaxed text-slate-600 font-medium whitespace-pre-wrap p-5 bg-slate-50/50 rounded-2xl border border-slate-100/50"
            >
              {{
                aiReport.etiquetteProse || 'Waiting for etiquette analysis...'
              }}
            </div>
          </div>
        </div>
      </div>

      <!-- 6. AI Q&A Section -->
      <div
        ref="chatSection"
        class="bg-white rounded-[32px] shadow-sm border border-slate-100 flex flex-col overflow-hidden h-[600px] scroll-mt-6"
      >
        <div
          class="p-6 md:p-8 flex items-center justify-between border-b border-slate-100 flex-shrink-0"
        >
          <div
            class="flex items-center text-slate-900 font-black text-sm tracking-tight uppercase"
          >
            <font-awesome-icon
              icon="fa-solid fa-wand-magic-sparkles"
              class="mr-2 text-indigo-500"
            />
            AI Real-time Q&A
          </div>
          <span class="text-[10px] font-bold text-slate-300"
            >Ask anything about this event</span
          >
        </div>
        <div class="flex-1 overflow-hidden">
          <ChatAI
            is-component
            :category="categoryName"
            :target-name="formDetail?.targetName"
            :culture-base="formDetail?.cultureBase"
            :room-id="route.query.roomId as string"
          />
        </div>
      </div>
    </div>

    <!-- Floating Chat Button -->
    <div
      class="fixed bottom-6 right-6 flex flex-col items-end space-y-3 z-50 group"
    >
      <button
        @click="scrollToChat"
        class="w-14 h-14 bg-slate-900 text-white hover:bg-slate-800 active:scale-90 transition-all duration-200 rounded-full flex items-center justify-center shadow-xl relative"
      >
        <font-awesome-icon icon="fa-solid fa-comments" class="h-5 w-5" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import surveyData from '@/assets/surveyData.json';
import ChatAI from './ChatAI.vue';
import apiClient from '../utils/api';

const route = useRoute();
const router = useRouter();

const chatSection = ref<HTMLElement | null>(null);
const isLoading = ref(true);
const isReportExpanded = ref(false);
const formDetail = ref<any>(null);

const loadingSteps = reactive({
  amount: false,
  etiquette: false,
  message: false,
});

const aiReport = ref({
  intro: '',
  amount: 0,
  currency: 'KRW',
  amountProse: '', // Original text for amount
  villainPreventionSummary: '',
  etiquetteProse: '', // Original text for etiquette
  messageGuide: '',
});

const categoryName = computed(() => {
  const cat = (route.params.category as string) || formDetail.value?.category;
  if (!cat) return 'Unknown';

  for (const groupKey in surveyData) {
    const group = (surveyData as any)[groupKey];
    if (group[cat]) {
      return group[cat].title;
    }
  }
  return 'Unknown';
});

const parsedVillainTips = computed(() => {
  const raw = aiReport.value.villainPreventionSummary;
  if (!raw) return [];
  if (Array.isArray(raw)) return raw;
  return raw
    .split('\n')
    .map((line: string) => line.replace(/^[•\-\*\d\.]+\s*/, '').trim())
    .filter(Boolean);
});

const parsedMessages = computed(() => {
  const raw = aiReport.value.messageGuide;
  if (!raw) return [];
  if (Array.isArray(raw)) return raw;
  return raw
    .split('\n')
    .map((line: string) =>
      line.replace(/^[•\-\*\d\.]+\s*|^["']|["']$/g, '').trim(),
    )
    .filter(Boolean);
});

const parseStepResult = (step: number, answer: string) => {
  if (step === 0) {
    try {
      // JSON 응답 대응
      const parsed = typeof answer === 'string' ? JSON.parse(answer) : answer;

      // intro 카드
      aiReport.value.intro =
        parsed.intro ||
        `${formDetail.value?.targetName || '상대'}를 위한 맞춤 가이드입니다.`;

      // money 문자열
      const moneyText = parsed.money || '';

      // "50,000 KRW ~ 100,000 KRW"
      const amountMatch = moneyText.match(/([\d,]+)\s*(KRW|USD|JPY|EUR)/i);

      if (amountMatch) {
        aiReport.value.amount = parseInt(amountMatch[1].replace(/,/g, ''));

        aiReport.value.currency = amountMatch[2];
      }

      // 전체 금액 텍스트 저장
      aiReport.value.amountProse = parsed.text || parsed.analysis || '';
    } catch (e) {
      // 기존 fallback
      aiReport.value.amountProse = answer;

      const lines = answer.split('\n').filter((l: string) => l.trim());

      if (lines.length >= 2) {
        aiReport.value.intro = lines[0];

        const amountMatch = lines[1].match(/(\d+)\s*(\w+)/);

        if (amountMatch) {
          aiReport.value.amount = parseInt(amountMatch[1]);
          aiReport.value.currency = amountMatch[2];
        }
      } else {
        aiReport.value.intro = answer;
      }
    }
  } else if (step === 1) {
    try {
      const etiquetteData =
        typeof answer === 'string' ? JSON.parse(answer) : answer;

      aiReport.value.villainPreventionSummary =
        etiquetteData.summary || etiquetteData.tips || '';

      aiReport.value.etiquetteProse =
        etiquetteData.fullReport || etiquetteData.text || answer;
    } catch (e) {
      aiReport.value.etiquetteProse = answer;
      aiReport.value.villainPreventionSummary = answer;
    }
  } else if (step === 2) {
    try {
      const messageData =
        typeof answer === 'string' ? JSON.parse(answer) : answer;

      aiReport.value.messageGuide =
        messageData.messages || messageData.text || '';
    } catch (e) {
      aiReport.value.messageGuide = answer;
    }
  }
};

onMounted(async () => {
  let roomId = route.query.roomId as string;
  const pendingFormStr = sessionStorage.getItem('pendingForm');

  try {
    // 1. If no roomId but pending data, create the form first
    if (!roomId && pendingFormStr) {
      const pendingData = JSON.parse(pendingFormStr);
      loadingSteps.amount = true;
      loadingSteps.etiquette = true;
      loadingSteps.message = true;

      const createResponse = await apiClient.post('/form/new', pendingData);
      if (createResponse.data.success) {
        roomId = createResponse.data.formId;
        router.replace({
          query: { ...route.query, roomId },
          params: route.params,
        });
        sessionStorage.removeItem('pendingForm');
      } else {
        const errorDetail =
          createResponse.data.detail || 'Failed to save form data';
        throw new Error(errorDetail);
      }
    }

    if (roomId) {
      // 2. Fetch Form Details
      const formResponse = await apiClient.get(`/form/${roomId}`);
      if (formResponse.data.success) {
        formDetail.value = formResponse.data.form;
      }

      isLoading.value = false;

      // 3. Fetch or Trigger Analysis
      const chatResponse = await apiClient.get(`/chat/list?formId=${roomId}`);
      if (chatResponse.data.success) {
        let chatItems = chatResponse.data.chatItems;

        chatItems.forEach((item: any, idx: number) => {
          if (idx < 3) parseStepResult(idx, item.answer);
        });

        const currentCount = chatItems.length;

        if (currentCount < 1) loadingSteps.amount = true;
        if (currentCount < 2) loadingSteps.etiquette = true;
        if (currentCount < 3) loadingSteps.message = true;

        if (currentCount < 1) {
          const res = await apiClient.post('/chat/new', {
            formId: roomId,
            question: '__CHAT_ITEM__',
          });
          if (res.data.success) parseStepResult(0, res.data.answer);
          loadingSteps.amount = false;
        } else {
          loadingSteps.amount = false;
        }

        if (currentCount < 2) {
          const res = await apiClient.post('/chat/new', {
            formId: roomId,
            question: '__CHAT_ITEM__',
          });
          if (res.data.success) parseStepResult(1, res.data.answer);
          loadingSteps.etiquette = false;
        } else {
          loadingSteps.etiquette = false;
        }

        if (currentCount < 3) {
          const res = await apiClient.post('/chat/new', {
            formId: roomId,
            question: '__CHAT_ITEM__',
          });
          if (res.data.success) parseStepResult(2, res.data.answer);
          loadingSteps.message = false;
        } else {
          loadingSteps.message = false;
        }
      }
    } else {
      isLoading.value = false;
    }
  } catch (error: any) {
    console.error('Error in Result page lifecycle:', error);
    const msg =
      error.response?.data?.detail ||
      error.message ||
      'Analysis failed. Please try again.';
    alert(`Error: ${msg}`);
    isLoading.value = false;
    loadingSteps.amount = false;
    loadingSteps.etiquette = false;
    loadingSteps.message = false;
  }
});

const goHome = () => {
  router.push('/');
};

const scrollToChat = () => {
  if (chatSection.value) {
    chatSection.value.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
};

const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text).then(() => {
    alert('Message copied to clipboard!');
  });
};
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}
</style>
