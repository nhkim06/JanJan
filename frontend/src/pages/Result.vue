<template>
  <div class="min-h-screen bg-slate-50 flex flex-col items-center p-6 pb-24 font-sans text-slate-800">
    <div v-if="isLoading" class="flex-1 flex flex-col items-center justify-center">
      <div class="w-12 h-12 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin mb-4"></div>
      <p class="text-slate-500 font-medium text-lg">AI is preparing your guide...</p>
    </div>

    <div v-else-if="!formDetail" class="flex-1 flex flex-col items-center justify-center">
      <p class="text-slate-400 font-medium">Data not found.</p>
      <button @click="goHome" class="mt-4 text-indigo-600 font-bold hover:underline">Go Home</button>
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
        <span class="text-sm font-extrabold text-slate-400 tracking-widest uppercase">Analysis Result</span>
        <div class="w-10"></div>
      </div>

      <!-- 1. Intro Card -->
      <div class="bg-white rounded-[32px] p-8 shadow-sm border border-slate-100 overflow-hidden relative group">
        <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 to-violet-500"></div>
        <div class="flex items-center space-x-3 mb-4">
           <span class="px-3 py-1 bg-indigo-50 text-indigo-600 rounded-lg text-[10px] font-black tracking-wider uppercase">
             {{ categoryName }}
           </span>
           <span class="text-[10px] font-bold text-slate-300">Base: {{ formDetail.cultureBase }}</span>
        </div>
        <h1 class="text-2xl md:text-3xl font-black text-slate-900 leading-tight">
          {{ aiReport.intro || `Custom guide for ${formDetail.targetName}.` }}
        </h1>
      </div>

      <!-- 2. Recommended Amount Card -->
      <div class="bg-indigo-600 rounded-[32px] p-10 shadow-xl shadow-indigo-100 flex flex-col items-center justify-center text-center text-white relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_30%_20%,_rgba(255,255,255,0.1),_transparent)]"></div>
        <h2 class="text-sm font-bold opacity-80 mb-2 uppercase tracking-widest">Recommended Amount</h2>
        <div class="flex items-baseline space-x-2">
          <span class="text-6xl md:text-7xl font-black tracking-tighter">
            {{ (aiReport.amount || 0).toLocaleString() }}
          </span>
          <span class="text-2xl font-bold opacity-90">{{ aiReport.currency || 'KRW' }}</span>
        </div>
      </div>

      <!-- 3. Etiquette & 4. Message Guide -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- 3. Etiquette Villain Prevention -->
        <div class="bg-rose-50/50 rounded-[32px] p-7 border border-rose-100 flex flex-col">
          <div class="flex items-center text-rose-600 font-black text-sm mb-4 tracking-tight uppercase">
            <font-awesome-icon icon="fa-solid fa-shield-halved" class="mr-2" />
            Etiquette Pitfalls
          </div>
          <div class="space-y-3">
             <div v-for="(tip, idx) in parsedVillainTips" :key="idx" class="flex items-start">
               <span class="text-rose-400 mt-1 mr-2 flex-shrink-0">•</span>
               <p class="text-sm md:text-base font-bold text-rose-900 leading-snug">{{ tip }}</p>
             </div>
          </div>
        </div>

        <!-- 4. Message Guide -->
        <div class="bg-emerald-50/50 rounded-[32px] p-7 border border-emerald-100 flex flex-col">
          <div class="flex items-center text-emerald-700 font-black text-sm mb-4 tracking-tight uppercase">
            <font-awesome-icon icon="fa-solid fa-pen-nib" class="mr-2" />
            Message Template
          </div>
          <div class="space-y-4">
             <div v-for="(msg, idx) in parsedMessages" :key="idx" class="bg-white/80 rounded-2xl p-4 border border-emerald-100/50 shadow-sm relative group cursor-pointer hover:border-emerald-300 transition-all active:scale-95" @click="copyToClipboard(msg)">
               <p class="text-xs md:text-sm font-bold text-emerald-900 italic leading-relaxed">"{{ msg }}"</p>
               <div class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                 <font-awesome-icon icon="fa-solid fa-copy" class="text-emerald-400 text-[10px]" />
               </div>
             </div>
          </div>
        </div>
      </div>

      <!-- 5. Full Report -->
      <div class="bg-white rounded-[32px] p-8 shadow-sm border border-slate-100 space-y-6">
        <div class="flex items-center justify-between border-b border-slate-50 pb-5">
           <div class="flex items-center text-slate-900 font-black text-sm tracking-tight uppercase">
             <font-awesome-icon icon="fa-solid fa-file-invoice" class="mr-2 text-indigo-500" />
             AI Full Analysis Report
           </div>
           <button @click="isReportExpanded = !isReportExpanded" class="text-xs font-bold text-slate-400 hover:text-indigo-600 transition-colors">
              {{ isReportExpanded ? 'Close' : 'View More' }}
           </button>
        </div>

        <div 
          :class="[
            'text-sm md:text-base leading-relaxed text-slate-600 font-medium whitespace-pre-wrap transition-all duration-500 overflow-hidden',
            isReportExpanded ? 'max-h-[2000px]' : 'max-h-40 relative'
          ]"
        >
          {{ aiReport.fullReport }}
          <div v-if="!isReportExpanded" class="absolute bottom-0 left-0 w-full h-20 bg-gradient-to-t from-white to-transparent"></div>
        </div>
      </div>

      <!-- AI Chat -->
      <div
        ref="chatSection"
        class="bg-white rounded-[32px] shadow-sm border border-slate-100 flex flex-col overflow-hidden h-[600px] scroll-mt-6"
      >
        <div class="p-6 md:p-8 flex items-center justify-between border-b border-slate-100 flex-shrink-0">
          <div class="flex items-center text-slate-900 font-black text-sm tracking-tight uppercase">
            <font-awesome-icon icon="fa-solid fa-wand-magic-sparkles" class="mr-2 text-indigo-500" />
            AI Real-time Q&A
          </div>
          <span class="text-[10px] font-bold text-slate-300">Ask anything about this event</span>
        </div>
        <div class="flex-1 overflow-hidden">
          <ChatAI
            is-component
            :category="categoryName"
            :target-name="formDetail.targetName"
            :culture-base="formDetail.cultureBase"
            :room-id="route.query.roomId"
          />
        </div>
      </div>
    </div>

    <!-- Floating Button -->
    <div class="fixed bottom-6 right-6 flex flex-col items-end space-y-3 z-50 group">
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
import { ref, onMounted, computed } from 'vue';
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

