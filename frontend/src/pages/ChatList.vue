<template>
  <div class="flex justify-center bg-gray-50 min-h-screen">
    <div
      class="w-full max-w-md md:max-w-2xl lg:max-w-4xl bg-white flex flex-col px-6 pt-12 pb-6 min-h-screen relative select-none"
    >
      <header class="flex items-center py-4 border-b border-slate-100 mb-6">
        <button
          @click="router.back()"
          class="mr-4 text-slate-600 hover:text-slate-900 active:scale-95 transition bg-white w-10 h-10 rounded-full flex items-center justify-center shadow-sm border border-slate-100"
        >
          <font-awesome-icon
            icon="fa-solid fa-chevron-left"
            class="w-4 h-4"
          />
        </button>
        <h1 class="text-xl md:text-2xl font-extrabold text-slate-950 text-ellipsis overflow-hidden whitespace-nowrap">
          {{ personName }}님 기록
        </h1>
      </header>

      <!-- 로딩 상태 -->
      <div v-if="isLoading" class="flex flex-col items-center justify-center h-64">
        <div class="w-10 h-10 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin mb-3"></div>
        <p class="text-sm font-medium text-slate-400">내역을 불러오는 중...</p>
      </div>

      <div
        v-else-if="combinedList.length === 0"
        class="flex flex-col items-center justify-center h-64 text-slate-400"
      >
        <p class="text-sm md:text-base font-medium">진행 중인 대화나 기록이 없습니다.</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
        <template v-for="(item, idx) in combinedList" :key="idx">
          <!-- 1. AI 상담 카드 -->
          <button
            v-if="item.type === 'consultation'"
            @click="enterChatRoom(item.roomId)"
            class="w-full flex items-center justify-between p-5 bg-white rounded-2xl border border-slate-100 shadow-[0_8px_25px_rgb(0,0,0,0.01)] hover:border-indigo-100 active:scale-[0.99] transition-all text-left group"
          >
            <div class="flex-1 min-w-0 pr-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-[10px] md:text-xs font-bold px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-600 uppercase">
                  AI 상담
                </span>
                <span class="text-[11px] md:text-xs text-slate-400 font-medium">{{ item.lastTime }}</span>
              </div>
              <h4 class="font-bold text-slate-800 text-sm md:text-base truncate mb-0.5 group-hover:text-indigo-600 transition-colors">
                {{ item.title }}
              </h4>
              <p class="text-xs md:text-sm text-slate-500 truncate font-medium">
                {{ item.lastMessage }}
              </p>
            </div>
            <div class="text-slate-300 group-hover:text-indigo-500 transition-colors">
              <font-awesome-icon icon="fa-solid fa-robot" class="w-5 h-5 md:w-6 md:h-6" />
            </div>
          </button>

          <!-- 2. 직접 기록 카드 (연하늘/연초록) -->
          <div
            v-else-if="item.type === 'history'"
            :class="[
              'w-full flex flex-col p-5 rounded-2xl border shadow-sm transition-all',
              item.received 
                ? 'bg-emerald-50/60 border-emerald-100 text-emerald-900' 
                : 'bg-sky-50/60 border-sky-100 text-sky-900'
            ]"
          >
            <div class="flex justify-between items-center mb-3">
              <span class="text-[10px] font-bold uppercase tracking-wider opacity-60 px-2 py-0.5 rounded-md bg-white/50">
                {{ item.received ? '내가 받음' : '내가 보냄' }}
              </span>
              <span class="text-[10px] font-bold opacity-50">{{ item.date }}</span>
            </div>
            <div class="flex justify-between items-end">
              <div>
                <h4 class="font-bold text-base md:text-lg mb-0.5">{{ item.category }}</h4>
                <p class="text-[11px] font-bold opacity-60">{{ item.targetName }}</p>
              </div>
              <div class="text-right">
                <span class="text-xl font-black">
                  {{ item.value.toLocaleString() }}
                </span>
                <span class="text-xs font-bold ml-1">원</span>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '../utils/api';

const route = useRoute();
const router = useRouter();

const personName = computed(() => route.params.personId as string);
const chatRooms = ref<any[]>([]);
const histories = ref<any[]>([]);
const isLoading = ref(true);

onMounted(async () => {
  try {
    await Promise.all([
      fetchChatRooms(),
      fetchHistories()
    ]);
  } finally {
    isLoading.value = false;
  }
});

const fetchChatRooms = async () => {
  try {
    const response = await apiClient.get('/form/list');
    if (response.data.success) {
      chatRooms.value = response.data.forms
        .filter((form: any) => form.targetName === personName.value)
        .map((form: any) => ({
          roomId: form.formId,
          type: 'consultation',
          title: `${form.targetName}님 상담 내역`,
          lastMessage: 'AI 분석 결과 보기',
          lastTime: new Date(form.updatedAt).toLocaleDateString(),
          category: '축하', // 기본값
          targetName: form.targetName,
          cultureBase: form.cultureBase
        }));
    }
  } catch (error) {
    console.error('상담 목록 조회 에러:', error);
  }
};

const fetchHistories = async () => {
  try {
    const response = await apiClient.get(`/history/list?targetName=${personName.value}`);
    if (response.data.success) {
      histories.value = response.data.histories.map((h: any) => ({
        ...h,
        type: 'history'
      }));
    }
  } catch (error) {
    console.error('기록 목록 조회 에러:', error);
  }
};

const combinedList = computed(() => {
  return [...chatRooms.value, ...histories.value].sort((a, b) => {
    const dateA = new Date(a.date || a.lastTime).getTime();
    const dateB = new Date(b.date || b.lastTime).getTime();
    return dateB - dateA;
  });
});

const enterChatRoom = (roomId: number) => {
  const room = chatRooms.value.find(r => r.roomId === roomId);
  if (room) {
    router.push({
      name: 'result',
      params: { category: room.category },
      query: { 
        targetName: room.targetName, 
        cultureBase: room.cultureBase,
        roomId: room.roomId
      }
    });
  }
};
</script>