const categoryName = computed(() => {
  const cat = route.params.category as string || formDetail.value?.category;
  if (!cat) return 'Unknown';
  
  for (const groupKey in surveyData) {
    const group = (surveyData as any)[groupKey];
    if (group[cat]) {
      return group[cat].title;
    }
  }
  return 'Unknown';
});

const aiReport = computed(() => {
  return formDetail.value?.aiResponse || {};
});

const parsedVillainTips = computed(() => {
  const raw = aiReport.value.villainPreventionSummary;
  if (!raw) return [];
  if (Array.isArray(raw)) return raw;
  return raw.split('\n').map((line: string) => line.replace(/^[•\-\*\d\.]+\s*/, '').trim()).filter(Boolean);
});

const parsedMessages = computed(() => {
  const raw = aiReport.value.messageGuide;
  if (!raw) return [];
  if (Array.isArray(raw)) return raw;
  return raw.split('\n').map((line: string) => line.replace(/^[•\-\*\d\.]+\s*|^["']|["']$/g, '').trim()).filter(Boolean);
});

onMounted(async () => {
  const roomId = route.query.roomId;
  if (roomId) {
    try {
      const response = await apiClient.get(`/form/${roomId}`);
      if (response.data.success) {
        formDetail.value = response.data.form;
      }
    } catch (error) {
      console.error('Error loading result data:', error);
    } finally {
      isLoading.value = false;
    }
  } else {
    isLoading.value = false;
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
.max-h-40 {
  mask-image: linear-gradient(to bottom, black 50%, transparent 100%);
}
</style>
